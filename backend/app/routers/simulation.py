from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import SimulationConfig, SimulationResponse
from app.simulation.traffic_generator import TrafficProfile, TrafficProfileFactory, SteadyProfile
from app.simulation.traffic_simulator import TrafficGenerator
from app.simulation.server_pool import ServerPool
from app.routers.metrics import broadcast_to_all
import asyncio

router = APIRouter()

# Simulation state
_simulation_running = False
_simulation_task: Optional[asyncio.Task] = None
_traffic_generator: Optional[TrafficGenerator] = None

# ML predictor
_predictor = None


def get_ml_predictor():
    """Lazy load the LSTM predictor."""
    global _predictor
    if _predictor is None:
        try:
            from app.ml.lstm_model import get_predictor, add_sample
            _predictor = get_predictor()
        except Exception as e:
            print(f"Failed to load LSTM predictor: {e}")
            _predictor = None
    return _predictor


@router.get("/config", response_model=SimulationConfig)
async def get_simulation_config():
    """Get current simulation configuration."""
    if _traffic_generator:
        return SimulationConfig(
            profile=_traffic_generator.profile_name,
            rate=_traffic_generator.base_rate,
            duration=_traffic_generator.duration
        )
    return SimulationConfig()


@router.put("/config", response_model=SimulationConfig)
async def update_simulation_config(config: SimulationConfig):
    """Update simulation configuration."""
    global _traffic_generator

    profile = TrafficProfileFactory.create(config.profile)
    if not profile:
        raise HTTPException(status_code=400, detail=f"Unknown profile: {config.profile}")

    _traffic_generator = TrafficGenerator(profile, config.rate, config.duration)

    return config


async def simulation_loop():
    """Background loop that generates traffic and broadcasts metrics."""
    global _simulation_running, _traffic_generator

    print(f"[LOOP] Starting. generator={_traffic_generator is not None}")

    elapsed = 0.0
    iteration = 0
    current_algorithm = "round_robin"

    # Get ML predictor (create fresh for each simulation run)
    predictor = get_ml_predictor()

    # Track recent traffic for LSTM input - use deque for efficient popleft
    from collections import deque
    traffic_history: deque = deque(maxlen=100)

    # Pre-fill with current rate for faster LSTM warmup
    initial_rate = _traffic_generator.get_current_rate() if _traffic_generator else 100.0
    for _ in range(20):
        traffic_history.append(initial_rate)

    while _simulation_running:
        try:
            if _traffic_generator:
                requests = _traffic_generator.generate_traffic(delta_time=1.0)
                current_rate = _traffic_generator.get_current_rate()

                # Add to traffic history for LSTM
                traffic_history.append(current_rate)
                # deque with maxlen auto-removes oldest when full

                # Feed to LSTM predictor
                if predictor:
                    predictor.add_traffic_sample(current_rate)
                    predictions = predictor.predict()
                else:
                    predictions = None

                # If no LSTM predictions, generate realistic fallback
                if predictions is None or len(predictions) == 0:
                    predictions = generate_predictions_fallback(current_rate, elapsed, _traffic_generator.profile_name, list(traffic_history))

                # Rotate algorithm based on predictions
                if predictions and len(predictions) >= 5:
                    avg_pred = sum(predictions) / len(predictions)
                    threshold = current_rate * 1.5

                    # If predicted load exceeds threshold, switch to least_connections
                    if avg_pred > threshold and current_algorithm != "least_connections":
                        current_algorithm = "least_connections"
                    elif avg_pred <= threshold * 0.8 and current_algorithm != "round_robin":
                        current_algorithm = "round_robin"

                # Generate routing decisions
                routing_decisions = generate_routing_decisions(iteration, current_algorithm)

                await broadcast_to_all({
                    "type": "metric_update",
                    "timestamp": datetime.now().isoformat(),
                    "servers": generate_mock_servers(elapsed, iteration, current_rate),
                    "algorithms": [],
                    "predictions": predictions[:5] if predictions else None,
                    "prediction_confidence": predictor.get_mape([current_rate] * 5, predictions[:5]) if predictor and predictions else None,
                    "decisions": routing_decisions,
                    "active_algorithm": current_algorithm,
                    "smart_router_active": current_algorithm == "least_connections",
                    "simulation": {
                        "running": True,
                        "profile": _traffic_generator.profile_name,
                        "rate": current_rate,
                        "total_requests": _traffic_generator.total_requests,
                        "elapsed": elapsed
                    }
                })

            elapsed += 1.0
            iteration += 1
            await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            print("[LOOP] Cancelled")
            break
        except Exception as e:
            print(f"[LOOP] Error: {e}")
            await asyncio.sleep(1.0)

    print("[LOOP] Exited")


