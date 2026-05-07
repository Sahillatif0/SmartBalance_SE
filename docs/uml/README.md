# SmartBalance UML Diagrams

This directory contains all UML diagrams documenting the SmartBalance architecture.

## Diagram Overview

| Diagram | File | Description |
|---------|------|-------------|
| Architecture | [architecture.md](architecture.md) | Component hierarchy and system structure |
| Deployment | [deployment.md](deployment.md) | Infrastructure, containers, and network topology |
| Sequence | [sequence.md](sequence.md) | Dynamic behavior and interaction flows |
| Class | [class-diagrams.md](class-diagrams.md) | Static structure and class relationships |

## Quick Reference

### System Components
```
Frontend (React)          →  Backend (FastAPI)           →  Data (SQLite)
├── Dashboard.tsx          ├── /api/v1/servers            ├── ServerModel
├── ServerList.tsx          ├── /api/v1/algorithms        └── MetricModel
├── MetricsChart.tsx        ├── /api/v1/metrics
├── TrafficSimulator.tsx    └── /api/v1/simulation
└── useWebSocket.ts
```

### Load Balancing Algorithms
| Algorithm | Time Complexity | Use Case |
|-----------|-----------------|----------|
| RoundRobin | O(1) | Homogeneous servers |
| LeastConnections | O(log n) | Variable request duration |
| WeightedRR | O(1) | Heterogeneous capacities |
| SmartRouter | Adaptive | AI-driven switching |

### ML Model
- **Input**: 60-step sliding window
- **Hidden**: 64 units, 2 layers
- **Output**: 15-step forecast
- **Target**: MAPE < 15%

### Traffic Profiles
- `steady` - Constant rate
- `burst` - High/low alternating
- `ramp` - Gradual increase
- `wave` - Sinusoidal pattern