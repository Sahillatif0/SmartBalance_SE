# SmartBalance Deployment Diagram

```mermaid
graph TB
    subgraph Clients["Client Layer"]
        Browser["Web Browser"]
    end

    subgraph WebServer["Web Server Layer"]
        Nginx["Nginx Reverse Proxy"]
    end

    subgraph Application["Application Layer"]
        FastAPI["FastAPI Application"]
        Uvicorn["Uvicorn ASGI Server"]

        subgraph BackendApp["Backend Application"]
            Routers["API Routers"]
            Core["Load Balancing Core"]
            ML["ML Module"]
            Simulation["Simulation"]
        end
    end

    subgraph Data["Data Layer"]
        SQLite["SQLite Database"]
    end

    subgraph Containers["Container Orchestration"]
        DockerCompose["docker-compose.yml"]
        Docker1["FastAPI Container"]
        Docker2["React Frontend"]
        Docker3["Nginx Container"]
    end

    Browser -->|HTTPS| Nginx
    Nginx -->|Proxy| Uvicorn
    Uvicorn -->|Runs| FastAPI

    FastAPI -->|Uses| Routers
    FastAPI -->|Uses| Core
    FastAPI -->|Uses| ML
    FastAPI -->|Uses| Simulation

    FastAPI -->|CRUD| SQLite
    FastAPI -->|WebSocket| Browser

    DockerCompose -->|Orchestrates| Docker1
    DockerCompose -->|Orchestrates| Docker2
    DockerCompose -->|Orchestrates| Docker3
```

## Environment Configuration

```mermaid
graph LR
    subgraph Config["Configuration (.env)"]
        DB["DATABASE_URL"]
        HCI["HEALTH_CHECK_INTERVAL"]
        HCF["HEALTH_CHECK_FAILURE_THRESHOLD"]
        LWS["LSTM_WINDOW_SIZE"]
        LFS["LSTM_FORECAST_STEPS"]
        SRT["SMART_ROUTER_THRESHOLD"]
        MTR["MAPE_TARGET"]
    end

    subgraph Defaults["Default Values"]
        D1["5 seconds"]
        D2["3 failures"]
        D3["60 steps"]
        D4["15 steps"]
        D5["1.5x multiplier"]
        D6["15% MAPE"]
    end

    Config --> Defaults
```

## Network Ports

| Service | Port | Protocol |
|---------|------|----------|
| FastAPI | 8000 | HTTP/HTTPs |
| React Dev | 5173 | HTTP |
| React Prod | 80 | HTTP |
| Nginx | 443 | HTTPS |
| WebSocket | 8000 | WS |