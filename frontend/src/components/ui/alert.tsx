import { forwardRef, HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
}

const icons = {
  info: Info,
  success: CheckCircle,
  warning: AlertCircle,
  error: XCircle,
};

const variants = {
  info: 'bg-primary-50 border-primary-200 text-primary-800',
  success: 'bg-success-50 border-success-500/20 text-success-600',
  warning: 'bg-warning-50 border-warning-500/20 text-warning-600',
  error: 'bg-error-50 border-error-500/20 text-error-600',
};

const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'info', children, ...props }, ref) => {
    const Icon = icons[variant];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          'flex items-start gap-3 rounded-lg border p-4',
          variants[variant],
          className
        )}
        {...props}
      >
        <Icon className="h-5 w-5 flex-shrink-0" />
        <div className="text-sm">{children}</div>
      </div>
    );
  }
);

Alert.displayName = 'Alert';

export { Alert };
