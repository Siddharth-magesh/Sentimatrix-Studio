'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  data: () => [...dashboardKeys.all, 'data'] as const,
  summary: () => [...dashboardKeys.all, 'summary'] as const,
};

export function useDashboard() {
  return useQuery({
    queryKey: dashboardKeys.data(),
    queryFn: () => api.getDashboard(),
  });
}

export function useDashboardSummary() {
  return useQuery({
    queryKey: dashboardKeys.summary(),
    queryFn: () => api.getDashboardSummary(),
  });
}
