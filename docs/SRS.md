# Software Requirements Specification (SRS)

## SmartBalance: AI-Driven Intelligent Load Balancer

**Version:** 1.0
**Date:** 2026-05-04
**Project Status:** 100% Complete

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements for **SmartBalance**, an AI-driven load balancer that combines classical routing algorithms with LSTM-based traffic prediction for adaptive, real-time request distribution.

### 1.2 Scope

SmartBalance provides:
- Three load balancing algorithms (Round Robin, Least Connections, Weighted Round Robin)
- AI-based traffic prediction using LSTM neural networks
- Real-time WebSocket dashboard streaming
- Configurable traffic simulation for testing
- Automatic server health monitoring with failover
- RESTful API for management and configuration

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **Load Balancer** | System that distributes incoming traffic across multiple servers |
| **LSTM** | Long Short-Term Memory (recurrent neural network) |
| **Algorithm** | Mathematical rule for selecting target server |
| **Health Check** | Periodic verification of server availability |
| **Traffic Profile** | Configurable pattern for generating simulated load |
| **WebSocket** | Bidirectional real-time communication protocol |
| **API** | Application Programming Interface |
| **O(1), O(log n), O(n)** | Algorithm time complexity notations |

### 1.4 References

- [README.md](README.md) — Project overview and setup instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) — Technical architecture documentation
- [IEEE SRS Template](srs_template-ieee.pdf) — SRS format reference

### 1.5 Overview

Subsequent sections provide:
- **Section 2**: Overall product description and constraints
- **Section 3**: Detailed functional and non-functional requirements

---

## 2. Overall Description

### 2.1 Product Perspective

SmartBalance is a backend service that sits between client requests and a pool of backend servers. It uses AI to predict traffic spikes and automatically switches algorithms for optimal distribution.

```
                    ┌─────────────────────────────────┐
                    │         SmartBalance             │
Client Requests ──▶ │  ┌─────────┐   ┌──────────┐  │ ──▶ Server Pool
                    │  │ Smart   │──▶│  LSTM     │  │     ┌───┐ ┌───┐
                    │  │ Router  │   │ Predictor │  │     │ A │ │ B │
                    │  └────┬────┘   └───────────┘  │     └───┘ └───┘
                    │       │                         │
                    │  ┌────▼────────────────────┐   │
                    │  │  WebSocket Dashboard    │   │
                    │  └─────────────────────────┘   │
                    └─────────────────────────────────┘
```

### 2.2 Product Functions

#### 2.2.1 Load Balancing Algorithms

| ID | Function | Description |
|----|----------|-------------|
| F1.1 | Round Robin | Distributes requests evenly in circular order |
| F1.2 | Least Connections | Routes to server with fewest active connections |
| F1.3 | Weighted Round Robin | Distributes based on server weight/capacity |

#### 2.2.2 AI-Based Routing

| ID | Function | Description |
|----|----------|-------------|
| F2.1 | Traffic Prediction | LSTM model forecasts 15 steps ahead |
| F2.2 | Algorithm Switching | Automatically switches algorithms based on predicted load |
| F2.3 | Threshold Control | Configurable load threshold for switching (default: 150%) |

#### 2.2.3 Traffic Simulation

| ID | Function | Description |
|----|----------|-------------|
| F3.1 | Traffic Generation | Generates synthetic requests based on profile |
| F3.2 | Profile: Steady | Constant request rate |
| F3.3 | Profile: Burst | Alternating high/low periods |
| F3.4 | Profile: Ramp | Linear increase/decrease over time |
| F3.5 | Profile: Wave | Sinusoidal oscillation pattern |

#### 2.2.4 Health Monitoring

| ID | Function | Description |
|----|----------|-------------|
| F4.1 | Health Checks | Periodic HTTP health check to servers |
| F4.2 | Automatic Failover | Removes unhealthy servers from pool |
| F4.3 | Recovery Detection | Re-adds recovered servers automatically |

#### 2.2.5 Real-Time Dashboard

| ID | Function | Description |
|----|----------|-------------|
| F5.1 | WebSocket Streaming | Pushes live metrics to frontend |
| F5.2 | Server Updates | Broadcasts server health/connection status |
| F5.3 | Prediction Display | Streams LSTM forecast data |

### 2.3 User Classes and Characteristics

| User Class | Description | Typical Interaction |
|------------|-------------|---------------------|
| **Administrator** | Manages servers, configures algorithms | API calls via dashboard or curl |
| **Developer** | Integrates load balancer into application | REST API integration |
| **Tester** | Validates load balancing behavior | Traffic simulation controls |

### 2.4 Operating Environment

| Component | Technology |
|-----------|------------|
| Backend | Python 3.9+, FastAPI |
| ML Framework | PyTorch |
| Database | SQLite |
| Frontend | React + TypeScript + Tailwind CSS + Vite |
| Containerization | Docker + Docker Compose |
| Async HTTP | aiohttp |

