import { Brain, TrendingUp, AlertTriangle, Sparkles } from 'lucide-react';

interface ForecastOverlayProps {
  predictions?: number[];
}

export function ForecastOverlay({ predictions }: ForecastOverlayProps) {
  const defaultPredictions = [100, 120, 150, 180, 200];
  const data = predictions && predictions.length > 0 ? predictions : defaultPredictions;

  const maxPrediction = Math.max(...data);
  const avgPrediction = data.reduce((a, b) => a + b, 0) / data.length;
  const isSpike = maxPrediction > avgPrediction * 1.5;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'rgba(168,85,247,0.1)' }}>
            <Brain className="w-4 h-4" style={{ color: '#a855f7' }} />
          </div>
          <div>
            <h2 className="text-base font-semibold">AI Forecast</h2>
            <p className="text-xs mt-0.5" style={{ color: '#48484a' }}>15-minute prediction</p>
          </div>
        </div>
        {isSpike && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full animate-pulse-glow"
               style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)' }}>
            <AlertTriangle className="w-3.5 h-3.5" style={{ color: '#f59e0b' }} />
            <span className="text-xs font-medium" style={{ color: '#f59e0b' }}>Spike Alert</span>
          </div>
        )}
      </div>

      {/* Prediction Bars */}
      <div className="flex items-end gap-3 h-24 mb-6">
        {data.map((pred, idx) => {
          const height = (pred / maxPrediction) * 100;
          const isHigh = pred > avgPrediction * 1.3;
          const color = isHigh ? '#f59e0b' : '#a855f7';

          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-2">
              <span className="text-xs font-mono font-medium" style={{ color }}>
                {Math.round(pred)}
              </span>
              <div className="w-full h-16 rounded-lg overflow-hidden relative"
                   style={{ background: 'rgba(255,255,255,0.04)' }}>
                <div
                  className="absolute bottom-0 left-0 right-0 rounded-lg transition-all duration-500"
                  style={{
                    height: `${height}%`,
                    background: `linear-gradient(to top, ${color}, ${color}80)`,
                    boxShadow: isHigh ? `0 0 20px ${color}40` : 'none'
                  }}
                />
              </div>
              <span className="text-xs" style={{ color: '#48484a' }}>+{idx + 1}m</span>
            </div>
          );
        })}
      </div>

      {/* Stats Row */}
      <div className="flex justify-between items-center mb-4 p-3 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)' }}>
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4" style={{ color: '#48484a' }} />
          <span className="text-sm" style={{ color: '#86868b' }}>Peak</span>
          <span className="font-mono font-medium" style={{ color: isSpike ? '#f59e0b' : '#a855f7' }}>
            {Math.round(maxPrediction)} req/s
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm" style={{ color: '#86868b' }}>Avg</span>
          <span className="font-mono text-sm">{Math.round(avgPrediction)} req/s</span>
        </div>
      </div>

      {/* Alert Message */}
      {isSpike && (
        <div className="p-3 rounded-xl flex items-start gap-3"
             style={{ background: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.2)' }}>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
               style={{ background: 'rgba(245,158,11,0.1)' }}>
            <Sparkles className="w-4 h-4" style={{ color: '#f59e0b' }} />
          </div>
          <p className="text-sm" style={{ color: '#f59e0b' }}>
            Smart router will switch to Least Connections mode to handle the load spike.
          </p>
        </div>
      )}
    </div>
  );
}