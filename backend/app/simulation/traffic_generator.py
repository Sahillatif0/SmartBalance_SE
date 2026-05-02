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

    def __init__(self, rate: float = 100.0):
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
        base: float = 50.0,
        burst_factor: float = 5.0,
        period: float = 10.0
    ):
        self._base = base
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
        start: float = 10.0,
        end: float = 200.0,
        duration: float = 60.0
    ):
        self._start = start
        self._end = end
        self._duration = duration

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
        base: float = 100.0,
        amplitude: float = 100.0,
        period: float = 30.0
    ):
        self._base = base
        self._amplitude = amplitude
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