### 2.5 Design and Implementation Constraints

| Constraint | Description |
|------------|-------------|
| **C1** | SQLite database (single-file, no external DB required) |
| **C2** | LSTM model runs on CPU (no GPU required) |
| **C3** | WebSocket connections limited by server resources |
| **C4** | Health checks are HTTP only (no HTTPS for internal checks) |
| **C5** | Single-instance deployment (no horizontal scaling of load balancer) |

### 2.6 Assumptions and Dependencies

| ID | Assumption/Dependency | Impact |
|----|----------------------|--------|
| A1 | Backend servers expose HTTP `/health` endpoint | Required for health checks |
| A2 | Server hardware is homogeneous (network latency similar) | Affects algorithm selection |
| A3 | Traffic patterns follow one of four predefined profiles | Limits prediction accuracy |
| D1 | `fastapi` >= 0.100 | API framework |
| D2 | `uvicorn` >= 0.20 | ASGI server |
| D3 | `torch` >= 2.0 | ML framework |
| D4 | `sqlalchemy` >= 2.0 | Database ORM |
| D5 | `aiohttp` >= 3.8 | Async HTTP client |

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 Server Management API

| ID | Requirement | Endpoint | Method |
|----|-------------|----------|--------|
| FR-SM-01 | List all registered servers | `/api/v1/servers` | GET |
| FR-SM-02 | Register a new server | `/api/v1/servers` | POST |
| FR-SM-03 | Get server details by ID | `/api/v1/servers/{id}` | GET |
| FR-SM-04 | Update server configuration | `/api/v1/servers/{id}` | PUT |
| FR-SM-05 | Remove a server | `/api/v1/servers/{id}` | DELETE |

**Request Body (POST/PUT)**:
```json
{
  "id": "server-1",
  "host": "192.168.1.10",
  "port": 8080,
  "weight": 2
}
```

#### 3.1.2 Algorithm Management API

| ID | Requirement | Endpoint | Method |
|----|-------------|----------|--------|
| FR-AM-01 | List available algorithms | `/api/v1/algorithms` | GET |
| FR-AM-02 | Get algorithm details | `/api/v1/algorithms/{name}` | GET |
| FR-AM-03 | Switch active algorithm | `/api/v1/algorithms/{name}/select` | POST |

**Algorithm Details Response**:
```json
{
  "name": "round_robin",
  "complexity": "O(1) circular distribution",
  "description": "Simple and fair for homogeneous pools"
}
```

#### 3.1.3 Traffic Simulation API

| ID | Requirement | Endpoint | Method |
|----|-------------|----------|--------|
| FR-TS-01 | Start traffic simulation | `/api/v1/simulation/start` | POST |
| FR-TS-02 | Stop traffic simulation | `/api/v1/simulation/stop` | POST |
| FR-TS-03 | Get simulation status | `/api/v1/simulation/status` | GET |

**Start Request Body**:
```json
{
  "profile": "burst",
  "base_rate": 100.0,
  "duration": 60
}
```

**Supported Profiles**: `steady`, `burst`, `ramp`, `wave`

#### 3.1.4 Real-Time Metrics WebSocket

| ID | Requirement | Endpoint |
|----|-------------|----------|
| FR-WS-01 | Connect to live metrics stream | `ws://localhost:8000/api/v1/metrics/live` |

**Message Types**:

```json
// Server Update
{
  "type": "server_update",
  "servers": [
    {
      "id": "server-1",
      "host": "192.168.1.10",
      "port": 8080,
      "healthy": true,
      "connections": 5
    }
  ]
}

// Routing Decision
{
  "type": "routing_decision",
  "algorithm": "round_robin",
  "selected_server": "server-1",
  "request_count": 150
}

// Traffic Prediction
{
  "type": "prediction",
  "predictions": [105.2, 112.8, 118.4, ...],
  "horizon": 15
}
```

#### 3.1.5 Load Balancing Logic

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-LB-01 | Round Robin Selection | Select servers in circular order, skip unhealthy |
| FR-LB-02 | Least Connections Selection | Select server with minimum connection count using min-heap |
| FR-LB-03 | Weighted Distribution | Allocate requests proportional to server weight |

#### 3.1.6 Smart Router Behavior

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-SR-01 | Auto-switch | Switch to Least Connections when predicted load > threshold × current load |
| FR-SR-02 | Fallback return | Return to primary algorithm when load normalizes |
| FR-SR-03 | Manual override | Allow forced algorithm switch via API |

**Default Threshold**: 150% (configurable)

#### 3.1.7 Health Monitoring

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-HM-01 | Periodic checks | Check server health every 5 seconds (configurable) |
| FR-HM-02 | Failure threshold | Mark unhealthy after 3 consecutive failures |
| FR-HM-03 | Recovery check | Attempt recovery check for unhealthy servers |

