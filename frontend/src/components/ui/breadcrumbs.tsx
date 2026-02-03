'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  separator?: React.ReactNode;
  showHome?: boolean;
  homeHref?: string;
  className?: string;
}

export function Breadcrumbs({
  items,
  separator = <ChevronRight className="h-4 w-4 text-neutral-400" />,
  showHome = true,
  homeHref = '/dashboard',
  className,
}: BreadcrumbsProps) {
  const pathname = usePathname();

  // Auto-generate breadcrumbs from pathname if items not provided
  const breadcrumbItems = items || generateBreadcrumbs(pathname);

  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center', className)}>
      <ol className="flex items-center space-x-2">
        {showHome && (
          <>
            <li>
              <Link
                href={homeHref}
                className="text-neutral-500 hover:text-neutral-700 transition-colors"
              >
                <Home className="h-4 w-4" />
                <span className="sr-only">Home</span>
              </Link>
            </li>
            {breadcrumbItems.length > 0 && (
              <li className="flex items-center">{separator}</li>
            )}
          </>
        )}
        {breadcrumbItems.map((item, index) => {
          const isLast = index === breadcrumbItems.length - 1;

          return (
            <React.Fragment key={index}>
              <li>
                {isLast || !item.href ? (
                  <span
                    className={cn(
                      'flex items-center gap-1.5 text-sm',
                      isLast ? 'font-medium text-neutral-900' : 'text-neutral-500'
                    )}
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {item.icon}
                    {item.label}
                  </span>
                ) : (
                  <Link
                    href={item.href}
                    className="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-700 transition-colors"
                  >
                    {item.icon}
                    {item.label}
                  </Link>
                )}
              </li>
              {!isLast && <li className="flex items-center">{separator}</li>}
            </React.Fragment>
          );
        })}
      </ol>
    </nav>
  );
}

// Helper function to generate breadcrumbs from pathname
function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];

  // Route label mappings
  const labelMap: Record<string, string> = {
    dashboard: 'Dashboard',
    projects: 'Projects',
    new: 'New Project',
    settings: 'Settings',
    presets: 'Presets',
    results: 'Results',
    auth: 'Authentication',
    login: 'Login',
    register: 'Register',
    'forgot-password': 'Forgot Password',
    'reset-password': 'Reset Password',
  };

  let currentPath = '';

  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    const isLast = index === segments.length - 1;

    // Skip certain segments
    if (segment === 'dashboard' && index === 0) {
      return;
    }

    // Handle dynamic segments (e.g., [id])
    const isDynamic = segment.match(/^[a-f0-9-]{20,}$/i);
    const label = isDynamic
      ? 'Details'
      : labelMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);

    breadcrumbs.push({
      label,
      href: isLast ? undefined : currentPath,
    });
  });

  return breadcrumbs;
}

// Breadcrumb with dropdown for overflow
interface BreadcrumbsWithOverflowProps extends BreadcrumbsProps {
  maxItems?: number;
}

export function BreadcrumbsWithOverflow({
  items,
  maxItems = 4,
  ...props
}: BreadcrumbsWithOverflowProps) {
  const pathname = usePathname();
  const allItems = items || generateBreadcrumbs(pathname);

  if (allItems.length <= maxItems) {
    return <Breadcrumbs items={allItems} {...props} />;
  }

  // Show first item, ellipsis, and last (maxItems - 2) items
  const visibleItems: BreadcrumbItem[] = [
    allItems[0],
    { label: '...', href: undefined },
    ...allItems.slice(-(maxItems - 2)),
  ];

  return <Breadcrumbs items={visibleItems} {...props} />;
}

// Page header with breadcrumbs
interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  breadcrumbs,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <Breadcrumbs items={breadcrumbs} />
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">{title}</h1>
          {description && (
            <p className="mt-1 text-sm text-neutral-500">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}
