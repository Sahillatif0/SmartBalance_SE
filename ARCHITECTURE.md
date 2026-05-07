# SmartBalance Technical Architecture

## Overview

SmartBalance is an AI-driven intelligent load balancer that combines classical load balancing algorithms with LSTM-based traffic prediction for adaptive, real-time request routing.

---

## Core Features

### 1. Load Balancing Algorithms

SmartBalance implements three classical algorithms via an abstract base class:

| Algorithm | Time Complexity | Use Case |
|-----------|-----------------|----------|
| Round Robin | O(1) | Homogeneous servers, simple deployments |
| Least Connections | O(log n) | Variable-duration requests, heterogeneous workloads |
| Weighted Round Robin | O(n) | Servers with different capacities |

#### Round Robin (`round_robin.py`)
```
Requests → [Server A] → [Server B] → [Server C] → [Server A] → ...
```
- Cycles through healthy servers in order
- Ignores server load or capacity
- Maintains `_current_index` counter

#### Least Connections (`least_connections.py`)
```
Requests → Server with fewest active connections
```
- Uses a **min-heap** data structure for O(log n) selection
- Adaptive to varying request durations
- Heap entries: `(connection_count, index, server_id)`

#### Weighted Round Robin (`weighted_rr.py`)
- Servers receive requests proportional to weight
- Higher weight = more requests allocated

#### Algorithm Registry (`algorithm_registry.py`)
- Factory pattern for algorithm instantiation
- Algorithms registered by name string

---

### 2. Smart Router (AI-Driven Routing)

**File**: `core/smart_router.py`

The Smart Router is the core AI component that **automatically switches between algorithms** based on predicted traffic.

```
Traffic Pattern → LSTM Predictor → Load Evaluation → Algorithm Switch
                                                    ↓
                              Round Robin ←→ Least Connections
```

**Switch Logic**:
```python
if max_predicted_load > (threshold × current_load):
    switch to Least Connections  # Handle high load
else:
    switch to Round Robin       # Optimal for steady state
```

**Default Threshold**: 150% (configurable via `settings.smart_router_threshold`)

**Key Properties**:
- `_switch_count`: Number of algorithm transitions
- `_using_fallback`: Boolean flag indicating current mode
- `force_switch()`: Manual algorithm override

---

### 3. LSTM Traffic Prediction

**File**: `ml/lstm_model.py`

Two-layer LSTM neural network for traffic forecasting.

#### Architecture
```
Input:  60-step sliding window (normalized request rates)
    ↓
LSTM Layer 1: 64 hidden units, dropout=0.2
    ↓
LSTM Layer 2: 64 hidden units, dropout=0.2
    ↓
Dense Layer: 64 → 32 (ReLU activation)
    ↓
Output: 15-step ahead predictions
```

#### Training
- Pre-initialized with **4 synthetic traffic patterns**:
  - **Steady**: Constant baseline ± Gaussian noise
  - **Burst**: 50% duty cycle (high/low alternation)
  - **Ramp**: Linear increase over time
  - **Wave**: Sinusoidal pattern

#### Prediction Flow
```
1. Traffic sample added to 60-step trajectory buffer
2. Buffer normalized to [0, 1] range
3. LSTM forward pass → 15 denormalized predictions
4. Gaussian noise added for realism
```

#### API
```python
predictor = TrafficPredictor(window_size=60, forecast_steps=15)
predictor.add_traffic_sample(request_rate)
predictions = predictor.predict()  # List[15 float values]
```

---

### 4. Traffic Simulation

**Files**: `simulation/traffic_generator.py`, `traffic_simulator.py`

Generates synthetic traffic for testing load balancing behavior.

#### Traffic Profiles
| Profile | Behavior |
|---------|----------|
| `steady` | Constant rate with minimal variance |
| `burst` | Alternating high/low periods (simulates traffic spikes) |
| `ramp` | Linear increase or decrease over time |
| `wave` | Sinusoidal pattern (mimics daily traffic cycles) |

