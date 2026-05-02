from typing import Optional, List
from app.core.load_balancer import LoadBalancer, Server
from app.core.round_robin import RoundRobinLB
from app.core.least_connections import LeastConnectionsLB
from app.core.weighted_rr import WeightedRoundRobinLB


class AlgorithmRegistry:
    """Registry for load balancer algorithms."""

    _algorithms: dict = {
        "round_robin": RoundRobinLB,
        "least_connections": LeastConnectionsLB,
        "weighted_round_robin": WeightedRoundRobinLB,
    }

    _descriptions: dict = {
        "round_robin": ("O(1) circular distribution", "Simple and fair for homogeneous pools"),
        "least_connections": ("O(log n) min-heap selection", "Optimal for variable-duration requests"),
        "weighted_round_robin": ("O(1) weight-based distribution", "For heterogeneous server capacities"),
    }

    @classmethod
    def get(cls, name: str) -> Optional[LoadBalancer]:
        """Get an instance of the algorithm by name."""
        algorithm_class = cls._algorithms.get(name)
        if algorithm_class:
            return algorithm_class()
        return None

    @classmethod
    def get_all_names(cls) -> List[str]:
        """Get all registered algorithm names."""
        return list(cls._algorithms.keys())

    @classmethod
    def get_info(cls, name: str) -> Optional[tuple]:
        """Get (complexity, description) tuple for algorithm."""
        return cls._descriptions.get(name)

    @classmethod
    def create_instance(cls, name: str) -> Optional[LoadBalancer]:
        """Alias for get() - creates a new instance."""
        return cls.get(name)
