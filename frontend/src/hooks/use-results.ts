'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui';

// Query keys
export const resultKeys = {
  all: ['results'] as const,
  lists: () => [...resultKeys.all, 'list'] as const,
  list: (projectId: string, filters: Record<string, unknown>) =>
    [...resultKeys.lists(), projectId, filters] as const,
  details: () => [...resultKeys.all, 'detail'] as const,
  detail: (projectId: string, id: string) => [...resultKeys.details(), projectId, id] as const,
  analytics: (projectId: string) => [...resultKeys.all, 'analytics', projectId] as const,
  timeline: (projectId: string, params: Record<string, unknown>) =>
    [...resultKeys.analytics(projectId), 'timeline', params] as const,
};

// Get results for a project (or all projects if projectId is 'all')
export function useResults(
  projectId: string,
  params?: {
    page?: number;
    limit?: number;
    sentiment?: string;
    platform?: string;
    search?: string;
    start_date?: string;
    end_date?: string;
  }
) {
  const isAllProjects = projectId === 'all';

  return useQuery({
    queryKey: resultKeys.list(projectId, params || {}),
    queryFn: () => isAllProjects
      ? api.getAllResults(params)
      : api.getResults(projectId, params),
    enabled: !!projectId && projectId !== 'undefined',
  });
}

// Get single result
export function useResult(projectId: string, resultId: string) {
  return useQuery({
    queryKey: resultKeys.detail(projectId, resultId),
    queryFn: () => api.getResult(projectId, resultId),
    enabled: !!projectId && !!resultId && projectId !== 'undefined' && resultId !== 'undefined',
  });
}

// Get analytics summary
export function useAnalyticsSummary(projectId: string) {
  return useQuery({
    queryKey: resultKeys.analytics(projectId),
    queryFn: () => api.getAnalyticsSummary(projectId),
    enabled: !!projectId,
  });
}

// Get sentiment timeline (project-specific)
export function useSentimentTimeline(
  projectId: string,
  params?: { start_date?: string; end_date?: string; interval?: string }
) {
  return useQuery({
    queryKey: resultKeys.timeline(projectId, params || {}),
    queryFn: () => api.getSentimentTimeline(projectId, params),
    enabled: !!projectId,
  });
}

// Get global sentiment timeline for dashboard
export function useGlobalSentimentTimeline(
  params?: { days?: number; interval?: string }
) {
  return useQuery({
    queryKey: ['dashboard', 'timeline', params || {}],
    queryFn: () => api.getGlobalSentimentTimeline(params),
  });
}

// Delete result
export function useDeleteResult() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ projectId, resultId }: { projectId: string; resultId: string }) =>
      api.deleteResult(projectId, resultId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: resultKeys.lists() });
      queryClient.invalidateQueries({ queryKey: resultKeys.analytics(projectId) });
      toast.success('Result deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete result');
    },
  });
}

// Export results
export function useExportResults() {
  const toast = useToast();

  return useMutation({
    mutationFn: ({ projectId, format }: { projectId: string; format: 'csv' | 'json' | 'xlsx' }) =>
      api.exportResults(projectId, format),
    onSuccess: (blob, { format }) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `results.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Results exported successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to export results');
    },
  });
}
