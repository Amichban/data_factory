'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface QualityMetrics {
  instrument: string;
  timeframe: string;
  total_candles: number;
  complete_candles: number;
  missing_periods: number;
  duplicate_periods: number;
  price_gaps: number;
  volume_anomalies: number;
  completeness_ratio: number;
  quality_score: number;
  last_updated: string;
}

const INSTRUMENTS = [
  'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD', 'NZD_USD'
];

const TIMEFRAMES = ['H1', 'H4', 'D', 'W'];

export function DataQualityMetrics() {
  const [metrics, setMetrics] = useState<QualityMetrics | null>(null);
  const [selectedInstrument, setSelectedInstrument] = useState('EUR_USD');
  const [selectedTimeframe, setSelectedTimeframe] = useState('H1');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/market-data/quality/${selectedInstrument}?timeframe=${selectedTimeframe}`
        );
        
        if (!response.ok) throw new Error('Failed to fetch metrics');
        
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch quality metrics');
        setMetrics(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [selectedInstrument, selectedTimeframe]);

  const getQualityBadge = (score: number) => {
    if (score >= 0.9) return <Badge variant="success">Excellent</Badge>;
    if (score >= 0.7) return <Badge variant="secondary">Good</Badge>;
    if (score >= 0.5) return <Badge variant="warning">Fair</Badge>;
    return <Badge variant="destructive">Poor</Badge>;
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.9) return 'text-green-500';
    if (score >= 0.7) return 'text-blue-500';
    if (score >= 0.5) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Data Quality Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-10 bg-gray-200 rounded"></div>
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
            <CardTitle>Data Quality Metrics</CardTitle>
            <CardDescription>Monitor data completeness and quality</CardDescription>
          </div>
          <BarChart3 className="h-5 w-5 text-gray-500" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Select value={selectedInstrument} onValueChange={setSelectedInstrument}>
            <SelectTrigger>
              <SelectValue placeholder="Select instrument" />
            </SelectTrigger>
            <SelectContent>
              {INSTRUMENTS.map(inst => (
                <SelectItem key={inst} value={inst}>{inst}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
            <SelectTrigger>
              <SelectValue placeholder="Select timeframe" />
            </SelectTrigger>
            <SelectContent>
              {TIMEFRAMES.map(tf => (
                <SelectItem key={tf} value={tf}>{tf}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {error && (
          <div className="flex items-center text-red-500">
            <AlertCircle className="h-4 w-4 mr-2" />
            {error}
          </div>
        )}

        {metrics && (
          <>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Overall Quality Score</p>
                <p className={`text-3xl font-bold ${getQualityColor(metrics.quality_score)}`}>
                  {(metrics.quality_score * 100).toFixed(1)}%
                </p>
              </div>
              {getQualityBadge(metrics.quality_score)}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Total Candles</p>
                <p className="text-xl font-bold">{metrics.total_candles.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Complete Candles</p>
                <p className="text-xl font-bold">{metrics.complete_candles.toLocaleString()}</p>
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-500">Completeness</span>
                <span className="text-sm font-medium">
                  {(metrics.completeness_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <Progress value={metrics.completeness_ratio * 100} />
            </div>

            <div className="space-y-2 pt-2 border-t">
              <h4 className="text-sm font-medium">Data Issues</h4>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Missing Periods</span>
                <span className={`text-sm font-medium ${metrics.missing_periods > 0 ? 'text-yellow-500' : 'text-green-500'}`}>
                  {metrics.missing_periods}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Duplicate Periods</span>
                <span className={`text-sm font-medium ${metrics.duplicate_periods > 0 ? 'text-yellow-500' : 'text-green-500'}`}>
                  {metrics.duplicate_periods}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Price Gaps</span>
                <span className={`text-sm font-medium ${metrics.price_gaps > 0 ? 'text-yellow-500' : 'text-green-500'}`}>
                  {metrics.price_gaps}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Volume Anomalies</span>
                <span className={`text-sm font-medium ${metrics.volume_anomalies > 0 ? 'text-yellow-500' : 'text-green-500'}`}>
                  {metrics.volume_anomalies}
                </span>
              </div>
            </div>

            {metrics.last_updated && (
              <div className="text-xs text-gray-500 pt-2 border-t">
                Last updated: {new Date(metrics.last_updated).toLocaleString()}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}