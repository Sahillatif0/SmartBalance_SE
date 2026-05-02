from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Server as ServerModel
from app.schemas import ServerCreate, ServerUpdate, ServerResponse
from app.core.load_balancer import Server

router = APIRouter()

# In-memory server pool for load balancing
server_pool: List[Server] = []
server_models: dict = {}


def sync_server_models():
    """Sync in-memory pool with database models."""
    global server_pool, server_models
    server_pool = [
        Server(
            id=m.id,
            host=m.host,
            port=m.port,
            weight=m.weight,
            connections=m.connections,
            healthy=m.healthy,
            failure_count=m.failure_count
        )
        for m in server_models.values()
    ]


@router.get("", response_model=List[ServerResponse])
async def list_servers(db: AsyncSession = Depends(get_db)):
    """List all servers."""
    result = await db.execute(select(ServerModel))
    servers = result.scalars().all()
    return servers


@router.post("", response_model=ServerResponse, status_code=201)
async def create_server(server: ServerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new server."""
    result = await db.execute(select(ServerModel).where(ServerModel.id == server.id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Server with this ID already exists")

    db_server = ServerModel(
        id=server.id,
        host=server.host,
        port=server.port,
        weight=server.weight
    )
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)

    server_models[db_server.id] = db_server
    sync_server_models()

    return db_server


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(server_id: str, db: AsyncSession = Depends(get_db)):
    """Get server by ID."""
    result = await db.execute(select(ServerModel).where(ServerModel.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: str,
    server_update: ServerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update server."""
    result = await db.execute(select(ServerModel).where(ServerModel.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    update_data = server_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(server, field, value)

    await db.commit()
    await db.refresh(server)

    server_models[server.id] = server
    sync_server_models()

    return server


@router.delete("/{server_id}", status_code=204)
async def delete_server(server_id: str, db: AsyncSession = Depends(get_db)):
    """Delete server."""
    result = await db.execute(select(ServerModel).where(ServerModel.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    await db.delete(server)
    await db.commit()

    if server_id in server_models:
        del server_models[server_id]
    sync_server_models()


@router.put("/{server_id}/health", response_model=ServerResponse)
async def update_health(
    server_id: str,
    healthy: bool,
    db: AsyncSession = Depends(get_db)
):
    """Update server health status."""
    result = await db.execute(select(ServerModel).where(ServerModel.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    server.healthy = healthy
    server.failure_count = 0 if healthy else server.failure_count + 1

    await db.commit()
    await db.refresh(server)

    server_models[server.id] = server
    sync_server_models()

    return server


def get_server_pool() -> List[Server]:
    """Get the current server pool."""
    return server_pool
