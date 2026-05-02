from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import SimulationConfig, SimulationResponse
from app.simulation.traffic_generator import TrafficProfile, TrafficProfileFactory, SteadyProfile
from app.simulation.traffic_simulator import TrafficGenerator
from app.simulation.server_pool import ServerPool
import asyncio

router = APIRouter()

# Simulation state
_simulation_running = False
_simulation_task: Optional[asyncio.Task] = None
_traffic_generator: Optional[TrafficGenerator] = None


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

    from app.routers.metrics import broadcast_to_all

    elapsed = 0.0
    iteration = 0
    current_algorithm = "round_robin"

    while _simulation_running:
        try:
            if _traffic_generator:
                requests = _traffic_generator.generate_traffic(delta_time=1.0)
                current_rate = _traffic_generator.get_current_rate()

                # Rotate algorithm every 10 iterations for demo
                if iteration % 10 == 0:
                    algorithms = ["round_robin", "least_connections", "weighted_round_robin"]
                    current_algorithm = algorithms[(iteration // 10) % 3]

                # Generate routing decisions
                routing_decisions = generate_routing_decisions(iteration, current_algorithm)

                await broadcast_to_all({
                    "type": "metric_update",
                    "timestamp": datetime.now().isoformat(),
                    "servers": generate_mock_servers(elapsed, iteration),
                    "algorithms": [],
                    "predictions": generate_mock_predictions(current_rate),
                    "decisions": routing_decisions,
                    "active_algorithm": current_algorithm,
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
            break
        except Exception as e:
            print(f"Simulation loop error: {e}")
            await asyncio.sleep(1.0)


def generate_mock_servers(elapsed: float, iteration: int) -> list:
    """Generate mock server data for the dashboard."""
    return [
        {
            "id": "s1",
            "host": "10.0.0.1",
            "port": 8080,
            "weight": 1,
            "connections": (iteration % 10) + 5,
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
            "connections": (iteration % 8) + 3,
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
            "connections": (iteration % 6) + 2,
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
            "connections": (iteration % 4) + 1,
            "healthy": iteration % 20 < 18,  # Occasionally unhealthy
            "failure_count": 0 if iteration % 20 < 18 else 3,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]


def generate_mock_predictions(current_rate: float) -> list:
    """Generate mock AI predictions."""
    base = current_rate
    return [
        base * 0.9,
        base * 1.1,
        base * 1.3,
        base * 1.5,
        base * 1.2
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

    if _simulation_running:
        raise HTTPException(status_code=400, detail="Simulation already running")

    if config:
        profile = TrafficProfileFactory.create(config.profile)
        if not profile:
            raise HTTPException(status_code=400, detail=f"Unknown profile: {config.profile}")
        _traffic_generator = TrafficGenerator(profile, config.rate, config.duration)
    elif not _traffic_generator:
        profile = SteadyProfile(rate=100.0)
        _traffic_generator = TrafficGenerator(profile, 100.0)

    _simulation_running = True
    _simulation_task = asyncio.create_task(simulation_loop())

    return SimulationResponse(
        status="started",
        profile=_traffic_generator.profile_name,
        rate=_traffic_generator.base_rate,
        message="Traffic simulation started"
    )


@router.post("/stop", response_model=SimulationResponse)
async def stop_simulation():
    """Stop traffic simulation."""
    global _simulation_running, _simulation_task

    if not _simulation_running:
        raise HTTPException(status_code=400, detail="No simulation running")

    _simulation_running = False
    if _simulation_task:
        _simulation_task.cancel()
        try:
            await _simulation_task
        except asyncio.CancelledError:
            pass
        _simulation_task = None

    return SimulationResponse(
        status="stopped",
        profile=_traffic_generator.profile_name if _traffic_generator else "unknown",
        rate=_traffic_generator.base_rate if _traffic_generator else 0,
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


def get_simulation_generator() -> Optional[TrafficGenerator]:
    """Get the current traffic generator."""
    return _traffic_generator


def is_simulation_running() -> bool:
    """Check if simulation is running."""
    return _simulation_running
