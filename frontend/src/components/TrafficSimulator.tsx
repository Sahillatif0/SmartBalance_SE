import { useState, useEffect } from 'react';
import { startSimulation, stopSimulation, getSimulationStatus } from '../services/api';
import { Play, Square, Activity, Zap, TrendingUp, Waves } from 'lucide-react';

export function TrafficSimulator() {
  const [running, setRunning] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [profile, setProfile] = useState<'steady' | 'burst' | 'ramp' | 'wave'>('steady');
  const [rate, setRate] = useState(100);

  // Poll for status - poll more frequently when not running to catch restart
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    const pollStatus = () => {
      getSimulationStatus()
        .then((status) => {
          setRunning(status.running);
          setStopping(false);
        })
        .catch(console.error);
    };

    // Initial poll
    pollStatus();

    // Poll every second when not running, every 2 seconds when running
    interval = setInterval(() => {
      pollStatus();
    }, running ? 2000 : 1000);

    return () => clearInterval(interval);
  }, [running]);

  const handleStart = async () => {
    // Don't start if already running or stopping
    if (running || stopping) {
      console.log('Cannot start: running=', running, 'stopping=', stopping);
      return;
    }
    try {
      console.log('Starting simulation:', { profile, rate });
      await startSimulation({ profile, rate });
      setRunning(true);
      setStopping(false);
    } catch (e) {
      console.error('Failed to start simulation:', e);
      // Refresh status on error
      getSimulationStatus().then((status) => setRunning(status.running));
    }
  };

  const handleStop = async () => {
    // Don't stop if not running or already stopping
    if (!running || stopping) {
      console.log('Cannot stop: running=', running, 'stopping=', stopping);
      return;
    }
    try {
      console.log('Stopping simulation');
      setStopping(true);
      await stopSimulation();
      setRunning(false);
      setStopping(false);
    } catch (e) {
      console.error('Failed to stop simulation:', e);
      setStopping(false);
      // Refresh status on error
      getSimulationStatus().then((status) => setRunning(status.running));
    }
  };

  type ProfileId = 'steady' | 'burst' | 'ramp' | 'wave';

  const profiles: { id: ProfileId; name: string; icon: typeof Activity; desc: string; color: string }[] = [
    { id: 'steady', name: 'Steady', icon: Activity, desc: 'Constant flow', color: '#22c55e' },
    { id: 'burst', name: 'Burst', icon: Zap, desc: 'Periodic spikes', color: '#f59e0b' },
    { id: 'ramp', name: 'Ramp', icon: TrendingUp, desc: 'Linear climb', color: '#6366f1' },
    { id: 'wave', name: 'Wave', icon: Waves, desc: 'Sine pattern', color: '#ec4899' },
  ];

  const selectedProfile = profiles.find(p => p.id === profile)!;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
             style={{ background: 'rgba(245,158,11,0.1)' }}>
          <Zap className="w-4 h-4" style={{ color: '#f59e0b' }} />
        </div>
        <h2 className="text-base font-semibold">Traffic Simulator</h2>
      </div>

      {/* Profile Grid */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {profiles.map((p) => {
          const Icon = p.icon;
          const isSelected = profile === p.id;

          return (
            <button
              key={p.id}
              onClick={() => setProfile(p.id)}
              className="relative rounded-xl p-4 text-left transition-all duration-300 overflow-hidden group"
              style={{
                background: isSelected ? p.color + '10' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isSelected ? p.color + '40' : 'rgba(255,255,255,0.06)'}`,
              }}
            >
              {/* Hover glow */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                   style={{ background: `radial-gradient(circle at 50% 100%, ${p.color}10, transparent 70%)` }} />

              <div className="flex items-center gap-3 relative">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                     style={{ background: isSelected ? p.color + '20' : 'rgba(255,255,255,0.05)' }}>
                  <Icon className="w-5 h-5" style={{ color: isSelected ? p.color : '#86868b' }} />
                </div>
                <div>
                  <div className="text-sm font-medium">{p.name}</div>
                  <div className="text-xs" style={{ color: '#48484a' }}>{p.desc}</div>
                </div>
              </div>

              {/* Selected indicator */}
              {isSelected && (
                <div className="absolute top-2 right-2 w-2 h-2 rounded-full" style={{ background: p.color, boxShadow: `0 0 8px ${p.color}` }} />
              )}
            </button>
          );
        })}
      </div>

      {/* Rate Slider */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm" style={{ color: '#86868b' }}>Request Rate</span>
          <span className="font-mono font-medium" style={{ color: selectedProfile.color }}>
            {rate} <span style={{ color: '#48484a' }}>req/s</span>
          </span>
        </div>
        <div className="relative">
          <input
            type="range"
            min="10"
            max="500"
            step="10"
            value={rate}
            onChange={(e) => setRate(Number(e.target.value))}
            className="w-full h-2 rounded-full appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, ${selectedProfile.color} 0%, ${selectedProfile.color} ${(rate - 10) / 490 * 100}%, rgba(255,255,255,0.06) ${(rate - 10) / 490 * 100}%, rgba(255,255,255,0.06) 100%)`
            }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs" style={{ color: '#48484a' }}>
          <span>10</span>
          <span>250</span>
          <span>500</span>
        </div>
      </div>

      {/* Control Button */}
      <button
        onClick={running ? handleStop : handleStart}
        disabled={stopping}
        className="w-full py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-all duration-300 relative overflow-hidden group disabled:opacity-50"
        style={{
          background: running ? '#ef4444' : '#22c55e',
          color: '#fff'
        }}
      >
        {/* Shine effect */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
             style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)' }} />

        {stopping ? (
          <>
            <Square className="w-4 h-4 relative animate-pulse" />
            <span className="relative">Stopping...</span>
          </>
        ) : running ? (
          <>
            <Square className="w-4 h-4 relative" />
            <span className="relative">Stop Simulation</span>
          </>
        ) : (
          <>
            <Play className="w-4 h-4 relative" />
            <span className="relative">Start Simulation</span>
          </>
        )}
      </button>
    </div>
  );
}