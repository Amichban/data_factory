/**
 * Events Page
 * 
 * Main page for event visualization and analysis
 */

'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Activity, 
  BarChart3, 
  Download, 
  RefreshCw, 
  Wifi, 
  WifiOff,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { EventFilters } from '@/components/events/EventFilters';
import { EventTable } from '@/components/events/EventTable';
import { CandlestickChart } from '@/components/charts/CandlestickChart';
import { useEventStream, ConnectionState } from '@/hooks/useEventStream';
import { 
  EventsAPI, 
  EventFilter, 
  PaginationParams, 
  ResistanceEvent,
  EventStatistics,
  EventListResponse 
} from '@/lib/api/events';
import { featureFlags, eventsConfig, INSTRUMENTS, TIMEFRAMES } from '@/lib/config';
import { format } from 'date-fns';

export default function EventsPage() {
  // State management
  const [events, setEvents] = useState<ResistanceEvent[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(eventsConfig.defaultPageSize);
  const [sortBy, setSortBy] = useState<PaginationParams['sort_by']>('event_timestamp');
  const [sortOrder, setSortOrder] = useState<PaginationParams['sort_order']>('desc');
  const [filters, setFilters] = useState<EventFilter>({});
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<EventStatistics | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<ResistanceEvent | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'chart' | 'split'>('split');
  
  // API client
  const api = useMemo(() => new EventsAPI(), []);

  // Real-time event stream
  const {
    events: streamEvents,
    connectionState,
    isConnected,
    metrics: streamMetrics,
    connect: connectStream,
    disconnect: disconnectStream,
    subscribeAll,
    clearEvents: clearStreamEvents,
  } = useEventStream({
    enabled: featureFlags.realTimeUI,
    instruments: filters.instrument || [],
    timeframes: filters.timeframe || [],
    maxEvents: 50,
    onEvent: (event) => {
      // Prepend new event to the list if it matches filters
      if (matchesFilters(event, filters)) {
        setEvents(prev => [event, ...prev].slice(0, pageSize));
        setTotalCount(prev => prev + 1);
      }
    },
  });

  // Check if event matches current filters
  const matchesFilters = (event: ResistanceEvent, filters: EventFilter): boolean => {
    if (filters.instrument && !filters.instrument.includes(event.instrument)) return false;
    if (filters.timeframe && !filters.timeframe.includes(event.timeframe)) return false;
    if (filters.event_type && !filters.event_type.includes(event.event_type)) return false;
    if (filters.min_resistance_level && event.resistance_level < filters.min_resistance_level) return false;
    if (filters.max_resistance_level && event.resistance_level > filters.max_resistance_level) return false;
    if (filters.min_rebound_percentage && event.rebound_percentage < filters.min_rebound_percentage) return false;
    if (filters.max_rebound_percentage && event.rebound_percentage > filters.max_rebound_percentage) return false;
    return true;
  };

  // Fetch events from API
  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.listEvents(filters, {
        page: currentPage,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      
      setEvents(response.items);
      setTotalCount(response.total);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    } finally {
      setLoading(false);
    }
  }, [api, filters, currentPage, pageSize, sortBy, sortOrder]);

  // Fetch statistics
  const fetchStatistics = useCallback(async () => {
    try {
      const stats = await api.getStatistics(filters);
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  }, [api, filters]);

  // Load data on mount and when dependencies change
  useEffect(() => {
    fetchEvents();
    fetchStatistics();
  }, [fetchEvents, fetchStatistics]);

  // Handle filter changes
  const handleFilterChange = (newFilters: EventFilter) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page on filter change
  };

  // Handle filter reset
  const handleFilterReset = () => {
    setFilters({});
    setCurrentPage(1);
  };

  // Handle pagination
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  // Handle sorting
  const handleSortChange = (field: PaginationParams['sort_by'], order: PaginationParams['sort_order']) => {
    setSortBy(field);
    setSortOrder(order);
  };

  // Handle event click
  const handleEventClick = (event: ResistanceEvent) => {
    setSelectedEvent(event);
    if (viewMode === 'table') {
      setViewMode('split');
    }
  };

  // Handle export
  const handleExport = async () => {
    try {
      const blob = await api.exportEvents({
        format: 'csv',
        filters,
        include_metadata: true,
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `events_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export events:', error);
    }
  };

  // Toggle real-time streaming
  const toggleStreaming = () => {
    if (isConnected) {
      disconnectStream();
    } else {
      connectStream();
      if (!filters.instrument || filters.instrument.length === 0) {
        subscribeAll();
      }
    }
  };

  // Mock candle data for chart (in production, this would come from market data API)
  const mockCandles = useMemo(() => {
    const candles = [];
    const basePrice = 1.0850;
    const now = new Date();
    
    for (let i = 100; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 3600000); // 1 hour intervals
      const open = basePrice + (Math.random() - 0.5) * 0.002;
      const close = open + (Math.random() - 0.5) * 0.001;
      const high = Math.max(open, close) + Math.random() * 0.0005;
      const low = Math.min(open, close) - Math.random() * 0.0005;
      
      candles.push({
        timestamp: timestamp.toISOString(),
        open,
        high,
        low,
        close,
        volume: Math.floor(Math.random() * 10000 + 1000),
      });
    }
    
    return candles;
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Activity className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Event Analysis
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Real-time resistance event detection and analysis
                </p>
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'table'
                      ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Table
                </button>
                <button
                  onClick={() => setViewMode('chart')}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'chart'
                      ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Chart
                </button>
                <button
                  onClick={() => setViewMode('split')}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'split'
                      ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Split
                </button>
              </div>

              {/* Real-time Toggle */}
              {featureFlags.realTimeUI && (
                <button
                  onClick={toggleStreaming}
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-md transition-colors ${
                    isConnected
                      ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  }`}
                >
                  {isConnected ? (
                    <>
                      <Wifi className="w-4 h-4" />
                      <span className="text-sm font-medium">Live</span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="w-4 h-4" />
                      <span className="text-sm font-medium">Offline</span>
                    </>
                  )}
                </button>
              )}

              {/* Refresh Button */}
              <button
                onClick={fetchEvents}
                className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                title="Refresh"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Bar */}
      {statistics && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {statistics.total_events}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Total Events</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {(statistics.avg_rebound_percentage * 100).toFixed(2)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Avg Rebound</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Object.keys(statistics.events_by_instrument).length}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Instruments</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {statistics.most_active_hour ?? '-'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Peak Hour</p>
              </div>
              {isConnected && (
                <>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {streamMetrics.eventsReceived}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Live Events</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {streamEvents.length}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">In Buffer</p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="space-y-6">
          {/* Filters */}
          <EventFilters
            onFilterChange={handleFilterChange}
            onReset={handleFilterReset}
          />

          {/* Content based on view mode */}
          {viewMode === 'table' && (
            <EventTable
              events={events}
              totalCount={totalCount}
              currentPage={currentPage}
              pageSize={pageSize}
              sortBy={sortBy}
              sortOrder={sortOrder}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
              onSortChange={handleSortChange}
              onEventClick={handleEventClick}
              onExport={featureFlags.exportEnabled ? handleExport : undefined}
              loading={loading}
            />
          )}

          {viewMode === 'chart' && (
            <CandlestickChart
              candles={mockCandles}
              events={events}
              selectedEvent={selectedEvent}
              height={600}
              showVolume={true}
              instrument={filters.instrument?.[0] || 'EUR_USD'}
              timeframe={filters.timeframe?.[0] || 'H1'}
              onEventClick={handleEventClick}
            />
          )}

          {viewMode === 'split' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CandlestickChart
                candles={mockCandles}
                events={events}
                selectedEvent={selectedEvent}
                height={400}
                instrument={filters.instrument?.[0] || 'EUR_USD'}
                timeframe={filters.timeframe?.[0] || 'H1'}
                onEventClick={handleEventClick}
              />
              <div className="max-h-[400px] overflow-auto">
                <EventTable
                  events={events}
                  totalCount={totalCount}
                  currentPage={currentPage}
                  pageSize={Math.min(pageSize, 10)}
                  sortBy={sortBy}
                  sortOrder={sortOrder}
                  onPageChange={handlePageChange}
                  onPageSizeChange={handlePageSizeChange}
                  onSortChange={handleSortChange}
                  onEventClick={handleEventClick}
                  loading={loading}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}