#### TrafficGenerator Class
```python
generator = TrafficGenerator(profile=TrafficProfile.STEADY, base_rate=100.0)
generator.start()
requests = generator.generate_traffic(delta_time=1.0)  # Requests in last second
```

---

### 5. Health Monitoring

**File**: `simulation/health_checker.py`

Background service that monitors server health via HTTP health checks.

#### Configuration
```python
interval = 5 seconds (default)
failure_threshold = 3 consecutive failures
timeout = 2 seconds per check
```

#### Health Check Flow
```
For each server:
  1. GET http://{host}:{port}/health
  2. Success (200) → reset failure_count
  3. Failure → increment failure_count
  4. If failure_count >= threshold → mark unhealthy
```

#### Async Implementation
- Uses `aiohttp` for non-blocking HTTP requests
- Parallel checks via `asyncio.gather()`
- Callbacks: `on_unhealthy`, `on_healthy`

---

### 6. Real-Time WebSocket Streaming

**File**: `services/websocket_manager.py`

Pushes live metrics to the frontend dashboard.

#### Message Types
| Type | Payload |
|------|---------|
| `server_update` | Current server list with health/connections |
| `routing_decision` | Selected server, algorithm used |
| `prediction` | 15-step LSTM forecast array |

#### API
```python
await ws_manager.broadcast({"type": "prediction", "predictions": [...]})
await ws_manager.broadcast_server_update([...])
```

---

### 7. Server Pool Management

**File**: `simulation/server_pool.py`

Manages the dynamic server registry.

#### Server Entity
```python
@dataclass
class Server:
    id: str
    host: str
    port: int
    weight: int = 1
    connections: int = 0
    healthy: bool = True
    failure_count: int = 0
```

#### Operations
- Add/remove servers dynamically
- Track active connections per server
- Coordinate with health checker

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/servers` | GET | List all servers |
| `/api/v1/servers` | POST | Register new server |
| `/api/v1/servers/{id}` | DELETE | Remove server |
| `/api/v1/algorithms` | GET | List available algorithms |
| `/api/v1/algorithms/{name}/select` | POST | Switch active algorithm |
| `/api/v1/simulation/start` | POST | Start traffic simulation |
| `/api/v1/metrics/live` | WebSocket | Real-time metrics stream |
| `/health` | GET | Service health check |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│   WebSocket Connection ── Real-time Dashboard                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WS / HTTP
┌─────────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Servers  │  │Algorithms│  │Simulation│  │  WebSocket   │    │
│  │ Router   │  │ Router   │  │  Router  │  │   Manager    │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘    │
│       └──────────────┼─────────────┼───────────────┘             │
│                      ▼                                           │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    Smart Router                           │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐  │   │
│  │  │ LSTM Model  │───▶│  Threshold  │───▶│   Algorithm │  │   │
│  │  │  Predictor  │    │  Evaluator  │    │   Switcher  │  │   │
│  │  └─────────────┘    └─────────────┘    └──────┬───────┘  │   │
│  └─────────────────────────────────────────────────│─────────┘   │
│                      ┌───────────────────────────┼───┐          │
│                      ▼                           ▼   ▼          │
│              ┌───────────────┐  ┌────────────────────────┐      │
│              │  Load          │  │   Traffic Simulator    │      │
│              │  Balancers     │  │   (generates requests)│      │
│              └───────┬────────┘  └────────────────────────┘      │
└──────────────────────┼───────────────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   Server Pool    │
              │  ┌───┐ ┌───┐    │
              │  │ A │ │ B │    │
              │  └───┘ └───┘    │
              └──────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI |
| ML Framework | PyTorch |
| Database | SQLite |
| Async HTTP | aiohttp |
| Frontend | React + TypeScript |
| Styling | Tailwind CSS |
| Build Tool | Vite |
| Containerization | Docker |

---

## Configuration

Environment variables in `backend/app/config.py`:
- `health_check_interval`: Health check frequency (seconds)
- `health_check_failure_threshold`: Failures before marking unhealthy
- `smart_router_threshold`: Load threshold for algorithm switching
- `app_name`, `app_version`: Service metadata