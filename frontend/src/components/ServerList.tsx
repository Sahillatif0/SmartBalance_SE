import type { Server } from '../types';
import { Server as ServerIcon, Wifi, WifiOff } from 'lucide-react';

interface ServerListProps {
  servers: Server[];
}

export function ServerList({ servers }: ServerListProps) {
  const defaultServers: Server[] = servers.length > 0 ? servers : [
    { id: 's1', host: '10.0.0.1', port: 8080, weight: 1, connections: 0, healthy: true, failure_count: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: 's2', host: '10.0.0.2', port: 8080, weight: 2, connections: 0, healthy: true, failure_count: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: 's3', host: '10.0.0.3', port: 8080, weight: 1, connections: 0, healthy: true, failure_count: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: 's4', host: '10.0.0.4', port: 8080, weight: 3, connections: 0, healthy: false, failure_count: 3, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  ];

  const healthyCount = defaultServers.filter(s => s.healthy).length;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'rgba(99,102,241,0.1)' }}>
            <ServerIcon className="w-4 h-4" style={{ color: '#6366f1' }} />
          </div>
          <h2 className="text-base font-semibold">Server Pool</h2>
        </div>
        <div className="stat-pill">
          <span className="font-medium" style={{ color: healthyCount === defaultServers.length ? '#22c55e' : '#f59e0b' }}>
            {healthyCount}
          </span>
          <span className="text-xs" style={{ color: '#48484a' }}>/{defaultServers.length} online</span>
        </div>
      </div>

      {/* Server Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {defaultServers.map((server, idx) => (
          <div
            key={server.id}
            className="relative rounded-xl p-4 transition-all duration-300 group"
            style={{
              background: server.healthy ? 'rgba(255,255,255,0.02)' : 'rgba(239,68,68,0.05)',
              border: `1px solid ${server.healthy ? 'rgba(255,255,255,0.06)' : 'rgba(239,68,68,0.2)'}`,
              opacity: 0,
              animation: `fadeInUp 0.4s ease-out ${idx * 0.05}s forwards`
            }}
          >
            {/* Glow on hover */}
            <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                 style={{ background: 'radial-gradient(circle at center, rgba(245,158,11,0.05) 0%, transparent 70%)' }} />

            {/* Header */}
            <div className="flex items-center justify-between mb-4 relative">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-medium">{server.id}</span>
                {server.healthy ? (
                  <Wifi className="w-4 h-4" style={{ color: '#22c55e' }} />
                ) : (
                  <WifiOff className="w-4 h-4" style={{ color: '#ef4444' }} />
                )}
              </div>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-md ${
                server.healthy
                  ? 'bg-emerald-500/10 text-emerald-400'
                  : 'bg-rose-500/10 text-rose-400'
              }`}>
                {server.healthy ? 'Online' : 'Offline'}
              </span>
            </div>

            {/* Host */}
            <div className="text-xs font-mono mb-4" style={{ color: '#48484a' }}>
              {server.host}:{server.port}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <div className="text-xs mb-1" style={{ color: '#48484a' }}>Weight</div>
                <div className="font-mono text-sm">{server.weight}</div>
              </div>
              <div>
                <div className="text-xs mb-1" style={{ color: '#48484a' }}>Connections</div>
                <div className="font-mono text-sm" style={{ color: server.healthy ? '#6366f1' : '#ef4444' }}>
                  {server.connections}
                </div>
              </div>
            </div>

            {/* Connection Bar */}
            <div className="h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(100, server.connections * 5)}%`,
                  background: server.healthy
                    ? 'linear-gradient(90deg, #6366f1, #8b5cf6)'
                    : '#ef4444'
                }}
              />
            </div>

            {/* Failure Badge */}
            {!server.healthy && (
              <div className="mt-3 text-xs flex items-center gap-1" style={{ color: '#ef4444' }}>
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                {server.failure_count}/3 failures
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}