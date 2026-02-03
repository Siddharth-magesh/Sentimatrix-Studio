'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ChartContainerProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  loading?: boolean;
  empty?: boolean;
  emptyMessage?: string;
}

export function ChartContainer({
  children,
  className,
  title,
  description,
  loading = false,
  empty = false,
  emptyMessage = 'No data available',
}: ChartContainerProps) {
  if (loading) {
    return (
      <div className={cn('relative', className)}>
        {title && (
          <div className="mb-4">
            <div className="h-6 w-32 bg-neutral-200 rounded animate-pulse" />
            {description && (
              <div className="h-4 w-48 bg-neutral-100 rounded animate-pulse mt-1" />
            )}
          </div>
        )}
        <div className="h-64 bg-neutral-100 rounded-lg animate-pulse flex items-center justify-center">
          <span className="text-neutral-400">Loading chart...</span>
        </div>
      </div>
    );
  }

  if (empty) {
    return (
      <div className={cn('relative', className)}>
        {title && (
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-neutral-900">{title}</h3>
            {description && (
              <p className="text-sm text-neutral-500">{description}</p>
            )}
          </div>
        )}
        <div className="h-64 bg-neutral-50 rounded-lg border-2 border-dashed border-neutral-200 flex items-center justify-center">
          <span className="text-neutral-500">{emptyMessage}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('relative', className)}>
      {title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-neutral-900">{title}</h3>
          {description && (
            <p className="text-sm text-neutral-500">{description}</p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}

interface ChartLegendItem {
  label: string;
  color: string;
  value?: number | string;
}

interface ChartLegendProps {
  items: ChartLegendItem[];
  className?: string;
  direction?: 'horizontal' | 'vertical';
}

export function ChartLegend({
  items,
  className,
  direction = 'horizontal',
}: ChartLegendProps) {
  return (
    <div
      className={cn(
        'flex gap-4',
        direction === 'vertical' ? 'flex-col' : 'flex-row flex-wrap justify-center',
        className
      )}
    >
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div
            className="h-3 w-3 rounded-full"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-sm text-neutral-600">{item.label}</span>
          {item.value !== undefined && (
            <span className="text-sm font-medium text-neutral-900">{item.value}</span>
          )}
        </div>
      ))}
    </div>
  );
}

interface ChartTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  valueFormatter?: (value: number) => string;
  labelFormatter?: (label: string) => string;
}

export function ChartTooltip({
  active,
  payload,
  label,
  valueFormatter = (v) => v.toString(),
  labelFormatter = (l) => l,
}: ChartTooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-neutral-200 p-3">
      {label && (
        <p className="text-sm font-medium text-neutral-900 mb-2">
          {labelFormatter(label)}
        </p>
      )}
      <div className="space-y-1">
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-neutral-600">{entry.name}:</span>
            <span className="text-sm font-medium text-neutral-900">
              {valueFormatter(entry.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Color constants for consistent chart styling
export const CHART_COLORS = {
  positive: '#22c55e', // green-500
  negative: '#ef4444', // red-500
  neutral: '#6b7280', // gray-500
  mixed: '#f59e0b', // amber-500
  primary: '#6366f1', // indigo-500
  secondary: '#8b5cf6', // violet-500
  info: '#0ea5e9', // sky-500

  // For multi-series charts
  series: [
    '#6366f1', // indigo
    '#8b5cf6', // violet
    '#ec4899', // pink
    '#f59e0b', // amber
    '#22c55e', // green
    '#0ea5e9', // sky
    '#ef4444', // red
    '#84cc16', // lime
  ],

  // Emotion colors
  emotions: {
    joy: '#fbbf24', // amber-400
    sadness: '#3b82f6', // blue-500
    anger: '#ef4444', // red-500
    fear: '#8b5cf6', // violet-500
    surprise: '#f97316', // orange-500
    disgust: '#22c55e', // green-500
  },
};

// Format percentage for display
export function formatPercentage(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

// Format large numbers
export function formatCompactNumber(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
}
