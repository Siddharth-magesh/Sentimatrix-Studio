'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, CreatePresetData, CreateWebhookData, ScheduleConfig } from '@/lib/api';
import { useToast } from '@/components/ui';

// ============================================
// API Keys
// ============================================

export const apiKeyKeys = {
  all: ['api-keys'] as const,
  list: () => [...apiKeyKeys.all, 'list'] as const,
};

export function useApiKeys() {
  return useQuery({
    queryKey: apiKeyKeys.list(),
    queryFn: () => api.getApiKeys(),
  });
}

export function useAddApiKey() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: { provider: string; api_key: string }) => api.addApiKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.list() });
      toast.success('API key added successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to add API key');
    },
  });
}

export function useDeleteApiKey() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (provider: string) => api.deleteApiKey(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.list() });
      toast.success('API key deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete API key');
    },
  });
}

export function useTestApiKey() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: (provider: string) => api.testApiKey(provider),
    onSuccess: (result, provider) => {
      if (result.success) {
        toast.success(`${provider} API key is valid (${result.latency_ms?.toFixed(0)}ms)`);
      } else {
        toast.error(`${provider} API key test failed: ${result.error}`);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to test API key');
    },
  });
}

// ============================================
// Presets
// ============================================

export const presetKeys = {
  all: ['presets'] as const,
  list: () => [...presetKeys.all, 'list'] as const,
  detail: (id: string) => [...presetKeys.all, 'detail', id] as const,
};

export function usePresets() {
  return useQuery({
    queryKey: presetKeys.list(),
    queryFn: () => api.getPresets(),
  });
}

export function usePreset(id: string) {
  return useQuery({
    queryKey: presetKeys.detail(id),
    queryFn: () => api.getPreset(id),
    enabled: !!id,
  });
}

export function useCreatePreset() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: CreatePresetData) => api.createPreset(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: presetKeys.list() });
      toast.success('Preset created successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create preset');
    },
  });
}

export function useUpdatePreset() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreatePresetData> }) =>
      api.updatePreset(id, data),
    onSuccess: (preset) => {
      queryClient.invalidateQueries({ queryKey: presetKeys.list() });
      queryClient.setQueryData(presetKeys.detail(preset.id), preset);
      toast.success('Preset updated successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update preset');
    },
  });
}

export function useDeletePreset() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => api.deletePreset(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: presetKeys.list() });
      queryClient.removeQueries({ queryKey: presetKeys.detail(id) });
      toast.success('Preset deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete preset');
    },
  });
}

// ============================================
// LLM Providers
// ============================================

export const llmKeys = {
  providers: ['llm-providers'] as const,
};

export function useLLMProviders() {
  return useQuery({
    queryKey: llmKeys.providers,
    queryFn: () => api.getLLMProviders(),
  });
}

// ============================================
// Webhooks
// ============================================

export const webhookKeys = {
  all: ['webhooks'] as const,
  list: () => [...webhookKeys.all, 'list'] as const,
  detail: (id: string) => [...webhookKeys.all, 'detail', id] as const,
};

export function useWebhooks() {
  return useQuery({
    queryKey: webhookKeys.list(),
    queryFn: () => api.getWebhooks(),
  });
}

export function useCreateWebhook() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: CreateWebhookData) => api.createWebhook(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: webhookKeys.list() });
      toast.success('Webhook created successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create webhook');
    },
  });
}

export function useUpdateWebhook() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateWebhookData> }) =>
      api.updateWebhook(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: webhookKeys.list() });
      toast.success('Webhook updated successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update webhook');
    },
  });
}

export function useDeleteWebhook() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => api.deleteWebhook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: webhookKeys.list() });
      toast.success('Webhook deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete webhook');
    },
  });
}

export function useTestWebhook() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => api.testWebhook(id),
    onSuccess: (result) => {
      if (result.success) {
        toast.success(`Webhook test successful (status: ${result.status_code})`);
      } else {
        toast.error(`Webhook test failed: ${result.error}`);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to test webhook');
    },
  });
}

// ============================================
// Schedules
// ============================================

export const scheduleKeys = {
  all: ['schedules'] as const,
  list: () => [...scheduleKeys.all, 'list'] as const,
  project: (projectId: string) => [...scheduleKeys.all, 'project', projectId] as const,
};

export function useSchedules() {
  return useQuery({
    queryKey: scheduleKeys.list(),
    queryFn: () => api.getSchedules(),
  });
}

export function useProjectSchedule(projectId: string) {
  return useQuery({
    queryKey: scheduleKeys.project(projectId),
    queryFn: () => api.getProjectSchedule(projectId),
    enabled: !!projectId,
  });
}

export function useSetProjectSchedule() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: ScheduleConfig }) =>
      api.setProjectSchedule(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: scheduleKeys.project(projectId) });
      queryClient.invalidateQueries({ queryKey: scheduleKeys.list() });
      toast.success('Schedule updated successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update schedule');
    },
  });
}

export function useToggleSchedule() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (projectId: string) => api.toggleSchedule(projectId),
    onSuccess: (schedule, projectId) => {
      queryClient.invalidateQueries({ queryKey: scheduleKeys.project(projectId) });
      queryClient.invalidateQueries({ queryKey: scheduleKeys.list() });
      toast.success(`Schedule ${schedule.enabled ? 'enabled' : 'disabled'}`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to toggle schedule');
    },
  });
}

export function useDeleteSchedule() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (projectId: string) => api.deleteSchedule(projectId),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: scheduleKeys.project(projectId) });
      queryClient.invalidateQueries({ queryKey: scheduleKeys.list() });
      toast.success('Schedule deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete schedule');
    },
  });
}
