'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';

interface RateLimit {
  requests_made: number;
  requests_remaining: number;
  reset_time: string;
  is_limited: boolean;
  usage_percentage: number;
}

export function RateLimitStatus() {
  const [rateLimit, setRateLimit] = useState<RateLimit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRateLimit = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/market-data/rate-limit`);
        if (!response.ok) throw new Error('Failed to fetch rate limit');
        const data = await response.json();
        setRateLimit(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch rate limit status');
        setLoading(false);
      }
    };

    fetchRateLimit();
    const interval = setInterval(fetchRateLimit, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const getTimeUntilReset = () => {
    if (!rateLimit) return '';
    
    const resetTime = new Date(rateLimit.reset_time);
    const now = new Date();
    const diff = resetTime.getTime() - now.getTime();
    
    if (diff <= 0) return 'Resetting...';
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    return `${minutes}m ${seconds}s`;
  };

  const getProgressColor = () => {
    if (!rateLimit) return 'bg-gray-200';
    
    if (rateLimit.usage_percentage >= 90) return 'bg-red-500';
    if (rateLimit.usage_percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Rate Limit Status</CardTitle>
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

  if (error || !rateLimit) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Rate Limit Status</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error || 'No data available'}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rate Limit Status</CardTitle>
        <CardDescription>
          API request limits and usage
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {rateLimit.is_limited && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Rate limit exceeded. Requests are being throttled.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Requests Made</p>
            <p className="text-2xl font-bold">{rateLimit.requests_made}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Requests Remaining</p>
            <p className="text-2xl font-bold">{rateLimit.requests_remaining}</p>
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-500">Usage</span>
            <span className="text-sm font-medium">{rateLimit.usage_percentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all ${getProgressColor()}`}
              style={{ width: `${Math.min(rateLimit.usage_percentage, 100)}%` }}
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="h-4 w-4 mr-2" />
            Reset in:
          </div>
          <span className="text-sm font-medium">{getTimeUntilReset()}</span>
        </div>

        <div className="flex items-center text-sm">
          {rateLimit.is_limited ? (
            <div className="flex items-center text-red-500">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Rate limited
            </div>
          ) : (
            <div className="flex items-center text-green-500">
              <CheckCircle className="h-4 w-4 mr-2" />
              Operating normally
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}