import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '@/lib/api';
import type { User, LoginCredentials, RegisterData } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  clearError: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await api.login(credentials);
          api.setAccessToken(tokens.access_token);
          const user = await api.getCurrentUser();

          set({
            user,
            accessToken: tokens.access_token,
            refreshToken: tokens.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Login failed',
          });
          throw error;
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          await api.register(data);
          // After registration, log the user in
          await get().login({ email: data.email, password: data.password });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Registration failed',
          });
          throw error;
        }
      },

      logout: async () => {
        const { refreshToken } = get();
        set({ isLoading: true });

        try {
          if (refreshToken) {
            await api.logout(refreshToken);
          }
        } catch {
          // Ignore logout errors
        } finally {
          api.setAccessToken(null);
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      refreshAuth: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return;

        try {
          const tokens = await api.refreshTokens(refreshToken);
          api.setAccessToken(tokens.access_token);

          set({
            accessToken: tokens.access_token,
            refreshToken: tokens.refresh_token,
          });
        } catch {
          // If refresh fails, logout
          await get().logout();
        }
      },

      clearError: () => set({ error: null }),

      initialize: async () => {
        const { accessToken, refreshToken } = get();

        if (!accessToken || !refreshToken) {
          set({ isAuthenticated: false });
          return;
        }

        api.setAccessToken(accessToken);

        try {
          const user = await api.getCurrentUser();
          set({ user, isAuthenticated: true });
        } catch {
          // Token might be expired, try refreshing
          try {
            await get().refreshAuth();
            const user = await api.getCurrentUser();
            set({ user, isAuthenticated: true });
          } catch {
            await get().logout();
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
