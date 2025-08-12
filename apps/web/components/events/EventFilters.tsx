/**
 * Event Filters Component
 * 
 * Provides comprehensive filtering interface for events
 */

import React, { useState, useCallback } from 'react';
import { Calendar, Filter, X, ChevronDown } from 'lucide-react';
import { INSTRUMENTS, TIMEFRAMES, EVENT_TYPES } from '@/lib/config';
import { EventFilter } from '@/lib/api/events';

interface EventFiltersProps {
  onFilterChange: (filters: EventFilter) => void;
  onReset: () => void;
  className?: string;
}

export const EventFilters: React.FC<EventFiltersProps> = ({
  onFilterChange,
  onReset,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState<EventFilter>({});
  const [selectedInstruments, setSelectedInstruments] = useState<Set<string>>(new Set());
  const [selectedTimeframes, setSelectedTimeframes] = useState<Set<string>>(new Set());
  const [selectedEventTypes, setSelectedEventTypes] = useState<Set<string>>(new Set());

  const handleFilterChange = useCallback((newFilters: Partial<EventFilter>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    onFilterChange(updatedFilters);
  }, [filters, onFilterChange]);

  const handleInstrumentToggle = (instrument: string) => {
    const updated = new Set(selectedInstruments);
    if (updated.has(instrument)) {
      updated.delete(instrument);
    } else {
      updated.add(instrument);
    }
    setSelectedInstruments(updated);
    handleFilterChange({ instrument: Array.from(updated) });
  };

  const handleTimeframeToggle = (timeframe: string) => {
    const updated = new Set(selectedTimeframes);
    if (updated.has(timeframe)) {
      updated.delete(timeframe);
    } else {
      updated.add(timeframe);
    }
    setSelectedTimeframes(updated);
    handleFilterChange({ timeframe: Array.from(updated) });
  };

  const handleEventTypeToggle = (eventType: string) => {
    const updated = new Set(selectedEventTypes);
    if (updated.has(eventType)) {
      updated.delete(eventType);
    } else {
      updated.add(eventType);
    }
    setSelectedEventTypes(updated);
    handleFilterChange({ event_type: Array.from(updated) });
  };

  const handleReset = () => {
    setFilters({});
    setSelectedInstruments(new Set());
    setSelectedTimeframes(new Set());
    setSelectedEventTypes(new Set());
    onReset();
  };

  const activeFilterCount = 
    selectedInstruments.size + 
    selectedTimeframes.size + 
    selectedEventTypes.size +
    (filters.start_date ? 1 : 0) +
    (filters.end_date ? 1 : 0) +
    (filters.min_resistance_level ? 1 : 0) +
    (filters.max_resistance_level ? 1 : 0);

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Filter Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-gray-500" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Filters</h3>
            {activeFilterCount > 0 && (
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                {activeFilterCount} active
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {activeFilterCount > 0 && (
              <button
                onClick={handleReset}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
              >
                Clear all
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            >
              <ChevronDown 
                className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Filters */}
      <div className="p-4 space-y-4">
        {/* Date Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Start Date
            </label>
            <input
              type="datetime-local"
              value={filters.start_date || ''}
              onChange={(e) => handleFilterChange({ start_date: e.target.value || undefined })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              End Date
            </label>
            <input
              type="datetime-local"
              value={filters.end_date || ''}
              onChange={(e) => handleFilterChange({ end_date: e.target.value || undefined })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
        </div>

        {/* Instrument Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Instruments
          </label>
          <div className="flex flex-wrap gap-2">
            {INSTRUMENTS.slice(0, 8).map((instrument) => (
              <button
                key={instrument}
                onClick={() => handleInstrumentToggle(instrument)}
                className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                  selectedInstruments.has(instrument)
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-blue-500'
                }`}
              >
                {instrument}
              </button>
            ))}
            {INSTRUMENTS.length > 8 && !isExpanded && (
              <button
                onClick={() => setIsExpanded(true)}
                className="px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700"
              >
                +{INSTRUMENTS.length - 8} more
              </button>
            )}
          </div>
        </div>

        {/* Event Types */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Event Types
          </label>
          <div className="flex flex-wrap gap-2">
            {EVENT_TYPES.map((type) => (
              <button
                key={type.value}
                onClick={() => handleEventTypeToggle(type.value)}
                className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                  selectedEventTypes.has(type.value)
                    ? 'text-white border-current'
                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600'
                }`}
                style={
                  selectedEventTypes.has(type.value)
                    ? { backgroundColor: type.color, borderColor: type.color }
                    : {}
                }
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
          {/* Timeframes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Timeframes
            </label>
            <div className="flex flex-wrap gap-2">
              {TIMEFRAMES.map((timeframe) => (
                <button
                  key={timeframe.value}
                  onClick={() => handleTimeframeToggle(timeframe.value)}
                  className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                    selectedTimeframes.has(timeframe.value)
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-blue-500'
                  }`}
                >
                  {timeframe.label}
                </button>
              ))}
            </div>
          </div>

          {/* All Instruments */}
          {INSTRUMENTS.length > 8 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                All Instruments
              </label>
              <div className="flex flex-wrap gap-2">
                {INSTRUMENTS.map((instrument) => (
                  <button
                    key={instrument}
                    onClick={() => handleInstrumentToggle(instrument)}
                    className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                      selectedInstruments.has(instrument)
                        ? 'bg-blue-500 text-white border-blue-500'
                        : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-blue-500'
                    }`}
                  >
                    {instrument}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Value Ranges */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Min Resistance Level
              </label>
              <input
                type="number"
                step="0.0001"
                value={filters.min_resistance_level || ''}
                onChange={(e) => handleFilterChange({ 
                  min_resistance_level: e.target.value ? parseFloat(e.target.value) : undefined 
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., 1.0800"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Max Resistance Level
              </label>
              <input
                type="number"
                step="0.0001"
                value={filters.max_resistance_level || ''}
                onChange={(e) => handleFilterChange({ 
                  max_resistance_level: e.target.value ? parseFloat(e.target.value) : undefined 
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., 1.1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Min Rebound %
              </label>
              <input
                type="number"
                step="0.01"
                value={filters.min_rebound_percentage || ''}
                onChange={(e) => handleFilterChange({ 
                  min_rebound_percentage: e.target.value ? parseFloat(e.target.value) : undefined 
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., 0.10"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Max Rebound %
              </label>
              <input
                type="number"
                step="0.01"
                value={filters.max_rebound_percentage || ''}
                onChange={(e) => handleFilterChange({ 
                  max_rebound_percentage: e.target.value ? parseFloat(e.target.value) : undefined 
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., 0.50"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};