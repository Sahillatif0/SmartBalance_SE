import { useState, useEffect } from 'react';
import { fetchAlgorithms, selectAlgorithm } from '../services/api';
import type { Algorithm } from '../types';
import { Cpu, Zap, Gauge } from 'lucide-react';

interface AlgorithmSelectorProps {
  activeAlgorithm: string;
  onSelect: (algorithm: string) => void;
}

export function AlgorithmSelector({ activeAlgorithm, onSelect }: AlgorithmSelectorProps) {
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAlgorithms()
      .then(setAlgorithms)
      .catch(console.error);
  }, []);

  const handleSelect = async (name: string) => {
    if (loading) return;
    setLoading(true);
    try {
      await selectAlgorithm(name);
      onSelect(name);
    } catch (e) {
      console.error('Failed to select algorithm:', e);
    } finally {
      setLoading(false);
    }
  };

  const algorithmMeta: Record<string, { icon: typeof Zap, color: string, bg: string }> = {
    round_robin: { icon: Gauge, color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
    least_connections: { icon: Zap, color: '#22c55e', bg: 'rgba(34,197,94,0.1)' },
    weighted_round_robin: { icon: Cpu, color: '#6366f1', bg: 'rgba(99,102,241,0.1)' },
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
             style={{ background: 'rgba(34,197,94,0.1)' }}>
          <Cpu className="w-4 h-4" style={{ color: '#22c55e' }} />
        </div>
        <h2 className="text-base font-semibold">Algorithm</h2>
      </div>

      {/* Algorithm List */}
      <div className="space-y-3">
        {algorithms.map((alg, idx) => {
          const isActive = activeAlgorithm === alg.name;
          const meta = algorithmMeta[alg.name] || { icon: Cpu, color: '#86868b', bg: 'rgba(134,134,139,0.1)' };
          const Icon = meta.icon;

          return (
            <button
              key={alg.name}
              onClick={() => handleSelect(alg.name)}
              disabled={loading}
              className="w-full text-left rounded-xl p-4 transition-all duration-300 group relative overflow-hidden"
              style={{
                background: isActive ? meta.bg : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isActive ? meta.color + '40' : 'rgba(255,255,255,0.06)'}`,
                opacity: 0,
                animation: `fadeInUp 0.4s ease-out ${idx * 0.05}s forwards`
              }}
            >
              {/* Active glow */}
              {isActive && (
                <div className="absolute inset-0 opacity-30"
                     style={{ background: `radial-gradient(circle at 0% 50%, ${meta.color}15, transparent 50%)` }} />
              )}

              <div className="flex items-center justify-between relative">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center transition-colors"
                       style={{
                         background: isActive ? meta.color + '20' : 'rgba(255,255,255,0.05)',
                       }}>
                    <Icon className="w-5 h-5" style={{ color: isActive ? meta.color : '#86868b' }} />
                  </div>
                  <div>
                    <div className="font-medium text-sm">
                      {alg.name.replace(/_/g, ' ')}
                    </div>
                    <div className="text-xs mt-0.5" style={{ color: '#48484a' }}>
                      {alg.complexity}
                    </div>
                  </div>
                </div>

                {/* Active indicator */}
                {isActive && (
                  <div className="w-6 h-6 rounded-full flex items-center justify-center"
                       style={{ background: meta.color }}>
                    <svg className="w-3 h-3 text-black" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                    </svg>
                  </div>
                )}
              </div>

              {/* Hover accent line */}
              <div className="absolute bottom-0 left-0 right-0 h-0.5 origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300"
                   style={{ background: `linear-gradient(90deg, ${meta.color}, transparent)` }} />
            </button>
          );
        })}
      </div>
    </div>
  );
}