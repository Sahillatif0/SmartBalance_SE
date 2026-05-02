export interface Server {
  id: string;
  host: string;
  port: number;
  weight: number;
  connections: number;
  healthy: boolean;
  failure_count: number;
  created_at: string;
  updated_at: string;
}

export interface Algorithm {
  name: string;
  description: string;
  complexity: string;
}

export interface MetricPoint {
  timestamp: string;
  latency: number;
  connections: number;
  errorRate: number;
}

export interface RoutingDecision {
  algorithm: string;
  server_id: string;
  timestamp: string;
}

export interface Prediction {
  predictions: number[];
  timestamps: string[];
  confidence?: number;
}

export interface SimulationConfig {
  profile: 'steady' | 'burst' | 'ramp' | 'wave';
  rate: number;
  duration?: number;
}

export interface DashboardMessage {
  type: 'server_update' | 'metric_update' | 'routing_decision' | 'prediction' | 'heartbeat';
  timestamp: string;
  servers?: Server[];
  metrics?: MetricPoint[];
  decisions?: RoutingDecision[];
  predictions?: number[];
  active_algorithm?: string;
  simulation?: {
    running: boolean;
    profile: string;
    rate: number;
    total_requests: number;
    elapsed: number;
  };
}
