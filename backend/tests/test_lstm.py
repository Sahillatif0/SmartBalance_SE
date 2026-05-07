import pytest
from app.ml.lstm_model import TrafficPredictor, LSTMModel
from app.ml.metrics_calculator import calculate_mape, calculate_directional_accuracy
from app.core.smart_router import SmartRouter
from app.core.load_balancer import Server


class TestLSTMModel:
    """Tests for the LSTM model and TrafficPredictor."""

    def test_lstm_model_forward(self):
        """Test LSTM model forward pass."""
        model = LSTMModel(input_size=1, hidden_size=64, num_layers=2, output_steps=15)
        import torch
        x = torch.randn(8, 60, 1)  # batch=8, seq=60, input=1
        output = model(x)
        assert output.shape == (8, 15)

    def test_traffic_predictor_initialization(self):
        """Test TrafficPredictor initializes and trains on patterns."""
        predictor = TrafficPredictor(window_size=60, forecast_steps=15)
        assert predictor.is_trained is True
        assert predictor.window_size == 60
        assert predictor.forecast_steps == 15

    def test_traffic_predictor_add_sample(self):
        """Test adding traffic samples to trajectory."""
        predictor = TrafficPredictor(window_size=10, forecast_steps=5)
        for i in range(15):
            predictor.add_traffic_sample(100 + i)

        assert len(predictor.trajectory) == 10  # Should be capped at window_size

    def test_traffic_predictor_predict_with_data(self):
        """Test prediction with sufficient trajectory data."""
        predictor = TrafficPredictor(window_size=60, forecast_steps=15)

        # Add enough samples
        for i in range(70):
            predictor.add_traffic_sample(100 + (i % 10) * 2)

        predictions = predictor.predict()
        assert predictions is not None
        assert len(predictions) == 15
        # All predictions should be positive
        assert all(p > 0 for p in predictions)

    def test_traffic_predictor_predict_fallback(self):
        """Test prediction fallback when not enough data."""
        predictor = TrafficPredictor(window_size=60, forecast_steps=15)

        # Add only a few samples
        predictor.add_traffic_sample(100)
        predictor.add_traffic_sample(105)

        predictions = predictor.predict()
        assert predictions is not None
        assert len(predictions) == 15

    def test_traffic_predictor_mape(self):
        """Test MAPE calculation."""
        predictor = TrafficPredictor()
        actual = [100, 110, 120, 130, 140]
        predicted = [105, 108, 125, 128, 145]
        mape = predictor.get_mape(actual, predicted)
        assert mape > 0
        assert mape < 100  # Should be reasonable percentage


class TestMetricsCalculator:
    """Tests for metrics calculator utilities."""

    def test_calculate_mape(self):
        """Test MAPE calculation."""
        actual = [100, 110, 120, 130, 140]
        predicted = [105, 108, 125, 128, 145]
        mape = calculate_mape(actual, predicted)
        assert mape > 0
        assert mape < 50

    def test_calculate_mape_empty(self):
        """Test MAPE with empty data returns 0."""
        assert calculate_mape([], []) == 0.0
        assert calculate_mape([100], []) == 0.0

    def test_calculate_directional_accuracy(self):
        """Test directional accuracy calculation."""
        actual = [100, 110, 120, 110, 100]  # up, up, up, down, down
        predicted = [100, 108, 125, 115, 95]  # same directions
        accuracy = calculate_directional_accuracy(actual, predicted)
        assert accuracy == 100.0  # All directions correct


class TestSmartRouter:
    """Tests for SmartRouter with LSTM integration."""

    def test_smart_router_initialization(self):
        """Test SmartRouter initializes correctly."""
        predictor = TrafficPredictor()
        router = SmartRouter(
            primary_algorithm='round_robin',
            fallback_algorithm='least_connections',
            predictor=predictor
        )
        assert router.active_algorithm == 'round_robin'
        assert router.is_using_fallback is False
        assert router.switch_count == 0

    def test_smart_router_switch_on_high_load(self):
        """Test SmartRouter switches to fallback on high predicted load."""
        predictor = TrafficPredictor(window_size=60, forecast_steps=15)

        # Add samples showing increasing traffic
        for i in range(70):
            predictor.add_traffic_sample(200 + i * 5)  # Rising traffic

        router = SmartRouter(
            primary_algorithm='round_robin',
            fallback_algorithm='least_connections',
            predictor=predictor,
            threshold=1.0  # Lower threshold for testing
        )

        servers = [
            Server(id='s1', host='10.0.0.1', port=8080, weight=1),
            Server(id='s2', host='10.0.0.2', port=8080, weight=2),
        ]

        # With high predicted load and low current_load, should trigger switch
        router.evaluate_and_switch(servers, current_load=100.0)

        # Verify predictions are working
        preds = predictor.predict()
        assert preds is not None
        assert len(preds) == 15

    def test_smart_router_selects_server(self):
        """Test SmartRouter can select servers."""
        predictor = TrafficPredictor()
        router = SmartRouter(predictor=predictor)

        servers = [
            Server(id='s1', host='10.0.0.1', port=8080, weight=1),
            Server(id='s2', host='10.0.0.2', port=8080, weight=2),
        ]

        selected = router.select_server(servers)
        assert selected is not None
        assert selected.id in ['s1', 's2']

    def test_smart_router_force_switch(self):
        """Test forced algorithm switching."""
        router = SmartRouter(primary_algorithm='round_robin')

        result = router.force_switch('least_connections')
        assert result is True
        assert router.active_algorithm == 'least_connections'
        assert router.is_using_fallback is True

    def test_smart_router_stats(self):
        """Test getting router statistics."""
        predictor = TrafficPredictor()
        router = SmartRouter(predictor=predictor)

        stats = router.get_stats()
        assert 'active_algorithm' in stats
        assert 'using_fallback' in stats
        assert 'switch_count' in stats
        assert 'total_requests' in stats
        assert 'threshold' in stats
