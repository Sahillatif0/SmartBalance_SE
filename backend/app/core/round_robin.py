from typing import List, Optional
from app.core.load_balancer import LoadBalancer, Server


class RoundRobinLB(LoadBalancer):
    """
    Round Robin load balancer - distributes requests in a circular sequence.

    Time Complexity: O(1)
    Space Complexity: O(1)

    Simple and fair for homogeneous server pools but ignores server state.
    """

    def __init__(self):
        self._current_index: int = 0
        self._request_count: int = 0

    @property
    def name(self) -> str:
        return "round_robin"

    @property
    def description(self) -> str:
        return "Distributes requests in a circular sequence across all healthy servers."

    @property
    def complexity(self) -> str:
        return "O(1)"

    def select_server(self, servers: List[Server]) -> Optional[Server]:
        healthy = self.filter_healthy(servers)
        if not healthy:
            return None

        server = healthy[self._current_index % len(healthy)]
        self._current_index = (self._current_index + 1) % len(healthy)
        self._request_count += 1
        server.increment_connections()
        return server

    def reset(self):
        """Reset the index counter."""
        self._current_index = 0
        self._request_count = 0

    @property
    def request_count(self) -> int:
        return self._request_count
