/**
 * Events API Client
 * 
 * Provides methods for interacting with the Event Management REST API
 */

import { API_BASE_URL } from '../config';

// Types
export interface CandleData {
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface ResistanceEvent {
  id: string;
  event_type: 'resistance_bounce' | 'support_bounce' | 'breakout' | 'breakdown' | 'spike';
  instrument: string;
  timeframe: string;
  event_timestamp: string;
  resistance_level: number;
  rebound_amplitude: number;
  rebound_percentage: number;
  green_candle: CandleData;
  red_candle: CandleData;
  atr_value?: number;
  rebound_in_atr?: number;
  day_of_week: number;
  hour_of_day: number;
  detected_at: string;
  processing_latency_ms?: number;
  created_at: string;
  updated_at?: string;
}

export interface EventFilter {
  event_type?: string[];
  instrument?: string[];
  timeframe?: string[];
  start_date?: string;
  end_date?: string;
  min_resistance_level?: number;
  max_resistance_level?: number;
  min_rebound_percentage?: number;
  max_rebound_percentage?: number;
  day_of_week?: number[];
  hour_of_day?: number[];
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: 'event_timestamp' | 'detected_at' | 'resistance_level' | 'rebound_amplitude' | 'rebound_percentage';
  sort_order?: 'asc' | 'desc';
}

export interface EventListResponse {
  items: ResistanceEvent[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface EventStatistics {
  total_events: number;
  events_by_type: Record<string, number>;
  events_by_instrument: Record<string, number>;
  events_by_timeframe: Record<string, number>;
  avg_rebound_percentage: number;
  avg_rebound_amplitude: number;
  most_active_hour?: number;
  most_active_day?: number;
  date_range: {
    start?: string;
    end?: string;
  };
  top_resistance_levels: Array<{
    level: number;
    count: number;
    instruments: string[];
  }>;
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
  count: number;
}

export interface EventTimeSeries {
  interval: 'hour' | 'day' | 'week';
  data: TimeSeriesPoint[];
  total_events: number;
}

export interface HeatmapData {
  type: 'hour_day' | 'instrument_timeframe';
  metric: 'count' | 'avg_rebound';
  data: number[][];
  x_labels: string[];
  y_labels: string[];
}

export interface ExportRequest {
  format: 'csv' | 'json';
  filters?: EventFilter;
  include_metadata?: boolean;
  compress?: boolean;
}

/**
 * Events API client class
 */
export class EventsAPI {
  private baseUrl: string;
  private headers: HeadersInit;

  constructor(apiKey?: string) {
    this.baseUrl = `${API_BASE_URL}/api/v1`;
    this.headers = {
      'Content-Type': 'application/json',
      ...(apiKey && { 'X-API-Key': apiKey }),
    };
  }

  /**
   * Build query string from filters and pagination
   */
  private buildQueryString(params: Record<string, any>): string {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => queryParams.append(key, String(v)));
        } else {
          queryParams.append(key, String(value));
        }
      }
    });
    
    return queryParams.toString();
  }

  /**
   * Create a new event
   */
  async createEvent(eventData: Omit<ResistanceEvent, 'id' | 'detected_at' | 'created_at' | 'updated_at'>): Promise<ResistanceEvent> {
    const response = await fetch(`${this.baseUrl}/events/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(eventData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create event: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get event by ID
   */
  async getEvent(eventId: string): Promise<ResistanceEvent> {
    const response = await fetch(`${this.baseUrl}/events/${eventId}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to get event: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Update an event
   */
  async updateEvent(eventId: string, updateData: { metadata?: any; notes?: string; tags?: string[] }): Promise<ResistanceEvent> {
    const response = await fetch(`${this.baseUrl}/events/${eventId}`, {
      method: 'PUT',
      headers: this.headers,
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      throw new Error(`Failed to update event: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete an event
   */
  async deleteEvent(eventId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/events/${eventId}`, {
      method: 'DELETE',
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to delete event: ${response.statusText}`);
    }
  }

  /**
   * List events with filtering and pagination
   */
  async listEvents(filters?: EventFilter, pagination?: PaginationParams): Promise<EventListResponse> {
    const queryParams = this.buildQueryString({ ...filters, ...pagination });
    const url = `${this.baseUrl}/events/${queryParams ? `?${queryParams}` : ''}`;

    const response = await fetch(url, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to list events: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get recent events
   */
  async getRecentEvents(hours: number = 24, instrument?: string): Promise<ResistanceEvent[]> {
    const queryParams = this.buildQueryString({ hours, instrument });
    const response = await fetch(`${this.baseUrl}/events/recent?${queryParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to get recent events: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Search events by resistance level
   */
  async searchByResistanceLevel(level: number, tolerance: number = 0.0010, instrument?: string): Promise<ResistanceEvent[]> {
    const queryParams = this.buildQueryString({ level, tolerance, instrument });
    const response = await fetch(`${this.baseUrl}/events/search/by-resistance-level?${queryParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to search events: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Export events
   */
  async exportEvents(exportRequest: ExportRequest): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/events/export`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(exportRequest),
    });

    if (!response.ok) {
      throw new Error(`Failed to export events: ${response.statusText}`);
    }

    return response.blob();
  }

  /**
   * Get statistics overview
   */
  async getStatistics(filters?: EventFilter): Promise<EventStatistics> {
    const queryParams = this.buildQueryString(filters || {});
    const url = `${this.baseUrl}/statistics/overview${queryParams ? `?${queryParams}` : ''}`;

    const response = await fetch(url, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to get statistics: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get time series data
   */
  async getTimeSeries(interval: 'hour' | 'day' | 'week' = 'day', filters?: EventFilter): Promise<EventTimeSeries> {
    const queryParams = this.buildQueryString({ interval, ...filters });
    const response = await fetch(`${this.baseUrl}/statistics/time-series?${queryParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to get time series: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get heatmap data
   */
  async getHeatmapData(
    groupBy: 'hour_day' | 'instrument_timeframe' = 'hour_day',
    metric: 'count' | 'avg_rebound' = 'count',
    filters?: EventFilter
  ): Promise<HeatmapData> {
    const queryParams = this.buildQueryString({ group_by: groupBy, metric, ...filters });
    const response = await fetch(`${this.baseUrl}/statistics/heatmap-data?${queryParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to get heatmap data: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Compare instruments
   */
  async compareInstruments(instruments: string[], startDate?: string, endDate?: string): Promise<any> {
    const queryParams = this.buildQueryString({ 
      instruments, 
      start_date: startDate, 
      end_date: endDate 
    });
    
    const response = await fetch(`${this.baseUrl}/statistics/compare-instruments?${queryParams}`, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to compare instruments: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get instrument statistics
   */
  async getInstrumentStatistics(instrument: string, startDate?: string, endDate?: string): Promise<any> {
    const queryParams = this.buildQueryString({ start_date: startDate, end_date: endDate });
    const url = `${this.baseUrl}/statistics/by-instrument/${instrument}${queryParams ? `?${queryParams}` : ''}`;

    const response = await fetch(url, {
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to get instrument statistics: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Perform custom aggregation
   */
  async aggregateEvents(groupBy: string[], metrics: string[], filters?: EventFilter): Promise<any> {
    const response = await fetch(`${this.baseUrl}/statistics/aggregate`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        group_by: groupBy,
        metrics,
        filters,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to aggregate events: ${response.statusText}`);
    }

    return response.json();
  }
}

// Create default instance
const eventsAPI = new EventsAPI();

// Export default instance and class
export default eventsAPI;
export { eventsAPI };