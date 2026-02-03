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
} from 'recharts';
import { ChartContainer, ChartTooltip, CHART_COLORS, formatPercentage } from './chart-utils';

interface SentimentData {
  label: string;
  count: number;
  percentage: number;
}

interface SentimentChartProps {
  data: SentimentData[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  showPercentage?: boolean;
}

const getSentimentColor = (label: string): string => {
  switch (label.toLowerCase()) {
    case 'positive':
      return CHART_COLORS.positive;
    case 'negative':
      return CHART_COLORS.negative;
    case 'neutral':
      return CHART_COLORS.neutral;
    case 'mixed':
      return CHART_COLORS.mixed;
    default:
      return CHART_COLORS.primary;
  }
};

export function SentimentChart({
  data,
  loading = false,
  title = 'Sentiment Distribution',
  description,
  className,
  showPercentage = true,
}: SentimentChartProps) {
  const isEmpty = !data || data.length === 0;

  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No sentiment data available"
      className={className}
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
          <XAxis
            type="number"
            tickFormatter={(value) => showPercentage ? formatPercentage(value) : value.toString()}
            domain={showPercentage ? [0, 1] : [0, 'auto']}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fontSize: 14 }}
            width={80}
          />
          <Tooltip
            content={({ active, payload, label }) => (
              <ChartTooltip
                active={active}
                payload={payload}
                label={label}
                valueFormatter={(v) =>
                  showPercentage ? formatPercentage(v) : `${v} results`
                }
              />
            )}
          />
          <Bar
            dataKey={showPercentage ? 'percentage' : 'count'}
            name="Sentiment"
            radius={[0, 4, 4, 0]}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getSentimentColor(entry.label)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
