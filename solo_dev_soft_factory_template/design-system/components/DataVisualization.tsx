import React from 'react';
import { cn } from '../utils/cn';

// Chart Container with glass effect
export const ChartContainer = ({ 
  children, 
  className,
  title,
  subtitle 
}: {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
}) => {
  return (
    <div className={cn(
      'bg-glass-card backdrop-blur-md border border-glass-border rounded-card p-6',
      'shadow-glass-md hover:shadow-glass-lg transition-all duration-300',
      className
    )}>
      {(title || subtitle) && (
        <div className="mb-6">
          {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
};

// Metric Card for displaying single metrics
export const MetricCard = ({
  label,
  value,
  change,
  trend,
  icon,
  color = 'primary',
  className
}: {
  label: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
}) => {
  const trendColors = {
    up: 'text-emerald-400',
    down: 'text-red-400',
    neutral: 'text-gray-400'
  };

  const iconColors = {
    primary: 'bg-primary-500/10 text-primary-400',
    secondary: 'bg-secondary-500/10 text-secondary-400',
    success: 'bg-emerald-500/10 text-emerald-400',
    warning: 'bg-amber-500/10 text-amber-400',
    danger: 'bg-red-500/10 text-red-400',
  };

  return (
    <div className={cn(
      'bg-glass-card backdrop-blur-md border border-glass-border rounded-xl p-4',
      'hover:shadow-glass-md transition-all duration-300',
      className
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">
            {label}
          </p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {change && trend && (
            <p className={cn('text-sm mt-2', trendColors[trend])}>
              {trend === 'up' && '↑'}
              {trend === 'down' && '↓'}
              {trend === 'neutral' && '→'}
              {' '}{change}
            </p>
          )}
        </div>
        {icon && (
          <div className={cn(
            'p-2 rounded-lg',
            iconColors[color]
          )}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

// Progress Bar Component
export const ProgressBar = ({
  value,
  max = 100,
  label,
  showValue = true,
  color = 'primary',
  className,
  animated = true
}: {
  value: number;
  max?: number;
  label?: string;
  showValue?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
  animated?: boolean;
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  const colorClasses = {
    primary: 'bg-gradient-to-r from-primary-500 to-primary-400',
    secondary: 'bg-gradient-to-r from-secondary-500 to-secondary-400',
    success: 'bg-gradient-to-r from-emerald-500 to-emerald-400',
    warning: 'bg-gradient-to-r from-amber-500 to-amber-400',
    danger: 'bg-gradient-to-r from-red-500 to-red-400',
  };

  return (
    <div className={cn('space-y-2', className)}>
      {(label || showValue) && (
        <div className="flex justify-between items-center">
          {label && <span className="text-sm text-gray-400">{label}</span>}
          {showValue && (
            <span className="text-sm font-medium text-white">
              {percentage.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div className="h-2 bg-dark-400 rounded-full overflow-hidden">
        <div
          className={cn(
            colorClasses[color],
            'h-full rounded-full transition-all duration-500',
            animated && 'animate-pulse'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Data Grid Component (for tables)
export const DataGrid = ({
  columns,
  data,
  className
}: {
  columns: Array<{ key: string; label: string; width?: string }>;
  data: Array<Record<string, any>>;
  className?: string;
}) => {
  return (
    <div className={cn(
      'bg-glass-card backdrop-blur-md border border-glass-border rounded-card overflow-hidden',
      className
    )}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-glass-border">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    'px-6 py-4 text-left text-xs font-medium text-gray-400 uppercase tracking-wider',
                    col.width
                  )}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-glass-border">
            {data.map((row, idx) => (
              <tr
                key={idx}
                className="hover:bg-glass-hover transition-colors duration-150"
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className="px-6 py-4 text-sm text-gray-200"
                  >
                    {row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Activity Feed Component
export const ActivityFeed = ({
  items,
  className
}: {
  items: Array<{
    id: string;
    user: string;
    action: string;
    target?: string;
    time: string;
    icon?: React.ReactNode;
  }>;
  className?: string;
}) => {
  return (
    <div className={cn(
      'bg-glass-card backdrop-blur-md border border-glass-border rounded-card p-6',
      className
    )}>
      <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="flex items-start space-x-3">
            {item.icon && (
              <div className="flex-shrink-0 p-2 bg-primary-500/10 rounded-lg">
                {item.icon}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-200">
                <span className="font-medium text-white">{item.user}</span>
                {' '}{item.action}
                {item.target && (
                  <span className="font-medium text-primary-400"> {item.target}</span>
                )}
              </p>
              <p className="text-xs text-gray-500 mt-1">{item.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Sparkline Component (mini chart)
export const Sparkline = ({
  data,
  color = 'primary',
  height = 40,
  className
}: {
  data: number[];
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  height?: number;
  className?: string;
}) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = ((max - value) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  const colorClasses = {
    primary: 'stroke-primary-400',
    secondary: 'stroke-secondary-400',
    success: 'stroke-emerald-400',
    warning: 'stroke-amber-400',
    danger: 'stroke-red-400',
  };

  return (
    <svg
      className={cn('w-full', className)}
      height={height}
      viewBox={`0 0 100 ${height}`}
      preserveAspectRatio="none"
    >
      <polyline
        points={points}
        fill="none"
        className={colorClasses[color]}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};