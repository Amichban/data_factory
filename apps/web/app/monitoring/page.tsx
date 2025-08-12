'use client';

import { DataIngestionStatus } from '@/components/monitoring/DataIngestionStatus';
import { RateLimitStatus } from '@/components/monitoring/RateLimitStatus';
import { DataQualityMetrics } from '@/components/monitoring/DataQualityMetrics';
import { ServiceHealth } from '@/components/monitoring/ServiceHealth';
import { Activity } from 'lucide-react';

export default function MonitoringDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">System Monitoring Dashboard</h1>
          </div>
          <p className="text-gray-600">
            Real-time monitoring of market data ingestion and system health
          </p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Service Health - Full Width on Mobile, Half on Desktop */}
          <div className="lg:col-span-1">
            <ServiceHealth />
          </div>

          {/* Rate Limit Status */}
          <div className="lg:col-span-1">
            <RateLimitStatus />
          </div>

          {/* Data Ingestion Status */}
          <div className="lg:col-span-1">
            <DataIngestionStatus />
          </div>

          {/* Data Quality Metrics */}
          <div className="lg:col-span-1">
            <DataQualityMetrics />
          </div>
        </div>

        {/* Additional Stats Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Streams</p>
                <p className="text-2xl font-bold">0</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Candles Today</p>
                <p className="text-2xl font-bold">0</p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Data Quality Score</p>
                <p className="text-2xl font-bold">0%</p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}