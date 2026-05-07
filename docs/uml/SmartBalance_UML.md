# SmartBalance - UML Documentation

This document contains UML diagrams for the SmartBalance AI-driven load balancer system.

## System Architecture Overview

```mermaid
graph TB
    subgraph Frontend["Frontend (React/Vite)"]
        Dashboard["Dashboard.tsx"]
        ServerList["ServerList.tsx"]
        MetricsChart["MetricsChart.tsx"]
        TrafficSimulator["TrafficSimulator.tsx"]
        WebSocketHook["useWebSocket.ts"]
        MetricsHook["useMetrics.ts"]
    end

    subgraph Backend["Backend (FastAPI/Python)"]
        subgraph Core["Core - Load Balancing"]
            LB_Abstract["LoadBalancer (abstract)"]
            RR_LB["RoundRobinLB"]
            LC_LB["LeastConnectionsLB"]
            WRR_LB["WeightedRoundRobinLB"]
            Smart_Router["SmartRouter"]
        end

        subgraph ML["ML - LSTM Prediction"]
            LSTM["LSTMModel"]
            Predictor["TrafficPredictor"]
        end

        subgraph Simulation["Simulation Engine"]
            TrafficGen["TrafficGenerator"]
            HealthCheck["HealthChecker"]
            FaultInject["FaultInjector"]
        end

        subgraph Services["Services"]
            RoutingSvc["RoutingService"]
            WSManager["WebSocketManager"]
        end

        subgraph Routers["API Routers"]
            ServersAPI["servers_router"]
            AlgosAPI["algorithms_router"]
            SimAPI["simulation_router"]
            MetricsAPI["metrics_router"]
        end

        subgraph Data["Data Layer"]
            ServerModel["Server.model"]
            MetricModel["Metric.model"]
            RoutingModel["RoutingDecision.model"]
        end
    end

    subgraph Database["Database"]
        DB[("SQLite")]
    end

    Dashboard --> WebSocketHook
    ServerList --> WebSocketHook
    MetricsChart --> MetricsHook
    TrafficSimulator --> WebSocketHook
    WebSocketHook --> WSManager
    MetricsHook --> WSManager

    LB_Abstract <|-- RR_LB
    LB_Abstract <|-- LC_LB
    LB_Abstract <|-- WRR_LB
    LB_Abstract <|-- Smart_Router

    Smart_Router --> Predictor
    Smart_Router --> LC_LB
    RoutingSvc --> LB_Abstract
    RoutingSvc --> WSManager

    TrafficGen --> RoutingSvc
    HealthCheck --> RoutingSvc

    ServersAPI --> RoutingSvc
    AlgosAPI --> RoutingSvc
    SimAPI --> TrafficGen

    ServerModel --> DB
    MetricModel --> DB
    RoutingModel --> DB
```

## Class Diagram - Core Load Balancing

```mermaid
classDiagram
    class Server {
        +str id
        +str host
        +int port
        +int weight
        +int connections
        +bool healthy
        +int failure_count
        +datetime last_health_check
        +increment_connections()
        +decrement_connections()
        +mark_unhealthy()
        +mark_healthy()
    }

    class LoadBalancer {
        <<abstract>>
        +name: str
        +description: str
        +complexity: str
        +select_server(servers) Server
        +filter_healthy(servers) List~Server~
        +get_least_busy_server(servers) Server
    }

    class RoundRobinLB {
        -int current_index
        +select_server(servers) Server
        +name: str = "Round Robin"
        +complexity: str = "O(1)"
    }

    class LeastConnectionsLB {
        -List connection_heap
        +select_server(servers) Server
        +name: str = "Least Connections"
        +complexity: str = "O(log n)"
    }

    class WeightedRoundRobinLB {
        -Dict current_weights
        -bool cycle_complete
        +select_server(servers) Server
        +name: str = "Weighted Round Robin"
        +complexity: str = "O(n)"
    }

    class SmartRouter {
        -LoadBalancer inner_algorithm
        -float prediction_threshold = 1.5
        -TrafficPredictor traffic_predictor
        +select_server(servers) Server
        +update_predictions(traffic_rates)
        +should_switch_algorithm(prediction) bool
        +name: str = "Smart Router"
    }

    LoadBalancer <|-- RoundRobinLB
    LoadBalancer <|-- LeastConnectionsLB
    LoadBalancer <|-- WeightedRoundRobinLB
    LoadBalancer <|-- SmartRouter
    SmartRouter o-- LoadBalancer
    SmartRouter o-- TrafficPredictor
```

## Class Diagram - ML Prediction

```mermaid
classDiagram
    class LSTMModel {
        -nn.LSTM lstm
        -Sequential fc
        -int hidden_size = 64
        -int num_layers = 2
        -int output_steps = 15
        +forward(x) Tensor
    }

    class TrafficPredictor {
        -int window_size = 60
        -int forecast_steps = 15
        -LSTMModel model
        -List trajectory
        -bool is_trained
        +add_traffic_sample(rate: float)
        +predict() List~float~
        +get_mape(actual, predicted) float
        +train_model(X, y, epochs)
    }

    class RoutingService {
        -List servers
        -LoadBalancer load_balancer
        -TrafficPredictor predictor
        -WebSocketManager ws_manager
        +register_server(server)
        +remove_server(server_id)
        +route_request() RoutingResult
        +switch_algorithm(name)
        +get_metrics()
    }

    TrafficPredictor o-- LSTMModel
    RoutingService o-- LoadBalancer
    RoutingService o-- TrafficPredictor
    RoutingService o-- Server
```

## Sequence Diagram - Request Routing

