"""Metrics calculation utilities for ML predictions."""

import numpy as np
from typing import List, Optional


def calculate_mape(actual: List[float], predicted: List[float]) -> float:
    """
    Calculate Mean Absolute Percentage Error.

    Args:
        actual: List of actual values
        predicted: List of predicted values

    Returns:
        MAPE as a percentage
    """
    if not actual or not predicted:
        return 0.0

    if len(actual) != len(predicted):
        min_len = min(len(actual), len(predicted))
        actual = actual[:min_len]
        predicted = predicted[:min_len]

    errors = []
    for a, p in zip(actual, predicted):
        if a != 0:
            errors.append(abs((a - p) / a) * 100)

    return sum(errors) / len(errors) if errors else 0.0


def calculate_mae(actual: List[float], predicted: List[float]) -> float:
    """Calculate Mean Absolute Error."""
    if not actual or not predicted:
        return 0.0

    min_len = min(len(actual), len(predicted))
    actual = actual[:min_len]
    predicted = predicted[:min_len]

    return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)


def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
    """Calculate Root Mean Squared Error."""
    if not actual or not predicted:
        return 0.0

    min_len = min(len(actual), len(predicted))
    actual = actual[:min_len]
    predicted = predicted[:min_len]

    squared_errors = [(a - p) ** 2 for a, p in zip(actual, predicted)]
    return np.sqrt(sum(squared_errors) / len(squared_errors))


def calculate_directional_accuracy(
    actual: List[float],
    predicted: List[float]
) -> float:
    """
    Calculate directional accuracy (% of correct trend predictions).

    Args:
        actual: List of actual values
        predicted: List of predicted values

    Returns:
        Accuracy as a percentage (0-100)
    """
    if len(actual) < 2 or len(predicted) < 2:
        return 0.0

    correct = 0
    total = 0

    for i in range(1, min(len(actual), len(predicted))):
        actual_direction = actual[i] - actual[i - 1]
        predicted_direction = predicted[i] - predicted[i - 1]

        if actual_direction > 0 and predicted_direction > 0:
            correct += 1
        elif actual_direction < 0 and predicted_direction < 0:
            correct += 1
        elif actual_direction == 0 and predicted_direction == 0:
            correct += 1

        total += 1

    return (correct / total * 100) if total > 0 else 0.0
