from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Metric as MetricModel
from app.schemas import MetricResponse
import asyncio

router = APIRouter()

# Active WebSocket connections
_active_connections: dict[str, WebSocket] = {}


async def broadcast_to_all(data: dict):
    """Broadcast data to all connected WebSocket clients."""
    disconnected = []
    for client_id, ws in _active_connections.items():
        try:
            await ws.send_json(data)
        except Exception:
            disconnected.append(client_id)
    for client_id in disconnected:
        _active_connections.pop(client_id, None)


@router.get("", response_model=List[MetricResponse])
async def get_metrics(
    server_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get historical metrics."""
    query = select(MetricModel)
    if server_id:
        query = query.where(MetricModel.server_id == server_id)
    query = query.order_by(MetricModel.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    metrics = result.scalars().all()
    return metrics


@router.get("/latest")
async def get_latest_metrics(db: AsyncSession = Depends(get_db)):
    """Get the latest metrics for each server."""
    result = await db.execute(
        select(MetricModel).order_by(MetricModel.timestamp.desc()).limit(10)
    )
    metrics = result.scalars().all()
    return metrics


@router.websocket("/live")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming."""
    client_id = str(id(websocket))
    await websocket.accept()
    _active_connections[client_id] = websocket

    try:
        while True:
            try:
                # Wait for client message
                raw = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=10.0
                )

                # Handle ping
                if raw == "ping":
                    await websocket.send_text("pong")
                    continue

                # Send metrics back to this client
                await websocket.send_json({
                    "type": "metric_update",
                    "timestamp": datetime.now().isoformat(),
                    "servers": [],
                    "algorithms": [],
                    "predictions": []
                })

            except asyncio.TimeoutError:
                # Send heartbeat every 10 seconds if idle
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        _active_connections.pop(client_id, None)


def get_broadcast_func():
    """Return the broadcast function for use by other modules."""
    return broadcast_to_all
