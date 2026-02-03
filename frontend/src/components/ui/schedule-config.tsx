'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Select } from './select';
import { Input } from './input';
import { Label } from './label';
import { Checkbox } from './checkbox';
import { Switch } from './switch';
import { Clock, Calendar, RefreshCw } from 'lucide-react';

export interface ScheduleValue {
  frequency: 'hourly' | 'daily' | 'weekly' | 'monthly';
  time?: string; // HH:MM format
  days?: number[]; // 0-6 for weekly (Sun-Sat), 1-31 for monthly
  enabled: boolean;
}

interface ScheduleConfigProps {
  value: ScheduleValue;
  onChange: (value: ScheduleValue) => void;
  className?: string;
  disabled?: boolean;
}

const FREQUENCY_OPTIONS = [
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

const WEEKDAYS = [
  { value: 0, label: 'Sun' },
  { value: 1, label: 'Mon' },
  { value: 2, label: 'Tue' },
  { value: 3, label: 'Wed' },
  { value: 4, label: 'Thu' },
  { value: 5, label: 'Fri' },
  { value: 6, label: 'Sat' },
];

export function ScheduleConfig({
  value,
  onChange,
  className,
  disabled,
}: ScheduleConfigProps) {
  const handleFrequencyChange = (frequency: string) => {
    const newValue: ScheduleValue = {
      ...value,
      frequency: frequency as ScheduleValue['frequency'],
    };

    // Reset days when frequency changes
    if (frequency === 'weekly') {
      newValue.days = [1]; // Default to Monday
    } else if (frequency === 'monthly') {
      newValue.days = [1]; // Default to 1st of month
    } else {
      newValue.days = undefined;
    }

    // Set default time for non-hourly frequencies
    if (frequency !== 'hourly' && !newValue.time) {
      newValue.time = '09:00';
    }

    onChange(newValue);
  };

  const handleTimeChange = (time: string) => {
    onChange({ ...value, time });
  };

  const handleDayToggle = (day: number) => {
    const currentDays = value.days || [];
    const newDays = currentDays.includes(day)
      ? currentDays.filter((d) => d !== day)
      : [...currentDays, day].sort((a, b) => a - b);

    // Ensure at least one day is selected
    if (newDays.length === 0) return;

    onChange({ ...value, days: newDays });
  };

  const handleMonthDayChange = (dayStr: string) => {
    const day = parseInt(dayStr, 10);
    if (day >= 1 && day <= 31) {
      onChange({ ...value, days: [day] });
    }
  };

  const handleEnabledChange = (enabled: boolean) => {
    onChange({ ...value, enabled });
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Enable/Disable Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4 text-neutral-500" />
          <Label>Enable Schedule</Label>
        </div>
        <Switch
          checked={value.enabled}
          onCheckedChange={handleEnabledChange}
          disabled={disabled}
        />
      </div>

      <div className={cn(!value.enabled && 'opacity-50 pointer-events-none')}>
        {/* Frequency Selection */}
        <div className="space-y-2">
          <Label htmlFor="frequency">
            <Calendar className="inline h-4 w-4 mr-1" />
            Frequency
          </Label>
          <Select
            value={value.frequency}
            onChange={(e) => handleFrequencyChange(e.target.value)}
            options={FREQUENCY_OPTIONS}
            disabled={disabled || !value.enabled}
          />
        </div>

        {/* Time Selection (for non-hourly) */}
        {value.frequency !== 'hourly' && (
          <div className="space-y-2 mt-4">
            <Label htmlFor="time">
              <Clock className="inline h-4 w-4 mr-1" />
              Time
            </Label>
            <Input
              type="time"
              value={value.time || '09:00'}
              onChange={(e) => handleTimeChange(e.target.value)}
              disabled={disabled || !value.enabled}
            />
          </div>
        )}

        {/* Day Selection (for weekly) */}
        {value.frequency === 'weekly' && (
          <div className="space-y-2 mt-4">
            <Label>Days of Week</Label>
            <div className="flex gap-1">
              {WEEKDAYS.map((day) => (
                <button
                  key={day.value}
                  type="button"
                  onClick={() => handleDayToggle(day.value)}
                  disabled={disabled || !value.enabled}
                  className={cn(
                    'flex h-10 w-10 items-center justify-center rounded-lg text-sm font-medium transition-colors',
                    (value.days || []).includes(day.value)
                      ? 'bg-primary-600 text-white'
                      : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200',
                    (disabled || !value.enabled) && 'cursor-not-allowed opacity-50'
                  )}
                >
                  {day.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Day of Month Selection (for monthly) */}
        {value.frequency === 'monthly' && (
          <div className="space-y-2 mt-4">
            <Label htmlFor="monthDay">Day of Month</Label>
            <Select
              value={String(value.days?.[0] || 1)}
              onChange={(e) => handleMonthDayChange(e.target.value)}
              options={Array.from({ length: 31 }, (_, i) => ({
                value: String(i + 1),
                label: getOrdinal(i + 1),
              }))}
              disabled={disabled || !value.enabled}
            />
          </div>
        )}

        {/* Summary */}
        <div className="mt-4 p-3 bg-neutral-50 rounded-lg">
          <p className="text-sm text-neutral-600">
            <span className="font-medium">Schedule:</span>{' '}
            {getScheduleSummary(value)}
          </p>
        </div>
      </div>
    </div>
  );
}

// Helper function to get ordinal suffix
function getOrdinal(n: number): string {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

// Helper function to generate schedule summary
function getScheduleSummary(value: ScheduleValue): string {
  if (!value.enabled) {
    return 'Disabled';
  }

  const time = value.time || '09:00';
  const [hours, minutes] = time.split(':');
  const hour = parseInt(hours, 10);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const hour12 = hour % 12 || 12;
  const timeStr = `${hour12}:${minutes} ${ampm}`;

  switch (value.frequency) {
    case 'hourly':
      return 'Every hour';
    case 'daily':
      return `Daily at ${timeStr}`;
    case 'weekly': {
      const days = (value.days || [1])
        .map((d) => WEEKDAYS.find((w) => w.value === d)?.label)
        .join(', ');
      return `Weekly on ${days} at ${timeStr}`;
    }
    case 'monthly': {
      const day = value.days?.[0] || 1;
      return `Monthly on the ${getOrdinal(day)} at ${timeStr}`;
    }
    default:
      return 'Unknown schedule';
  }
}

// Compact version for inline display
interface ScheduleDisplayProps {
  value: ScheduleValue;
  className?: string;
}

export function ScheduleDisplay({ value, className }: ScheduleDisplayProps) {
  return (
    <div className={cn('flex items-center gap-2 text-sm', className)}>
      <RefreshCw
        className={cn(
          'h-4 w-4',
          value.enabled ? 'text-success-600' : 'text-neutral-400'
        )}
      />
      <span className={cn(value.enabled ? 'text-neutral-700' : 'text-neutral-400')}>
        {getScheduleSummary(value)}
      </span>
    </div>
  );
}
