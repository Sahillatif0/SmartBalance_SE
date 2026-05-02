from typing import List, Optional
from app.core.load_balancer import Server


class ServerPool:
    """Manages a pool of servers for load balancing."""

    def __init__(self):
        self._servers: List[Server] = []
        self._max_servers = 20

    def add_server(
        self,
        server_id: str,
        host: str,
        port: int,
        weight: int = 1
    ) -> Server:
        """Add a new server to the pool."""
        if len(self._servers) >= self._max_servers:
            raise ValueError(f"Maximum servers ({self._max_servers}) reached")

        server = Server(
            id=server_id,
            host=host,
            port=port,
            weight=weight
        )
        self._servers.append(server)
        return server

    def remove_server(self, server_id: str) -> bool:
        """Remove a server from the pool."""
        for i, server in enumerate(self._servers):
            if server.id == server_id:
                self._servers.pop(i)
                return True
        return False

    def get_server(self, server_id: str) -> Optional[Server]:
        """Get a server by ID."""
        for server in self._servers:
            if server.id == server_id:
                return server
        return None

    def get_healthy_servers(self) -> List[Server]:
        """Get all healthy servers."""
        return [s for s in self._servers if s.healthy]

    def get_all_servers(self) -> List[Server]:
        """Get all servers."""
        return self._servers.copy()

    @property
    def server_count(self) -> int:
        """Get total server count."""
        return len(self._servers)

    @property
    def healthy_count(self) -> int:
        """Get healthy server count."""
        return len(self.get_healthy_servers())

    def mark_unhealthy(self, server_id: str) -> bool:
        """Mark a server as unhealthy."""
        server = self.get_server(server_id)
        if server:
            server.mark_unhealthy()
            return True
        return False

    def mark_healthy(self, server_id: str) -> bool:
        """Mark a server as healthy."""
        server = self.get_server(server_id)
        if server:
            server.mark_healthy()
            return True
        return False

    def get_total_connections(self) -> int:
        """Get total connections across all servers."""
        return sum(s.connections for s in self._servers)

    def get_average_connections(self) -> float:
        """Get average connections per server."""
        if not self._servers:
            return 0.0
        return self.get_total_connections() / len(self._servers)

    def reset_all_connections(self):
        """Reset connection counts for all servers."""
        for server in self._servers:
            server.connections = 0
