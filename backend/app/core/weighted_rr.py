from typing import List, Optional
from app.core.load_balancer import LoadBalancer, Server


class WeightedRoundRobinLB(LoadBalancer):
    """
    Weighted Round Robin load balancer - distributes requests based on server weight.

    Time Complexity: O(1)
    Space Complexity: O(n)

    Servers with higher capacity receive proportionally more traffic.
    Ideal for heterogeneous environments (e.g., mixed instance types).
    """

    def __init__(self):
        self._current_index: int = 0
        self._current_weight: int = 0
        self._servers: List[Server] = []
        self._request_count: int = 0

    @property
    def name(self) -> str:
        return "weighted_round_robin"

    @property
    def description(self) -> str:
        return "Extends Round Robin with configurable weights. Higher weight = more traffic."

    @property
    def complexity(self) -> str:
        return "O(1)"

    def select_server(self, servers: List[Server]) -> Optional[Server]:
        healthy = self.filter_healthy(servers)
        if not healthy:
            return None

        server_ids = {s.id for s in healthy}
        if not self._servers or server_ids != {s.id for s in self._servers}:
            self._servers = healthy
            self._current_weight = max(s.weight for s in healthy) if healthy else 1
            self._current_index = 0

        max_attempts = len(healthy)
        for _ in range(max_attempts):
            server = healthy[self._current_index % len(healthy)]
            self._current_index += 1

            if server.weight >= self._current_weight:
                server.increment_connections()
                self._request_count += 1
                return server

            if self._current_index % len(healthy) == 0:
                self._current_weight -= 1
                if self._current_weight <= 0:
                    self._current_weight = max(s.weight for s in healthy)

        server = healthy[self._current_index % len(healthy)]
        server.increment_connections()
        self._request_count += 1
        return server

    def get_weight_ratio(self, server: Server) -> float:
        """Get weight ratio relative to max weight."""
        if not self._servers:
            return 1.0
        max_weight = max(s.weight for s in self._servers)
        return server.weight / max_weight if max_weight > 0 else 1.0

    @property
    def request_count(self) -> int:
        return self._request_count
