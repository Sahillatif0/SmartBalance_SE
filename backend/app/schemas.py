from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ServerBase(BaseModel):
    id: str
    host: str
    port: int = 8080
    weight: int = 1


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    weight: Optional[int] = None
    healthy: Optional[bool] = None
    connections: Optional[int] = None


class ServerResponse(ServerBase):
    connections: int = 0
    healthy: bool = True
    failure_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlgorithmResponse(BaseModel):
    name: str
    description: str
    complexity: str


class AlgorithmListResponse(BaseModel):
    algorithms: List[AlgorithmResponse]


class AlgorithmSelectResponse(BaseModel):
    active: str
    message: str


class AlgorithmStatsResponse(BaseModel):
    algorithm: str
    total_requests: int
    average_latency: float
    average_connections: float
    error_rate: float


class MetricResponse(BaseModel):
    id: int
    server_id: str
    timestamp: datetime
    latency: Optional[float]
    error_rate: Optional[float]
    throughput: Optional[float]

    class Config:
        from_attributes = True


class SimulationConfig(BaseModel):
    profile: str = Field(default="steady", pattern="^(steady|burst|ramp|wave)$")
    rate: float = 100.0
    duration: Optional[float] = None


class SimulationResponse(BaseModel):
    status: str
    profile: str
    rate: float
    message: str


class PredictionResponse(BaseModel):
    predictions: List[float]
    timestamps: List[datetime]
    confidence: Optional[float]
    model_version: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    servers: List[ServerResponse]
