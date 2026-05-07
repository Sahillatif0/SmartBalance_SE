from abc import ABC, abstractmethod
import math


class TrafficProfile(ABC):
    """Abstract base class for traffic profiles."""

    @abstractmethod
    def generate(self, t: float) -> float:
        """Generate traffic rate at time t (requests per second)."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class SteadyProfile(TrafficProfile):
    """Constant traffic rate."""

    def __init__(self, rate: float = 100.0, duration: float = None):
        self._rate = rate

    @property
    def name(self) -> str:
        return "steady"

    def generate(self, t: float) -> float:
        return self._rate


class BurstProfile(TrafficProfile):
    """Burst traffic pattern with periodic spikes."""

    def __init__(
        self,
        rate: float = 100.0,
        burst_factor: float = 5.0,
        period: float = 10.0,
        duration: float = None
    ):
        # Use rate as base for burst pattern
        self._base = rate
        self._burst_factor = burst_factor
        self._period = period

    @property
    def name(self) -> str:
        return "burst"

    def generate(self, t: float) -> float:
        phase = (t % self._period) / self._period
        intensity = 1 - abs(phase - 0.5) * 2
        return self._base * (1 + self._burst_factor * intensity)


class RampProfile(TrafficProfile):
    """Linear ramp traffic pattern."""

    def __init__(
        self,
        rate: float = 100.0,
        end_multiplier: float = 2.0,
        duration: float = 0.0
    ):
        # Start at rate, ramp up to rate * end_multiplier
        self._start = rate
        self._end = rate * end_multiplier
        self._duration = duration if duration > 0 else float('inf')  # Infinite if duration is 0

    @property
    def name(self) -> str:
        return "ramp"

    def generate(self, t: float) -> float:
        progress = min(t / self._duration, 1.0)
        return self._start + (self._end - self._start) * progress


class WaveProfile(TrafficProfile):
    """Sine wave traffic pattern."""

    def __init__(
        self,
        rate: float = 100.0,
        amplitude_multiplier: float = 1.0,
        period: float = 30.0,
        duration: float = None
    ):
        self._base = rate
        self._amplitude = rate * amplitude_multiplier
        self._period = period

    @property
    def name(self) -> str:
        return "wave"

    def generate(self, t: float) -> float:
        return self._base + self._amplitude * math.sin(2 * math.pi * t / self._period)


class TrafficProfileFactory:
    """Factory for creating traffic profiles."""

    _profiles = {
        "steady": SteadyProfile,
        "burst": BurstProfile,
        "ramp": RampProfile,
        "wave": WaveProfile,
    }

    @classmethod
    def create(cls, name: str, **kwargs) -> TrafficProfile:
        """Create a traffic profile by name."""
        profile_class = cls._profiles.get(name.lower())
        if not profile_class:
            return SteadyProfile()
        return profile_class(**kwargs)

    @classmethod
    def get_available_profiles(cls) -> list:
        """Get list of available profile names."""
        return list(cls._profiles.keys())