def generate_predictions_fallback(current_rate: float, elapsed: float, profile_name: str, history: list) -> list:
    """Generate predictions when LSTM is not available."""
    import math

    base = current_rate

    # Use history to detect trend
    if len(history) >= 5:
        recent_avg = sum(history[-5:]) / 5
        trend = (current_rate - recent_avg) / recent_avg if recent_avg > 0 else 0
    else:
        trend = 0

    if profile_name == "burst":
        phase = int(elapsed / 5) % 4
        if phase < 2:
            multipliers = [1.4, 1.6, 1.8, 2.0]
            mult = multipliers[min(phase, 3)]
        else:
            multipliers = [0.7, 0.5]
            mult = multipliers[phase - 2]
        return [base * mult * (0.9 + math.sin(elapsed * 0.3 + i) * 0.1) for i in range(5)]

    elif profile_name == "ramp":
        increment = 1 + (elapsed % 10) * 0.05
        return [base * (1 + i * 0.15 * increment) * (0.9 + i * 0.02) for i in range(5)]

    elif profile_name == "wave":
        phase_shift = elapsed * 0.5
        return [base * (1 + math.sin(phase_shift + i * 0.7) * 0.3) for i in range(5)]

    else:  # steady
        import random
        trend_factor = 1 + trend * 0.5
        return [base * trend_factor * (0.95 + random.random() * 0.15) for _ in range(5)]


