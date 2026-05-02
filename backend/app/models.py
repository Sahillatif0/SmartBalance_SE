from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(String, primary_key=True, index=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    weight = Column(Integer, default=1)
    connections = Column(Integer, default=0)
    healthy = Column(Boolean, default=True)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    server_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    latency = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    throughput = Column(Float, nullable=True)


class RoutingDecision(Base):
    __tablename__ = "routing_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    algorithm = Column(String, nullable=False)
    selected_server_id = Column(String, nullable=False)
    request_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=func.now())
    extra_data = Column(JSON, nullable=True)
