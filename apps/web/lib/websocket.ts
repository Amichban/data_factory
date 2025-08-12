/**
 * WebSocket Client for Real-time Event Streaming
 * 
 * Provides connection management, auto-reconnection, and event handling
 * for real-time resistance event notifications.
 */

import { EventEmitter } from 'events';

export interface ResistanceEvent {
  event_type: string;
  instrument: string;
  timeframe: string;
  event_timestamp: string;
  resistance_level: number;
  rebound_amplitude: number;
  rebound_percentage: number;
  green_candle: {
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
  };
  red_candle: {
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
  };
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  instrument?: string;
  timeframe?: string;
  timestamp?: string;
  message?: string;
  level?: string;
}

export interface ConnectionOptions {
  url: string;
  clientId?: string;
  token?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export enum ConnectionState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error',
}

export class WebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private options: Required<ConnectionOptions>;
  private state: ConnectionState = ConnectionState.DISCONNECTED;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private subscriptions = new Set<string>();
  private messageQueue: WebSocketMessage[] = [];
  private metrics = {
    messagesReceived: 0,
    eventsReceived: 0,
    connectionTime: null as Date | null,
    lastEventTime: null as Date | null,
  };

  constructor(options: ConnectionOptions) {
    super();
    
    this.options = {
      url: options.url,
      clientId: options.clientId || this.generateClientId(),
      token: options.token || '',
      autoReconnect: options.autoReconnect ?? true,
      reconnectInterval: options.reconnectInterval ?? 5000,
      maxReconnectAttempts: options.maxReconnectAttempts ?? 10,
      heartbeatInterval: options.heartbeatInterval ?? 30000,
    };
  }

  /**
   * Connect to WebSocket server
   */
  public async connect(): Promise<void> {
    if (this.state === ConnectionState.CONNECTED) {
      console.warn('WebSocket already connected');
      return;
    }

    this.setState(ConnectionState.CONNECTING);

    return new Promise((resolve, reject) => {
      try {
        const url = new URL(this.options.url);
        url.searchParams.append('client_id', this.options.clientId);
        if (this.options.token) {
          url.searchParams.append('token', this.options.token);
        }

        this.ws = new WebSocket(url.toString());

        this.ws.onopen = () => {
          this.handleOpen();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };

        this.ws.onerror = (error) => {
          this.handleError(error);
          reject(error);
        };

        this.ws.onclose = (event) => {
          this.handleClose(event);
        };

      } catch (error) {
        this.setState(ConnectionState.ERROR);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    this.options.autoReconnect = false;
    this.clearTimers();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.setState(ConnectionState.DISCONNECTED);
  }

  /**
   * Subscribe to events for specific instrument/timeframe
   */
  public subscribe(instrument: string, timeframe: string): void {
    const key = `${instrument}_${timeframe}`;
    
    if (this.subscriptions.has(key)) {
      return;
    }

    this.subscriptions.add(key);

    if (this.isConnected()) {
      this.send({
        type: 'subscribe',
        instrument,
        timeframe,
      });
    }
  }

  /**
   * Subscribe to all events
   */
  public subscribeAll(): void {
    this.subscribe('*', '*');
  }

  /**
   * Unsubscribe from events
   */
  public unsubscribe(instrument: string, timeframe: string): void {
    const key = `${instrument}_${timeframe}`;
    this.subscriptions.delete(key);

    if (this.isConnected()) {
      this.send({
        type: 'unsubscribe',
        instrument,
        timeframe,
      });
    }
  }

  /**
   * Request status information
   */
  public requestStatus(): void {
    this.send({ type: 'status' });
  }

  /**
   * Get connection state
   */
  public getState(): ConnectionState {
    return this.state;
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.state === ConnectionState.CONNECTED && this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection metrics
   */
  public getMetrics() {
    return {
      ...this.metrics,
      state: this.state,
      subscriptions: Array.from(this.subscriptions),
      queueSize: this.messageQueue.length,
      reconnectAttempts: this.reconnectAttempts,
    };
  }

  private handleOpen(): void {
    console.log('WebSocket connected');
    
    this.setState(ConnectionState.CONNECTED);
    this.reconnectAttempts = 0;
    this.metrics.connectionTime = new Date();

    // Resubscribe to previous subscriptions
    this.subscriptions.forEach((key) => {
      const [instrument, timeframe] = key.split('_');
      this.send({
        type: 'subscribe',
        instrument,
        timeframe,
      });
    });

    // Process queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }

    // Start heartbeat
    this.startHeartbeat();

    this.emit('connected');
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      this.metrics.messagesReceived++;

      switch (message.type) {
        case 'event':
          this.handleEvent(message);
          break;

        case 'connection':
          this.emit('connection', message);
          break;

        case 'subscription':
          this.emit('subscription', message);
          break;

        case 'pong':
          // Heartbeat response
          break;

        case 'status':
          this.emit('status', message);
          break;

        case 'system':
          this.emit('system', message);
          break;

        case 'error':
          this.emit('error', new Error(message.message || 'Unknown error'));
          break;

        default:
          console.warn('Unknown message type:', message.type);
      }

    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      this.emit('error', error);
    }
  }

  private handleEvent(message: WebSocketMessage): void {
    if (message.data) {
      const event: ResistanceEvent = message.data;
      this.metrics.eventsReceived++;
      this.metrics.lastEventTime = new Date();

      // Emit specific event
      this.emit('resistance-event', {
        event,
        instrument: message.instrument,
        timeframe: message.timeframe,
        timestamp: message.timestamp,
      });

      // Emit general event
      this.emit('event', message);
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
    this.emit('error', error);
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    
    this.ws = null;
    this.clearTimers();
    this.setState(ConnectionState.DISCONNECTED);

    // Auto-reconnect if enabled
    if (this.options.autoReconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this.scheduleReconnect();
    } else {
      this.emit('disconnected', { code: event.code, reason: event.reason });
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    this.reconnectAttempts++;
    const delay = this.options.reconnectInterval * Math.min(this.reconnectAttempts, 5);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.setState(ConnectionState.RECONNECTING);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect().catch((error) => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }

  private startHeartbeat(): void {
    this.clearHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' });
      }
    }, this.options.heartbeatInterval);
  }

  private clearHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private clearTimers(): void {
    this.clearHeartbeat();

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private send(message: any): void {
    if (this.isConnected() && this.ws) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send message:', error);
        this.messageQueue.push(message);
      }
    } else {
      // Queue message for later
      this.messageQueue.push(message);
    }
  }

  private setState(state: ConnectionState): void {
    if (this.state !== state) {
      this.state = state;
      this.emit('state-change', state);
    }
  }

  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// React Hook for WebSocket connection
export function useWebSocket(options: ConnectionOptions) {
  const [client, setClient] = React.useState<WebSocketClient | null>(null);
  const [state, setState] = React.useState<ConnectionState>(ConnectionState.DISCONNECTED);
  const [events, setEvents] = React.useState<ResistanceEvent[]>([]);

  React.useEffect(() => {
    const wsClient = new WebSocketClient(options);

    wsClient.on('state-change', (newState: ConnectionState) => {
      setState(newState);
    });

    wsClient.on('resistance-event', ({ event }: { event: ResistanceEvent }) => {
      setEvents((prev) => [...prev, event].slice(-100)); // Keep last 100 events
    });

    setClient(wsClient);
    wsClient.connect();

    return () => {
      wsClient.disconnect();
    };
  }, []);

  return {
    client,
    state,
    events,
    isConnected: state === ConnectionState.CONNECTED,
  };
}