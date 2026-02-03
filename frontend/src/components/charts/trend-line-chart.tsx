'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';
import { ChartContainer, CHART_COLORS, formatPercentage, formatCompactNumber } from './chart-utils';

interface TrendDataPoint {
  date: string;
  value: number;
  [key: string]: string | number;
}

interface TrendLineChartProps {
  data: TrendDataPoint[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  dataKey?: string;
  name?: string;
  color?: string;
  showAverage?: boolean;
  showTrend?: boolean;
  valueType?: 'number' | 'percentage';
}

interface MultiTrendLineChartProps {
  data: TrendDataPoint[];
  series: { key: string; name: string; color?: string }[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  showLegend?: boolean;
  valueType?: 'number' | 'percentage';
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const CustomTooltip = ({ active, payload, label, valueType }: any) => {
  if (!active || !payload?.length) return null;

  const formatter = valueType === 'percentage' ? formatPercentage : formatCompactNumber;

  return (
    <div className="bg-white rounded-lg shadow-lg border border-neutral-200 p-3">
      <p className="text-sm font-medium text-neutral-900 mb-2">
        {formatDate(label)}
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
            <span className="text-sm font-medium text-neutral-900">
              {formatter(entry.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export function TrendLineChart({
  data,
  loading = false,
  title = 'Trend',
  description,
  className,
  dataKey = 'value',
  name = 'Value',
  color = CHART_COLORS.primary,
  showAverage = false,
  showTrend = false,
  valueType = 'number',
}: TrendLineChartProps) {
  const isEmpty = !data || data.length === 0;

  // Calculate average for reference line
  const average = data.length > 0
    ? data.reduce((sum, d) => sum + (d[dataKey] as number), 0) / data.length
    : 0;

  // Calculate trend (simple linear regression)
  const trend = data.length > 1
    ? (data[data.length - 1][dataKey] as number) - (data[0][dataKey] as number)
    : 0;

  const formatter = valueType === 'percentage' ? formatPercentage : formatCompactNumber;

  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No trend data available"
      className={className}
    >
      {showTrend && data.length > 1 && (
        <div className="mb-4 flex items-center gap-2">
          <span className="text-sm text-neutral-500">Trend:</span>
          <span
            className={`text-sm font-medium ${
              trend > 0 ? 'text-success-600' : trend < 0 ? 'text-error-600' : 'text-neutral-600'
            }`}
          >
            {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {formatter(Math.abs(trend))}
          </span>
        </div>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            tickFormatter={formatter}
            tick={{ fontSize: 12 }}
            domain={valueType === 'percentage' ? [0, 1] : ['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip valueType={valueType} />} />
          {showAverage && (
            <ReferenceLine
              y={average}
              stroke={CHART_COLORS.neutral}
              strokeDasharray="5 5"
              label={{
                value: `Avg: ${formatter(average)}`,
                position: 'right',
                fontSize: 12,
                fill: CHART_COLORS.neutral,
              }}
            />
          )}
          <Line
            type="monotone"
            dataKey={dataKey}
            name={name}
            stroke={color}
            strokeWidth={2}
            dot={{ r: 4, fill: color }}
            activeDot={{ r: 6, fill: color }}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

export function MultiTrendLineChart({
  data,
  series,
  loading = false,
  title = 'Trends',
  description,
  className,
  showLegend = true,
  valueType = 'number',
}: MultiTrendLineChartProps) {
  const isEmpty = !data || data.length === 0;

  const formatter = valueType === 'percentage' ? formatPercentage : formatCompactNumber;

  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No trend data available"
      className={className}
    >
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            tickFormatter={formatter}
            tick={{ fontSize: 12 }}
            domain={valueType === 'percentage' ? [0, 1] : ['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip valueType={valueType} />} />
          {showLegend && (
            <Legend
              formatter={(value) => (
                <span className="text-sm text-neutral-600">{value}</span>
              )}
            />
          )}
          {series.map((s, index) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              name={s.name}
              stroke={s.color || CHART_COLORS.series[index % CHART_COLORS.series.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
