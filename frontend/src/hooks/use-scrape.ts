'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui';
import { projectKeys } from './use-projects';
import { resultKeys } from './use-results';

// Query keys
export const scrapeKeys = {
  all: ['scrape'] as const,
  jobs: (projectId: string) => [...scrapeKeys.all, 'jobs', projectId] as const,
  job: (projectId: string, jobId: string) => [...scrapeKeys.jobs(projectId), jobId] as const,
};

// Get scrape jobs for a project
export function useScrapeJobs(projectId: string) {
  return useQuery({
    queryKey: scrapeKeys.jobs(projectId),
    queryFn: () => api.getScrapeJobs(projectId),
    enabled: !!projectId,
  });
}

// Get single scrape job
export function useScrapeJob(projectId: string, jobId: string) {
  return useQuery({
    queryKey: scrapeKeys.job(projectId, jobId),
    queryFn: () => api.getScrapeJob(projectId, jobId),
    enabled: !!projectId && !!jobId,
    refetchInterval: (query) => {
      // Refetch every 2 seconds if job is running
      const data = query.state.data;
      return data?.status === 'running' || data?.status === 'pending' ? 2000 : false;
    },
  });
}

// Start scrape job
export function useStartScrape() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (projectId: string) => api.startScrape(projectId),
    onSuccess: (job, projectId) => {
      queryClient.invalidateQueries({ queryKey: scrapeKeys.jobs(projectId) });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
      toast.success('Scrape job started');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to start scrape job');
    },
  });
}

// Cancel scrape job
export function useCancelScrape() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ projectId, jobId }: { projectId: string; jobId: string }) =>
      api.cancelScrapeJob(projectId, jobId),
    onSuccess: (_, { projectId, jobId }) => {
      queryClient.invalidateQueries({ queryKey: scrapeKeys.job(projectId, jobId) });
      queryClient.invalidateQueries({ queryKey: scrapeKeys.jobs(projectId) });
      toast.success('Scrape job cancelled');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to cancel scrape job');
    },
  });
}
