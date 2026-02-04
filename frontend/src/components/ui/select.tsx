'use client';

import { forwardRef, SelectHTMLAttributes, useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, Check, X } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: SelectOption[];
  placeholder?: string;
  error?: boolean;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, options, placeholder = 'Select...', error, value, disabled, ...props }, ref) => {
    return (
      <div className="relative">
        <select
          ref={ref}
          value={value}
          disabled={disabled}
          className={cn(
            'flex h-10 w-full appearance-none rounded-lg border bg-white px-3 py-2 pr-10 text-sm',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error ? 'border-error-500' : 'border-neutral-300',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value} disabled={option.disabled}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500 pointer-events-none" />
      </div>
    );
  }
);

Select.displayName = 'Select';

// Multi-select component
export interface MultiSelectProps {
  options: SelectOption[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  error?: boolean;
  disabled?: boolean;
  className?: string;
  searchable?: boolean;
}

export function MultiSelect({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  error,
  disabled,
  className,
  searchable = false,
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = searchable
    ? options.filter((opt) => opt.label.toLowerCase().includes(search.toLowerCase()))
    : options;

  const toggleOption = (optionValue: string) => {
    if (value.includes(optionValue)) {
      onChange(value.filter((v) => v !== optionValue));
    } else {
      onChange([...value, optionValue]);
    }
  };

  const removeOption = (optionValue: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(value.filter((v) => v !== optionValue));
  };

  const selectedLabels = value
    .map((v) => options.find((opt) => opt.value === v)?.label)
    .filter(Boolean);

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      <div
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={cn(
          'flex min-h-10 w-full flex-wrap items-center gap-1 rounded-lg border bg-white px-3 py-2 text-sm cursor-pointer',
          'focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-transparent',
          disabled && 'cursor-not-allowed opacity-50',
          error ? 'border-error-500' : 'border-neutral-300'
        )}
      >
        {value.length === 0 ? (
          <span className="text-neutral-500">{placeholder}</span>
        ) : (
          selectedLabels.map((label, index) => (
            <span
              key={value[index]}
              className="inline-flex items-center gap-1 rounded-md bg-primary-100 px-2 py-0.5 text-xs text-primary-700"
            >
              {label}
              <X
                className="h-3 w-3 cursor-pointer hover:text-primary-900"
                onClick={(e) => removeOption(value[index], e)}
              />
            </span>
          ))
        )}
        <ChevronDown className="ml-auto h-4 w-4 text-neutral-500" />
      </div>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border border-neutral-200 bg-white shadow-lg">
          {searchable && (
            <div className="border-b border-neutral-200 p-2">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search..."
                className="w-full rounded-md border border-neutral-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          )}
          <div className="max-h-60 overflow-auto p-1">
            {filteredOptions.length === 0 ? (
              <div className="px-3 py-2 text-sm text-neutral-500">No options found</div>
            ) : (
              filteredOptions.map((option) => (
                <div
                  key={option.value}
                  onClick={() => !option.disabled && toggleOption(option.value)}
                  className={cn(
                    'flex items-center gap-2 rounded-md px-3 py-2 text-sm cursor-pointer',
                    option.disabled && 'cursor-not-allowed opacity-50',
                    value.includes(option.value)
                      ? 'bg-primary-50 text-primary-700'
                      : 'hover:bg-neutral-100'
                  )}
                >
                  <div
                    className={cn(
                      'flex h-4 w-4 items-center justify-center rounded border',
                      value.includes(option.value)
                        ? 'border-primary-600 bg-primary-600'
                        : 'border-neutral-300'
                    )}
                  >
                    {value.includes(option.value) && <Check className="h-3 w-3 text-white" />}
                  </div>
                  {option.label}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export { Select };
