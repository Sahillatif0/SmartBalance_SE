# SmartBalance System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend Layer (React/TypeScript)"]
        App["App.tsx"]
        Dashboard["Dashboard.tsx"]
        ServerList["ServerList.tsx"]
        MetricsChart["MetricsChart.tsx"]
        TrafficSimulator["TrafficSimulator.tsx"]
        AlgorithmSelector["AlgorithmSelector.tsx"]
        ForecastOverlay["ForecastOverlay.tsx"]
        RoutingLog["RoutingLog.tsx"]
        WebSocketHook["useWebSocket.ts"]
        API["api.ts"]
    end

    subgraph Backend["Backend Layer (Python/FastAPI)"]
        FastAPI["FastAPI Application"]
        Routers["API Routers"]
        Servers["servers.py"]
        Algorithms["algorithms.py"]
        Metrics["metrics.py"]
        Simulation["simulation.py"]

        subgraph Core["Core Load Balancing"]
            LoadBalancer["LoadBalancer (Abstract)"]
            RoundRobin["RoundRobinLB"]
            LeastConnections["LeastConnectionsLB"]
            WeightedRR["WeightedRoundRobinLB"]
            SmartRouter["SmartRouter"]
            Registry["AlgorithmRegistry"]
        end

        subgraph ML["ML Module"]
            LSTM["LSTMModel (PyTorch)"]
            Predictor["TrafficPredictor"]
            MetricsCalc["metrics_calculator.py"]
        end

        subgraph Simulation["Simulation Module"]
            TrafficGen["TrafficGenerator"]
            HealthCheck["HealthChecker"]
            ServerPool["ServerPool"]
            EventBus["EventBus"]
        end

        Services["Services Layer"]
        WebSocketMgr["websocket_manager.py"]
        Database["Database (SQLite/SQLAlchemy)"]
    end

    App --> Dashboard
    Dashboard --> ServerList
    Dashboard --> MetricsChart
    Dashboard --> TrafficSimulator
    Dashboard --> AlgorithmSelector
    Dashboard --> ForecastOverlay
    Dashboard --> RoutingLog

    Dashboard --> WebSocketHook
    WebSocketHook --> API

    API --> FastAPI
    FastAPI --> Routers

    Routers --> Servers
    Routers --> Algorithms
    Routers --> Metrics
    Routers --> Simulation

    Algorithms --> Registry
    Registry --> RoundRobin
    Registry --> LeastConnections
    Registry --> WeightedRR

    SmartRouter --> Registry
    SmartRouter --> Predictor

    Simulation --> TrafficGen
    Simulation --> HealthCheck

    Routers --> Services
    Services --> WebSocketMgr
    Services --> Database

    TrafficGen --> LSTM
    Predictor --> LSTM
```

## Component Descriptions

| Layer | Component | Description |
|-------|-----------|-------------|
| Frontend | Dashboard.tsx | Main grid container managing layout |
| Frontend | ServerList.tsx | Real-time server health cards |
| Frontend | MetricsChart.tsx | Recharts visualizations |
| Frontend | useWebSocket.ts | WebSocket connection hook |
| Backend | LoadBalancer | Abstract base class for algorithms |
| Backend | SmartRouter | AI-driven algorithm switching |
| Backend | LSTMModel | PyTorch two-layer LSTM |
| Backend | TrafficGenerator | Profile-based traffic simulation |
| Backend | HealthChecker | Background health monitoring |