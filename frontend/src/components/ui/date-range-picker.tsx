'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { Input } from './input';
import { Calendar, ChevronLeft, ChevronRight, X } from 'lucide-react';

interface DateRange {
  start: Date | null;
  end: Date | null;
}

interface DateRangePickerProps {
  value?: DateRange;
  onChange?: (range: DateRange) => void;
  minDate?: Date;
  maxDate?: Date;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function DateRangePicker({
  value,
  onChange,
  minDate,
  maxDate,
  placeholder = 'Select date range',
  className,
  disabled,
}: DateRangePickerProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const [currentMonth, setCurrentMonth] = React.useState(new Date());
  const [selecting, setSelecting] = React.useState<'start' | 'end'>('start');
  const [tempRange, setTempRange] = React.useState<DateRange>(
    value || { start: null, end: null }
  );
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Close on outside click
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatDate = (date: Date | null): string => {
    if (!date) return '';
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const displayValue = React.useMemo(() => {
    if (!value?.start && !value?.end) return '';
    if (value.start && value.end) {
      return `${formatDate(value.start)} - ${formatDate(value.end)}`;
    }
    return formatDate(value.start || value.end);
  }, [value]);

  const handleDateClick = (date: Date) => {
    if (selecting === 'start') {
      setTempRange({ start: date, end: null });
      setSelecting('end');
    } else {
      if (tempRange.start && date < tempRange.start) {
        setTempRange({ start: date, end: tempRange.start });
      } else {
        setTempRange({ ...tempRange, end: date });
      }
      setSelecting('start');
    }
  };

  const handleApply = () => {
    if (tempRange.start && tempRange.end) {
      onChange?.(tempRange);
      setIsOpen(false);
    }
  };

  const handleClear = () => {
    setTempRange({ start: null, end: null });
    onChange?.({ start: null, end: null });
    setSelecting('start');
  };

  const handleQuickSelect = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);
    setTempRange({ start, end });
    onChange?.({ start, end });
    setIsOpen(false);
  };

  const getDaysInMonth = (date: Date): Date[] => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const days: Date[] = [];

    // Add padding for first week
    const startPadding = firstDay.getDay();
    for (let i = startPadding - 1; i >= 0; i--) {
      const d = new Date(year, month, -i);
      days.push(d);
    }

    // Add days of month
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push(new Date(year, month, i));
    }

    // Add padding for last week
    const endPadding = 6 - lastDay.getDay();
    for (let i = 1; i <= endPadding; i++) {
      days.push(new Date(year, month + 1, i));
    }

    return days;
  };

  const isInRange = (date: Date): boolean => {
    if (!tempRange.start || !tempRange.end) return false;
    return date >= tempRange.start && date <= tempRange.end;
  };

  const isSelected = (date: Date): boolean => {
    if (tempRange.start && isSameDay(date, tempRange.start)) return true;
    if (tempRange.end && isSameDay(date, tempRange.end)) return true;
    return false;
  };

  const isSameDay = (d1: Date, d2: Date): boolean => {
    return (
      d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate()
    );
  };

  const isDisabled = (date: Date): boolean => {
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    return false;
  };

  const isCurrentMonth = (date: Date): boolean => {
    return date.getMonth() === currentMonth.getMonth();
  };

  const days = getDaysInMonth(currentMonth);
  const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      <div
        className={cn(
          'flex items-center gap-2 px-3 py-2 border rounded-lg cursor-pointer transition-colors',
          isOpen ? 'border-primary-500 ring-2 ring-primary-100' : 'border-neutral-300',
          disabled && 'cursor-not-allowed opacity-50 bg-neutral-50'
        )}
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        <Calendar className="h-4 w-4 text-neutral-500" />
        <span className={cn('flex-1 text-sm', !displayValue && 'text-neutral-400')}>
          {displayValue || placeholder}
        </span>
        {displayValue && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleClear();
            }}
            className="text-neutral-400 hover:text-neutral-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 bg-white rounded-lg shadow-lg border border-neutral-200 z-50 p-4">
          <div className="flex gap-4">
            {/* Quick select */}
            <div className="border-r pr-4 space-y-1">
              <p className="text-xs font-medium text-neutral-500 mb-2">Quick Select</p>
              {[
                { label: 'Last 7 days', days: 7 },
                { label: 'Last 14 days', days: 14 },
                { label: 'Last 30 days', days: 30 },
                { label: 'Last 90 days', days: 90 },
              ].map((option) => (
                <button
                  key={option.days}
                  onClick={() => handleQuickSelect(option.days)}
                  className="block w-full text-left px-3 py-1.5 text-sm text-neutral-600 hover:bg-neutral-100 rounded"
                >
                  {option.label}
                </button>
              ))}
            </div>

            {/* Calendar */}
            <div>
              {/* Month navigation */}
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={() => setCurrentMonth(new Date(currentMonth.setMonth(currentMonth.getMonth() - 1)))}
                  className="p-1 hover:bg-neutral-100 rounded"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <span className="font-medium">
                  {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </span>
                <button
                  onClick={() => setCurrentMonth(new Date(currentMonth.setMonth(currentMonth.getMonth() + 1)))}
                  className="p-1 hover:bg-neutral-100 rounded"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>

              {/* Week days */}
              <div className="grid grid-cols-7 gap-1 mb-2">
                {weekDays.map((day) => (
                  <div key={day} className="text-center text-xs font-medium text-neutral-500 py-1">
                    {day}
                  </div>
                ))}
              </div>

              {/* Days */}
              <div className="grid grid-cols-7 gap-1">
                {days.map((date, index) => {
                  const disabled = isDisabled(date);
                  const selected = isSelected(date);
                  const inRange = isInRange(date);
                  const currentMonth_ = isCurrentMonth(date);

                  return (
                    <button
                      key={index}
                      onClick={() => !disabled && handleDateClick(date)}
                      disabled={disabled}
                      className={cn(
                        'w-8 h-8 text-sm rounded transition-colors',
                        !currentMonth_ && 'text-neutral-300',
                        currentMonth_ && !selected && !inRange && 'text-neutral-700 hover:bg-neutral-100',
                        inRange && !selected && 'bg-primary-50',
                        selected && 'bg-primary-600 text-white',
                        disabled && 'opacity-50 cursor-not-allowed'
                      )}
                    >
                      {date.getDate()}
                    </button>
                  );
                })}
              </div>

              {/* Selected range display */}
              <div className="mt-4 pt-4 border-t flex items-center justify-between">
                <div className="text-sm">
                  <span className="text-neutral-500">
                    {tempRange.start ? formatDate(tempRange.start) : 'Start'} -{' '}
                    {tempRange.end ? formatDate(tempRange.end) : 'End'}
                  </span>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={handleClear}>
                    Clear
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleApply}
                    disabled={!tempRange.start || !tempRange.end}
                  >
                    Apply
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Simple date input for single date selection
interface DateInputProps {
  value?: Date | null;
  onChange?: (date: Date | null) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  error?: boolean;
}

export function DateInput({
  value,
  onChange,
  placeholder = 'Select date',
  className,
  disabled,
  error,
}: DateInputProps) {
  const formatForInput = (date: Date | null): string => {
    if (!date) return '';
    return date.toISOString().split('T')[0];
  };

  return (
    <Input
      type="date"
      value={formatForInput(value || null)}
      onChange={(e) => {
        const val = e.target.value;
        onChange?.(val ? new Date(val) : null);
      }}
      placeholder={placeholder}
      className={className}
      disabled={disabled}
      error={error}
    />
  );
}
