# SmartBalance Documentation

## Quick Links

| Section | Description |
|---------|-------------|
| [UML Diagrams](uml/) | Architecture, deployment, sequence, and class diagrams |

## Architecture Summary

SmartBalance is an AI-driven load balancer combining:
- **Classical algorithms**: Round Robin, Least Connections, Weighted RR
- **ML predictions**: LSTM-based traffic forecasting
- **Real-time dashboard**: WebSocket-connected React UI

## Key Files

- `backend/app/core/load_balancer.py` - Base algorithm class
- `backend/app/core/smart_router.py` - AI-driven routing
- `backend/app/ml/lstm_model.py` - PyTorch LSTM implementation
- `backend/app/simulation/health_checker.py` - Background health monitoring
- `frontend/src/components/Dashboard.tsx` - Main UI container
- `frontend/src/hooks/useWebSocket.ts` - Real-time connection hook