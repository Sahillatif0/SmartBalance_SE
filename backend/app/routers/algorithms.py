from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.schemas import (
    AlgorithmResponse,
    AlgorithmListResponse,
    AlgorithmSelectResponse,
    AlgorithmStatsResponse
)
from app.core.algorithm_registry import AlgorithmRegistry
from app.core.load_balancer import LoadBalancer

router = APIRouter()

# Current active algorithm
_active_algorithm: Dict[str, Any] = {
    "name": "round_robin",
    "instance": AlgorithmRegistry.get("round_robin"),
    "stats": {"total_requests": 0, "total_latency": 0.0, "error_count": 0}
}


@router.get("", response_model=AlgorithmListResponse)
async def list_algorithms():
    """List all available algorithms."""
    algorithms = []
    for name in AlgorithmRegistry.get_all_names():
        info = AlgorithmRegistry.get_info(name)
        if info:
            complexity, description = info
            algorithms.append(AlgorithmResponse(
                name=name,
                description=description,
                complexity=complexity
            ))
    return AlgorithmListResponse(algorithms=algorithms)


@router.get("/{algorithm_name}")
async def get_algorithm(algorithm_name: str):
    """Get algorithm details."""
    info = AlgorithmRegistry.get_info(algorithm_name)
    if not info:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    complexity, description = info
    instance = AlgorithmRegistry.get(algorithm_name)

    return {
        "name": algorithm_name,
        "description": description,
        "complexity": complexity,
        "is_active": _active_algorithm["name"] == algorithm_name
    }


@router.post("/{algorithm_name}/select", response_model=AlgorithmSelectResponse)
async def select_algorithm(algorithm_name: str):
    """Switch to a different algorithm."""
    instance = AlgorithmRegistry.get(algorithm_name)
    if not instance:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    _active_algorithm["name"] = algorithm_name
    _active_algorithm["instance"] = instance
    _active_algorithm["stats"] = {"total_requests": 0, "total_latency": 0.0, "error_count": 0}

    return AlgorithmSelectResponse(
        active=algorithm_name,
        message=f"Successfully switched to {algorithm_name}"
    )


@router.get("/{algorithm_name}/stats", response_model=AlgorithmStatsResponse)
async def get_algorithm_stats(algorithm_name: str):
    """Get algorithm performance statistics."""
    if _active_algorithm["name"] != algorithm_name:
        raise HTTPException(status_code=404, detail="Algorithm not active")

    stats = _active_algorithm["stats"]
    total = stats["total_requests"]

    return AlgorithmStatsResponse(
        algorithm=algorithm_name,
        total_requests=total,
        average_latency=stats["total_latency"] / total if total > 0 else 0.0,
        average_connections=0.0,
        error_rate=stats["error_count"] / total if total > 0 else 0.0
    )


def get_active_algorithm() -> LoadBalancer:
    """Get the currently active algorithm instance."""
    return _active_algorithm["instance"]


def get_active_algorithm_name() -> str:
    """Get the name of the currently active algorithm."""
    return _active_algorithm["name"]


def update_algorithm_stats(latency: float = 0.0, error: bool = False):
    """Update stats for the active algorithm."""
    stats = _active_algorithm["stats"]
    stats["total_requests"] += 1
    stats["total_latency"] += latency
    if error:
        stats["error_count"] += 1
