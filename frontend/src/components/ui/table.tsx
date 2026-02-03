import { cn } from '@/lib/utils';
import { ReactNode } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';

// Table Root
export interface TableProps {
  children: ReactNode;
  className?: string;
}

export function Table({ children, className }: TableProps) {
  return (
    <div className={cn('w-full overflow-auto', className)}>
      <table className="w-full caption-bottom text-sm">{children}</table>
    </div>
  );
}

// Table Header
export function TableHeader({ children, className }: TableProps) {
  return <thead className={cn('[&_tr]:border-b', className)}>{children}</thead>;
}

// Table Body
export function TableBody({ children, className }: TableProps) {
  return <tbody className={cn('[&_tr:last-child]:border-0', className)}>{children}</tbody>;
}

// Table Footer
export function TableFooter({ children, className }: TableProps) {
  return (
    <tfoot className={cn('border-t bg-neutral-50 font-medium', className)}>
      {children}
    </tfoot>
  );
}

// Table Row
export interface TableRowProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  selected?: boolean;
}

export function TableRow({ children, className, onClick, selected }: TableRowProps) {
  return (
    <tr
      onClick={onClick}
      className={cn(
        'border-b transition-colors',
        onClick && 'cursor-pointer hover:bg-neutral-50',
        selected && 'bg-primary-50',
        className
      )}
    >
      {children}
    </tr>
  );
}

// Table Head Cell
export interface TableHeadProps {
  children?: ReactNode;
  className?: string;
  sortable?: boolean;
  sortDirection?: 'asc' | 'desc' | null;
  onSort?: () => void;
}

export function TableHead({
  children,
  className,
  sortable,
  sortDirection,
  onSort,
}: TableHeadProps) {
  return (
    <th
      onClick={sortable ? onSort : undefined}
      className={cn(
        'h-12 px-4 text-left align-middle font-medium text-neutral-500',
        sortable && 'cursor-pointer hover:text-neutral-900 select-none',
        className
      )}
    >
      <div className="flex items-center gap-2">
        {children}
        {sortable && (
          <span className="text-neutral-400">
            {sortDirection === 'asc' ? (
              <ChevronUp className="h-4 w-4" />
            ) : sortDirection === 'desc' ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronsUpDown className="h-4 w-4" />
            )}
          </span>
        )}
      </div>
    </th>
  );
}

// Table Cell
export interface TableCellProps {
  children?: ReactNode;
  className?: string;
  colSpan?: number;
}

export function TableCell({ children, className, colSpan }: TableCellProps) {
  return (
    <td className={cn('p-4 align-middle', className)} colSpan={colSpan}>
      {children}
    </td>
  );
}

// Table Caption
export function TableCaption({ children, className }: TableProps) {
  return (
    <caption className={cn('mt-4 text-sm text-neutral-500', className)}>
      {children}
    </caption>
  );
}

// Empty Table State
export interface TableEmptyProps {
  colSpan: number;
  message?: string;
  children?: ReactNode;
}

export function TableEmpty({ colSpan, message = 'No data available', children }: TableEmptyProps) {
  return (
    <TableRow>
      <TableCell colSpan={colSpan} className="h-32 text-center">
        <div className="flex flex-col items-center justify-center gap-2 text-neutral-500">
          {children || message}
        </div>
      </TableCell>
    </TableRow>
  );
}

// Loading Table State
export interface TableLoadingProps {
  colSpan: number;
  rows?: number;
}

export function TableLoading({ colSpan, rows = 5 }: TableLoadingProps) {
  return (
    <>
      {Array.from({ length: rows }).map((_, index) => (
        <TableRow key={index}>
          {Array.from({ length: colSpan }).map((_, cellIndex) => (
            <TableCell key={cellIndex}>
              <div className="h-4 w-full animate-pulse rounded bg-neutral-200" />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </>
  );
}
