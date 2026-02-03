import { renderHook, act } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useAuthGuard } from '@/hooks/use-auth-guard';
import { useAuthStore } from '@/stores/auth';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the auth store
jest.mock('@/stores/auth', () => ({
  useAuthStore: jest.fn(),
}));

const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  refresh: jest.fn(),
};

const mockUseRouter = useRouter as jest.Mock;
const mockUseAuthStore = useAuthStore as jest.Mock;

describe('useAuthGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRouter.mockReturnValue(mockRouter);
  });

  it('calls initialize on mount', () => {
    const initialize = jest.fn();
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      initialize,
    });

    renderHook(() => useAuthGuard());

    expect(initialize).toHaveBeenCalledTimes(1);
  });

  it('returns isAuthenticated and isLoading', () => {
    const initialize = jest.fn();
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      initialize,
    });

    const { result } = renderHook(() => useAuthGuard());

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);
  });

  it('redirects to login when not authenticated and not loading', () => {
    const initialize = jest.fn();
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      initialize,
    });

    renderHook(() => useAuthGuard());

    expect(mockRouter.push).toHaveBeenCalledWith('/auth/login');
  });

  it('does not redirect when loading', () => {
    const initialize = jest.fn();
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
      initialize,
    });

    renderHook(() => useAuthGuard());

    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('does not redirect when authenticated', () => {
    const initialize = jest.fn();
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      initialize,
    });

    renderHook(() => useAuthGuard());

    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('redirects when authentication state changes to unauthenticated', () => {
    const initialize = jest.fn();

    // Initially authenticated
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      initialize,
    });

    const { rerender } = renderHook(() => useAuthGuard());

    expect(mockRouter.push).not.toHaveBeenCalled();

    // Change to unauthenticated
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      initialize,
    });

    rerender();

    expect(mockRouter.push).toHaveBeenCalledWith('/auth/login');
  });

  it('handles transition from loading to authenticated', () => {
    const initialize = jest.fn();

    // Initially loading
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
      initialize,
    });

    const { rerender } = renderHook(() => useAuthGuard());

    expect(mockRouter.push).not.toHaveBeenCalled();

    // Transition to authenticated
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      initialize,
    });

    rerender();

    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('handles transition from loading to unauthenticated', () => {
    const initialize = jest.fn();

    // Initially loading
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
      initialize,
    });

    const { rerender } = renderHook(() => useAuthGuard());

    expect(mockRouter.push).not.toHaveBeenCalled();

    // Transition to unauthenticated
    mockUseAuthStore.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      initialize,
    });

    rerender();

    expect(mockRouter.push).toHaveBeenCalledWith('/auth/login');
  });
});
