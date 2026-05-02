from fastapi import WebSocket
from typing import Dict, List
import asyncio
import json


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_personal(self, client_id: str, message: dict):
        """Send message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception:
                self.disconnect(client_id)

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

    async def broadcast_server_update(self, servers: List[dict]):
        """Broadcast server status update."""
        await self.broadcast({
            "type": "server_update",
            "servers": servers
        })

    async def broadcast_routing_decision(self, decision: dict):
        """Broadcast a routing decision."""
        await self.broadcast({
            "type": "routing_decision",
            "decision": decision
        })

    async def broadcast_prediction(self, predictions: List[float]):
        """Broadcast AI prediction update."""
        await self.broadcast({
            "type": "prediction",
            "predictions": predictions
        })


# Global WebSocket manager instance
ws_manager = WebSocketManager()
