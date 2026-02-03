import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import {
  useSubscription,
  useUsageStats,
  usePlans,
  useInvoices,
  useCreateCheckoutSession,
  useCancelSubscription,
  useResumeSubscription,
  billingKeys,
} from '@/hooks/use-billing';
import { api } from '@/lib/api';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    getSubscription: jest.fn(),
    getUsageStats: jest.fn(),
    getPlans: jest.fn(),
    getInvoices: jest.fn(),
    createCheckoutSession: jest.fn(),
    cancelSubscription: jest.fn(),
    resumeSubscription: jest.fn(),
    getCustomerPortalUrl: jest.fn(),
  },
}));

const mockApi = api as jest.Mocked<typeof api>;

// Create a wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('billingKeys', () => {
  it('generates correct key for all billing', () => {
    expect(billingKeys.all).toEqual(['billing']);
  });

  it('generates correct key for subscription', () => {
    expect(billingKeys.subscription()).toEqual(['billing', 'subscription']);
  });

  it('generates correct key for usage', () => {
    expect(billingKeys.usage('month')).toEqual(['billing', 'usage', 'month']);
  });

  it('generates correct key for plans', () => {
    expect(billingKeys.plans()).toEqual(['billing', 'plans']);
  });

  it('generates correct key for invoices', () => {
    expect(billingKeys.invoices()).toEqual(['billing', 'invoices']);
  });
});

describe('useSubscription', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches subscription successfully', async () => {
    const mockSubscription = {
      id: 'sub_123',
      plan_id: 'plan_pro',
      plan_name: 'Pro',
      status: 'active',
      current_period_start: '2024-01-01',
      current_period_end: '2024-02-01',
    };

    mockApi.getSubscription.mockResolvedValueOnce(mockSubscription);

    const { result } = renderHook(() => useSubscription(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockSubscription);
    expect(mockApi.getSubscription).toHaveBeenCalled();
  });

  it('handles error state', async () => {
    mockApi.getSubscription.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSubscription(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useUsageStats', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches usage stats successfully', async () => {
    const mockUsage = {
      period: { start: '2024-01-01', end: '2024-01-31' },
      projects: { used: 5, limit: 10, percentage: 50 },
      results: { used: 1000, limit: 5000, percentage: 20 },
      api_calls: { used: 100, limit: 1000, percentage: 10 },
      storage_mb: { used: 50, limit: 500, percentage: 10 },
      scrape_jobs: { used: 3, limit: 10, percentage: 30 },
      history: [],
    };

    mockApi.getUsageStats.mockResolvedValueOnce(mockUsage);

    const { result } = renderHook(() => useUsageStats('month'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockUsage);
    expect(mockApi.getUsageStats).toHaveBeenCalledWith({ period: 'month' });
  });

  it('passes different periods correctly', async () => {
    mockApi.getUsageStats.mockResolvedValueOnce({} as any);

    renderHook(() => useUsageStats('day'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(mockApi.getUsageStats).toHaveBeenCalledWith({ period: 'day' });
    });
  });
});

describe('usePlans', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches plans successfully', async () => {
    const mockPlans = [
      {
        id: 'free',
        name: 'Free',
        price_monthly: 0,
        price_yearly: 0,
        features: [],
        limits: {},
      },
      {
        id: 'pro',
        name: 'Pro',
        price_monthly: 29,
        price_yearly: 290,
        features: [],
        limits: {},
        is_popular: true,
      },
    ];

    mockApi.getPlans.mockResolvedValueOnce(mockPlans);

    const { result } = renderHook(() => usePlans(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPlans);
    expect(result.current.data).toHaveLength(2);
  });
});

describe('useInvoices', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches invoices successfully', async () => {
    const mockInvoices = [
      {
        id: 'inv_123',
        number: 'INV-001',
        amount: 2900,
        currency: 'usd',
        status: 'paid',
        period_start: '2024-01-01',
        period_end: '2024-01-31',
        created_at: '2024-01-01',
      },
    ];

    mockApi.getInvoices.mockResolvedValueOnce(mockInvoices);

    const { result } = renderHook(() => useInvoices(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockInvoices);
  });
});

describe('useCreateCheckoutSession', () => {
  const originalLocation = window.location;

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.location
    delete (window as any).location;
    window.location = { ...originalLocation, href: '' };
  });

  afterEach(() => {
    window.location = originalLocation;
  });

  it('creates checkout session and redirects', async () => {
    const mockCheckout = { checkout_url: 'https://checkout.stripe.com/session123' };
    mockApi.createCheckoutSession.mockResolvedValueOnce(mockCheckout);

    const { result } = renderHook(() => useCreateCheckoutSession(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('plan_pro');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.createCheckoutSession).toHaveBeenCalledWith('plan_pro');
    expect(window.location.href).toBe(mockCheckout.checkout_url);
  });

  it('handles error state', async () => {
    mockApi.createCheckoutSession.mockRejectedValueOnce(new Error('Payment failed'));

    const { result } = renderHook(() => useCreateCheckoutSession(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('plan_pro');

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useCancelSubscription', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('cancels subscription successfully', async () => {
    const mockResult = { success: true, cancels_at: '2024-02-01' };
    mockApi.cancelSubscription.mockResolvedValueOnce(mockResult);

    const { result } = renderHook(() => useCancelSubscription(), {
      wrapper: createWrapper(),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.cancelSubscription).toHaveBeenCalled();
  });

  it('handles cancel error', async () => {
    mockApi.cancelSubscription.mockRejectedValueOnce(new Error('Cancel failed'));

    const { result } = renderHook(() => useCancelSubscription(), {
      wrapper: createWrapper(),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useResumeSubscription', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('resumes subscription successfully', async () => {
    const mockSubscription = {
      id: 'sub_123',
      plan_id: 'plan_pro',
      status: 'active',
      cancel_at_period_end: false,
    };
    mockApi.resumeSubscription.mockResolvedValueOnce(mockSubscription);

    const { result } = renderHook(() => useResumeSubscription(), {
      wrapper: createWrapper(),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.resumeSubscription).toHaveBeenCalled();
  });

  it('handles resume error', async () => {
    mockApi.resumeSubscription.mockRejectedValueOnce(new Error('Resume failed'));

    const { result } = renderHook(() => useResumeSubscription(), {
      wrapper: createWrapper(),
    });

    result.current.mutate();

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
