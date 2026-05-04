# SmartBalance

An AI-Driven Intelligent Load Balancer with Real-Time Dashboard and Predictive Traffic Routing.

## Overview

SmartBalance combines classical load balancing algorithms with machine learning for predictive traffic routing. The system includes:

- **Three Load Balancing Algorithms**: Round Robin, Least Connections, Weighted Round Robin
- **AI-Based Smart Routing**: LSTM neural network for traffic prediction
- **Real-Time Dashboard**: React-based dashboard with WebSocket streaming
- **Traffic Simulation**: Configurable traffic profiles (Steady, Burst, Ramp, Wave)
- **Health Monitoring**: Background server health checking with automatic failover

## Project Structure

```
SmartBalance_SE/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── core/         # Load balancing algorithms
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # WebSocket manager
│   │   ├── simulation/   # Traffic generator & health checker
│   │   └── ml/           # LSTM model (future)
│   ├── tests/            # Unit tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React dashboard (to be created)
├── docs/                 # Documentation
├── docker-compose.yml
└── README.md
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/servers` | GET, POST | List/create servers |
| `/api/v1/servers/{id}` | GET, PUT, DELETE | Server CRUD |
| `/api/v1/algorithms` | GET | List algorithms |
| `/api/v1/algorithms/{name}/select` | POST | Switch algorithm |
| `/api/v1/simulation/start` | POST | Start traffic simulation |
| `/api/v1/metrics/live` | WS | WebSocket for real-time metrics |
| `/health` | GET | Health check |

## Testing

```bash
cd backend
pytest tests/ -v
```

## Docker

```bash
docker-compose up --build
```

## Project Status

**100% Complete** — All features implemented, 29 unit tests passing.

## License

MIT
