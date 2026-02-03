'use client';

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { ChartContainer, CHART_COLORS, formatPercentage } from './chart-utils';

interface EmotionData {
  emotion: string;
  value: number;
  fullMark?: number;
}

interface EmotionRadarChartProps {
  data: EmotionData[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  fillOpacity?: number;
}

const getEmotionColor = (emotion: string): string => {
  const colors = CHART_COLORS.emotions as Record<string, string>;
  return colors[emotion.toLowerCase()] || CHART_COLORS.primary;
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-neutral-200 p-3">
      <div className="flex items-center gap-2 mb-1">
        <div
          className="h-3 w-3 rounded-full"
          style={{ backgroundColor: getEmotionColor(data.emotion) }}
        />
        <span className="font-medium text-neutral-900 capitalize">{data.emotion}</span>
      </div>
      <div className="text-sm text-neutral-600">
        Score: {formatPercentage(data.value)}
      </div>
    </div>
  );
};

export function EmotionRadarChart({
  data,
  loading = false,
  title = 'Emotion Analysis',
  description,
  className,
  fillOpacity = 0.6,
}: EmotionRadarChartProps) {
  const isEmpty = !data || data.length === 0;

  // Ensure all data points have fullMark
  const normalizedData = data.map((d) => ({
    ...d,
    fullMark: d.fullMark ?? 1,
  }));

  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No emotion data available"
      className={className}
    >
      <ResponsiveContainer width="100%" height={350}>
        <RadarChart data={normalizedData} cx="50%" cy="50%" outerRadius="80%">
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="emotion"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickFormatter={(value) => value.charAt(0).toUpperCase() + value.slice(1)}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 1]}
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => formatPercentage(value, 0)}
          />
          <Radar
            name="Emotion Score"
            dataKey="value"
            stroke={CHART_COLORS.primary}
            fill={CHART_COLORS.primary}
            fillOpacity={fillOpacity}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}

// Multi-series radar chart for comparing emotions across different data sets
interface MultiEmotionData {
  emotion: string;
  [key: string]: string | number;
}

interface MultiEmotionRadarChartProps {
  data: MultiEmotionData[];
  series: { key: string; name: string; color?: string }[];
  loading?: boolean;
  title?: string;
  description?: string;
  className?: string;
  fillOpacity?: number;
}

export function MultiEmotionRadarChart({
  data,
  series,
  loading = false,
  title = 'Emotion Comparison',
  description,
  className,
  fillOpacity = 0.4,
}: MultiEmotionRadarChartProps) {
  const isEmpty = !data || data.length === 0;

  return (
    <ChartContainer
      title={title}
      description={description}
      loading={loading}
      empty={isEmpty}
      emptyMessage="No emotion data available"
      className={className}
    >
      <ResponsiveContainer width="100%" height={350}>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="80%">
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="emotion"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickFormatter={(value) => value.charAt(0).toUpperCase() + value.slice(1)}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 1]}
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => formatPercentage(value, 0)}
          />
          {series.map((s, index) => (
            <Radar
              key={s.key}
              name={s.name}
              dataKey={s.key}
              stroke={s.color || CHART_COLORS.series[index % CHART_COLORS.series.length]}
              fill={s.color || CHART_COLORS.series[index % CHART_COLORS.series.length]}
              fillOpacity={fillOpacity}
            />
          ))}
          <Tooltip />
          <Legend
            formatter={(value) => (
              <span className="text-sm text-neutral-600">{value}</span>
            )}
          />
        </RadarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
