'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui';
import { projectKeys } from './use-projects';

// Query keys
export const targetKeys = {
  all: ['targets'] as const,
  lists: () => [...targetKeys.all, 'list'] as const,
  list: (projectId: string) => [...targetKeys.lists(), projectId] as const,
};

// Get targets for a project
export function useTargets(projectId: string) {
  return useQuery({
    queryKey: targetKeys.list(projectId),
    queryFn: () => api.getTargets(projectId),
    enabled: !!projectId && projectId !== 'undefined',
  });
}

// Add target
export function useAddTarget() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: { url: string; name?: string } }) =>
      api.addTarget(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: targetKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
      toast.success('Target added successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to add target');
    },
  });
}

// Add multiple targets
export function useAddTargetsBulk() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ projectId, urls }: { projectId: string; urls: string[] }) =>
      api.addTargetsBulk(projectId, urls),
    onSuccess: (targets, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: targetKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
      toast.success(`${targets.length} targets added successfully`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to add targets');
    },
  });
}

// Delete target
export function useDeleteTarget() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ projectId, targetId }: { projectId: string; targetId: string }) =>
      api.deleteTarget(projectId, targetId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: targetKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
      toast.success('Target deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete target');
    },
  });
}
