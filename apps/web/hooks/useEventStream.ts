/**
 * useEventStream Hook
 * 
 * React hook for real-time event streaming via WebSocket
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { WebSocketClient, ConnectionState } from '@/lib/websocket';
import { ResistanceEvent } from '@/lib/api/events';
import { WS_BASE_URL, featureFlags } from '@/lib/config';

interface UseEventStreamOptions {
  enabled?: boolean;
  instruments?: string[];
  timeframes?: string[];
  autoReconnect?: boolean;
  maxEvents?: number;
  onEvent?: (event: ResistanceEvent) => void;
  onConnectionChange?: (state: ConnectionState) => void;
}

interface UseEventStreamReturn {
  events: ResistanceEvent[];
  connectionState: ConnectionState;
  isConnected: boolean;
  metrics: {
    eventsReceived: number;
    lastEventTime: Date | null;
    connectionTime: Date | null;
  };
  connect: () => Promise<void>;
  disconnect: () => void;
  subscribe: (instrument: string, timeframe: string) => void;
  unsubscribe: (instrument: string, timeframe: string) => void;
  subscribeAll: () => void;
  clearEvents: () => void;
}

export function useEventStream(options: UseEventStreamOptions = {}): UseEventStreamReturn {
  const {
    enabled = featureFlags.realTimeUI,
    instruments = [],
    timeframes = [],
    autoReconnect = true,
    maxEvents = 100,
    onEvent,
    onConnectionChange,
  } = options;

  const [events, setEvents] = useState<ResistanceEvent[]>([]);
  const [connectionState, setConnectionState] = useState<ConnectionState>(ConnectionState.DISCONNECTED);
  const [metrics, setMetrics] = useState({
    eventsReceived: 0,
    lastEventTime: null as Date | null,
    connectionTime: null as Date | null,
  });

  const clientRef = useRef<WebSocketClient | null>(null);
  const eventsRef = useRef<ResistanceEvent[]>([]);

  // Initialize WebSocket client
  useEffect(() => {
    if (!enabled) return;

    const client = new WebSocketClient({
      url: WS_BASE_URL,
      autoReconnect,
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
    });

    // Set up event handlers
    client.on('state-change', (state: ConnectionState) => {
      setConnectionState(state);
      if (onConnectionChange) {
        onConnectionChange(state);
      }
    });

    client.on('connected', () => {
      setMetrics(prev => ({
        ...prev,
        connectionTime: new Date(),
      }));

      // Resubscribe to configured instruments and timeframes
      instruments.forEach(instrument => {
        timeframes.forEach(timeframe => {
          client.subscribe(instrument, timeframe);
        });
      });
    });

    client.on('resistance-event', ({ event }: { event: ResistanceEvent }) => {
      // Add event to the list
      eventsRef.current = [event, ...eventsRef.current].slice(0, maxEvents);
      setEvents([...eventsRef.current]);

      // Update metrics
      setMetrics(prev => ({
        eventsReceived: prev.eventsReceived + 1,
        lastEventTime: new Date(),
        connectionTime: prev.connectionTime,
      }));

      // Call event callback
      if (onEvent) {
        onEvent(event);
      }
    });

    client.on('error', (error: Error) => {
      console.error('WebSocket error:', error);
    });

    clientRef.current = client;

    // Auto-connect if configured
    if (instruments.length > 0 || timeframes.length > 0) {
      client.connect().catch(error => {
        console.error('Failed to connect to WebSocket:', error);
      });
    }

    // Cleanup on unmount
    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect();
        clientRef.current = null;
      }
    };
  }, [enabled, autoReconnect, maxEvents]);

  // Update subscriptions when instruments or timeframes change
  useEffect(() => {
    if (!clientRef.current || !clientRef.current.isConnected()) return;

    // Clear existing subscriptions and resubscribe
    instruments.forEach(instrument => {
      timeframes.forEach(timeframe => {
        clientRef.current?.subscribe(instrument, timeframe);
      });
    });
  }, [instruments, timeframes]);

  const connect = useCallback(async () => {
    if (clientRef.current) {
      await clientRef.current.connect();
    }
  }, []);

  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
    }
  }, []);

  const subscribe = useCallback((instrument: string, timeframe: string) => {
    if (clientRef.current) {
      clientRef.current.subscribe(instrument, timeframe);
    }
  }, []);

  const unsubscribe = useCallback((instrument: string, timeframe: string) => {
    if (clientRef.current) {
      clientRef.current.unsubscribe(instrument, timeframe);
    }
  }, []);

  const subscribeAll = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.subscribeAll();
    }
  }, []);

  const clearEvents = useCallback(() => {
    eventsRef.current = [];
    setEvents([]);
    setMetrics(prev => ({
      ...prev,
      eventsReceived: 0,
      lastEventTime: null,
    }));
  }, []);

  return {
    events,
    connectionState,
    isConnected: connectionState === ConnectionState.CONNECTED,
    metrics,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    subscribeAll,
    clearEvents,
  };
}

// Export for convenience
export { ConnectionState } from '@/lib/websocket';
export type { ResistanceEvent } from '@/lib/api/events';