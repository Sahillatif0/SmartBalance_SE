import heapq
from typing import List, Optional, Dict, Tuple
from app.core.load_balancer import LoadBalancer, Server


class LeastConnectionsLB(LoadBalancer):
    """
    Least Connections load balancer - routes to server with fewest active connections.

    Time Complexity: O(log n) for selection
    Space Complexity: O(n)

    Adaptive and optimal for long-lived or variable-duration requests.
    Uses a min-heap for efficient selection.
    """

    def __init__(self):
        self._heap: List[Tuple[int, int, str]] = []  # (connections, index, server_id)
        self._server_map: Dict[str, Server] = {}
        self._server_indices: Dict[str, int] = {}
        self._request_count: int = 0
        self._index_counter: int = 0

    @property
    def name(self) -> str:
        return "least_connections"

    @property
    def description(self) -> str:
        return "Routes each new request to the server with the fewest active connections."

    @property
    def complexity(self) -> str:
        return "O(log n)"

    def _rebuild_heap(self, servers: List[Server]) -> None:
        """Rebuild the heap when server set changes."""
        healthy = self.filter_healthy(servers)
        self._server_map = {s.id: s for s in healthy}
        self._server_indices = {}
        self._heap = []
        self._index_counter = 0

        for server in healthy:
            self._server_indices[server.id] = self._index_counter
            heapq.heappush(
                self._heap,
                (server.connections, self._index_counter, server.id)
            )
            self._index_counter += 1

    def select_server(self, servers: List[Server]) -> Optional[Server]:
        healthy = self.filter_healthy(servers)
        if not healthy:
            return None

        server_ids = {s.id for s in healthy}
        if not self._heap or server_ids != set(self._server_map.keys()):
            self._rebuild_heap(servers)

        while self._heap:
            connections, idx, server_id = heapq.heappop(self._heap)
            server = self._server_map.get(server_id)
            if server and server.healthy:
                server.increment_connections()
                self._request_count += 1
                new_connections = server.connections
                heapq.heappush(
                    self._heap,
                    (new_connections, self._index_counter, server_id)
                )
                self._index_counter += 1
                return server

        return None

    def get_least_busy(self) -> Optional[Server]:
        """Get server with minimum connections without incrementing."""
        if not self._heap:
            return None
        _, _, server_id = self._heap[0]
        return self._server_map.get(server_id)

    @property
    def request_count(self) -> int:
        return self._request_count
