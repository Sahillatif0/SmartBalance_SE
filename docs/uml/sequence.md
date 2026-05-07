# SmartBalance Sequence Diagrams

## 1. Request Routing Sequence

```mermaid
sequenceDiagram
    participant Client as Client Browser
    participant API as FastAPI Server
    participant Registry as AlgorithmRegistry
    participant Algorithm as Active Algorithm
    participant WS as WebSocket Manager
    participant LSTM as Traffic Predictor

    Client->>API: POST /api/v1/algorithms/select
    Note over API: User selects algorithm
    API->>Registry: AlgorithmRegistry.get(name)
    Registry-->>API: Algorithm instance
    Note over API: Switch active algorithm

    Client->>API: WebSocket /api/v1/metrics/live
    API->>WS: Accept connection

    loop Every 1 second (Simulation)
        API->>API: Generate traffic
        API->>LSTM: add_traffic_sample(rate)
        LSTM-->>API: Sample added

        API->>LSTM: predict()
        LSTM-->>API: Predictions[]

        API->>Algorithm: select_server(servers)
        alt Smart Router active
            API->>Algorithm: evaluate_and_switch(servers, load)
            Algorithm->>LSTM: Check predictions
            Algorithm->>Registry: Switch algorithm
        end

        Algorithm-->>API: Selected Server
        API->>WS: Broadcast routing decision
        WS-->>Client: {type: "routing_decision", ...}
    end
```

## 2. Server Health Check Sequence

```mermaid
sequenceDiagram
    participant HC as HealthChecker
    participant Server as Server Instance
    participant Pool as ServerPool
    participant DB as Database
    participant WS as WebSocket Manager

    loop Every HEALTH_CHECK_INTERVAL seconds
        HC->>HC: _check_loop()
        HC->>Server: _ping_server(server)

        alt Server responds OK
            Server-->>HC: HTTP 200
            HC->>Server: Reset failure_count
            HC->>Server: mark_healthy()
        else Server fails
            Server-->>HC: Exception/Timeout
            HC->>Server: failure_count++
            alt failure_count >= threshold
                HC->>Server: mark_unhealthy()
                HC->>Pool: Remove from pool
                HC->>DB: Update healthy=false
                HC->>WS: Broadcast server_update
            end
        end
    end
```

## 3. Algorithm Switching Sequence

```mermaid
sequenceDiagram
    participant SR as SmartRouter
    participant P as TrafficPredictor
    participant Primary as RoundRobinLB
    participant Fallback as LeastConnectionsLB

    Note over SR: Threshold = 1.5x current load

    SR->>P: predict()
    P-->>SR: predictions[]

    alt max(predictions) > threshold * current_load
        SR->>SR: _switch_to_fallback()
        SR->>Fallback: Activate
        Note over SR: Now using Least Connections

        loop Continuous monitoring
            SR->>P: predict()
            alt max(predictions) <= threshold * 0.8
                SR->>SR: _switch_to_primary()
                SR->>Primary: Activate
                Note over SR: Back to Round Robin
            end
        end
    end
```

## 4. Client Dashboard Connection Sequence

```mermaid
sequenceDiagram
    participant UI as React Dashboard
    participant WS as useWebSocket Hook
    participant API as FastAPI WebSocket

    UI->>WS: Connect to ws://.../metrics/live
    WS->>API: WebSocket handshake
    API-->>WS: Connection accepted

    loop Every second
        API->>WS: metric_update message
        WS->>UI: onMessage(metric)
        Note over UI: Update charts & lists
    end

    UI->>WS: sendMessage({action: "ping"})
    WS->>API: ping
    API-->>WS: pong

    Note over WS: Auto-reconnect on disconnect
```

## 5. LSTM Traffic Prediction Sequence

```mermaid
sequenceDiagram
    participant Sim as Traffic Simulator
    participant TG as TrafficGenerator
    participant P as TrafficPredictor
    participant Model as LSTMModel

    Sim->>TG: generate_traffic(delta_time)
    TG-->>Sim: current_rate

    Sim->>P: add_traffic_sample(rate)
    Note over P: Add to sliding window
    P->>P: Maintain 60 samples max

    Sim->>P: predict()
    alt Enough samples (>=10)
        P->>P: Normalize trajectory
        P->>Model: forward(input_tensor)
        Model-->>P: normalized_predictions
        P->>P: Denormalize predictions
        P-->>Sim: predictions[15]
    else Not enough data
        P-->>Sim: Simple extrapolation
    end

    Sim->>P: get_mape(actual, predicted)
    P-->>Sim: MAPE percentage
```