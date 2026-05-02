import { GitBranch, Clock, ArrowRight } from 'lucide-react';

interface RoutingDecision {
  algorithm: string;
  server_id: string;
  timestamp: string;
}

interface RoutingLogProps {
  decisions: RoutingDecision[];
}

const algorithmMeta: Record<string, { color: string; bg: string }> = {
  'round_robin': { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
  'least_connections': { color: '#22c55e', bg: 'rgba(34,197,94,0.1)' },
  'weighted_round_robin': { color: '#6366f1', bg: 'rgba(99,102,241,0.1)' },
};

export function RoutingLog({ decisions = [] }: RoutingLogProps) {
  const displayDecisions = decisions.length > 0 ? decisions : [
    { algorithm: 'round_robin', server_id: 's1', timestamp: new Date().toISOString() },
    { algorithm: 'round_robin', server_id: 's2', timestamp: new Date().toISOString() },
    { algorithm: 'round_robin', server_id: 's3', timestamp: new Date().toISOString() },
    { algorithm: 'least_connections', server_id: 's1', timestamp: new Date().toISOString() },
    { algorithm: 'least_connections', server_id: 's2', timestamp: new Date().toISOString() },
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'rgba(168,85,247,0.1)' }}>
            <GitBranch className="w-4 h-4" style={{ color: '#a855f7' }} />
          </div>
          <h2 className="text-base font-semibold">Routing Log</h2>
        </div>
        <span className="text-xs font-mono px-2 py-1 rounded-md" style={{ background: 'rgba(255,255,255,0.04)', color: '#86868b' }}>
          {displayDecisions.length} recent
        </span>
      </div>

      {/* Decisions List */}
      <div className="space-y-2 max-h-56 overflow-y-auto">
        {displayDecisions.map((decision, idx) => {
          const meta = algorithmMeta[decision.algorithm] || { color: '#86868b', bg: 'rgba(134,134,139,0.1)' };

          return (
            <div
              key={`${decision.timestamp}-${idx}`}
              className="flex items-center justify-between p-3 rounded-xl transition-all duration-200"
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.06)',
                opacity: 0,
                animation: `slide-in 0.3s ease-out ${idx * 0.05}s forwards`
              }}
            >
              <div className="flex items-center gap-3">
                {/* Algorithm badge */}
                <span className="px-2.5 py-1 rounded-md text-xs font-medium"
                      style={{ background: meta.bg, color: meta.color }}>
                  {decision.algorithm.replace('_', ' ')}
                </span>

                {/* Arrow */}
                <ArrowRight className="w-4 h-4" style={{ color: '#48484a' }} />

                {/* Server */}
                <span className="font-mono text-sm">{decision.server_id}</span>
              </div>

              {/* Timestamp */}
              <div className="flex items-center gap-1.5 text-xs" style={{ color: '#48484a' }}>
                <Clock className="w-3 h-3" />
                {new Date(decision.timestamp).toLocaleTimeString()}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}