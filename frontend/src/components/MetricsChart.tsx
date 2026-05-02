import { Activity } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { MetricPoint } from '../types';

interface MetricsChartProps {
  data: MetricPoint[];
}

export function MetricsChart({ data }: MetricsChartProps) {
  const chartData = data.length > 0 ? data : [
    { timestamp: new Date(Date.now() - 40000).toISOString(), latency: 45, connections: 12, errorRate: 0.001 },
    { timestamp: new Date(Date.now() - 30000).toISOString(), latency: 52, connections: 18, errorRate: 0.002 },
    { timestamp: new Date(Date.now() - 20000).toISOString(), latency: 48, connections: 15, errorRate: 0.001 },
    { timestamp: new Date(Date.now() - 10000).toISOString(), latency: 55, connections: 22, errorRate: 0.003 },
    { timestamp: new Date().toISOString(), latency: 50, connections: 19, errorRate: 0.001 },
  ];

  const latestMetric = chartData[chartData.length - 1];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="rounded-xl p-3 border" style={{ background: '#0a0a0f', borderColor: 'rgba(255,255,255,0.1)' }}>
        <p className="text-xs mb-2 font-mono" style={{ color: '#86868b' }}>
          {new Date(label).toLocaleTimeString()}
        </p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span style={{ color: '#86868b' }}>{entry.name}:</span>
            <span className="font-mono font-medium">{entry.value.toFixed(2)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'rgba(245,158,11,0.1)' }}>
            <Activity className="w-4 h-4" style={{ color: '#f59e0b' }} />
          </div>
          <h2 className="text-base font-semibold">Real-Time Metrics</h2>
        </div>

        {latestMetric && (
          <div className="flex items-center gap-3">
            <div className="stat-pill">
              <span className="font-mono font-medium">{latestMetric.latency.toFixed(0)}</span>
              <span className="text-xs ml-1" style={{ color: '#48484a' }}>ms</span>
            </div>
            <div className="stat-pill">
              <span className="font-mono font-medium" style={{ color: '#22c55e' }}>{latestMetric.connections}</span>
              <span className="text-xs ml-1" style={{ color: '#48484a' }}>conn</span>
            </div>
            <div className="stat-pill">
              <span className="font-mono font-medium" style={{ color: '#f59e0b' }}>{(latestMetric.errorRate * 100).toFixed(2)}%</span>
              <span className="text-xs ml-1" style={{ color: '#48484a' }}>err</span>
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="connectionsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
            <XAxis
              dataKey="timestamp"
              stroke="#48484a"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis stroke="#48484a" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="latency"
              stroke="#f59e0b"
              strokeWidth={2}
              fill="url(#latencyGradient)"
              name="Latency"
              dot={false}
              activeDot={{ r: 4, fill: '#f59e0b' }}
            />
            <Area
              type="monotone"
              dataKey="connections"
              stroke="#22c55e"
              strokeWidth={2}
              fill="url(#connectionsGradient)"
              name="Connections"
              dot={false}
              activeDot={{ r: 4, fill: '#22c55e' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}