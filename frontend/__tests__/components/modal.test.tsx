import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal, ConfirmModal, ModalFooter } from '@/components/ui/modal';

describe('Modal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    children: <div>Modal content</div>,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders when isOpen is true', () => {
    render(<Modal {...defaultProps} />);
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(<Modal {...defaultProps} isOpen={false} />);
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('displays title when provided', () => {
    render(<Modal {...defaultProps} title="Test Modal" />);
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
  });

  it('displays description when provided', () => {
    render(
      <Modal {...defaultProps} title="Title" description="Modal description" />
    );
    expect(screen.getByText('Modal description')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const handleClose = jest.fn();
    render(<Modal {...defaultProps} title="Test" onClose={handleClose} />);

    const closeButton = screen.getByRole('button');
    await userEvent.click(closeButton);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay is clicked by default', async () => {
    const handleClose = jest.fn();
    render(<Modal {...defaultProps} onClose={handleClose} />);

    // Click on the overlay (the backdrop)
    const overlay = document.querySelector('.bg-black\\/50');
    if (overlay) {
      await userEvent.click(overlay);
    }

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose when overlay clicked and closeOnOverlayClick is false', async () => {
    const handleClose = jest.fn();
    render(
      <Modal {...defaultProps} onClose={handleClose} closeOnOverlayClick={false} />
    );

    const overlay = document.querySelector('.bg-black\\/50');
    if (overlay) {
      await userEvent.click(overlay);
    }

    expect(handleClose).not.toHaveBeenCalled();
  });

  it('does not close when clicking inside modal content', async () => {
    const handleClose = jest.fn();
    render(<Modal {...defaultProps} onClose={handleClose} />);

    await userEvent.click(screen.getByText('Modal content'));

    expect(handleClose).not.toHaveBeenCalled();
  });

  it('hides close button when showCloseButton is false', () => {
    render(<Modal {...defaultProps} title="Test" showCloseButton={false} />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('applies different size classes', () => {
    const { rerender, container } = render(<Modal {...defaultProps} size="sm" />);
    expect(container.querySelector('.max-w-sm')).toBeInTheDocument();

    rerender(<Modal {...defaultProps} size="lg" />);
    expect(container.querySelector('.max-w-lg')).toBeInTheDocument();

    rerender(<Modal {...defaultProps} size="xl" />);
    expect(container.querySelector('.max-w-xl')).toBeInTheDocument();

    rerender(<Modal {...defaultProps} size="full" />);
    expect(container.querySelector('.max-w-4xl')).toBeInTheDocument();
  });
});

describe('ConfirmModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    onConfirm: jest.fn(),
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with title and message', () => {
    render(<ConfirmModal {...defaultProps} />);

    expect(screen.getByText('Confirm Action')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument();
  });

  it('displays default button text', () => {
    render(<ConfirmModal {...defaultProps} />);

    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirm' })).toBeInTheDocument();
  });

  it('displays custom button text', () => {
    render(
      <ConfirmModal
        {...defaultProps}
        confirmText="Delete"
        cancelText="Keep"
      />
    );

    expect(screen.getByRole('button', { name: 'Keep' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
  });

  it('calls onClose when cancel button is clicked', async () => {
    const handleClose = jest.fn();
    render(<ConfirmModal {...defaultProps} onClose={handleClose} />);

    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('calls onConfirm when confirm button is clicked', async () => {
    const handleConfirm = jest.fn();
    render(<ConfirmModal {...defaultProps} onConfirm={handleConfirm} />);

    await userEvent.click(screen.getByRole('button', { name: 'Confirm' }));

    expect(handleConfirm).toHaveBeenCalledTimes(1);
  });

  it('disables buttons when isLoading is true', () => {
    render(<ConfirmModal {...defaultProps} isLoading />);

    expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
    // Confirm button shows loading spinner
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    expect(confirmButton).toBeDisabled();
  });

  it('does not render when isOpen is false', () => {
    render(<ConfirmModal {...defaultProps} isOpen={false} />);

    expect(screen.queryByText('Confirm Action')).not.toBeInTheDocument();
  });
});

describe('ModalFooter', () => {
  it('renders children correctly', () => {
    render(
      <ModalFooter>
        <button>Action 1</button>
        <button>Action 2</button>
      </ModalFooter>
    );

    expect(screen.getByRole('button', { name: 'Action 1' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Action 2' })).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <ModalFooter className="custom-class">
        <button>Action</button>
      </ModalFooter>
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('applies default styling', () => {
    const { container } = render(
      <ModalFooter>
        <button>Action</button>
      </ModalFooter>
    );

    expect(container.firstChild).toHaveClass('flex');
    expect(container.firstChild).toHaveClass('justify-end');
    expect(container.firstChild).toHaveClass('gap-3');
  });
});
