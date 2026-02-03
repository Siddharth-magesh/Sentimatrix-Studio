import { render, screen } from '@testing-library/react';
import { Spinner, LoadingOverlay, PageLoader, InlineLoader } from '@/components/ui/spinner';

describe('Spinner', () => {
  it('renders with default size', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('h-6', 'w-6'); // md is default
  });

  it('renders with sm size', () => {
    const { container } = render(<Spinner size="sm" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-4', 'w-4');
  });

  it('renders with lg size', () => {
    const { container } = render(<Spinner size="lg" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-8', 'w-8');
  });

  it('renders with xl size', () => {
    const { container } = render(<Spinner size="xl" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-12', 'w-12');
  });

  it('applies animate-spin class', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('animate-spin');
  });

  it('applies custom className', () => {
    const { container } = render(<Spinner className="custom-spinner" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('custom-spinner');
  });
});

describe('LoadingOverlay', () => {
  it('renders children always', () => {
    render(
      <LoadingOverlay isLoading={false}>
        <div>Content</div>
      </LoadingOverlay>
    );
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('shows overlay when isLoading is true', () => {
    render(
      <LoadingOverlay isLoading={true}>
        <div>Content</div>
      </LoadingOverlay>
    );

    // Content should still be visible
    expect(screen.getByText('Content')).toBeInTheDocument();
    // Spinner should be visible
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('hides overlay when isLoading is false', () => {
    render(
      <LoadingOverlay isLoading={false}>
        <div>Content</div>
      </LoadingOverlay>
    );

    const spinner = document.querySelector('.animate-spin');
    expect(spinner).not.toBeInTheDocument();
  });

  it('displays loading text when provided', () => {
    render(
      <LoadingOverlay isLoading={true} text="Please wait...">
        <div>Content</div>
      </LoadingOverlay>
    );

    expect(screen.getByText('Please wait...')).toBeInTheDocument();
  });

  it('applies blur effect by default', () => {
    const { container } = render(
      <LoadingOverlay isLoading={true}>
        <div>Content</div>
      </LoadingOverlay>
    );

    const overlay = container.querySelector('.backdrop-blur-sm');
    expect(overlay).toBeInTheDocument();
  });

  it('removes blur effect when blur is false', () => {
    const { container } = render(
      <LoadingOverlay isLoading={true} blur={false}>
        <div>Content</div>
      </LoadingOverlay>
    );

    const overlay = container.querySelector('.backdrop-blur-sm');
    expect(overlay).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <LoadingOverlay isLoading={false} className="custom-overlay">
        <div>Content</div>
      </LoadingOverlay>
    );

    expect(container.firstChild).toHaveClass('custom-overlay');
  });
});

describe('PageLoader', () => {
  it('renders with default text', () => {
    render(<PageLoader />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders with custom text', () => {
    render(<PageLoader text="Fetching data..." />);
    expect(screen.getByText('Fetching data...')).toBeInTheDocument();
  });

  it('renders spinner with xl size', () => {
    const { container } = render(<PageLoader />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-12', 'w-12');
  });

  it('has minimum height styling', () => {
    const { container } = render(<PageLoader />);
    expect(container.firstChild).toHaveClass('min-h-[400px]');
  });

  it('centers content', () => {
    const { container } = render(<PageLoader />);
    expect(container.firstChild).toHaveClass('flex', 'items-center', 'justify-center');
  });
});

describe('InlineLoader', () => {
  it('renders spinner without text by default', () => {
    const { container } = render(<InlineLoader />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(screen.queryByRole('paragraph')).not.toBeInTheDocument();
  });

  it('renders with text when provided', () => {
    render(<InlineLoader text="Loading items..." />);
    expect(screen.getByText('Loading items...')).toBeInTheDocument();
  });

  it('renders with sm size by default', () => {
    const { container } = render(<InlineLoader />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-4', 'w-4');
  });

  it('renders with md size when specified', () => {
    const { container } = render(<InlineLoader size="md" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-6', 'w-6');
  });

  it('displays text with proper styling', () => {
    render(<InlineLoader text="Loading..." />);
    const text = screen.getByText('Loading...');
    expect(text).toHaveClass('text-sm', 'text-neutral-600');
  });

  it('uses flex layout with gap', () => {
    const { container } = render(<InlineLoader text="Loading..." />);
    expect(container.firstChild).toHaveClass('flex', 'items-center', 'gap-2');
  });
});
