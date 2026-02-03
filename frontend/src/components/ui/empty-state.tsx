import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import {
  FolderOpen,
  Search,
  FileText,
  BarChart3,
  Bell,
  Settings,
  Target,
  Zap,
  Plus,
} from 'lucide-react';
import { Button } from './button';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    icon?: ReactNode;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className,
  size = 'md',
}: EmptyStateProps) {
  const sizes = {
    sm: {
      container: 'py-8',
      iconContainer: 'w-12 h-12',
      icon: 'w-6 h-6',
      title: 'text-base',
      description: 'text-sm',
    },
    md: {
      container: 'py-12',
      iconContainer: 'w-16 h-16',
      icon: 'w-8 h-8',
      title: 'text-lg',
      description: 'text-sm',
    },
    lg: {
      container: 'py-16',
      iconContainer: 'w-20 h-20',
      icon: 'w-10 h-10',
      title: 'text-xl',
      description: 'text-base',
    },
  };

  const sizeConfig = sizes[size];

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center px-4',
        sizeConfig.container,
        className
      )}
    >
      {icon && (
        <div
          className={cn(
            'rounded-full bg-neutral-100 flex items-center justify-center mb-4',
            sizeConfig.iconContainer
          )}
        >
          <div className={cn('text-neutral-400', sizeConfig.icon)}>{icon}</div>
        </div>
      )}
      <h3 className={cn('font-semibold text-neutral-900 mb-2', sizeConfig.title)}>
        {title}
      </h3>
      {description && (
        <p className={cn('text-neutral-600 mb-6 max-w-sm', sizeConfig.description)}>
          {description}
        </p>
      )}
      {(action || secondaryAction) && (
        <div className="flex items-center gap-3">
          {action && (
            <Button onClick={action.onClick}>
              {action.icon || <Plus className="w-4 h-4 mr-2" />}
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button variant="outline" onClick={secondaryAction.onClick}>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

// Pre-configured empty states for common scenarios
function EmptyProjects({ onCreateProject }: { onCreateProject: () => void }) {
  return (
    <EmptyState
      icon={<FolderOpen className="w-full h-full" />}
      title="No projects yet"
      description="Create your first project to start analyzing sentiment from reviews, comments, and more."
      action={{
        label: 'Create Project',
        onClick: onCreateProject,
      }}
    />
  );
}

function EmptyTargets({ onAddTarget }: { onAddTarget: () => void }) {
  return (
    <EmptyState
      icon={<Target className="w-full h-full" />}
      title="No targets added"
      description="Add URLs to scrape and analyze. Supports Amazon, Steam, YouTube, Reddit, and more."
      action={{
        label: 'Add Target',
        onClick: onAddTarget,
      }}
    />
  );
}

function EmptyResults({ onRunScrape }: { onRunScrape?: () => void }) {
  return (
    <EmptyState
      icon={<BarChart3 className="w-full h-full" />}
      title="No results yet"
      description="Run a scrape job to collect and analyze data from your targets."
      action={
        onRunScrape
          ? {
              label: 'Run Scrape',
              onClick: onRunScrape,
              icon: <Zap className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
    />
  );
}

function EmptySearch({ query }: { query?: string }) {
  return (
    <EmptyState
      icon={<Search className="w-full h-full" />}
      title="No results found"
      description={
        query
          ? `No results match "${query}". Try adjusting your search or filters.`
          : 'No results match your search criteria.'
      }
    />
  );
}

function EmptyWebhooks({ onCreateWebhook }: { onCreateWebhook: () => void }) {
  return (
    <EmptyState
      icon={<Bell className="w-full h-full" />}
      title="No webhooks configured"
      description="Set up webhooks to receive notifications when scrape jobs complete or fail."
      action={{
        label: 'Add Webhook',
        onClick: onCreateWebhook,
      }}
    />
  );
}

function EmptySchedules({ onCreateSchedule }: { onCreateSchedule: () => void }) {
  return (
    <EmptyState
      icon={<Settings className="w-full h-full" />}
      title="No schedules set up"
      description="Automate your scraping by scheduling regular jobs for your projects."
      action={{
        label: 'Create Schedule',
        onClick: onCreateSchedule,
      }}
    />
  );
}

function EmptyDocuments() {
  return (
    <EmptyState
      icon={<FileText className="w-full h-full" />}
      title="No documents"
      description="Documents will appear here once available."
    />
  );
}

export {
  EmptyState,
  EmptyProjects,
  EmptyTargets,
  EmptyResults,
  EmptySearch,
  EmptyWebhooks,
  EmptySchedules,
  EmptyDocuments,
};
