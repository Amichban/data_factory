'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  Database, 
  Cloud, 
  AlertCircle, 
  CheckCircle2,
  XCircle,
  RefreshCw
} from 'lucide-react';

interface HealthStatus {
  status: string;
  data_provider?: {
    source_name: string;
    is_available: boolean;
    response_time_ms?: number;
    error_message?: string;
  };
  firestore?: {
    status: string;
    connected: boolean;
    error?: string;
  };
  rate_limiting?: {
    is_limited: boolean;
    requests_made: number;
    requests_remaining: number;
  };
  supported_instruments?: string[];
  supported_timeframes?: string[];
  last_check: string;
}

export function ServiceHealth() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchHealth = async () => {
    try {
      setIsRefreshing(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/market-data/health`
      );
      
      if (!response.ok) throw new Error('Failed to fetch health status');
      
      const data = await response.json();
      setHealth(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch service health');
      setHealth(null);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <Badge variant="success">Healthy</Badge>;
      case 'degraded':
        return <Badge variant="warning">Degraded</Badge>;
      case 'unhealthy':
        return <Badge variant="destructive">Unhealthy</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  if (loading && !health) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Service Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Service Health</CardTitle>
            <CardDescription>System components status</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchHealth}
              disabled={isRefreshing}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            {health && getStatusBadge(health.status)}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {health && (
          <>
            <div className="space-y-3">
              {/* Data Provider Status */}
              {health.data_provider && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Cloud className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="font-medium">Data Provider</p>
                      <p className="text-sm text-gray-500">
                        {health.data_provider.source_name.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {health.data_provider.response_time_ms && (
                      <span className="text-sm text-gray-500">
                        {health.data_provider.response_time_ms.toFixed(0)}ms
                      </span>
                    )}
                    {health.data_provider.is_available ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>
              )}

              {/* Firestore Status */}
              {health.firestore && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Database className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="font-medium">Firestore</p>
                      <p className="text-sm text-gray-500">Database</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {health.firestore.status === 'healthy' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>
              )}

              {/* Rate Limiting Status */}
              {health.rate_limiting && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Activity className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="font-medium">Rate Limiting</p>
                      <p className="text-sm text-gray-500">
                        {health.rate_limiting.requests_remaining} requests remaining
                      </p>
                    </div>
                  </div>
                  <div>
                    {!health.rate_limiting.is_limited ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-yellow-500" />
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Supported Configuration */}
            <div className="pt-2 border-t">
              <div className="grid grid-cols-2 gap-4 text-sm">
                {health.supported_instruments && (
                  <div>
                    <p className="text-gray-500">Instruments</p>
                    <p className="font-medium">{health.supported_instruments.length} supported</p>
                  </div>
                )}
                {health.supported_timeframes && (
                  <div>
                    <p className="text-gray-500">Timeframes</p>
                    <p className="font-medium">{health.supported_timeframes.join(', ')}</p>
                  </div>
                )}
              </div>
            </div>

            {health.last_check && (
              <div className="text-xs text-gray-500 pt-2 border-t">
                Last checked: {new Date(health.last_check).toLocaleString()}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}