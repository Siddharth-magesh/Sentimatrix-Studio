'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { Subscription, UsageStats, Plan, Invoice } from '@/lib/api';

// Query keys
export const billingKeys = {
  all: ['billing'] as const,
  subscription: () => [...billingKeys.all, 'subscription'] as const,
  usage: (period?: string) => [...billingKeys.all, 'usage', period] as const,
  plans: () => [...billingKeys.all, 'plans'] as const,
  invoices: () => [...billingKeys.all, 'invoices'] as const,
};

/**
 * Hook to fetch current subscription info.
 */
export function useSubscription() {
  return useQuery({
    queryKey: billingKeys.subscription(),
    queryFn: () => api.getSubscription(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch usage statistics.
 */
export function useUsageStats(period?: 'day' | 'week' | 'month' | 'year') {
  return useQuery({
    queryKey: billingKeys.usage(period),
    queryFn: () => api.getUsageStats({ period }),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Hook to fetch available plans.
 */
export function usePlans() {
  return useQuery({
    queryKey: billingKeys.plans(),
    queryFn: () => api.getPlans(),
    staleTime: 30 * 60 * 1000, // 30 minutes - plans don't change often
  });
}

/**
 * Hook to fetch invoices/billing history.
 */
export function useInvoices() {
  return useQuery({
    queryKey: billingKeys.invoices(),
    queryFn: () => api.getInvoices(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to create checkout session for upgrading plan.
 */
export function useCreateCheckoutSession() {
  return useMutation({
    mutationFn: (planId: string) => api.createCheckoutSession(planId),
    onSuccess: (data) => {
      // Redirect to checkout URL
      window.location.href = data.checkout_url;
    },
  });
}

/**
 * Hook to cancel subscription.
 */
export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => api.cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription() });
    },
  });
}

/**
 * Hook to resume cancelled subscription.
 */
export function useResumeSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => api.resumeSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: billingKeys.subscription() });
    },
  });
}

/**
 * Hook to get customer portal URL.
 */
export function useCustomerPortal() {
  return useMutation({
    mutationFn: () => api.getCustomerPortalUrl(),
    onSuccess: (data) => {
      window.open(data.portal_url, '_blank');
    },
  });
}
