from typing import Optional
from datetime import datetime
from app.simulation.traffic_generator import TrafficProfile


class TrafficGenerator:
    """
    Generates traffic based on a configured profile.

    This is a simplified simulation generator. In production,
    this would interface with actual load testing tools.
    """

    def __init__(
        self,
        profile: TrafficProfile,
        base_rate: float = 100.0,
        duration: Optional[float] = None
    ):
        self.profile = profile
        self.base_rate = base_rate
        self.duration = duration
        self._start_time: Optional[datetime] = None
        self._elapsed_time: float = 0.0
        self._total_requests: int = 0

    @property
    def profile_name(self) -> str:
        return self.profile.name

    @property
    def elapsed_time(self) -> float:
        return self._elapsed_time

    @property
    def total_requests(self) -> int:
        return self._total_requests

    def start(self):
        """Start the traffic generator."""
        self._start_time = datetime.now()
        self._elapsed_time = 0.0
        self._total_requests = 0

    def generate_traffic(self, delta_time: float = 1.0) -> float:
        """
        Generate traffic for the given time delta.

        Args:
            delta_time: Time elapsed since last call (seconds)

        Returns:
            Number of requests in this time period
        """
        if not self._start_time:
            self.start()

        self._elapsed_time += delta_time

        # Only check duration if explicitly set (not None or 0)
        if self.duration and self.duration > 0 and self._elapsed_time > self.duration:
            return 0

        rate = self.profile.generate(self._elapsed_time)
        requests = int(rate * delta_time)
        self._total_requests += requests
        return requests

    def get_current_rate(self) -> float:
        """Get the current traffic rate."""
        return self.profile.generate(self._elapsed_time)

    def reset(self):
        """Reset the generator."""
        self._start_time = None
        self._elapsed_time = 0.0
        self._total_requests = 0
