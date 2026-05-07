import torch
import torch.nn as nn
import numpy as np
from typing import List, Optional
from collections import deque
import random


class LSTMModel(nn.Module):
    """
    Two-layer LSTM for traffic prediction.

    Architecture:
    - Input: 60-step sliding window of normalized request rates
    - Hidden: 64 units per layer, batch_first=True
    - Output: 15-step ahead forecast
    - Loss: MSE with Adam optimizer
    """

    def __init__(self, input_size: int = 1, hidden_size: int = 64, num_layers: int = 2, output_steps: int = 15):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_steps = output_steps

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, output_steps)
        )

    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # Get last time step output
        last_output = lstm_out[:, -1, :]
        predictions = self.fc(last_output)
        return predictions


class TrafficPredictor:
    """
    LSTM-based traffic prediction system.

    Maintains a sliding window of traffic history and generates
    15-step ahead forecasts using a trained LSTM model.
    """

    def __init__(
        self,
        window_size: int = 60,
        forecast_steps: int = 15,
        hidden_size: int = 64,
        device: str = "cpu"
    ):
        self.window_size = window_size
        self.forecast_steps = forecast_steps
        self.device = torch.device(device)

        # Initialize model
        self.model = LSTMModel(
            input_size=1,
            hidden_size=hidden_size,
            num_layers=2,
            output_steps=forecast_steps
        ).to(self.device)

        # Trajectory buffer for sliding window - use deque for efficient popleft
        self.trajectory: deque = deque(maxlen=window_size)
        self.is_trained = False

        # Train with synthetic patterns
        self._initialize_with_patterns()

    def _initialize_with_patterns(self):
        """
        Initialize model with common traffic patterns.
        This simulates having trained on historical data.
        """
        patterns = []

        # Steady pattern
        for _ in range(50):
            base = random.uniform(80, 120)
            pattern = [base + random.gauss(0, 5) for _ in range(self.window_size + self.forecast_steps)]
            patterns.append(pattern)

        # Burst pattern
        for _ in range(50):
            base = random.uniform(60, 100)
            pattern = []
            for i in range(self.window_size + self.forecast_steps):
                if (i % 10) < 5:
                    pattern.append(base * 1.8 + random.gauss(0, 10))
                else:
                    pattern.append(base * 0.6 + random.gauss(0, 5))
            patterns.append(pattern)

        # Ramp pattern
        for _ in range(50):
            start = random.uniform(50, 80)
            end = random.uniform(150, 200)
            pattern = [start + (end - start) * (i / (self.window_size + self.forecast_steps)) + random.gauss(0, 5)
                      for i in range(self.window_size + self.forecast_steps)]
            patterns.append(pattern)

        # Wave pattern
        for _ in range(50):
            base = random.uniform(80, 120)
            pattern = [base * (1 + 0.4 * np.sin(i * 0.3)) + random.gauss(0, 5)
                      for i in range(self.window_size + self.forecast_steps)]
            patterns.append(pattern)

        # Train on all patterns
        X_train = []
        y_train = []
        for pattern in patterns:
            X_train.append(pattern[:self.window_size])
            y_train.append(pattern[self.window_size:])

        self.train_model(X_train, y_train, epochs=30)
        self.is_trained = True

    def train_model(self, X: List[List[float]], y: List[List[float]], epochs: int = 30):
        """Train the LSTM model on provided data."""
        if not X or not y:
            return

        # Normalize data
        all_values = [v for seq in X + y for v in seq]
        min_val = min(all_values) if all_values else 0
        max_val = max(all_values) if all_values else 1
        if max_val == min_val:
            max_val = min_val + 1

        # Prepare training data
        X_tensor = []
        y_tensor = []
        for seq, target in zip(X, y):
            # Normalize input sequence
            normalized_seq = [[(v - min_val) / (max_val - min_val)] for v in seq]
            normalized_target = [(v - min_val) / (max_val - min_val) for v in target]

            X_tensor.append(normalized_seq)
            y_tensor.append(normalized_target)

        X_tensor = torch.FloatTensor(X_tensor).to(self.device)
        y_tensor = torch.FloatTensor(y_tensor).to(self.device)

        # Training
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        criterion = nn.MSELoss()

        for epoch in range(epochs):
            optimizer.zero_grad()
            output = self.model(X_tensor)
            loss = criterion(output, y_tensor)
            loss.backward()
            optimizer.step()

    def add_traffic_sample(self, request_rate: float):
        """Add a new traffic sample to the trajectory buffer."""
        self.trajectory.append(request_rate)
        # deque with maxlen auto-removes oldest when full

    def predict(self) -> Optional[List[float]]:
        """
        Generate 15-step ahead predictions based on current trajectory.

        Returns:
            List of predicted request rates for next 15 time steps
        """
        if not self.is_trained or len(self.trajectory) < 10:
            # Not enough data, return simple extrapolation
            if self.trajectory:
                base = self.trajectory[-1]
                return [base * (1 + i * 0.02 + random.uniform(-0.05, 0.05))
                       for i in range(self.forecast_steps)]
            return None

        self.model.eval()
        with torch.no_grad():
            # Normalize trajectory - convert deque to list for slicing
            trajectory_list = list(self.trajectory)
            min_val = min(trajectory_list) if trajectory_list else 0
            max_val = max(trajectory_list) if trajectory_list else 1
            if max_val == min_val:
                max_val = min_val + 1

            # Get last window_size samples
            samples = trajectory_list[-self.window_size:] if len(trajectory_list) >= self.window_size else trajectory_list

            normalized = [[(v - min_val) / (max_val - min_val)] for v in samples]

            # Pad if needed
            while len(normalized) < self.window_size:
                normalized.insert(0, normalized[0])

            input_tensor = torch.FloatTensor([normalized]).to(self.device)
            output = self.model(input_tensor)

            # Denormalize predictions
            predictions = output.cpu().numpy()[0]
            denormalized = [p * (max_val - min_val) + min_val for p in predictions]

            # Add some realistic noise
            denormalized = [max(0, v + random.gauss(0, v * 0.02)) for v in denormalized]

            return denormalized

    def get_mape(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate Mean Absolute Percentage Error."""
        if not actual or not predicted:
            return 0.0

        errors = []
        for a, p in zip(actual, predicted):
            if a != 0:
                errors.append(abs((a - p) / a) * 100)

        return sum(errors) / len(errors) if errors else 0.0


# Global predictor instance
_predictor: Optional[TrafficPredictor] = None


def get_predictor() -> TrafficPredictor:
    """Get or create the global traffic predictor."""
    global _predictor
    if _predictor is None:
        _predictor = TrafficPredictor(
            window_size=60,
            forecast_steps=15,
            hidden_size=64
        )
    return _predictor


def predict_next() -> Optional[List[float]]:
    """Get next set of predictions."""
    predictor = get_predictor()
    return predictor.predict()


def add_sample(rate: float):
    """Add a traffic sample for prediction."""
    predictor = get_predictor()
    predictor.add_traffic_sample(rate)