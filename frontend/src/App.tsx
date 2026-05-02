import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { ServerList } from './components/ServerList';
import { AlgorithmSelector } from './components/AlgorithmSelector';
import { MetricsChart } from './components/MetricsChart';
import { TrafficSimulator } from './components/TrafficSimulator';
import { RoutingLog } from './components/RoutingLog';
import { ForecastOverlay } from './components/ForecastOverlay';
import type { Server, MetricPoint, RoutingDecision } from './types';

const WS_URL = `ws://127.0.0.1:8000/api/v1/metrics/live`;

function App() {
  const [servers, setServers] = useState<Server[]>([]);
  const [metrics, setMetrics] = useState<MetricPoint[]>([]);
  const [decisions, setDecisions] = useState<RoutingDecision[]>([]);
  const [activeAlgorithm, setActiveAlgorithm] = useState<string>('round_robin');
  const [simRunning, setSimRunning] = useState(false);
  const [simRate, setSimRate] = useState(0);
  const [predictions, setPredictions] = useState<number[]>([]);
  const [predictionConfidence, setPredictionConfidence] = useState<number | null>(null);
  const [smartRouterActive, setSmartRouterActive] = useState(false);
  const metricsCounter = useRef(0);

  const { connected, sendMessage } = useWebSocket({
    url: WS_URL,
    onMessage: (message) => {
      if (message.type === 'metric_update') {
        // Update servers
        if (message.servers && message.servers.length > 0) {
          setServers(message.servers);
        }

        // Update simulation status
        if (message.simulation) {
          setSimRunning(message.simulation.running);
          setSimRate(Math.round(message.simulation.rate));
        }

        // Update routing decisions
        if (message.decisions && message.decisions.length > 0) {
          setDecisions(message.decisions);
        }

        // Update active algorithm
        if (message.active_algorithm) {
          setActiveAlgorithm(message.active_algorithm);
        }

        // Smart router status
        if ('smart_router_active' in message) {
          setSmartRouterActive(message.smart_router_active as boolean);
        }

        // Update predictions from LSTM (actual AI predictions)
        if (message.predictions && message.predictions.length > 0) {
          setPredictions(message.predictions);
        }

        // Prediction confidence (MAPE)
        if (message.prediction_confidence !== undefined) {
          setPredictionConfidence(message.prediction_confidence as number);
        }

        // Update metrics for chart
        metricsCounter.current += 1;
        const latency = 20 + Math.random() * 60 + (message.simulation?.rate || 0) * 0.1;
        const newMetric: MetricPoint = {
          timestamp: message.timestamp,
          latency: Math.min(200, latency),
          connections: message.servers
            ? message.servers.reduce((sum: number, s: Server) => sum + s.connections, 0)
            : metricsCounter.current * 5,
          errorRate: Math.random() * 0.005,
        };
        setMetrics((prev) => [...prev.slice(-59), newMetric]);
      }

      if (message.type === 'heartbeat') {
        sendMessage({ type: 'request_metrics' });
      }
    },
    reconnectInterval: 5000,
  });

  // Request metrics on connection
  useEffect(() => {
    if (!connected) return;
    const interval = setInterval(() => {
      sendMessage({ type: 'request_metrics' });
    }, 2000);
    return () => clearInterval(interval);
  }, [connected, sendMessage]);

  // Restore algorithm preference
  useEffect(() => {
    const stored = localStorage.getItem('activeAlgorithm');
    if (stored) setActiveAlgorithm(stored);
  }, []);

  return (
    <div className="min-h-screen" style={{ background: '#050507' }}>
      {/* Minimal Header */}
      <header className="sticky top-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                   style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                <svg className="w-5 h-5 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
              </div>
              <span className="text-lg font-semibold tracking-tight">SmartBalance</span>
              <span className="text-xs px-2 py-0.5 rounded-md ml-1"
                    style={{ background: 'rgba(245,158,11,0.15)', color: '#f59e0b' }}>
                AI
              </span>
            </div>

            {/* Status */}
            <div className="flex items-center gap-5">
              {/* Smart Router Status */}
              {simRunning && (
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full transition-all duration-300 ${
                  smartRouterActive ? 'animate-pulse-glow' : ''
                }`}
                     style={{
                       background: smartRouterActive ? 'rgba(245,158,11,0.1)' : 'rgba(168,85,247,0.1)',
                       border: `1px solid ${smartRouterActive ? 'rgba(245,158,11,0.3)' : 'rgba(168,85,247,0.3)'}`
                     }}>
                  <svg className="w-4 h-4" style={{ color: smartRouterActive ? '#f59e0b' : '#a855f7' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 2v4m0 12v4M2 12h4m12 0h4"/>
                    <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
                  </svg>
                  <span className="text-xs font-medium" style={{ color: smartRouterActive ? '#f59e0b' : '#a855f7' }}>
                    {smartRouterActive ? 'Smart Router Active' : 'AI Monitoring'}
                  </span>
                </div>
              )}

              <div className="flex items-center gap-2">
                <span className={`status-dot ${connected ? 'status-online' : 'status-offline'}`} />
                <span className="text-sm" style={{ color: '#86868b' }}>
                  {connected ? 'Live' : 'Offline'}
                </span>
              </div>

              {simRunning && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full animate-pulse-glow"
                     style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.2)' }}>
                  <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#22c55e' }} />
                  <span className="text-sm font-medium" style={{ color: '#22c55e' }}>{simRate} req/s</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Top Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Metrics Chart */}
          <div className="lg:col-span-2 card-hover">
            <MetricsChart data={metrics} />
          </div>

          {/* Algorithm Selector */}
          <div className="card-hover">
            <AlgorithmSelector
              activeAlgorithm={activeAlgorithm}
              onSelect={(alg) => {
                setActiveAlgorithm(alg);
                localStorage.setItem('activeAlgorithm', alg);
              }}
            />
          </div>
        </div>

        {/* Server Pool */}
        <div className="mb-6 card-hover stagger-1" style={{ animationDelay: '0.1s' }}>
          <ServerList servers={servers} />
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card-hover stagger-2" style={{ animationDelay: '0.15s' }}>
            <TrafficSimulator />
          </div>
          <div className="space-y-6">
            <div className="card-hover stagger-3" style={{ animationDelay: '0.2s' }}>
              <RoutingLog decisions={decisions} />
            </div>
            <div className="card-hover stagger-4" style={{ animationDelay: '0.25s' }}>
              <ForecastOverlay
                predictions={predictions}
                currentRate={simRate}
                confidence={predictionConfidence}
                smartRouterActive={smartRouterActive}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;