'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Activity, Database, AlertCircle, CheckCircle2 } from 'lucide-react';

interface IngestionStatus {
  request_id: string;
  status: string;
  message: string;
  instruments_processed: number;
  candles_ingested: number;
  candles_failed: number;
  processing_time_seconds?: number;
  errors: string[];
}

export function DataIngestionStatus() {
  const [status, setStatus] = useState<IngestionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        // This would be replaced with actual API call
        // const response = await fetch('/api/v1/market-data/status');
        // const data = await response.json();
        
        // Mock data for now
        setStatus({
          request_id: 'mock-123',
          status: 'processing',
          message: 'Ingesting market data...',
          instruments_processed: 15,
          candles_ingested: 2456,
          candles_failed: 3,
          processing_time_seconds: 45.2,
          errors: []
        });
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch ingestion status');
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    if (!status) return null;
    
    switch (status.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <Activity className="h-5 w-5 text-blue-500 animate-pulse" />;
      default:
        return <Database className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    if (!status) return 'default';
    
    switch (status.status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'destructive';
      case 'processing':
        return 'secondary';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Data Ingestion Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Data Ingestion Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center text-red-500">
            <AlertCircle className="h-5 w-5 mr-2" />
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) return null;

  const successRate = status.candles_ingested > 0 
    ? ((status.candles_ingested / (status.candles_ingested + status.candles_failed)) * 100).toFixed(1)
    : '0';

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Data Ingestion Status</CardTitle>
            <CardDescription>{status.message}</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <Badge variant={getStatusColor() as any}>
              {status.status.toUpperCase()}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Instruments Processed</p>
            <p className="text-2xl font-bold">{status.instruments_processed}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Candles Ingested</p>
            <p className="text-2xl font-bold">{status.candles_ingested.toLocaleString()}</p>
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-500">Success Rate</span>
            <span className="text-sm font-medium">{successRate}%</span>
          </div>
          <Progress value={parseFloat(successRate)} />
        </div>

        {status.processing_time_seconds && (
          <div className="pt-2 border-t">
            <p className="text-sm text-gray-500">
              Processing Time: <span className="font-medium">{status.processing_time_seconds.toFixed(1)}s</span>
            </p>
          </div>
        )}

        {status.errors.length > 0 && (
          <div className="pt-2 border-t">
            <p className="text-sm font-medium text-red-500 mb-2">Errors:</p>
            <ul className="text-sm text-gray-600 space-y-1">
              {status.errors.map((error, idx) => (
                <li key={idx} className="flex items-start">
                  <AlertCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                  {error}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}