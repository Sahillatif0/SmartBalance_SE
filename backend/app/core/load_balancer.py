from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Server:
    id: str
    host: str
    port: int
    weight: int = 1
    connections: int = 0
    healthy: bool = True
    failure_count: int = 0
    last_health_check: Optional[datetime] = None

    def increment_connections(self):
        self.connections += 1

    def decrement_connections(self):
        self.connections = max(0, self.connections - 1)

    def mark_unhealthy(self):
        self.healthy = False
        self.failure_count += 1

    def mark_healthy(self):
        self.healthy = True
        self.failure_count = 0


class LoadBalancer(ABC):
    @abstractmethod
    def select_server(self, servers: List[Server]) -> Optional[Server]:
        """Select next server for routing. Returns None if no healthy servers."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the algorithm name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of the algorithm."""
        pass

    @property
    @abstractmethod
    def complexity(self) -> str:
        """Return time complexity."""
        pass

    def filter_healthy(self, servers: List[Server]) -> List[Server]:
        """Filter out unhealthy servers."""
        return [s for s in servers if s.healthy]

    def get_least_busy_server(self, servers: List[Server]) -> Optional[Server]:
        """Helper to find server with minimum connections."""
        healthy = self.filter_healthy(servers)
        if not healthy:
            return None
        return min(healthy, key=lambda s: s.connections)
