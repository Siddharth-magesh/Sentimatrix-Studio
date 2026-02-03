import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

export interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'outline';
  size?: 'sm' | 'md';
  className?: string;
}

const variantClasses = {
  default: 'bg-neutral-100 text-neutral-700',
  primary: 'bg-primary-100 text-primary-700',
  success: 'bg-success-100 text-success-700',
  warning: 'bg-warning-100 text-warning-700',
  error: 'bg-error-100 text-error-700',
  outline: 'border border-neutral-300 text-neutral-700 bg-transparent',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
};

export function Badge({ children, variant = 'default', size = 'sm', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
}

// Status Badge with dot indicator
export interface StatusBadgeProps {
  status: 'active' | 'paused' | 'completed' | 'failed' | 'pending' | 'running' | 'cancelled' | 'archived';
  className?: string;
}

const statusConfig: Record<string, { label: string; variant: BadgeProps['variant']; dotColor: string }> = {
  active: { label: 'Active', variant: 'success', dotColor: 'bg-success-500' },
  running: { label: 'Running', variant: 'primary', dotColor: 'bg-primary-500' },
  pending: { label: 'Pending', variant: 'warning', dotColor: 'bg-warning-500' },
  completed: { label: 'Completed', variant: 'success', dotColor: 'bg-success-500' },
  failed: { label: 'Failed', variant: 'error', dotColor: 'bg-error-500' },
  cancelled: { label: 'Cancelled', variant: 'default', dotColor: 'bg-neutral-400' },
  paused: { label: 'Paused', variant: 'warning', dotColor: 'bg-warning-500' },
  archived: { label: 'Archived', variant: 'default', dotColor: 'bg-neutral-400' },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending;

  return (
    <Badge variant={config.variant} className={cn('gap-1.5', className)}>
      <span className={cn('h-1.5 w-1.5 rounded-full', config.dotColor)} />
      {config.label}
    </Badge>
  );
}

// Sentiment Badge
export interface SentimentBadgeProps {
  sentiment: 'positive' | 'negative' | 'neutral' | 'mixed';
  score?: number;
  className?: string;
}

const sentimentConfig: Record<string, { variant: BadgeProps['variant'] }> = {
  positive: { variant: 'success' },
  negative: { variant: 'error' },
  neutral: { variant: 'default' },
  mixed: { variant: 'warning' },
};

export function SentimentBadge({ sentiment, score, className }: SentimentBadgeProps) {
  const config = sentimentConfig[sentiment] || sentimentConfig.neutral;
  const label = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);

  return (
    <Badge variant={config.variant} className={className}>
      {label}
      {score !== undefined && ` (${Math.round(score * 100)}%)`}
    </Badge>
  );
}
