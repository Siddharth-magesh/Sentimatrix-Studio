'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface RadioOption {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
}

interface RadioGroupProps {
  name: string;
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  orientation?: 'horizontal' | 'vertical';
  className?: string;
  error?: boolean;
}

export function RadioGroup({
  name,
  options,
  value,
  onChange,
  orientation = 'vertical',
  className,
  error,
}: RadioGroupProps) {
  return (
    <div
      className={cn(
        'flex gap-3',
        orientation === 'vertical' ? 'flex-col' : 'flex-row flex-wrap',
        className
      )}
      role="radiogroup"
    >
      {options.map((option) => (
        <Radio
          key={option.value}
          name={name}
          value={option.value}
          label={option.label}
          description={option.description}
          checked={value === option.value}
          onChange={() => onChange?.(option.value)}
          disabled={option.disabled}
          error={error}
        />
      ))}
    </div>
  );
}

interface RadioProps {
  name: string;
  value: string;
  label: string;
  description?: string;
  checked?: boolean;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  error?: boolean;
  className?: string;
}

export const Radio = React.forwardRef<HTMLInputElement, RadioProps>(
  ({ name, value, label, description, checked, onChange, disabled, error, className }, ref) => {
    const id = `${name}-${value}`;

    return (
      <label
        htmlFor={id}
        className={cn(
          'flex items-start gap-3 cursor-pointer',
          disabled && 'cursor-not-allowed opacity-50',
          className
        )}
      >
        <div className="flex items-center h-5">
          <input
            ref={ref}
            type="radio"
            id={id}
            name={name}
            value={value}
            checked={checked}
            onChange={onChange}
            disabled={disabled}
            className={cn(
              'h-4 w-4 border-2 text-primary-600 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              error ? 'border-error-500' : 'border-neutral-300',
              disabled && 'cursor-not-allowed'
            )}
          />
        </div>
        <div className="flex flex-col">
          <span
            className={cn(
              'text-sm font-medium',
              error ? 'text-error-700' : 'text-neutral-900'
            )}
          >
            {label}
          </span>
          {description && (
            <span className="text-sm text-neutral-500">{description}</span>
          )}
        </div>
      </label>
    );
  }
);

Radio.displayName = 'Radio';

// Card-style radio for more prominent selections
interface RadioCardProps {
  name: string;
  value: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
  checked?: boolean;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  className?: string;
}

export function RadioCard({
  name,
  value,
  label,
  description,
  icon,
  checked,
  onChange,
  disabled,
  className,
}: RadioCardProps) {
  const id = `${name}-${value}`;

  return (
    <label
      htmlFor={id}
      className={cn(
        'relative flex cursor-pointer rounded-lg border p-4 transition-colors',
        checked
          ? 'border-primary-600 bg-primary-50 ring-2 ring-primary-600'
          : 'border-neutral-200 hover:border-neutral-300',
        disabled && 'cursor-not-allowed opacity-50',
        className
      )}
    >
      <input
        type="radio"
        id={id}
        name={name}
        value={value}
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="sr-only"
      />
      <div className="flex items-start gap-3">
        {icon && (
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-lg',
              checked ? 'bg-primary-100 text-primary-600' : 'bg-neutral-100 text-neutral-600'
            )}
          >
            {icon}
          </div>
        )}
        <div className="flex flex-col">
          <span
            className={cn(
              'text-sm font-medium',
              checked ? 'text-primary-900' : 'text-neutral-900'
            )}
          >
            {label}
          </span>
          {description && (
            <span className="text-sm text-neutral-500">{description}</span>
          )}
        </div>
      </div>
      {checked && (
        <div className="absolute top-4 right-4">
          <svg
            className="h-5 w-5 text-primary-600"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      )}
    </label>
  );
}

interface RadioCardGroupProps {
  name: string;
  options: (RadioOption & { icon?: React.ReactNode })[];
  value?: string;
  onChange?: (value: string) => void;
  columns?: 1 | 2 | 3 | 4;
  className?: string;
}

export function RadioCardGroup({
  name,
  options,
  value,
  onChange,
  columns = 2,
  className,
}: RadioCardGroupProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={cn('grid gap-3', gridCols[columns], className)} role="radiogroup">
      {options.map((option) => (
        <RadioCard
          key={option.value}
          name={name}
          value={option.value}
          label={option.label}
          description={option.description}
          icon={option.icon}
          checked={value === option.value}
          onChange={() => onChange?.(option.value)}
          disabled={option.disabled}
        />
      ))}
    </div>
  );
}
