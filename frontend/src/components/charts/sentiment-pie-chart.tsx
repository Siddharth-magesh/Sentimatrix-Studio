'use client';

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { ChartContainer, CHART_COLORS, formatPercentage } from './chart-utils';

interface SentimentPieData {
  label: string;
  count: number;
  percentage: number;
}

interface SentimentPieChartProps {
  data: SentimentPieData[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  innerRadius?: number;
  outerRadius?: number;
  showLabels?: boolean;
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

const CustomLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  label,
}: any) => {
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  if (percent < 0.05) return null; // Hide labels for very small slices

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      className="text-xs font-medium"
    >
      {formatPercentage(percent, 0)}
    </text>
  );
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-neutral-200 p-3">
      <div className="flex items-center gap-2 mb-1">
        <div
          className="h-3 w-3 rounded-full"
          style={{ backgroundColor: getSentimentColor(data.label) }}
        />
        <span className="font-medium text-neutral-900">{data.label}</span>
      </div>
      <div className="text-sm text-neutral-600">
        <div>{data.count.toLocaleString()} results</div>
        <div>{formatPercentage(data.percentage)}</div>
      </div>
    </div>
  );
};

export function SentimentPieChart({
  data,
  loading = false,
  title = 'Sentiment Breakdown',
  description,
  className,
  innerRadius = 60,
  outerRadius = 100,
  showLabels = true,
}: SentimentPieChartProps) {
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
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={showLabels ? CustomLabel : undefined}
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            dataKey="count"
            nameKey="label"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getSentimentColor(entry.label)}
                strokeWidth={2}
                stroke="#fff"
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => (
              <span className="text-sm text-neutral-600">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
