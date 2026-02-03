import { cn } from '@/lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

function Spinner({ size = 'md', className }: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  };

  return (
    <svg
      className={cn('animate-spin text-primary-600', sizes[size], className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

interface LoadingOverlayProps {
  isLoading: boolean;
  children: React.ReactNode;
  text?: string;
  blur?: boolean;
  className?: string;
}

function LoadingOverlay({
  isLoading,
  children,
  text,
  blur = true,
  className,
}: LoadingOverlayProps) {
  return (
    <div className={cn('relative', className)}>
      {children}
      {isLoading && (
        <div
          className={cn(
            'absolute inset-0 flex flex-col items-center justify-center bg-white/80 z-50',
            blur && 'backdrop-blur-sm'
          )}
        >
          <Spinner size="lg" />
          {text && (
            <p className="mt-3 text-sm text-neutral-600 font-medium">{text}</p>
          )}
        </div>
      )}
    </div>
  );
}

interface PageLoaderProps {
  text?: string;
}

function PageLoader({ text = 'Loading...' }: PageLoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <Spinner size="xl" />
      <p className="mt-4 text-neutral-600">{text}</p>
    </div>
  );
}

interface InlineLoaderProps {
  text?: string;
  size?: 'sm' | 'md';
}

function InlineLoader({ text, size = 'sm' }: InlineLoaderProps) {
  return (
    <div className="flex items-center gap-2">
      <Spinner size={size} />
      {text && <span className="text-sm text-neutral-600">{text}</span>}
    </div>
  );
}

export { Spinner, LoadingOverlay, PageLoader, InlineLoader };
