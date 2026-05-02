import asyncio
import aiohttp
from typing import Optional, List, Callable
from datetime import datetime
from app.core.load_balancer import Server
from app.config import get_settings

settings = get_settings()


class HealthChecker:
    """
    Background health checker that monitors server health.

    Pings each server's /health endpoint at a configurable interval.
    Marks server unhealthy after a configurable number of consecutive failures.
    """

    def __init__(
        self,
        interval: float = None,
        failure_threshold: int = None,
        on_unhealthy: Optional[Callable] = None,
        on_healthy: Optional[Callable] = None
    ):
        self.interval = interval or settings.health_check_interval
        self.failure_threshold = failure_threshold or settings.health_check_failure_threshold
        self.on_unhealthy = on_unhealthy
        self.on_healthy = on_healthy
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_check_time: Optional[datetime] = None

    async def start(self, servers: List[Server]):
        """Start the health check loop."""
        self._running = True
        self._task = asyncio.create_task(self._check_loop(servers))

    async def stop(self):
        """Stop the health check loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _check_loop(self, servers: List[Server]):
        """Main health check loop."""
        while self._running:
            await self._check_servers(servers)
            self._last_check_time = datetime.now()
            await asyncio.sleep(self.interval)

    async def _check_servers(self, servers: List[Server]):
        """Check health of all servers."""
        tasks = [self._ping_server(server) for server in servers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for server, is_healthy in zip(servers, results):
            if isinstance(is_healthy, Exception):
                is_healthy = False

            was_healthy = server.healthy
            if is_healthy:
                server.failure_count = 0
                if not was_healthy:
                    server.mark_healthy()
                    if self.on_healthy:
                        self.on_healthy(server)
            else:
                server.failure_count += 1
                if server.failure_count >= self.failure_threshold and was_healthy:
                    server.mark_unhealthy()
                    if self.on_unhealthy:
                        self.on_unhealthy(server)

    async def _ping_server(self, server: Server) -> bool:
        """Ping a single server's health endpoint."""
        try:
            timeout = aiohttp.ClientTimeout(total=2)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"http://{server.host}:{server.port}/health"
                async with session.get(url) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def check_single(self, server: Server) -> bool:
        """Check health of a single server."""
        return await self._ping_server(server)

    @property
    def is_running(self) -> bool:
        """Check if health checker is running."""
        return self._running

    @property
    def last_check(self) -> Optional[datetime]:
        """Get the time of the last check."""
        return self._last_check_time
