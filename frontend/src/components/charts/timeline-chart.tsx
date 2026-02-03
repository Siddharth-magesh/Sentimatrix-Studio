'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { ChartContainer, CHART_COLORS, formatPercentage } from './chart-utils';

interface TimelineDataPoint {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
  mixed?: number;
  total?: number;
}

interface TimelineChartProps {
  data: TimelineDataPoint[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  stacked?: boolean;
  showTotal?: boolean;
  dateFormat?: 'short' | 'long';
}

const formatDate = (dateStr: string, format: 'short' | 'long'): string => {
  const date = new Date(dateStr);
  if (format === 'short') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;

  const total = payload.reduce((sum: number, entry: any) => sum + (entry.value || 0), 0);

  return (
    <div className="bg-white rounded-lg shadow-lg border border-neutral-200 p-3">
      <p className="text-sm font-medium text-neutral-900 mb-2">
        {formatDate(label, 'long')}
      </p>
      <div className="space-y-1">
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm text-neutral-600">{entry.name}</span>
            </div>
            <span className="text-sm font-medium text-neutral-900">{entry.value}</span>
          </div>
        ))}
        <div className="border-t pt-1 mt-1 flex items-center justify-between">
          <span className="text-sm text-neutral-600">Total</span>
          <span className="text-sm font-medium text-neutral-900">{total}</span>
        </div>
      </div>
    </div>
  );
};

export function TimelineChart({
  data,
  loading = false,
  title = 'Sentiment Over Time',
  description,
  className,
  stacked = true,
  showTotal = false,
  dateFormat = 'short',
}: TimelineChartProps) {
  const isEmpty = !data || data.length === 0;

  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No timeline data available"
      className={className}
    >
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorPositive" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.positive} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.positive} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorNegative" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.negative} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.negative} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorNeutral" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.neutral} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.neutral} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorMixed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.mixed} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.mixed} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => formatDate(value, dateFormat)}
            tick={{ fontSize: 12 }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => (
              <span className="text-sm text-neutral-600">{value}</span>
            )}
          />
          <Area
            type="monotone"
            dataKey="positive"
            name="Positive"
            stackId={stacked ? '1' : undefined}
            stroke={CHART_COLORS.positive}
            fill="url(#colorPositive)"
          />
          <Area
            type="monotone"
            dataKey="neutral"
            name="Neutral"
            stackId={stacked ? '1' : undefined}
            stroke={CHART_COLORS.neutral}
            fill="url(#colorNeutral)"
          />
          <Area
            type="monotone"
            dataKey="negative"
            name="Negative"
            stackId={stacked ? '1' : undefined}
            stroke={CHART_COLORS.negative}
            fill="url(#colorNegative)"
          />
          {data[0]?.mixed !== undefined && (
            <Area
              type="monotone"
              dataKey="mixed"
              name="Mixed"
              stackId={stacked ? '1' : undefined}
              stroke={CHART_COLORS.mixed}
              fill="url(#colorMixed)"
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
