'use client';

import { useState } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Button,
  Badge,
  Alert,
  Skeleton,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Modal,
} from '@/components/ui';
import {
  useSubscription,
  useUsageStats,
  usePlans,
  useInvoices,
  useCreateCheckoutSession,
  useCancelSubscription,
  useResumeSubscription,
  useCustomerPortal,
} from '@/hooks';
import {
  CreditCard,
  Zap,
  Check,
  X,
  AlertTriangle,
  Download,
  ExternalLink,
  TrendingUp,
  BarChart3,
  Database,
  Clock,
  Calendar,
  FileText,
  Sparkles,
} from 'lucide-react';
import type { Plan, UsageHistoryItem } from '@/lib/api';

export default function BillingPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [usagePeriod, setUsagePeriod] = useState<'day' | 'week' | 'month' | 'year'>('month');

  const { data: subscription, isLoading: loadingSubscription } = useSubscription();
  const { data: usage, isLoading: loadingUsage } = useUsageStats(usagePeriod);
  const { data: plans, isLoading: loadingPlans } = usePlans();
  const { data: invoices, isLoading: loadingInvoices } = useInvoices();

  const createCheckout = useCreateCheckoutSession();
  const cancelSubscription = useCancelSubscription();
  const resumeSubscription = useResumeSubscription();
  const customerPortal = useCustomerPortal();

  const handleUpgrade = (planId: string) => {
    createCheckout.mutate(planId);
  };

  const handleCancel = () => {
    cancelSubscription.mutate(undefined, {
      onSuccess: () => setShowCancelModal(false),
    });
  };

  const handleResume = () => {
    resumeSubscription.mutate();
  };

  const handleManageBilling = () => {
    customerPortal.mutate();
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: 'success' | 'warning' | 'error' | 'default'; label: string }> = {
      active: { variant: 'success', label: 'Active' },
      trialing: { variant: 'default', label: 'Trial' },
      cancelled: { variant: 'warning', label: 'Cancelled' },
      past_due: { variant: 'error', label: 'Past Due' },
      inactive: { variant: 'error', label: 'Inactive' },
    };
    const config = variants[status] || { variant: 'default', label: status };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Billing & Usage</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Manage your subscription, view usage statistics, and download invoices
        </p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="plans">Plans</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Current Plan Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Current Plan
                  </CardTitle>
                  <CardDescription>Your subscription details</CardDescription>
                </div>
                {subscription && getStatusBadge(subscription.status)}
              </div>
            </CardHeader>
            <CardContent>
              {loadingSubscription ? (
                <div className="space-y-4">
                  <Skeleton className="h-8 w-48" />
                  <Skeleton className="h-4 w-64" />
                  <Skeleton className="h-4 w-56" />
                </div>
              ) : subscription ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-neutral-900">
                      {subscription.plan_name}
                    </h3>
                    {subscription.cancel_at_period_end && (
                      <Alert variant="warning" className="mt-2">
                        <AlertTriangle className="h-4 w-4" />
                        <span>
                          Your subscription will be cancelled on{' '}
                          {new Date(subscription.cancels_at!).toLocaleDateString()}
                        </span>
                      </Alert>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-neutral-500">Billing Period</span>
                      <p className="font-medium">
                        {new Date(subscription.current_period_start).toLocaleDateString()} -{' '}
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </p>
                    </div>
                    {subscription.trial_end && new Date(subscription.trial_end) > new Date() && (
                      <div>
                        <span className="text-neutral-500">Trial Ends</span>
                        <p className="font-medium">
                          {new Date(subscription.trial_end).toLocaleDateString()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Zap className="mx-auto h-12 w-12 text-neutral-300" />
                  <h3 className="mt-4 text-lg font-medium">No Active Subscription</h3>
                  <p className="mt-2 text-sm text-neutral-500">
                    Choose a plan to get started with Sentimatrix Studio
                  </p>
                  <Button className="mt-4" onClick={() => setActiveTab('plans')}>
                    View Plans
                  </Button>
                </div>
              )}
            </CardContent>
            {subscription && (
              <CardFooter className="flex gap-2">
                <Button variant="outline" onClick={handleManageBilling} disabled={customerPortal.isPending}>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Manage Billing
                </Button>
                {subscription.cancel_at_period_end ? (
                  <Button onClick={handleResume} disabled={resumeSubscription.isPending}>
                    Resume Subscription
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    className="text-error-600 hover:text-error-700"
                    onClick={() => setShowCancelModal(true)}
                  >
                    Cancel Subscription
                  </Button>
                )}
              </CardFooter>
            )}
          </Card>

          {/* Quick Usage Stats */}
          {usage && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <UsageStatCard
                title="Projects"
                used={usage.projects.used}
                limit={usage.projects.limit}
                icon={<Database className="h-5 w-5" />}
                percentage={usage.projects.percentage}
              />
              <UsageStatCard
                title="Results This Month"
                used={usage.results.used}
                limit={usage.results.limit}
                icon={<BarChart3 className="h-5 w-5" />}
                percentage={usage.results.percentage}
              />
              <UsageStatCard
                title="API Calls"
                used={usage.api_calls.used}
                limit={usage.api_calls.limit}
                icon={<Zap className="h-5 w-5" />}
                percentage={usage.api_calls.percentage}
              />
              <UsageStatCard
                title="Scrape Jobs Today"
                used={usage.scrape_jobs.used}
                limit={usage.scrape_jobs.limit}
                icon={<Clock className="h-5 w-5" />}
                percentage={usage.scrape_jobs.percentage}
              />
            </div>
          )}
        </TabsContent>

        {/* Usage Tab */}
        <TabsContent value="usage" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Usage Statistics
                  </CardTitle>
                  <CardDescription>Monitor your resource consumption</CardDescription>
                </div>
                <div className="flex gap-2">
                  {(['day', 'week', 'month', 'year'] as const).map((period) => (
                    <Button
                      key={period}
                      variant={usagePeriod === period ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setUsagePeriod(period)}
                    >
                      {period.charAt(0).toUpperCase() + period.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loadingUsage ? (
                <div className="space-y-4">
                  <Skeleton className="h-48 w-full" />
                </div>
              ) : usage ? (
                <div className="space-y-6">
                  {/* Usage Bars */}
                  <div className="space-y-4">
                    <UsageBar
                      label="Projects"
                      used={usage.projects.used}
                      limit={usage.projects.limit}
                      percentage={usage.projects.percentage}
                    />
                    <UsageBar
                      label="Results"
                      used={usage.results.used}
                      limit={usage.results.limit}
                      percentage={usage.results.percentage}
                    />
                    <UsageBar
                      label="API Calls"
                      used={usage.api_calls.used}
                      limit={usage.api_calls.limit}
                      percentage={usage.api_calls.percentage}
                    />
                    <UsageBar
                      label="Storage"
                      used={usage.storage_mb.used}
                      limit={usage.storage_mb.limit}
                      percentage={usage.storage_mb.percentage}
                      unit="MB"
                    />
                    <UsageBar
                      label="Scrape Jobs"
                      used={usage.scrape_jobs.used}
                      limit={usage.scrape_jobs.limit}
                      percentage={usage.scrape_jobs.percentage}
                    />
                  </div>

                  {/* Usage History */}
                  {usage.history && usage.history.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-4">Usage History</h4>
                      <div className="overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Date</TableHead>
                              <TableHead className="text-right">API Calls</TableHead>
                              <TableHead className="text-right">Results</TableHead>
                              <TableHead className="text-right">Scrape Jobs</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {usage.history.slice(0, 10).map((item: UsageHistoryItem) => (
                              <TableRow key={item.date}>
                                <TableCell>{new Date(item.date).toLocaleDateString()}</TableCell>
                                <TableCell className="text-right">{item.api_calls.toLocaleString()}</TableCell>
                                <TableCell className="text-right">{item.results.toLocaleString()}</TableCell>
                                <TableCell className="text-right">{item.scrape_jobs}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-neutral-500">
                  No usage data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Plans Tab */}
        <TabsContent value="plans" className="space-y-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-neutral-900">Choose Your Plan</h2>
            <p className="mt-2 text-neutral-500">
              Select the plan that best fits your needs
            </p>
          </div>

          {loadingPlans ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-96 w-full" />
              ))}
            </div>
          ) : plans ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {plans.map((plan) => (
                <PlanCard
                  key={plan.id}
                  plan={plan}
                  isCurrentPlan={subscription?.plan_id === plan.id}
                  onSelect={() => handleUpgrade(plan.id)}
                  isLoading={createCheckout.isPending}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-neutral-500">
              No plans available
            </div>
          )}
        </TabsContent>

        {/* Invoices Tab */}
        <TabsContent value="invoices" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Billing History
              </CardTitle>
              <CardDescription>View and download your invoices</CardDescription>
            </CardHeader>
            <CardContent>
              {loadingInvoices ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </div>
              ) : invoices && invoices.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Invoice</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Period</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {invoices.map((invoice) => (
                      <TableRow key={invoice.id}>
                        <TableCell className="font-medium">{invoice.number}</TableCell>
                        <TableCell>{new Date(invoice.created_at).toLocaleDateString()}</TableCell>
                        <TableCell>
                          {new Date(invoice.period_start).toLocaleDateString()} -{' '}
                          {new Date(invoice.period_end).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          ${(invoice.amount / 100).toFixed(2)} {invoice.currency.toUpperCase()}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              invoice.status === 'paid'
                                ? 'success'
                                : invoice.status === 'pending'
                                ? 'warning'
                                : 'error'
                            }
                          >
                            {invoice.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          {invoice.pdf_url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(invoice.pdf_url, '_blank')}
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-neutral-300" />
                  <h3 className="mt-4 text-lg font-medium">No Invoices</h3>
                  <p className="mt-2 text-sm text-neutral-500">
                    Your invoices will appear here once you subscribe
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Cancel Subscription Modal */}
      <Modal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        title="Cancel Subscription"
      >
        <div className="space-y-4">
          <Alert variant="warning">
            <AlertTriangle className="h-4 w-4" />
            <span>
              Your subscription will remain active until the end of the current billing period.
            </span>
          </Alert>
          <p className="text-neutral-600">
            Are you sure you want to cancel your subscription? You will lose access to premium
            features at the end of your billing period.
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowCancelModal(false)}>
              Keep Subscription
            </Button>
            <Button
              variant="destructive"
              onClick={handleCancel}
              disabled={cancelSubscription.isPending}
            >
              {cancelSubscription.isPending ? 'Cancelling...' : 'Yes, Cancel'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

// Usage Stat Card Component
interface UsageStatCardProps {
  title: string;
  used: number;
  limit: number;
  icon: React.ReactNode;
  percentage: number;
}

function UsageStatCard({ title, used, limit, icon, percentage }: UsageStatCardProps) {
  const getColor = () => {
    if (percentage >= 90) return 'text-error-600';
    if (percentage >= 75) return 'text-warning-600';
    return 'text-success-600';
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="text-neutral-500">{icon}</div>
          <span className={`text-sm font-medium ${getColor()}`}>{percentage}%</span>
        </div>
        <div className="mt-4">
          <h4 className="text-sm font-medium text-neutral-500">{title}</h4>
          <p className="mt-1 text-2xl font-bold">
            {used.toLocaleString()} <span className="text-sm text-neutral-400">/ {limit === -1 ? '∞' : limit.toLocaleString()}</span>
          </p>
        </div>
        <div className="mt-4 h-2 w-full rounded-full bg-neutral-100">
          <div
            className={`h-full rounded-full ${
              percentage >= 90
                ? 'bg-error-500'
                : percentage >= 75
                ? 'bg-warning-500'
                : 'bg-success-500'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      </CardContent>
    </Card>
  );
}

// Usage Bar Component
interface UsageBarProps {
  label: string;
  used: number;
  limit: number;
  percentage: number;
  unit?: string;
}

function UsageBar({ label, used, limit, percentage, unit = '' }: UsageBarProps) {
  const getColor = () => {
    if (percentage >= 90) return 'bg-error-500';
    if (percentage >= 75) return 'bg-warning-500';
    return 'bg-primary-500';
  };

  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <span className="font-medium text-neutral-700">{label}</span>
        <span className="text-neutral-500">
          {used.toLocaleString()}{unit} / {limit === -1 ? 'Unlimited' : `${limit.toLocaleString()}${unit}`}
        </span>
      </div>
      <div className="h-3 w-full rounded-full bg-neutral-100">
        <div
          className={`h-full rounded-full transition-all ${getColor()}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}

// Plan Card Component
interface PlanCardProps {
  plan: Plan;
  isCurrentPlan: boolean;
  onSelect: () => void;
  isLoading: boolean;
}

function PlanCard({ plan, isCurrentPlan, onSelect, isLoading }: PlanCardProps) {
  return (
    <Card className={`relative ${plan.is_popular ? 'border-primary-500 border-2' : ''}`}>
      {plan.is_popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge className="bg-primary-500 text-white">
            <Sparkles className="mr-1 h-3 w-3" />
            Most Popular
          </Badge>
        </div>
      )}
      <CardHeader className="text-center pt-8">
        <CardTitle className="text-xl">{plan.name}</CardTitle>
        <CardDescription>{plan.description}</CardDescription>
        <div className="mt-4">
          <span className="text-4xl font-bold">${plan.price_monthly}</span>
          <span className="text-neutral-500">/month</span>
        </div>
        {plan.price_yearly && (
          <p className="text-sm text-neutral-500 mt-1">
            or ${plan.price_yearly}/year (save {Math.round((1 - plan.price_yearly / (plan.price_monthly * 12)) * 100)}%)
          </p>
        )}
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-start gap-2">
              {feature.included ? (
                <Check className="h-5 w-5 text-success-500 flex-shrink-0" />
              ) : (
                <X className="h-5 w-5 text-neutral-300 flex-shrink-0" />
              )}
              <span className={feature.included ? 'text-neutral-700' : 'text-neutral-400'}>
                {feature.name}
                {feature.value && <span className="font-medium"> ({feature.value})</span>}
              </span>
            </li>
          ))}
        </ul>

        <div className="mt-6 pt-4 border-t border-neutral-100">
          <h4 className="text-sm font-medium text-neutral-500 mb-2">Limits</h4>
          <ul className="space-y-1 text-sm text-neutral-600">
            <li>{plan.limits.projects === -1 ? 'Unlimited' : plan.limits.projects} Projects</li>
            <li>{plan.limits.results_per_month === -1 ? 'Unlimited' : plan.limits.results_per_month.toLocaleString()} Results/month</li>
            <li>{plan.limits.api_calls_per_month === -1 ? 'Unlimited' : plan.limits.api_calls_per_month.toLocaleString()} API calls/month</li>
            <li>{plan.limits.scrape_jobs_per_day === -1 ? 'Unlimited' : plan.limits.scrape_jobs_per_day} Scrape jobs/day</li>
          </ul>
        </div>
      </CardContent>
      <CardFooter>
        {isCurrentPlan ? (
          <Button className="w-full" disabled>
            Current Plan
          </Button>
        ) : plan.is_enterprise ? (
          <Button className="w-full" variant="outline" onClick={() => window.location.href = 'mailto:sales@sentimatrix.io'}>
            Contact Sales
          </Button>
        ) : (
          <Button
            className="w-full"
            variant={plan.is_popular ? 'primary' : 'outline'}
            onClick={onSelect}
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : 'Upgrade'}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
