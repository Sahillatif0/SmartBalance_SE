import pytest
from app.core.round_robin import RoundRobinLB
from app.core.least_connections import LeastConnectionsLB
from app.core.weighted_rr import WeightedRoundRobinLB
from app.core.load_balancer import Server


class TestServer:
    """Tests for the Server dataclass."""

    def test_server_creation(self):
        server = Server("s1", "10.0.0.1", 8080, weight=2)
        assert server.id == "s1"
        assert server.host == "10.0.0.1"
        assert server.port == 8080
        assert server.weight == 2
        assert server.connections == 0
        assert server.healthy is True
        assert server.failure_count == 0

    def test_increment_connections(self):
        server = Server("s1", "10.0.0.1", 8080)
        server.increment_connections()
        server.increment_connections()
        assert server.connections == 2

    def test_decrement_connections(self):
        server = Server("s1", "10.0.0.1", 8080, connections=5)
        server.decrement_connections()
        assert server.connections == 4

    def test_decrement_not_below_zero(self):
        server = Server("s1", "10.0.0.1", 8080)
        server.decrement_connections()
        assert server.connections == 0

    def test_mark_unhealthy(self):
        server = Server("s1", "10.0.0.1", 8080, healthy=True)
        server.mark_unhealthy()
        assert server.healthy is False
        assert server.failure_count == 1

    def test_mark_healthy(self):
        server = Server("s1", "10.0.0.1", 8080, healthy=False, failure_count=2)
        server.mark_healthy()
        assert server.healthy is True
        assert server.failure_count == 0


class TestRoundRobinLB:
    """Tests for Round Robin load balancer."""

    def test_selects_all_servers_evenly(self, healthy_servers):
        lb = RoundRobinLB()
        selections = [lb.select_server(healthy_servers).id for _ in range(12)]
        assert selections.count("s1") == 4
        assert selections.count("s2") == 4
        assert selections.count("s3") == 4

    def test_skips_unhealthy_servers(self, mixed_servers):
        lb = RoundRobinLB()
        selected = [lb.select_server(mixed_servers).id for _ in range(6)]
        assert "s2" not in selected
        assert "s4" not in selected
        assert selected.count("s1") == 3
        assert selected.count("s3") == 3

    def test_returns_none_when_no_servers(self):
        lb = RoundRobinLB()
        assert lb.select_server([]) is None

    def test_returns_none_when_all_unhealthy(self, mixed_servers):
        lb = RoundRobinLB()
        all_unhealthy = [Server("s1", "10.0.0.1", 8080, healthy=False)]
        assert lb.select_server(all_unhealthy) is None

    def test_name_property(self):
        lb = RoundRobinLB()
        assert lb.name == "round_robin"

    def test_complexity_property(self):
        lb = RoundRobinLB()
        assert lb.complexity == "O(1)"

    def test_reset(self, healthy_servers):
        lb = RoundRobinLB()
        lb.select_server(healthy_servers)
        lb.select_server(healthy_servers)
        lb.reset()
        # After reset, should start from beginning
        selections = [lb.select_server(healthy_servers).id for _ in range(3)]
        assert selections == ["s1", "s2", "s3"]


class TestLeastConnectionsLB:
    """Tests for Least Connections load balancer."""

    def test_selects_least_busy_server(self, healthy_servers):
        healthy_servers[0].connections = 5
        healthy_servers[1].connections = 1
        healthy_servers[2].connections = 3
        lb = LeastConnectionsLB()
        selected = lb.select_server(healthy_servers)
        assert selected.id == "s2"

    def test_increments_after_selection(self, healthy_servers):
        lb = LeastConnectionsLB()
        lb.select_server(healthy_servers)
        # All servers start at 0, first selection increments the selected one
        assert any(s.connections > 0 for s in healthy_servers)

    def test_handles_busy_servers(self, busy_servers):
        lb = LeastConnectionsLB()
        selected = lb.select_server(busy_servers)
        # Should select s2 which has only 2 connections
        assert selected.id == "s2"
        assert selected.connections == 3

    def test_skips_unhealthy_servers(self, mixed_servers):
        lb = LeastConnectionsLB()
        healthy = [s for s in mixed_servers if s.healthy]
        selected = lb.select_server(mixed_servers)
        assert selected.id in [s.id for s in healthy]

    def test_returns_none_when_no_servers(self):
        lb = LeastConnectionsLB()
        assert lb.select_server([]) is None

    def test_name_property(self):
        lb = LeastConnectionsLB()
        assert lb.name == "least_connections"

    def test_complexity_property(self):
        lb = LeastConnectionsLB()
        assert lb.complexity == "O(log n)"


class TestWeightedRoundRobinLB:
    """Tests for Weighted Round Robin load balancer."""

    def test_respects_weights(self, weighted_servers):
        lb = WeightedRoundRobinLB()
        selections = [lb.select_server(weighted_servers).id for _ in range(40)]
        s4_count = selections.count("s4")
        s1_count = selections.count("s1")
        assert s4_count > s1_count

    def test_distributes_based_on_weight_ratio(self, weighted_servers):
        lb = WeightedRoundRobinLB()
        # After many selections, distribution should approach weight ratios
        selections = [lb.select_server(weighted_servers).id for _ in range(100)]
        # s4 (weight 4) should be selected more than s1 (weight 1)
        assert selections.count("s4") > selections.count("s1")

    def test_skips_unhealthy_servers(self, mixed_servers):
        lb = WeightedRoundRobinLB()
        selected = lb.select_server(mixed_servers)
        assert selected.healthy is True

    def test_returns_none_when_no_servers(self):
        lb = WeightedRoundRobinLB()
        assert lb.select_server([]) is None

    def test_name_property(self):
        lb = WeightedRoundRobinLB()
        assert lb.name == "weighted_round_robin"

    def test_complexity_property(self):
        lb = WeightedRoundRobinLB()
        assert lb.complexity == "O(1)"


class TestAlgorithmRegistry:
    """Tests for the Algorithm Registry."""

    def test_get_all_names(self):
        from app.core.algorithm_registry import AlgorithmRegistry
        names = AlgorithmRegistry.get_all_names()
        assert "round_robin" in names
        assert "least_connections" in names
        assert "weighted_round_robin" in names

    def test_get_valid_algorithm(self):
        from app.core.algorithm_registry import AlgorithmRegistry
        lb = AlgorithmRegistry.get("round_robin")
        assert lb is not None
        assert lb.name == "round_robin"

    def test_get_invalid_algorithm(self):
        from app.core.algorithm_registry import AlgorithmRegistry
        lb = AlgorithmRegistry.get("invalid_algorithm")
        assert lb is None
