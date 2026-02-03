'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import { ChartContainer, CHART_COLORS, formatCompactNumber } from './chart-utils';

interface PlatformData {
  platform: string;
  count: number;
  positive?: number;
  negative?: number;
  neutral?: number;
}

interface PlatformBarChartProps {
  data: PlatformData[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  showSentimentBreakdown?: boolean;
  layout?: 'horizontal' | 'vertical';
}

const getPlatformIcon = (platform: string): string => {
  const icons: Record<string, string> = {
    amazon: '📦',
    youtube: '▶️',
    reddit: '🔗',
    trustpilot: '⭐',
    yelp: '🍽️',
    steam: '🎮',
    google: '🔍',
    twitter: '🐦',
    facebook: '📘',
  };
  return icons[platform.toLowerCase()] || '🌐';
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload;
  const total = data.count || payload.reduce((sum: number, p: any) => sum + p.value, 0);

  return (
    <div className="bg-white rounded-lg shadow-lg border border-neutral-200 p-3">
      <p className="text-sm font-medium text-neutral-900 mb-2 flex items-center gap-2">
        <span>{getPlatformIcon(data.platform)}</span>
        <span className="capitalize">{data.platform}</span>
      </p>
      <div className="space-y-1">
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm text-neutral-600 capitalize">{entry.name}</span>
            </div>
            <span className="text-sm font-medium text-neutral-900">
              {formatCompactNumber(entry.value)}
            </span>
          </div>
        ))}
        {payload.length > 1 && (
          <div className="border-t pt-1 mt-1 flex items-center justify-between">
            <span className="text-sm text-neutral-600">Total</span>
            <span className="text-sm font-medium text-neutral-900">
              {formatCompactNumber(total)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export function PlatformBarChart({
  data,
  loading = false,
  title = 'Results by Platform',
  description,
  className,
  showSentimentBreakdown = false,
  layout = 'vertical',
}: PlatformBarChartProps) {
  const isEmpty = !data || data.length === 0;

  // Sort by count descending
  const sortedData = [...data].sort((a, b) => b.count - a.count);

  if (layout === 'vertical') {
    return (
      <ChartContainer
        title={title}
        description={description}
        loading={loading}
        empty={isEmpty}
        emptyMessage="No platform data available"
        className={className}
      >
        <ResponsiveContainer width="100%" height={Math.max(300, sortedData.length * 50)}>
          <BarChart data={sortedData} layout="vertical" margin={{ left: 20, right: 40 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
            <XAxis type="number" tickFormatter={formatCompactNumber} />
            <YAxis
              type="category"
              dataKey="platform"
              tick={{ fontSize: 14 }}
              width={100}
              tickFormatter={(value) => `${getPlatformIcon(value)} ${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            {showSentimentBreakdown ? (
              <>
                <Bar dataKey="positive" name="Positive" stackId="a" fill={CHART_COLORS.positive} />
                <Bar dataKey="neutral" name="Neutral" stackId="a" fill={CHART_COLORS.neutral} />
                <Bar dataKey="negative" name="Negative" stackId="a" fill={CHART_COLORS.negative} radius={[0, 4, 4, 0]} />
              </>
            ) : (
              <Bar dataKey="count" name="Results" radius={[0, 4, 4, 0]}>
                {sortedData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={CHART_COLORS.series[index % CHART_COLORS.series.length]}
                  />
                ))}
                <LabelList
                  dataKey="count"
                  position="right"
                  formatter={formatCompactNumber}
                  className="text-sm fill-neutral-600"
                />
              </Bar>
            )}
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
    );
  }

  // Horizontal layout
  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No platform data available"
      className={className}
    >
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={sortedData} margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="platform"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${getPlatformIcon(value)} ${value}`}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tickFormatter={formatCompactNumber} />
          <Tooltip content={<CustomTooltip />} />
          {showSentimentBreakdown ? (
            <>
              <Bar dataKey="positive" name="Positive" stackId="a" fill={CHART_COLORS.positive} />
              <Bar dataKey="neutral" name="Neutral" stackId="a" fill={CHART_COLORS.neutral} />
              <Bar dataKey="negative" name="Negative" stackId="a" fill={CHART_COLORS.negative} radius={[4, 4, 0, 0]} />
            </>
          ) : (
            <Bar dataKey="count" name="Results" radius={[4, 4, 0, 0]}>
              {sortedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={CHART_COLORS.series[index % CHART_COLORS.series.length]}
                />
              ))}
            </Bar>
          )}
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
