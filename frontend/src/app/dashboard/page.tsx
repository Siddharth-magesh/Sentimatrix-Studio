'use client';

import Link from 'next/link';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  SkeletonStats,
  StatusBadge,
} from '@/components/ui';
import { useAuthStore } from '@/stores/auth';
import { useDashboardSummary, useProjects, useGlobalSentimentTimeline } from '@/hooks';
import { SentimentPieChart, TimelineChart } from '@/components/charts';
import { formatNumber, formatRelativeTime } from '@/lib/utils';
import {
  FolderOpen,
  BarChart3,
  Clock,
  Zap,
  Plus,
  Settings,
  Layers,
  ArrowRight,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { data: summary, isLoading: summaryLoading } = useDashboardSummary();
  const { data: projects, isLoading: projectsLoading } = useProjects({ limit: 5 });
  const { data: timeline, isLoading: timelineLoading } = useGlobalSentimentTimeline({ days: 30 });

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">
            Welcome back, {user?.name?.split(' ')[0]}
          </h1>
          <p className="text-neutral-500">
            Here's an overview of your sentiment analysis activity.
          </p>
        </div>
        <Link href="/dashboard/projects/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      {summaryLoading ? (
        <SkeletonStats />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={<FolderOpen className="h-5 w-5" />}
            label="Total Projects"
            value={formatNumber(summary?.total_projects || 0)}
            change={
              summary?.active_projects
                ? `${summary.active_projects} active`
                : 'Create your first project'
            }
          />
          <StatCard
            icon={<BarChart3 className="h-5 w-5" />}
            label="Total Results"
            value={formatNumber(summary?.total_results || 0)}
            change={
              summary?.results_this_month
                ? `${formatNumber(summary.results_this_month)} this month`
                : 'Run your first analysis'
            }
            trend={summary?.results_trend}
          />
          <StatCard
            icon={<Clock className="h-5 w-5" />}
            label="Scrape Jobs"
            value={formatNumber(summary?.total_jobs || 0)}
            change={
              summary?.pending_jobs
                ? `${summary.pending_jobs} pending`
                : 'No scheduled jobs'
            }
          />
          <StatCard
            icon={<Zap className="h-5 w-5" />}
            label="API Calls"
            value={formatNumber(summary?.api_calls || 0)}
            change={
              summary?.api_calls_this_month
                ? `${formatNumber(summary.api_calls_this_month)} this month`
                : 'Connect your API keys'
            }
            trend={summary?.api_calls_trend}
          />
        </div>
      )}

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Sentiment Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Sentiment Trend (30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <TimelineChart
              data={timeline || []}
              loading={timelineLoading}
              title=""
            />
          </CardContent>
        </Card>

        {/* Sentiment Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Sentiment Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <SentimentPieChart
              data={summary?.sentiment_distribution || []}
              loading={summaryLoading}
              title=""
            />
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects & Quick Actions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Projects */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Projects</CardTitle>
            <Link href="/dashboard/projects">
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {projectsLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse flex items-center gap-3 py-2">
                    <div className="h-10 w-10 rounded bg-neutral-200" />
                    <div className="flex-1">
                      <div className="h-4 w-32 bg-neutral-200 rounded" />
                      <div className="h-3 w-24 bg-neutral-100 rounded mt-1" />
                    </div>
                  </div>
                ))}
              </div>
            ) : !projects?.items?.length ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <FolderOpen className="h-12 w-12 text-neutral-300" />
                <p className="mt-4 text-neutral-500">No projects yet</p>
                <p className="text-sm text-neutral-400">
                  Create your first project to start analyzing sentiment
                </p>
                <Link href="/dashboard/projects/new">
                  <Button className="mt-4" size="sm">
                    <Plus className="mr-2 h-4 w-4" />
                    Create Project
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {projects.items.map((project) => (
                  <Link
                    key={project.id}
                    href={`/dashboard/projects/${project.id}`}
                    className="flex items-center gap-3 rounded-lg border border-neutral-200 p-3 transition-colors hover:border-primary-300 hover:bg-primary-50"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
                      <FolderOpen className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-neutral-900 truncate">
                          {project.name}
                        </p>
                        <StatusBadge status={project.status} size="sm" />
                      </div>
                      <p className="text-sm text-neutral-500">
                        {project.stats?.total_results || 0} results •{' '}
                        {project.stats?.last_scrape_at
                          ? formatRelativeTime(project.stats.last_scrape_at)
                          : 'No scrapes yet'}
                      </p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-neutral-400" />
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <ActionItem
                icon={<Plus className="h-5 w-5" />}
                title="Create New Project"
                description="Set up a new sentiment analysis project"
                href="/dashboard/projects/new"
              />
              <ActionItem
                icon={<Settings className="h-5 w-5" />}
                title="Configure API Keys"
                description="Add your LLM provider API keys"
                href="/dashboard/settings"
              />
              <ActionItem
                icon={<Layers className="h-5 w-5" />}
                title="Browse Presets"
                description="Use pre-configured analysis settings"
                href="/dashboard/presets"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  change,
  trend,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  change: string;
  trend?: number;
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
            {icon}
          </div>
          <div>
            <p className="text-sm text-neutral-500">{label}</p>
            <p className="text-2xl font-semibold text-neutral-900">{value}</p>
          </div>
        </div>
        <div className="mt-2 flex items-center gap-2">
          {trend !== undefined && trend !== 0 && (
            <span
              className={`flex items-center text-xs font-medium ${
                trend > 0 ? 'text-success-600' : 'text-error-600'
              }`}
            >
              {trend > 0 ? (
                <TrendingUp className="h-3 w-3 mr-0.5" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-0.5" />
              )}
              {Math.abs(trend)}%
            </span>
          )}
          <span className="text-xs text-neutral-400">{change}</span>
        </div>
      </CardContent>
    </Card>
  );
}

function ActionItem({
  icon,
  title,
  description,
  href,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 rounded-lg border border-neutral-200 p-4 transition-colors hover:border-primary-300 hover:bg-primary-50"
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-neutral-100 text-neutral-600">
        {icon}
      </div>
      <div className="flex-1">
        <p className="font-medium text-neutral-900">{title}</p>
        <p className="text-sm text-neutral-500">{description}</p>
      </div>
      <ArrowRight className="h-4 w-4 text-neutral-400" />
    </Link>
  );
}
