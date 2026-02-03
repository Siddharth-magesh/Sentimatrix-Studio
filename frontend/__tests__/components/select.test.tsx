import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Select, MultiSelect } from '@/components/ui/select';

const mockOptions = [
  { value: 'option1', label: 'Option 1' },
  { value: 'option2', label: 'Option 2' },
  { value: 'option3', label: 'Option 3', disabled: true },
];

describe('Select', () => {
  it('renders with default props', () => {
    render(<Select options={mockOptions} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('displays placeholder when no value is selected', () => {
    render(<Select options={mockOptions} placeholder="Choose an option" />);
    expect(screen.getByRole('combobox')).toHaveDisplayValue('Choose an option');
  });

  it('displays all options', () => {
    render(<Select options={mockOptions} />);
    const options = screen.getAllByRole('option');
    // +1 for placeholder option
    expect(options).toHaveLength(mockOptions.length + 1);
  });

  it('calls onChange when selection changes', async () => {
    const handleChange = jest.fn();
    render(<Select options={mockOptions} onChange={handleChange} />);

    await userEvent.selectOptions(screen.getByRole('combobox'), 'option1');
    expect(handleChange).toHaveBeenCalledWith('option1');
  });

  it('applies error styles when error prop is true', () => {
    render(<Select options={mockOptions} error />);
    expect(screen.getByRole('combobox')).toHaveClass('border-error-500');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Select options={mockOptions} disabled />);
    expect(screen.getByRole('combobox')).toBeDisabled();
  });

  it('disables individual options when option.disabled is true', () => {
    render(<Select options={mockOptions} />);
    const disabledOption = screen.getByRole('option', { name: 'Option 3' });
    expect(disabledOption).toBeDisabled();
  });

  it('displays selected value correctly', () => {
    render(<Select options={mockOptions} value="option2" onChange={() => {}} />);
    expect(screen.getByRole('combobox')).toHaveValue('option2');
  });
});

describe('MultiSelect', () => {
  const defaultProps = {
    options: mockOptions,
    value: [] as string[],
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with placeholder when no values selected', () => {
    render(<MultiSelect {...defaultProps} placeholder="Select items" />);
    expect(screen.getByText('Select items')).toBeInTheDocument();
  });

  it('opens dropdown when clicked', async () => {
    render(<MultiSelect {...defaultProps} />);

    await userEvent.click(screen.getByText('Select...'));

    await waitFor(() => {
      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.getByText('Option 2')).toBeInTheDocument();
    });
  });

  it('selects an option when clicked', async () => {
    const handleChange = jest.fn();
    render(<MultiSelect {...defaultProps} onChange={handleChange} />);

    await userEvent.click(screen.getByText('Select...'));
    await userEvent.click(screen.getByText('Option 1'));

    expect(handleChange).toHaveBeenCalledWith(['option1']);
  });

  it('displays selected values as tags', () => {
    render(
      <MultiSelect
        {...defaultProps}
        value={['option1', 'option2']}
      />
    );

    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
  });

  it('removes a selected value when X is clicked', async () => {
    const handleChange = jest.fn();
    render(
      <MultiSelect
        {...defaultProps}
        value={['option1', 'option2']}
        onChange={handleChange}
      />
    );

    // Find the X button for Option 1
    const removeButtons = screen.getAllByRole('img', { hidden: true });
    await userEvent.click(removeButtons[0]);

    expect(handleChange).toHaveBeenCalledWith(['option2']);
  });

  it('deselects an option when clicked again', async () => {
    const handleChange = jest.fn();
    render(
      <MultiSelect
        {...defaultProps}
        value={['option1']}
        onChange={handleChange}
      />
    );

    await userEvent.click(screen.getByText('Option 1'));

    // Click on Option 1 in dropdown to deselect
    await waitFor(() => {
      const dropdownOption = screen.getAllByText('Option 1')[1];
      userEvent.click(dropdownOption);
    });

    expect(handleChange).toHaveBeenCalledWith([]);
  });

  it('applies error styles when error prop is true', () => {
    render(<MultiSelect {...defaultProps} error />);
    const container = screen.getByText('Select...').parentElement;
    expect(container).toHaveClass('border-error-500');
  });

  it('is disabled when disabled prop is true', () => {
    render(<MultiSelect {...defaultProps} disabled />);
    const container = screen.getByText('Select...').parentElement;
    expect(container).toHaveClass('cursor-not-allowed');
  });

  it('filters options when searchable and typing', async () => {
    render(<MultiSelect {...defaultProps} searchable />);

    await userEvent.click(screen.getByText('Select...'));

    const searchInput = screen.getByPlaceholderText('Search...');
    await userEvent.type(searchInput, 'Option 1');

    await waitFor(() => {
      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.queryByText('Option 2')).not.toBeInTheDocument();
    });
  });

  it('shows no options message when search has no results', async () => {
    render(<MultiSelect {...defaultProps} searchable />);

    await userEvent.click(screen.getByText('Select...'));

    const searchInput = screen.getByPlaceholderText('Search...');
    await userEvent.type(searchInput, 'xyz');

    await waitFor(() => {
      expect(screen.getByText('No options found')).toBeInTheDocument();
    });
  });

  it('closes dropdown when clicking outside', async () => {
    render(
      <div>
        <MultiSelect {...defaultProps} />
        <button>Outside</button>
      </div>
    );

    await userEvent.click(screen.getByText('Select...'));
    expect(screen.getByText('Option 1')).toBeInTheDocument();

    await userEvent.click(screen.getByText('Outside'));

    await waitFor(() => {
      expect(screen.queryByText('Option 1')).not.toBeInTheDocument();
    });
  });
});
