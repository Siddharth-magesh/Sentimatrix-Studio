import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableRow,
  TableHead,
  TableCell,
  TableCaption,
  TableEmpty,
  TableLoading,
} from '@/components/ui/table';

describe('Table', () => {
  it('renders table with all parts', () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>John Doe</TableCell>
            <TableCell>john@example.com</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('applies custom className to Table', () => {
    const { container } = render(
      <Table className="custom-table">
        <TableBody>
          <TableRow>
            <TableCell>Cell</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(container.firstChild).toHaveClass('custom-table');
  });
});

describe('TableHeader', () => {
  it('renders header with correct styling', () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Header</TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );

    const thead = screen.getByRole('rowgroup');
    expect(thead.tagName).toBe('THEAD');
  });
});

describe('TableRow', () => {
  it('renders row with children', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Content</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('row')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('handles onClick event', async () => {
    const handleClick = jest.fn();
    render(
      <Table>
        <TableBody>
          <TableRow onClick={handleClick}>
            <TableCell>Clickable Row</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    await userEvent.click(screen.getByRole('row'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies cursor-pointer when onClick is provided', () => {
    render(
      <Table>
        <TableBody>
          <TableRow onClick={() => {}}>
            <TableCell>Row</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('row')).toHaveClass('cursor-pointer');
  });

  it('applies selected styling when selected is true', () => {
    render(
      <Table>
        <TableBody>
          <TableRow selected>
            <TableCell>Selected Row</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('row')).toHaveClass('bg-primary-50');
  });
});

describe('TableHead', () => {
  it('renders sortable header with sort icons', () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead sortable>Sortable Column</TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );

    expect(screen.getByText('Sortable Column')).toBeInTheDocument();
    // Should have sort icon (ChevronsUpDown by default)
    expect(screen.getByRole('columnheader')).toHaveClass('cursor-pointer');
  });

  it('shows ascending sort icon when sortDirection is asc', () => {
    const { container } = render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead sortable sortDirection="asc">
              Ascending
            </TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );

    // ChevronUp should be rendered
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('shows descending sort icon when sortDirection is desc', () => {
    const { container } = render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead sortable sortDirection="desc">
              Descending
            </TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );

    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('calls onSort when sortable header is clicked', async () => {
    const handleSort = jest.fn();
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead sortable onSort={handleSort}>
              Sort Me
            </TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );

    await userEvent.click(screen.getByText('Sort Me'));
    expect(handleSort).toHaveBeenCalledTimes(1);
  });

  it('does not call onSort when non-sortable header is clicked', async () => {
    const handleSort = jest.fn();
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead onSort={handleSort}>Not Sortable</TableHead>
          </TableRow>
        </TableHeader>
      </Table>
    );

    await userEvent.click(screen.getByText('Not Sortable'));
    expect(handleSort).not.toHaveBeenCalled();
  });
});

describe('TableCell', () => {
  it('renders cell with children', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>Cell Content</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('cell')).toBeInTheDocument();
    expect(screen.getByText('Cell Content')).toBeInTheDocument();
  });

  it('applies colSpan when provided', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell colSpan={3}>Spanning Cell</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('cell')).toHaveAttribute('colspan', '3');
  });

  it('applies custom className', () => {
    render(
      <Table>
        <TableBody>
          <TableRow>
            <TableCell className="custom-cell">Cell</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('cell')).toHaveClass('custom-cell');
  });
});

describe('TableFooter', () => {
  it('renders footer with styling', () => {
    render(
      <Table>
        <TableFooter>
          <TableRow>
            <TableCell>Footer Content</TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    );

    const tfoot = document.querySelector('tfoot');
    expect(tfoot).toBeInTheDocument();
    expect(tfoot).toHaveClass('bg-neutral-50');
  });
});

describe('TableCaption', () => {
  it('renders caption with text', () => {
    render(
      <Table>
        <TableCaption>Table caption text</TableCaption>
        <TableBody>
          <TableRow>
            <TableCell>Cell</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByText('Table caption text')).toBeInTheDocument();
  });
});

describe('TableEmpty', () => {
  it('renders default empty message', () => {
    render(
      <Table>
        <TableBody>
          <TableEmpty colSpan={3} />
        </TableBody>
      </Table>
    );

    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  it('renders custom empty message', () => {
    render(
      <Table>
        <TableBody>
          <TableEmpty colSpan={3} message="No items found" />
        </TableBody>
      </Table>
    );

    expect(screen.getByText('No items found')).toBeInTheDocument();
  });

  it('renders custom children instead of message', () => {
    render(
      <Table>
        <TableBody>
          <TableEmpty colSpan={3}>
            <span>Custom empty state</span>
          </TableEmpty>
        </TableBody>
      </Table>
    );

    expect(screen.getByText('Custom empty state')).toBeInTheDocument();
    expect(screen.queryByText('No data available')).not.toBeInTheDocument();
  });

  it('applies correct colSpan', () => {
    render(
      <Table>
        <TableBody>
          <TableEmpty colSpan={5} />
        </TableBody>
      </Table>
    );

    expect(screen.getByRole('cell')).toHaveAttribute('colspan', '5');
  });
});

describe('TableLoading', () => {
  it('renders loading skeleton rows', () => {
    render(
      <Table>
        <TableBody>
          <TableLoading colSpan={3} rows={3} />
        </TableBody>
      </Table>
    );

    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(3);
  });

  it('renders default 5 rows when rows prop not provided', () => {
    render(
      <Table>
        <TableBody>
          <TableLoading colSpan={2} />
        </TableBody>
      </Table>
    );

    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(5);
  });

  it('renders correct number of cells per row', () => {
    render(
      <Table>
        <TableBody>
          <TableLoading colSpan={4} rows={1} />
        </TableBody>
      </Table>
    );

    const cells = screen.getAllByRole('cell');
    expect(cells).toHaveLength(4);
  });

  it('renders animated skeleton elements', () => {
    const { container } = render(
      <Table>
        <TableBody>
          <TableLoading colSpan={2} rows={1} />
        </TableBody>
      </Table>
    );

    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(2);
  });
});
