'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
  Label,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableEmpty,
  TableLoading,
  Badge,
  StatusBadge,
  Modal,
  ModalFooter,
  ConfirmModal,
  Alert,
  Select,
  Switch,
  EmptyWebhooks,
} from '@/components/ui';
import {
  useApiKeys,
  useAddApiKey,
  useDeleteApiKey,
  useTestApiKey,
  useWebhooks,
  useCreateWebhook,
  useDeleteWebhook,
  useTestWebhook,
  useLLMProviders,
} from '@/hooks';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import {
  User,
  Key,
  Bell,
  Shield,
  Plus,
  Trash2,
  TestTube,
  Check,
  X,
  Loader2,
  Eye,
  EyeOff,
} from 'lucide-react';

// Profile form schema
const profileSchema = z.object({
  name: z.string().min(1, 'Name is required'),
});

// Password form schema
const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

// API Key form schema
const apiKeySchema = z.object({
  provider: z.string().min(1, 'Provider is required'),
  api_key: z.string().min(1, 'API key is required'),
});

// Webhook form schema
const webhookSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  url: z.string().url('Must be a valid URL'),
  events: z.array(z.string()).min(1, 'Select at least one event'),
});

const webhookEvents = [
  { value: 'job.started', label: 'Job Started' },
  { value: 'job.completed', label: 'Job Completed' },
  { value: 'job.failed', label: 'Job Failed' },
  { value: 'result.created', label: 'Result Created' },
];

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [showAddApiKey, setShowAddApiKey] = useState(false);
  const [showAddWebhook, setShowAddWebhook] = useState(false);
  const [deleteApiKeyProvider, setDeleteApiKeyProvider] = useState<string | null>(null);
  const [deleteWebhookId, setDeleteWebhookId] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Data hooks
  const { data: apiKeys, isLoading: apiKeysLoading } = useApiKeys();
  const { data: webhooks, isLoading: webhooksLoading } = useWebhooks();
  const { data: llmProviders } = useLLMProviders();

  // Mutation hooks
  const addApiKey = useAddApiKey();
  const deleteApiKey = useDeleteApiKey();
  const testApiKey = useTestApiKey();
  const createWebhook = useCreateWebhook();
  const deleteWebhook = useDeleteWebhook();
  const testWebhook = useTestWebhook();

  // Profile form
  const profileForm = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: { name: user?.name || '' },
  });

  // Password form
  const passwordForm = useForm({
    resolver: zodResolver(passwordSchema),
    defaultValues: { current_password: '', new_password: '', confirm_password: '' },
  });

  // API Key form
  const apiKeyForm = useForm({
    resolver: zodResolver(apiKeySchema),
    defaultValues: { provider: '', api_key: '' },
  });

  // Webhook form
  const webhookForm = useForm({
    resolver: zodResolver(webhookSchema),
    defaultValues: { name: '', url: '', events: [] as string[] },
  });

  const handleProfileSubmit = async (data: { name: string }) => {
    try {
      await api.updateProfile(data);
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const handlePasswordSubmit = async (data: { current_password: string; new_password: string }) => {
    try {
      await api.changePassword(data);
      passwordForm.reset();
      setPasswordSuccess(true);
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to change password:', error);
    }
  };

  const handleAddApiKey = async (data: { provider: string; api_key: string }) => {
    await addApiKey.mutateAsync(data);
    setShowAddApiKey(false);
    apiKeyForm.reset();
  };

  const handleDeleteApiKey = async () => {
    if (deleteApiKeyProvider) {
      await deleteApiKey.mutateAsync(deleteApiKeyProvider);
      setDeleteApiKeyProvider(null);
    }
  };

  const handleAddWebhook = async (data: { name: string; url: string; events: string[] }) => {
    await createWebhook.mutateAsync(data);
    setShowAddWebhook(false);
    webhookForm.reset();
  };

  const handleDeleteWebhook = async () => {
    if (deleteWebhookId) {
      await deleteWebhook.mutateAsync(deleteWebhookId);
      setDeleteWebhookId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Settings</h1>
        <p className="text-sm text-neutral-500">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">
            <User className="mr-2 h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="api-keys">
            <Key className="mr-2 h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="webhooks">
            <Bell className="mr-2 h-4 w-4" />
            Webhooks
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="mr-2 h-4 w-4" />
            Security
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your account details</CardDescription>
            </CardHeader>
            <CardContent>
              {profileSuccess && (
                <Alert variant="success" className="mb-4">
                  Profile updated successfully!
                </Alert>
              )}
              <form onSubmit={profileForm.handleSubmit(handleProfileSubmit)} className="space-y-4 max-w-md">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    value={user?.email || ''}
                    disabled
                    className="bg-neutral-50"
                  />
                  <p className="mt-1 text-sm text-neutral-500">
                    Email cannot be changed
                  </p>
                </div>
                <div>
                  <Label htmlFor="name" required>Name</Label>
                  <Input
                    id="name"
                    error={!!profileForm.formState.errors.name}
                    {...profileForm.register('name')}
                  />
                  {profileForm.formState.errors.name && (
                    <p className="mt-1 text-sm text-error-600">
                      {profileForm.formState.errors.name.message}
                    </p>
                  )}
                </div>
                <Button type="submit">Save Changes</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api-keys">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>
                  Configure API keys for LLM providers and scraping services
                </CardDescription>
              </div>
              <Button onClick={() => setShowAddApiKey(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add API Key
              </Button>
            </CardHeader>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Provider</TableHead>
                  <TableHead>API Key</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Added</TableHead>
                  <TableHead className="w-[120px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {apiKeysLoading ? (
                  <TableLoading colSpan={5} rows={3} />
                ) : !apiKeys?.length ? (
                  <TableEmpty colSpan={5} message="No API keys configured" />
                ) : (
                  apiKeys.map((key) => (
                    <TableRow key={key.provider}>
                      <TableCell className="font-medium">{key.provider}</TableCell>
                      <TableCell className="font-mono text-sm">{key.masked_key}</TableCell>
                      <TableCell>
                        {key.is_valid ? (
                          <Badge variant="success">Valid</Badge>
                        ) : (
                          <Badge variant="error">Invalid</Badge>
                        )}
                      </TableCell>
                      <TableCell>{formatDate(key.created_at)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => testApiKey.mutate(key.provider)}
                            disabled={testApiKey.isPending}
                          >
                            <TestTube className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-error-600"
                            onClick={() => setDeleteApiKeyProvider(key.provider)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Webhooks Tab */}
        <TabsContent value="webhooks">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Webhooks</CardTitle>
                <CardDescription>
                  Receive notifications when events occur
                </CardDescription>
              </div>
              <Button onClick={() => setShowAddWebhook(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Webhook
              </Button>
            </CardHeader>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>URL</TableHead>
                  <TableHead>Events</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[120px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {webhooksLoading ? (
                  <TableLoading colSpan={5} rows={3} />
                ) : !webhooks?.length ? (
                  <TableEmpty colSpan={5}>
                    <EmptyWebhooks />
                  </TableEmpty>
                ) : (
                  webhooks.map((webhook) => (
                    <TableRow key={webhook.id}>
                      <TableCell className="font-medium">{webhook.name}</TableCell>
                      <TableCell className="font-mono text-sm max-w-xs truncate">
                        {webhook.url}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {webhook.events.map((event) => (
                            <Badge key={event} variant="outline" size="sm">
                              {event}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        {webhook.enabled ? (
                          <Badge variant="success">Active</Badge>
                        ) : (
                          <Badge variant="default">Disabled</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => testWebhook.mutate(webhook.id)}
                            disabled={testWebhook.isPending}
                          >
                            <TestTube className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-error-600"
                            onClick={() => setDeleteWebhookId(webhook.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>
                Update your password to keep your account secure
              </CardDescription>
            </CardHeader>
            <CardContent>
              {passwordSuccess && (
                <Alert variant="success" className="mb-4">
                  Password changed successfully!
                </Alert>
              )}
              <form onSubmit={passwordForm.handleSubmit(handlePasswordSubmit)} className="space-y-4 max-w-md">
                <div>
                  <Label htmlFor="current_password" required>Current Password</Label>
                  <Input
                    id="current_password"
                    type="password"
                    error={!!passwordForm.formState.errors.current_password}
                    {...passwordForm.register('current_password')}
                  />
                </div>
                <div>
                  <Label htmlFor="new_password" required>New Password</Label>
                  <Input
                    id="new_password"
                    type="password"
                    error={!!passwordForm.formState.errors.new_password}
                    {...passwordForm.register('new_password')}
                  />
                  {passwordForm.formState.errors.new_password && (
                    <p className="mt-1 text-sm text-error-600">
                      {passwordForm.formState.errors.new_password.message}
                    </p>
                  )}
                </div>
                <div>
                  <Label htmlFor="confirm_password" required>Confirm New Password</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    error={!!passwordForm.formState.errors.confirm_password}
                    {...passwordForm.register('confirm_password')}
                  />
                  {passwordForm.formState.errors.confirm_password && (
                    <p className="mt-1 text-sm text-error-600">
                      {passwordForm.formState.errors.confirm_password.message}
                    </p>
                  )}
                </div>
                <Button type="submit">Change Password</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add API Key Modal */}
      <Modal
        isOpen={showAddApiKey}
        onClose={() => setShowAddApiKey(false)}
        title="Add API Key"
      >
        <form onSubmit={apiKeyForm.handleSubmit(handleAddApiKey)} className="space-y-4">
          <div>
            <Label htmlFor="provider" required>Provider</Label>
            <Select
              options={[
                ...(llmProviders?.map((p) => ({ value: p.id, label: p.name })) || []),
                { value: 'scraperapi', label: 'ScraperAPI' },
                { value: 'apify', label: 'Apify' },
                { value: 'brightdata', label: 'Bright Data' },
                { value: 'scrapingbee', label: 'ScrapingBee' },
              ]}
              error={!!apiKeyForm.formState.errors.provider}
              {...apiKeyForm.register('provider')}
            />
          </div>
          <div>
            <Label htmlFor="api_key" required>API Key</Label>
            <div className="relative">
              <Input
                id="api_key"
                type={showApiKey ? 'text' : 'password'}
                error={!!apiKeyForm.formState.errors.api_key}
                className="pr-10"
                {...apiKeyForm.register('api_key')}
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
              >
                {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={() => setShowAddApiKey(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={addApiKey.isPending}>
              Add Key
            </Button>
          </ModalFooter>
        </form>
      </Modal>

      {/* Add Webhook Modal */}
      <Modal
        isOpen={showAddWebhook}
        onClose={() => setShowAddWebhook(false)}
        title="Add Webhook"
      >
        <form onSubmit={webhookForm.handleSubmit(handleAddWebhook)} className="space-y-4">
          <div>
            <Label htmlFor="webhook_name" required>Name</Label>
            <Input
              id="webhook_name"
              placeholder="My Webhook"
              error={!!webhookForm.formState.errors.name}
              {...webhookForm.register('name')}
            />
          </div>
          <div>
            <Label htmlFor="webhook_url" required>URL</Label>
            <Input
              id="webhook_url"
              placeholder="https://example.com/webhook"
              error={!!webhookForm.formState.errors.url}
              {...webhookForm.register('url')}
            />
          </div>
          <div>
            <Label required>Events</Label>
            <div className="space-y-2 mt-2">
              {webhookEvents.map((event) => (
                <label key={event.value} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    value={event.value}
                    {...webhookForm.register('events')}
                    className="rounded border-neutral-300"
                  />
                  <span className="text-sm">{event.label}</span>
                </label>
              ))}
            </div>
          </div>
          <ModalFooter>
            <Button variant="outline" onClick={() => setShowAddWebhook(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={createWebhook.isPending}>
              Add Webhook
            </Button>
          </ModalFooter>
        </form>
      </Modal>

      {/* Delete API Key Confirmation */}
      <ConfirmModal
        isOpen={!!deleteApiKeyProvider}
        onClose={() => setDeleteApiKeyProvider(null)}
        onConfirm={handleDeleteApiKey}
        title="Delete API Key"
        message={`Are you sure you want to delete the ${deleteApiKeyProvider} API key?`}
        confirmText="Delete"
        variant="danger"
        isLoading={deleteApiKey.isPending}
      />

      {/* Delete Webhook Confirmation */}
      <ConfirmModal
        isOpen={!!deleteWebhookId}
        onClose={() => setDeleteWebhookId(null)}
        onConfirm={handleDeleteWebhook}
        title="Delete Webhook"
        message="Are you sure you want to delete this webhook?"
        confirmText="Delete"
        variant="danger"
        isLoading={deleteWebhook.isPending}
      />
    </div>
  );
}
