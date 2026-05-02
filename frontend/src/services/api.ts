import type { Server, Algorithm, SimulationConfig } from '../types';

const API_BASE = '/api/v1';

export async function fetchServers(): Promise<Server[]> {
  const response = await fetch(`${API_BASE}/servers`);
  if (!response.ok) throw new Error('Failed to fetch servers');
  return response.json();
}

export async function createServer(server: Omit<Server, 'created_at' | 'updated_at' | 'connections' | 'healthy' | 'failure_count'>): Promise<Server> {
  const response = await fetch(`${API_BASE}/servers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(server),
  });
  if (!response.ok) throw new Error('Failed to create server');
  return response.json();
}

export async function deleteServer(serverId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/servers/${serverId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete server');
}

export async function fetchAlgorithms(): Promise<Algorithm[]> {
  const response = await fetch(`${API_BASE}/algorithms`);
  if (!response.ok) throw new Error('Failed to fetch algorithms');
  const data = await response.json();
  return data.algorithms;
}

export async function selectAlgorithm(name: string): Promise<void> {
  const response = await fetch(`${API_BASE}/algorithms/${name}/select`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to select algorithm');
}

export async function startSimulation(config?: SimulationConfig): Promise<void> {
  const response = await fetch(`${API_BASE}/simulation/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: config ? JSON.stringify(config) : '{}',
  });
  if (!response.ok) throw new Error('Failed to start simulation');
}

export async function stopSimulation(): Promise<void> {
  const response = await fetch(`${API_BASE}/simulation/stop`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to stop simulation');
}

export async function getSimulationStatus(): Promise<{ running: boolean; profile: string; rate: number }> {
  const response = await fetch(`${API_BASE}/simulation/status`);
  if (!response.ok) throw new Error('Failed to get simulation status');
  return response.json();
}
