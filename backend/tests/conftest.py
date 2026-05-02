import pytest
from app.core.load_balancer import Server


@pytest.fixture
def healthy_servers():
    """A pool of healthy servers."""
    return [
        Server("s1", "10.0.0.1", 8080, weight=1),
        Server("s2", "10.0.0.2", 8080, weight=2),
        Server("s3", "10.0.0.3", 8080, weight=1),
    ]


@pytest.fixture
def mixed_servers():
    """A pool with a mix of healthy and unhealthy servers."""
    return [
        Server("s1", "10.0.0.1", 8080, weight=1, healthy=True),
        Server("s2", "10.0.0.2", 8080, weight=1, healthy=False),
        Server("s3", "10.0.0.3", 8080, weight=1, healthy=True),
        Server("s4", "10.0.0.4", 8080, weight=1, healthy=False),
    ]


@pytest.fixture
def weighted_servers():
    """Servers with different weights."""
    return [
        Server("s1", "10.0.0.1", 8080, weight=1),
        Server("s2", "10.0.0.2", 8080, weight=2),
        Server("s3", "10.0.0.3", 8080, weight=3),
        Server("s4", "10.0.0.4", 8080, weight=4),
    ]


@pytest.fixture
def busy_servers():
    """Servers with varying connection counts."""
    s1 = Server("s1", "10.0.0.1", 8080, weight=1, connections=10)
    s2 = Server("s2", "10.0.0.2", 8080, weight=1, connections=2)
    s3 = Server("s3", "10.0.0.3", 8080, weight=1, connections=5)
    return [s1, s2, s3]