def generate_mock_servers(elapsed: float, iteration: int, traffic_rate: float = 100.0) -> list:
    """Generate mock server data for the dashboard based on traffic."""
    # Distribute traffic based on weights (s1=1, s2=2, s3=1, s4=3) = total 7
    total_weight = 7.0
    # Add some variance and iteration-based cycling
    base_connections = int(traffic_rate / total_weight)
    variance = (iteration % 10) - 5  # -5 to +5 variance

    s1_conn = max(1, base_connections * 1 + variance)
    s2_conn = max(2, base_connections * 2 + variance)
    s3_conn = max(1, base_connections * 1 + variance)
    s4_conn = max(1, base_connections * 3 + variance)

    return [
        {
            "id": "s1",
            "host": "10.0.0.1",
            "port": 8080,
            "weight": 1,
            "connections": s1_conn,
            "healthy": True,
            "failure_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "s2",
            "host": "10.0.0.2",
            "port": 8080,
            "weight": 2,
            "connections": s2_conn,
            "healthy": True,
            "failure_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "s3",
            "host": "10.0.0.3",
            "port": 8080,
            "weight": 1,
            "connections": s3_conn,
            "healthy": True,
            "failure_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "s4",
            "host": "10.0.0.4",
            "port": 8080,
            "weight": 3,
            "connections": s4_conn,
            "healthy": iteration % 20 < 18,
            "failure_count": 0 if iteration % 20 < 18 else 3,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]


def generate_routing_decisions(iteration: int, algorithm: str) -> list:
    """Generate routing decisions for the routing log."""
    servers = ['s1', 's2', 's3', 's4']
    decisions = []
    for i in range(min(3, iteration % 5 + 1)):
        decisions.append({
            "algorithm": algorithm,
            "server_id": servers[(iteration + i) % 4],
            "timestamp": datetime.now().isoformat()
        })
    return decisions


@router.post("/start", response_model=SimulationResponse)
async def start_simulation(config: Optional[SimulationConfig] = None):
    """Start traffic simulation."""
    global _simulation_running, _simulation_task, _traffic_generator

    print(f"[START] Called. Current state: running={_simulation_running}, task={_simulation_task}")

    if _simulation_running:
        raise HTTPException(status_code=400, detail="Simulation already running")

    # Clean up any lingering task
    if _simulation_task:
        print("[START] Found existing task, cleaning up...")
        _simulation_task.cancel()
        try:
            await asyncio.wait_for(_simulation_task, timeout=0.5)
        except Exception:
            pass
        _simulation_task = None

    # Use config rate or default to 100
    rate = config.rate if config and config.rate else 100.0

    # For ramp profile, use infinite duration (0) to keep ramping
    duration = config.duration if config and config.duration else 0.0

    # Always create a fresh generator when starting
    if config:
        profile = TrafficProfileFactory.create(config.profile, rate=rate, duration=duration)
        if not profile:
            raise HTTPException(status_code=400, detail=f"Unknown profile: {config.profile}")
        _traffic_generator = TrafficGenerator(profile, rate, None)
    else:
        # Use steady profile with default rate
        profile = SteadyProfile(rate=100.0)
        _traffic_generator = TrafficGenerator(profile, 100.0, None)

    # Start the generator
    _traffic_generator.start()

    _simulation_running = True
    _simulation_task = asyncio.create_task(simulation_loop())

    print(f"[START] Simulation started: profile={profile.name}, rate={rate}")

    return SimulationResponse(
        status="started",
        profile=_traffic_generator.profile_name,
        rate=_traffic_generator.base_rate,
        message="Traffic simulation started with LSTM predictions"
    )


@router.post("/stop", response_model=SimulationResponse)
async def stop_simulation():
    """Stop traffic simulation."""
    global _simulation_running, _simulation_task, _traffic_generator

    print(f"[STOP] Called. Current state: running={_simulation_running}, task={_simulation_task}")

    if not _simulation_running:
        raise HTTPException(status_code=400, detail="No simulation running")

    _simulation_running = False

    # Wait for task to complete cancellation
    if _simulation_task:
        _task = _simulation_task
        _task.cancel()
        try:
            await asyncio.wait_for(_task, timeout=2.0)
        except asyncio.CancelledError:
            pass
        except asyncio.TimeoutError:
            print("[STOP] Task did not cancel in time, forcing...")
            _task.cancel()
        except Exception as e:
            print(f"[STOP] Error during cancel: {e}")
        _simulation_task = None

    print("[STOP] Task cancelled, sending final broadcast...")

    # Send final broadcast with zeroed state
    await broadcast_to_all({
        "type": "metric_update",
        "timestamp": datetime.now().isoformat(),
        "servers": [
            {"id": "s1", "host": "10.0.0.1", "port": 8080, "weight": 1, "connections": 0, "healthy": True, "failure_count": 0, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "s2", "host": "10.0.0.2", "port": 8080, "weight": 2, "connections": 0, "healthy": True, "failure_count": 0, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "s3", "host": "10.0.0.3", "port": 8080, "weight": 1, "connections": 0, "healthy": True, "failure_count": 0, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "s4", "host": "10.0.0.4", "port": 8080, "weight": 3, "connections": 0, "healthy": True, "failure_count": 0, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
        ],
        "algorithms": [],
        "predictions": None,
        "prediction_confidence": None,
        "decisions": [],
        "active_algorithm": "round_robin",
        "smart_router_active": False,
        "simulation": {
            "running": False,
            "profile": _traffic_generator.profile_name if _traffic_generator else "unknown",
            "rate": 0,
            "total_requests": 0,
            "elapsed": 0
        }
    })

    # Reset traffic generator for next run
    if _traffic_generator:
        _traffic_generator.reset()

    return SimulationResponse(
        status="stopped",
        profile=_traffic_generator.profile_name if _traffic_generator else "unknown",
        rate=0,
        message="Traffic simulation stopped"
    )


@router.get("/status")
async def get_simulation_status():
    """Get simulation status."""
    return {
        "running": _simulation_running,
        "profile": _traffic_generator.profile_name if _traffic_generator else None,
        "rate": _traffic_generator.base_rate if _traffic_generator else None
    }


@router.get("/predictions")
async def get_predictions():
    """Get current LSTM predictions (for debugging)."""
    predictor = get_ml_predictor()
    if predictor:
        predictions = predictor.predict()
        return {
            "predictions": predictions[:5] if predictions else [],
            "model_type": "LSTM",
            "window_size": predictor.window_size,
            "forecast_steps": predictor.forecast_steps,
            "is_trained": predictor.is_trained
        }
    return {
        "predictions": [],
        "model_type": "none",
        "error": "LSTM model not initialized"
    }


def get_simulation_generator() -> Optional[TrafficGenerator]:
    """Get the current traffic generator."""
    return _traffic_generator


def is_simulation_running() -> bool:
    """Check if simulation is running."""
    return _simulation_running