import { forwardRef, LabelHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

const Label = forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, required, children, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn('text-sm font-medium text-neutral-700', className)}
        {...props}
      >
        {children}
        {required && <span className="ml-1 text-error-500">*</span>}
      </label>
    );
  }
);

Label.displayName = 'Label';

export { Label };
