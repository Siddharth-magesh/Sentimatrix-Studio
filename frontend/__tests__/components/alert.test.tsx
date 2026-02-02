import { render, screen } from '@testing-library/react';
import { Alert } from '@/components/ui/alert';

describe('Alert', () => {
  it('renders with default info variant', () => {
    render(<Alert>Info message</Alert>);
    expect(screen.getByRole('alert')).toHaveClass('bg-primary-50');
  });

  it('renders success variant', () => {
    render(<Alert variant="success">Success message</Alert>);
    expect(screen.getByRole('alert')).toHaveClass('bg-success-50');
  });

  it('renders warning variant', () => {
    render(<Alert variant="warning">Warning message</Alert>);
    expect(screen.getByRole('alert')).toHaveClass('bg-warning-50');
  });

  it('renders error variant', () => {
    render(<Alert variant="error">Error message</Alert>);
    expect(screen.getByRole('alert')).toHaveClass('bg-error-50');
  });

  it('renders children content', () => {
    render(<Alert>Custom alert content</Alert>);
    expect(screen.getByText('Custom alert content')).toBeInTheDocument();
  });
});
