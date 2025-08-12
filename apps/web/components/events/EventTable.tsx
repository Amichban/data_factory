/**
 * Event Table Component
 * 
 * Displays events in a sortable, responsive table with detailed views
 */

import React, { useState, useMemo } from 'react';
import { 
  ChevronUp, 
  ChevronDown, 
  ChevronLeft, 
  ChevronRight,
  Eye,
  Download,
  TrendingUp,
  TrendingDown,
  AlertCircle
} from 'lucide-react';
import { ResistanceEvent, PaginationParams } from '@/lib/api/events';
import { EVENT_TYPES, eventsConfig } from '@/lib/config';
import { format } from 'date-fns';

interface EventTableProps {
  events: ResistanceEvent[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  sortBy: PaginationParams['sort_by'];
  sortOrder: PaginationParams['sort_order'];
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  onSortChange: (field: PaginationParams['sort_by'], order: PaginationParams['sort_order']) => void;
  onEventClick?: (event: ResistanceEvent) => void;
  onExport?: () => void;
  loading?: boolean;
}

export const EventTable: React.FC<EventTableProps> = ({
  events,
  totalCount,
  currentPage,
  pageSize,
  sortBy,
  sortOrder,
  onPageChange,
  onPageSizeChange,
  onSortChange,
  onEventClick,
  onExport,
  loading = false,
}) => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const totalPages = Math.ceil(totalCount / pageSize);

  const handleSort = (field: PaginationParams['sort_by']) => {
    if (sortBy === field) {
      onSortChange(field, sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      onSortChange(field, 'desc');
    }
  };

  const SortIcon = ({ field }: { field: PaginationParams['sort_by'] }) => {
    if (sortBy !== field) {
      return <div className="w-4 h-4" />;
    }
    return sortOrder === 'asc' 
      ? <ChevronUp className="w-4 h-4" />
      : <ChevronDown className="w-4 h-4" />;
  };

  const getEventTypeConfig = (type: string) => {
    return EVENT_TYPES.find(t => t.value === type) || EVENT_TYPES[0];
  };

  const formatNumber = (value: number, decimals: number = 4) => {
    return value.toFixed(decimals);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const renderPagination = () => {
    const pageNumbers = [];
    const maxButtons = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);

    if (endPage - startPage < maxButtons - 1) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(i);
    }

    return (
      <div className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-700 dark:text-gray-300">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} events
          </span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          >
            {eventsConfig.tablePageSizes.map(size => (
              <option key={size} value={size}>{size} per page</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          {startPage > 1 && (
            <>
              <button
                onClick={() => onPageChange(1)}
                className="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded"
              >
                1
              </button>
              {startPage > 2 && <span className="px-2 text-gray-500">...</span>}
            </>
          )}

          {pageNumbers.map(page => (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`px-3 py-1 text-sm rounded ${
                page === currentPage
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              {page}
            </button>
          ))}

          {endPage < totalPages && (
            <>
              {endPage < totalPages - 1 && <span className="px-2 text-gray-500">...</span>}
              <button
                onClick={() => onPageChange(totalPages)}
                className="px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded"
              >
                {totalPages}
              </button>
            </>
          )}

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
      {/* Table Header Actions */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Resistance Events
        </h3>
        {onExport && (
          <button
            onClick={onExport}
            className="flex items-center space-x-2 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('event_timestamp')}
                  className="flex items-center space-x-1 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <span>Time</span>
                  <SortIcon field="event_timestamp" />
                </button>
              </th>
              <th className="px-6 py-3 text-left">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Type
                </span>
              </th>
              <th className="px-6 py-3 text-left">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Instrument
                </span>
              </th>
              <th className="px-6 py-3 text-left">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Timeframe
                </span>
              </th>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('resistance_level')}
                  className="flex items-center space-x-1 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <span>Level</span>
                  <SortIcon field="resistance_level" />
                </button>
              </th>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('rebound_percentage')}
                  className="flex items-center space-x-1 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <span>Rebound</span>
                  <SortIcon field="rebound_percentage" />
                </button>
              </th>
              <th className="px-6 py-3 text-left">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Actions
                </span>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {events.map((event) => {
              const eventType = getEventTypeConfig(event.event_type);
              const isExpanded = expandedRow === event.id;

              return (
                <React.Fragment key={event.id}>
                  <tr className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {format(new Date(event.event_timestamp), 'MMM dd, HH:mm')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span 
                        className="px-2 py-1 text-xs font-medium rounded-full text-white"
                        style={{ backgroundColor: eventType.color }}
                      >
                        {eventType.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                      {event.instrument}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {event.timeframe}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-gray-100">
                      {formatNumber(event.resistance_level, 5)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {event.rebound_percentage > 0 ? (
                          <TrendingUp className="w-4 h-4 text-green-500" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        )}
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {formatPercentage(event.rebound_percentage)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setExpandedRow(isExpanded ? null : event.id)}
                          className="p-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                          title="View details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {onEventClick && (
                          <button
                            onClick={() => onEventClick(event)}
                            className="p-1 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                            title="View on chart"
                          >
                            <AlertCircle className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>

                  {/* Expanded Row Details */}
                  {isExpanded && (
                    <tr>
                      <td colSpan={7} className="px-6 py-4 bg-gray-50 dark:bg-gray-900">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Green Candle (Before)
                            </h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Open:</span>
                                <span className="font-mono">{formatNumber(event.green_candle.open)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">High:</span>
                                <span className="font-mono">{formatNumber(event.green_candle.high)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Low:</span>
                                <span className="font-mono">{formatNumber(event.green_candle.low)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Close:</span>
                                <span className="font-mono">{formatNumber(event.green_candle.close)}</span>
                              </div>
                            </div>
                          </div>

                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Red Candle (After)
                            </h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Open:</span>
                                <span className="font-mono">{formatNumber(event.red_candle.open)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">High:</span>
                                <span className="font-mono">{formatNumber(event.red_candle.high)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Low:</span>
                                <span className="font-mono">{formatNumber(event.red_candle.low)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Close:</span>
                                <span className="font-mono">{formatNumber(event.red_candle.close)}</span>
                              </div>
                            </div>
                          </div>

                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Event Metrics
                            </h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Amplitude:</span>
                                <span className="font-mono">{formatNumber(event.rebound_amplitude)}</span>
                              </div>
                              {event.atr_value && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600 dark:text-gray-400">ATR:</span>
                                  <span className="font-mono">{formatNumber(event.atr_value)}</span>
                                </div>
                              )}
                              {event.rebound_in_atr && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600 dark:text-gray-400">Rebound/ATR:</span>
                                  <span className="font-mono">{event.rebound_in_atr.toFixed(2)}</span>
                                </div>
                              )}
                              <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">Detected:</span>
                                <span>{format(new Date(event.detected_at), 'HH:mm:ss')}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalCount > 0 && renderPagination()}

      {/* Empty State */}
      {events.length === 0 && !loading && (
        <div className="px-6 py-12 text-center">
          <AlertCircle className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500 dark:text-gray-400">No events found matching your filters</p>
        </div>
      )}
    </div>
  );
};