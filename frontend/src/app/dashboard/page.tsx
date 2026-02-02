'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { useAuthStore } from '@/stores/auth';
import { FolderOpen, BarChart3, Clock, Zap } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {user?.name}</h1>
        <p className="text-neutral-600">Here&apos;s an overview of your sentiment analysis activity.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<FolderOpen className="h-5 w-5" />}
          label="Total Projects"
          value="0"
          change="Get started by creating your first project"
        />
        <StatCard
          icon={<BarChart3 className="h-5 w-5" />}
          label="Analyses Run"
          value="0"
          change="Run your first analysis"
        />
        <StatCard
          icon={<Clock className="h-5 w-5" />}
          label="This Month"
          value="0"
          change="No activity yet"
        />
        <StatCard
          icon={<Zap className="h-5 w-5" />}
          label="API Calls"
          value="0"
          change="Connect your API keys"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <FolderOpen className="h-12 w-12 text-neutral-300" />
              <p className="mt-4 text-neutral-500">No projects yet</p>
              <p className="text-sm text-neutral-400">
                Create your first project to start analyzing sentiment
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <ActionItem
                title="Create New Project"
                description="Set up a new sentiment analysis project"
                href="/dashboard/projects/new"
              />
              <ActionItem
                title="Configure API Keys"
                description="Add your LLM provider API keys"
                href="/dashboard/settings"
              />
              <ActionItem
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
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  change: string;
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
            <p className="text-2xl font-semibold">{value}</p>
          </div>
        </div>
        <p className="mt-2 text-xs text-neutral-400">{change}</p>
      </CardContent>
    </Card>
  );
}

function ActionItem({
  title,
  description,
  href,
}: {
  title: string;
  description: string;
  href: string;
}) {
  return (
    <a
      href={href}
      className="block rounded-lg border border-neutral-200 p-4 transition-colors hover:border-primary-300 hover:bg-primary-50"
    >
      <p className="font-medium">{title}</p>
      <p className="text-sm text-neutral-500">{description}</p>
    </a>
  );
}
