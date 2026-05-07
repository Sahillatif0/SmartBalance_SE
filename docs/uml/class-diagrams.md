# SmartBalance Class Diagrams

## 1. Core Load Balancing Architecture

```mermaid
classDiagram
    class LoadBalancer {
        <<abstract>>
        +select_server(servers: List[Server]) Server*
        +name: str*
        +description: str*
        +complexity: str*
        +filter_healthy(servers) List[Server]
        +get_least_busy_server(servers) Server*
    }

    class Server {
        +id: str
        +host: str
        +port: int
        +weight: int
        +connections: int
        +healthy: bool
        +failure_count: int
        +last_health_check: datetime
        +increment_connections()
        +decrement_connections()
        +mark_unhealthy()
        +mark_healthy()
    }

    class RoundRobinLB {
        -_current_index: int
        -_request_count: int
        +select_server(servers) Server
        +name: str
        +description: str
        +complexity: str
        +reset()
        +request_count: int
    }

    class LeastConnectionsLB {
        -_heap: List[Tuple]
        -_server_map: Dict
        -_index_counter: int
        +_rebuild_heap(servers)
        +select_server(servers) Server
        +name: str
        +description: str
        +complexity: str
        +get_least_busy() Server
        +request_count: int
    }

    class WeightedRoundRobinLB {
        -_current_index: int
        -_weights: Dict
        -_current_weight: int
        +select_server(servers) Server
        +name: str
        +description: str
        +complexity: str
    }

    class SmartRouter {
        -_primary: LoadBalancer
        -_fallback: LoadBalancer
        -_current: LoadBalancer
        -_using_fallback: bool
        -_switch_count: int
        +select_server(servers) Server
        +evaluate_and_switch(servers, load) Server
        -_switch_to_fallback()
        -_switch_to_primary()
        +is_using_fallback: bool
        +active_algorithm: str
        +switch_count: int
        +force_switch(algorithm) bool
        +get_stats() Dict
    }

    class AlgorithmRegistry {
        -_algorithms: Dict
        -_descriptions: Dict
        +get(name) LoadBalancer
        +get_all_names() List[str]
        +get_info(name) tuple
        +create_instance(name) LoadBalancer
    }

    LoadBalancer <|-- RoundRobinLB
    LoadBalancer <|-- LeastConnectionsLB
    LoadBalancer <|-- WeightedRoundRobinLB
    LoadBalancer <|-- SmartRouter
    SmartRouter --> LoadBalancer : uses
    SmartRouter --> AlgorithmRegistry
```

## 2. ML Module Classes

```mermaid
classDiagram
    class LSTMModel {
        <<PyTorch nn.Module>>
        -hidden_size: int
        -num_layers: int
        -output_steps: int
        +lstm: nn.LSTM
        +fc: nn.Sequential
        +forward(x: Tensor) Tensor
    }

    class TrafficPredictor {
        -window_size: int
        -forecast_steps: int
        -device: torch.device
        -model: LSTMModel
        -trajectory: List[float]
        -is_trained: bool
        +_initialize_with_patterns()
        +train_model(X, y, epochs)
        +add_traffic_sample(rate)
        +predict() List[float]
        +get_mape(actual, predicted) float
    }

    class MetricsCalculator {
        +calculate_mape(actual, predicted) float
        +calculate_rmse(actual, predicted) float
        +calculate_mae(actual, predicted) float
    }

    TrafficPredictor --> LSTMModel : uses
```

## 3. Simulation Module Classes

```mermaid
classDiagram
    class TrafficProfile {
        <<abstract>>
        +name: str
        +generate(elapsed: float) float
    }

    class SteadyProfile {
        +rate: float
        +generate(elapsed) float
    }

    class BurstProfile {
        +base_rate: float
        +peak_duration: int
        +quiet_duration: int
        +generate(elapsed) float
    }

    class RampProfile {
        +start_rate: float
        +end_rate: float
        +ramp_duration: float
        +generate(elapsed) float
    }

    class WaveProfile {
        +base_rate: float
        +amplitude: float
        +frequency: float
        +generate(elapsed) float
    }

    class TrafficProfileFactory {
        +create(profile: str) TrafficProfile
    }

    class TrafficGenerator {
        +profile: TrafficProfile
        +base_rate: float
        +duration: float
        -_start_time: datetime
        -_elapsed_time: float
        -_total_requests: int
        +start()
        +generate_traffic(delta_time) float
        +get_current_rate() float
        +reset()
    }

    class HealthChecker {
        +interval: float
        +failure_threshold: int
        +on_unhealthy: Callable
        +on_healthy: Callable
        -_running: bool
        -_task: asyncio.Task
        +start(servers)
        +stop()
        +_check_loop(servers)
        +_check_servers(servers)
        +_ping_server(server) bool
        +check_single(server) bool
        +is_running: bool
        +last_check: datetime
    }

    class ServerPool {
        +servers: List[Server]
        +add_server(server)
        +remove_server(server_id)
        +get_server(server_id)
        +get_healthy_servers()
        +update_health(server_id, healthy)
    }

    TrafficProfile <|-- SteadyProfile
    TrafficProfile <|-- BurstProfile
    TrafficProfile <|-- RampProfile
    TrafficProfile <|-- WaveProfile
    TrafficGenerator --> TrafficProfile
```

