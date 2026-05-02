from typing import List, Optional, Dict, Any
from app.core.load_balancer import LoadBalancer, Server
from app.core.algorithm_registry import AlgorithmRegistry
from app.config import get_settings

settings = get_settings()


class SmartRouter:
    """
    AI-driven smart router that can switch algorithms based on traffic predictions.

    When predicted load exceeds threshold (default 150%) of current load,
    automatically switches from the primary algorithm to Least Connections
    for better traffic distribution.
    """

    def __init__(
        self,
        primary_algorithm: str = "round_robin",
        fallback_algorithm: str = "least_connections",
        threshold: float = None,
        predictor=None
    ):
        self.primary_name = primary_algorithm
        self.fallback_name = fallback_algorithm
        self.threshold = threshold or settings.smart_router_threshold
        self.predictor = predictor

        self._primary: LoadBalancer = AlgorithmRegistry.get(primary_algorithm)
        self._fallback: LoadBalancer = AlgorithmRegistry.get(fallback_algorithm)
        self._current: LoadBalancer = self._primary
        self._using_fallback = False
        self._switch_count = 0
        self._total_requests = 0

    def select_server(self, servers: List[Server]) -> Optional[Server]:
        """Select a server using the current active algorithm."""
        if not servers:
            return None

        self._total_requests += 1
        return self._current.select_server(servers)

    def evaluate_and_switch(
        self,
        servers: List[Server],
        current_load: float
    ) -> Optional[Server]:
        """
        Evaluate traffic predictions and switch algorithm if needed.

        Args:
            servers: List of available servers
            current_load: Current total load across all servers

        Returns:
            Selected server using the appropriate algorithm
        """
        if not self.predictor or not self._primary:
            return self.select_server(servers)

        predictions = self.predictor.get_next_predictions()
        if predictions is None or len(predictions) == 0:
            return self.select_server(servers)

        max_predicted_load = max(predictions)
        threshold_load = self.threshold * current_load

        if max_predicted_load > threshold_load and not self._using_fallback:
            self._switch_to_fallback()
        elif max_predicted_load <= threshold_load and self._using_fallback:
            self._switch_to_primary()

        return self.select_server(servers)

    def _switch_to_fallback(self) -> None:
        """Switch to fallback algorithm (Least Connections)."""
        if self._fallback and not self._using_fallback:
            self._current = self._fallback
            self._using_fallback = True
            self._switch_count += 1

    def _switch_to_primary(self) -> None:
        """Switch back to primary algorithm."""
        if self._primary and self._using_fallback:
            self._current = self._primary
            self._using_fallback = False

    @property
    def is_using_fallback(self) -> bool:
        """Check if currently using fallback algorithm."""
        return self._using_fallback

    @property
    def active_algorithm(self) -> str:
        """Get the name of the currently active algorithm."""
        return self._current.name if self._current else "unknown"

    @property
    def switch_count(self) -> int:
        """Get the number of algorithm switches performed."""
        return self._switch_count

    @property
    def total_requests(self) -> int:
        """Get total requests processed."""
        return self._total_requests

    def force_switch(self, algorithm: str) -> bool:
        """Manually force switch to a specific algorithm."""
        algorithm_instance = AlgorithmRegistry.get(algorithm)
        if algorithm_instance:
            self._current = algorithm_instance
            self._using_fallback = (algorithm == self.fallback_name)
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            "active_algorithm": self.active_algorithm,
            "using_fallback": self._using_fallback,
            "switch_count": self._switch_count,
            "total_requests": self._total_requests,
            "threshold": self.threshold
        }
