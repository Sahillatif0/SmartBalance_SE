from typing import Callable, Dict, List, Any
from datetime import datetime


class EventBus:
    """
    Simple event bus for pub/sub communication between components.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    async def publish(self, event_type: str, data: Any):
        """Publish an event."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)

    def clear(self, event_type: str = None):
        """Clear subscribers for an event type or all."""
        if event_type:
            self._subscribers.pop(event_type, None)
        else:
            self._subscribers.clear()


# Import asyncio at module level
import asyncio
