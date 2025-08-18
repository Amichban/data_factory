'use client';

import { useEffect, useState } from 'react';
import { HealthStatus, ServiceHealth } from '@/types';
import { checkFrontendHealth, checkHealth } from '@/lib/api/health';

interface HealthPageState {
  frontendHealth: HealthStatus | null;
  backendHealth: HealthStatus | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export default function HealthPage() {
  const [state, setState] = useState<HealthPageState>({
    frontendHealth: null,
    backendHealth: null,
    loading: true,
    error: null,
    lastUpdated: null,
  });

  const fetchHealthData = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const [frontendResult, backendResult] = await Promise.allSettled([
        checkFrontendHealth(),
        checkHealth(),
      ]);

      setState(prev => ({
        ...prev,
        frontendHealth: frontendResult.status === 'fulfilled' ? frontendResult.value : null,
        backendHealth: backendResult.status === 'fulfilled' ? backendResult.value : null,
        loading: false,
        lastUpdated: new Date(),
        error: frontendResult.status === 'rejected' && backendResult.status === 'rejected' 
          ? 'Failed to fetch health data' 
          : null,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      }));
    }
  };

  useEffect(() => {
    fetchHealthData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'unhealthy':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'healthy':
        return '✅';
      case 'degraded':
        return '⚠️';
      case 'unhealthy':
        return '❌';
      default:
        return '❓';
    }
  };

  const formatUptime = (uptime: number): string => {
    const seconds = Math.floor(uptime / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const renderServiceHealth = (service: ServiceHealth) => (
    <div
      key={service.name}
      className={`p-4 rounded-lg border ${getStatusColor(service.status)}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-lg">{getStatusIcon(service.status)}</span>
          <h3 className="font-medium">{service.name}</h3>
        </div>
        <span className="text-sm font-medium uppercase">
          {service.status}
        </span>
      </div>
      {service.responseTime && (
        <p className="mt-2 text-sm">
          Response Time: {service.responseTime}ms
        </p>
      )}
      {service.message && (
        <p className="mt-2 text-sm opacity-80">
          {service.message}
        </p>
      )}
    </div>
  );

  const renderHealthStatus = (title: string, health: HealthStatus | null) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      
      {health ? (
        <>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-4 ${getStatusColor(health.status)}`}>
            <span className="mr-2">{getStatusIcon(health.status)}</span>
            {health.status.toUpperCase()}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <h3 className="text-sm font-medium text-gray-600">Uptime</h3>
              <p className="text-lg">{formatUptime(health.uptime)}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-600">Version</h3>
              <p className="text-lg">{health.version || 'Unknown'}</p>
            </div>
          </div>
          
          {health.services && health.services.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-4">Services</h3>
              <div className="space-y-3">
                {health.services.map(renderServiceHealth)}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <span className="text-4xl">❓</span>
          <p className="mt-2 text-gray-600">No health data available</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">System Health</h1>
          <p className="text-gray-600">
            Monitor the health and status of all system components
          </p>
          {state.lastUpdated && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {state.lastUpdated.toLocaleString()}
            </p>
          )}
        </div>

        {state.loading && !state.frontendHealth && !state.backendHealth && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading health data...</p>
          </div>
        )}

        {state.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <span className="text-red-500 text-xl mr-2">⚠️</span>
              <div>
                <h3 className="text-red-800 font-medium">Error</h3>
                <p className="text-red-700 text-sm">{state.error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {renderHealthStatus('Frontend Health', state.frontendHealth)}
          {renderHealthStatus('Backend Health', state.backendHealth)}
        </div>

        <div className="mt-8 flex justify-center">
          <button
            onClick={fetchHealthData}
            disabled={state.loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {state.loading ? (
              <>
                <div className="animate-spin -ml-1 mr-3 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Refreshing...
              </>
            ) : (
              <>
                <svg
                  className="-ml-1 mr-2 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Refresh
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}