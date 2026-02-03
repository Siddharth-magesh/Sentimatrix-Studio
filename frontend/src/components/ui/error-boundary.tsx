'use client';

import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './button';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorDisplay
          error={this.state.error}
          onRetry={this.handleRetry}
        />
      );
    }

    return this.props.children;
  }
}

interface ErrorDisplayProps {
  error?: Error | null;
  title?: string;
  message?: string;
  onRetry?: () => void;
  showDetails?: boolean;
}

function ErrorDisplay({
  error,
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  onRetry,
  showDetails = false,
}: ErrorDisplayProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] p-8 text-center">
      <div className="w-16 h-16 rounded-full bg-error-100 flex items-center justify-center mb-4">
        <AlertTriangle className="w-8 h-8 text-error-600" />
      </div>
      <h3 className="text-lg font-semibold text-neutral-900 mb-2">{title}</h3>
      <p className="text-neutral-600 mb-6 max-w-md">{message}</p>
      {showDetails && error && (
        <pre className="text-left text-xs bg-neutral-100 p-4 rounded-lg mb-6 max-w-full overflow-auto">
          {error.message}
          {error.stack && (
            <>
              {'\n\n'}
              {error.stack}
            </>
          )}
        </pre>
      )}
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Try again
        </Button>
      )}
    </div>
  );
}

interface ErrorAlertProps {
  error: string | Error | null;
  title?: string;
  onDismiss?: () => void;
  className?: string;
}

function ErrorAlert({ error, title, onDismiss, className }: ErrorAlertProps) {
  if (!error) return null;

  const errorMessage = typeof error === 'string' ? error : error.message;

  return (
    <div
      className={`rounded-lg border border-error-200 bg-error-50 p-4 ${className}`}
      role="alert"
    >
      <div className="flex items-start">
        <AlertTriangle className="w-5 h-5 text-error-600 mt-0.5" />
        <div className="ml-3 flex-1">
          {title && (
            <h4 className="text-sm font-medium text-error-800">{title}</h4>
          )}
          <p className="text-sm text-error-700 mt-1">{errorMessage}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="ml-3 text-error-600 hover:text-error-800"
            aria-label="Dismiss"
          >
            <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

interface ApiErrorProps {
  status?: number;
  message?: string;
  onRetry?: () => void;
}

function ApiError({ status, message, onRetry }: ApiErrorProps) {
  const getErrorInfo = () => {
    switch (status) {
      case 400:
        return { title: 'Bad Request', message: message || 'The request was invalid.' };
      case 401:
        return { title: 'Unauthorized', message: 'Please log in to continue.' };
      case 403:
        return { title: 'Forbidden', message: 'You don\'t have permission to access this resource.' };
      case 404:
        return { title: 'Not Found', message: message || 'The requested resource was not found.' };
      case 429:
        return { title: 'Too Many Requests', message: 'Please slow down and try again later.' };
      case 500:
        return { title: 'Server Error', message: 'Something went wrong on our end. Please try again.' };
      case 503:
        return { title: 'Service Unavailable', message: 'The service is temporarily unavailable.' };
      default:
        return { title: 'Error', message: message || 'An unexpected error occurred.' };
    }
  };

  const errorInfo = getErrorInfo();

  return (
    <ErrorDisplay
      title={errorInfo.title}
      message={errorInfo.message}
      onRetry={onRetry}
    />
  );
}

export { ErrorBoundary, ErrorDisplay, ErrorAlert, ApiError };
