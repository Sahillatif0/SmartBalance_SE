import { useState, useEffect, useCallback, useRef } from 'react';
import type { DashboardMessage } from '../types';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: DashboardMessage) => void;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  connected: boolean;
  lastMessage: DashboardMessage | null;
  sendMessage: (message: unknown) => void;
  reconnect: () => void;
}

export function useWebSocket({
  url,
  onMessage,
  reconnectInterval = 5000,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<DashboardMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const shouldReconnect = useRef(true);

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    shouldReconnect.current = false;
    clearReconnectTimeout();
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, [clearReconnectTimeout]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return;

    shouldReconnect.current = true;
    clearReconnectTimeout();

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;
        if (shouldReconnect.current) {
          reconnectTimeoutRef.current = window.setTimeout(connect, reconnectInterval);
        }
      };

      ws.onerror = () => {
        setConnected(false);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as DashboardMessage;
          setLastMessage(message);
          onMessage?.(message);
        } catch (e) {
          // Ignore non-JSON messages (like "pong")
        }
      };
    } catch (e) {
      console.error('WebSocket connection error:', e);
      setConnected(false);
      if (shouldReconnect.current) {
        reconnectTimeoutRef.current = window.setTimeout(connect, reconnectInterval);
      }
    }
  }, [url, onMessage, reconnectInterval, clearReconnectTimeout]);

  const sendMessage = useCallback((message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 100);
  }, [connect, disconnect]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    connected,
    lastMessage,
    sendMessage,
    reconnect,
  };
}