```mermaid
sequenceDiagram
    actor Client
    participant FE as Frontend Dashboard
    participant WS as WebSocket
    participant Routing as RoutingService
    participant LB as LoadBalancer
    participant Predictor as LSTM Predictor
    participant Backend as Backend Server

    Client->>FE: HTTP Request
    FE->>WS: Route Request
    WS->>Routing: route_request()
    Routing->>LB: select_server(servers)
    LB->>Backend: Select Server
    Backend-->>LB: Selected Server
    LB-->>Routing: RoutingResult
    Routing->>WS: Broadcast Update
    WS-->>FE: Server Update
    FE-->>Client: Response

    alt Predicted Load > 150% Capacity
        Routing->>Predictor: predict_next()
        Predictor-->>Routing: predictions[]
        Routing->>Routing: switch_algorithm("least_connections")
        Routing->>LB: Update Algorithm
        Routing->>WS: Broadcast Algorithm Change
    end
```

## Sequence Diagram - Traffic Simulation

```mermaid
sequenceDiagram
    actor Operator
    participant FE as Frontend Dashboard
    participant WS as WebSocket
    participant Routing as RoutingService
    participant TrafficGen as TrafficGenerator
    participant HealthCheck as HealthChecker
    participant Server as Backend Server

    Operator->>FE: Configure Simulation
    FE->>WS: /simulation/config
    WS->>Routing: Update Config
    Routing->>TrafficGen: Apply Profile

    loop Every Interval
        TrafficGen->>Routing: Generate Traffic
        Routing->>Server: Route Request
        Server-->>Routing: Response
    end

    loop Every 5 seconds
        HealthCheck->>Server: Health Check
        alt 3 Consecutive Failures
            HealthCheck->>Server: mark_unhealthy()
            HealthCheck->>WS: Broadcast Health Update
        else Server Responds
            HealthCheck->>Server: mark_healthy()
        end
    end
```

## State Diagram - Server Health

```mermaid
stateDiagram-v2
    [*] --> Healthy
    Healthy --> Degraded: Single Health Check Failure
    Degraded --> Healthy: Health Check Success
    Degraded --> Unhealthy: 3 Consecutive Failures
    Unhealthy --> Degraded: Manual Recovery
    Unhealthy --> Healthy: Automatic Recovery
    Healthy --> [*]: Removed from Pool
    Unhealthy --> [*]: Removed from Pool
```

## State Diagram - Algorithm Selection

```mermaid
stateDiagram-v2
    [*] --> RoundRobin

    state RoundRobin {
        [*] --> NormalTraffic
        NormalTraffic --> UnderLoad: Traffic Increases
        UnderLoad --> NormalTraffic: Traffic Decreases
    }

    state LeastConnections {
        [*] --> BurstTraffic
        BurstTraffic --> Balancing: Traffic Stabilizes
        Balancing --> BurstTraffic: New Burst Detected
    }

    RoundRobin --> LeastConnections: Predicted Load > 150%
    LeastConnections --> RoundRobin: Load Returns Normal
```

## Data Model

```mermaid
erDiagram
    Server {
        string id PK
        string host
        int port
        int weight
        int connections
        bool healthy
        int failure_count
        datetime created_at
        datetime updated_at
    }

    Metric {
        int id PK
        string server_id FK
        datetime timestamp
        float latency
        float error_rate
        float throughput
    }

    RoutingDecision {
        int id PK
        string algorithm
        string selected_server_id
        int request_count
        datetime timestamp
        json extra_data
    }

    Server ||--o{ Metric : "has many"
    Server ||--o{ RoutingDecision : "generates"
```

## API Endpoints

```mermaid
graph LR
    subgraph Servers["Server Management"]
        GET_S["GET /api/v1/servers"]
        POST_S["POST /api/v1/servers"]
        GET_S_ID["GET /api/v1/servers/{id}"]
        PUT_S["PUT /api/v1/servers/{id}"]
        DEL_S["DELETE /api/v1/servers/{id}"]
    end

    subgraph Algorithms["Algorithm Control"]
        GET_A["GET /api/v1/algorithms"]
        POST_A["POST /api/v1/algorithms/{name}/select"]
        GET_A_STATS["GET /api/v1/algorithms/stats"]
    end

    subgraph Simulation["Traffic Simulation"]
        POST_START["POST /api/v1/simulation/start"]
        POST_STOP["POST /api/v1/simulation/stop"]
        GET_CONFIG["GET /api/v1/simulation/config"]
        PUT_CONFIG["PUT /api/v1/simulation/config"]
    end

    subgraph Metrics["Metrics & Predictions"]
        GET_METRICS["GET /api/v1/metrics"]
        WS_LIVE["WS /api/v1/metrics/live"]
        GET_PRED["GET /api/v1/predictions"]
    end

    subgraph Health["System"]
        GET_HEALTH["GET /health"]
    end
```

## Algorithm Specifications

| Algorithm | Time Complexity | Use Case |
|-----------|-----------------|----------|
| Round Robin | O(1) | Default, even traffic distribution |
| Least Connections | O(log n) | Variable request durations |
| Weighted Round Robin | O(n) | Servers with different capacities |
| Smart Router | O(n) | AI-driven auto-switching based on LSTM predictions |

## LSTM Model Architecture

```
Input Layer: 60-step sliding window (normalized request rates)
           ↓
Hidden Layer 1: LSTM (64 units, dropout=0.2)
           ↓
Hidden Layer 2: LSTM (64 units, dropout=0.2)
           ↓
Fully Connected: Linear(64 → 32 → 15)
           ↓
Output Layer: 15-step ahead forecast
```

**Training:**
- Loss: MSE with Adam optimizer
- Target MAPE: < 15%
- Patterns: Steady, Burst, Ramp, Wave

---

*Generated from SmartBalance codebase - AI-Driven Load Balancer System*