### 3.2 Non-Functional Requirements

#### 3.2.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-P01 | Algorithm selection | < 1ms per request |
| NFR-P02 | WebSocket latency | < 100ms message delivery |
| NFR-P03 | Health check response | < 2 seconds timeout |
| NFR-P04 | API response time | < 200ms for CRUD operations |

#### 3.2.2 Scalability

| ID | Requirement | Constraint |
|----|-------------|-------------|
| NFR-S01 | Server pool size | Up to 50 servers |
| NFR-S02 | Concurrent WebSocket connections | Up to 100 clients |
| NFR-S03 | Requests per second | Up to 10,000 RPS |

#### 3.2.3 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-R01 | Uptime | 99.9% (excluding planned maintenance) |
| NFR-R02 | Health check accuracy | 100% detection of unreachable servers |
| NFR-R03 | Algorithm switch success | Always succeeds or maintains previous algorithm |

#### 3.2.4 Security

| ID | Requirement | Status |
|----|-------------|--------|
| NFR-SC01 | CORS configuration | Allow all origins (configurable) |
| NFR-SC02 | API authentication | Not implemented (Phase 2) |
| NFR-SC03 | HTTPS support | Not implemented (Phase 2) |

#### 3.2.5 Maintainability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-M01 | Code coverage | 29 tests passing, core algorithms fully tested |
| NFR-M02 | Documentation | All public APIs documented |
| NFR-M03 | Logging | Structured logging for all operations |

### 3.3 Data Models

#### 3.3.1 Server Entity

```
Server {
  id: String (PK)
  host: String
  port: Integer
  weight: Integer (default: 1)
  connections: Integer (default: 0)
  healthy: Boolean (default: true)
  failure_count: Integer (default: 0)
  created_at: DateTime
  updated_at: DateTime
}
```

#### 3.3.2 Metric Entity

```
Metric {
  id: Integer (PK, auto)
  server_id: String (FK)
  timestamp: DateTime
  latency: Float
  error_rate: Float
  throughput: Float
}
```

#### 3.3.3 RoutingDecision Entity

```
RoutingDecision {
  id: Integer (PK, auto)
  algorithm: String
  selected_server_id: String
  request_count: Integer
  timestamp: DateTime
  extra_data: JSON
}
```

### 3.4 External Interface Requirements

#### 3.4.1 HTTP REST API

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins

#### 3.4.2 WebSocket Protocol

- **Endpoint**: `/api/v1/metrics/live`
- **Protocol**: WSS (WebSocket Secure) when HTTPS enabled
- **Heartbeat**: Client should send ping every 30 seconds

#### 3.4.3 Backend Server Contract

Backend servers must implement:
- `GET /health` — Returns 200 OK when healthy
- Accept HTTP requests on configured port

---

## Appendix A: Current Implementation Status

| Component | Status | Details |
|-----------|--------|---------|
| Load Balancing Algorithms | **Complete** | Round Robin, Least Connections, Weighted Round Robin — 100% tested |
| Smart Router | **Complete** | Auto-switch logic with configurable threshold |
| LSTM Predictor | **Complete** | 2-layer LSTM, 64 hidden units, pre-trained on 4 patterns |
| Traffic Simulation | **Complete** | 4 profiles: Steady, Burst, Ramp, Wave |
| Health Monitoring | **Complete** | Async with aiohttp, configurable interval/failure threshold |
| WebSocket Streaming | **Complete** | Real-time broadcast to all connected clients |
| Server Pool Management | **Complete** | Full CRUD operations via REST API |
| REST API | **Complete** | FastAPI with 4 routers: servers, algorithms, metrics, simulation |
| Frontend Dashboard | **Complete** | React + TypeScript + Tailwind CSS + Recharts |
| Unit Tests | **Complete** | 29 tests passing, covers all algorithms and Server model |
| Docker | **Complete** | Dockerfile + docker-compose.yml for full-stack deployment |
| Documentation | **Complete** | README, ARCHITECTURE.md, SRS.md, SRS.docx |

### Test Coverage Summary
- Total Tests: 29
- Status: All Passing
- Coverage: Algorithms (Round Robin, Least Connections, Weighted Round Robin), Algorithm Registry, Server model

---

## Appendix B: Future Enhancements (Out of Scope)

- HTTPS/TLS termination
- API authentication (JWT/OAuth2)
- gRPC protocol support
- Layer 4 (TCP/UDP) load balancing
- Horizontal scaling with multiple instances
- Prometheus/Grafana integration
- Custom traffic profile definitions
- Multi-tenant support

---

**Document Version**: 1.0
**Last Updated**: 2026-05-04
**Author**: Project Team