## 4. API Router Classes

```mermaid
classDiagram
    class FastAPI {
        +title: str
        +version: str
        +include_router(router, prefix, tags)
        +add_middleware(cors)
    }

    class ServerRouter {
        +GET / list_servers()
        +POST / create_server()
        +GET /{server_id} get_server()
        +PUT /{server_id} update_server()
        +DELETE /{server_id} delete_server()
        +PUT /{server_id}/health update_health()
    }

    class AlgorithmRouter {
        +GET / list_algorithms()
        +GET /{algorithm_name} get_algorithm()
        +POST /{algorithm_name}/select select_algorithm()
        +GET /{algorithm_name}/stats get_algorithm_stats()
    }

    class MetricsRouter {
        +GET / get_metrics()
        +GET /latest get_latest_metrics()
        +WS /live websocket_metrics()
        +broadcast_to_all(data)
    }

    class SimulationRouter {
        +GET /config get_simulation_config()
        +PUT /config update_simulation_config()
        +POST /start start_simulation()
        +POST /stop stop_simulation()
        +GET /status get_simulation_status()
        +GET /predictions get_predictions()
    }

    FastAPI --> ServerRouter
    FastAPI --> AlgorithmRouter
    FastAPI --> MetricsRouter
    FastAPI --> SimulationRouter
```

## 5. Frontend Component Classes

```mermaid
classDiagram
    class App {
        +render()
    }

    class Dashboard {
        +servers: Server[]
        +metrics: MetricPoint[]
        +predictions: number[]
        +activeAlgorithm: string
        +render()
    }

    class ServerList {
        +servers: Server[]
        +renderServerCard()
    }

    class MetricsChart {
        +metrics: MetricPoint[]
        +predictions: number[]
        +renderLineChart()
        +renderAreaChart()
    }

    class TrafficSimulator {
        +profile: TrafficProfile
        +rate: number
        +running: boolean
        +handleStart()
        +handleStop()
        +handleProfileChange()
    }

    class AlgorithmSelector {
        +algorithms: Algorithm[]
        +activeAlgorithm: string
        +handleSelect()
    }

    class ForecastOverlay {
        +predictions: number[]
        +confidence: number
        +render()
    }

    class RoutingLog {
        +decisions: RoutingDecision[]
        +renderLogEntry()
    }

    class useWebSocket {
        +connected: boolean
        +lastMessage: DashboardMessage
        +connect()
        +disconnect()
        +sendMessage()
        +reconnect()
    }

    App --> Dashboard
    Dashboard --> ServerList
    Dashboard --> MetricsChart
    Dashboard --> TrafficSimulator
    Dashboard --> AlgorithmSelector
    Dashboard --> ForecastOverlay
    Dashboard --> RoutingLog
    Dashboard ..> useWebSocket
```

## 6. Data Models

```mermaid
classDiagram
    class ServerModel {
        <<SQLAlchemy ORM>>
        +id: String (PK)
        +host: String
        +port: Integer
        +weight: Integer
        +connections: Integer
        +healthy: Boolean
        +failure_count: Integer
        +created_at: DateTime
        +updated_at: DateTime
    }

    class MetricModel {
        <<SQLAlchemy ORM>>
        +id: Integer (PK)
        +server_id: String (FK)
        +timestamp: DateTime
        +latency: Float
        +connections: Integer
        +error_rate: Float
    }

    class ServerResponse {
        <<Pydantic>>
        +id: str
        +host: str
        +port: int
        +weight: int
        +connections: int
        +healthy: bool
    }

    class SimulationConfig {
        <<Pydantic>>
        +profile: str
        +rate: float
        +duration: float | None
    }

    class MetricPoint {
        <<TypeScript Interface>>
        +timestamp: string
        +latency: number
        +connections: number
        +errorRate: number
    }

    class DashboardMessage {
        <<TypeScript Interface>>
        +type: MessageType
        +timestamp: string
        +servers?: Server[]
        +metrics?: MetricPoint[]
        +predictions?: number[]
        +simulation?: SimulationState
    }

    ServerModel --> MetricModel : 1:N
```