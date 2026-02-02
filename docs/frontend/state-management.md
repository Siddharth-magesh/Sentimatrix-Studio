# State Management

## Overview

Sentimatrix Studio uses a combination of React Query for server state and Zustand for client state management.

## Server State (React Query)

Server state refers to data that originates from the server and needs to be synchronized.

### Configuration

```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

### Query Hooks

```typescript
// hooks/useProjects.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useProjects(options?: { status?: string }) {
  return useQuery({
    queryKey: ['projects', options],
    queryFn: () => api.projects.list(options),
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => api.projects.get(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.projects.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectData }) =>
      api.projects.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['project', id] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.projects.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
```

### Results Hook

```typescript
// hooks/useResults.ts
import { useInfiniteQuery } from '@tanstack/react-query';

export function useResults(projectId: string, filters?: ResultFilters) {
  return useInfiniteQuery({
    queryKey: ['results', projectId, filters],
    queryFn: ({ pageParam = 1 }) =>
      api.results.list(projectId, { ...filters, page: pageParam }),
    getNextPageParam: (lastPage) =>
      lastPage.meta.pagination.has_next
        ? lastPage.meta.pagination.page + 1
        : undefined,
  });
}
```

---

## Client State (Zustand)

Client state refers to UI state that doesn't need server synchronization.

### Auth Store

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;

  setUser: (user: User | null) => void;
  setAccessToken: (token: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      setUser: (user) =>
        set({ user, isAuthenticated: !!user }),

      setAccessToken: (accessToken) =>
        set({ accessToken }),

      logout: () =>
        set({ user: null, accessToken: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }), // Don't persist token
    }
  )
);
```

### UI Store

```typescript
// stores/uiStore.ts
import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  activeModal: string | null;
  notifications: Notification[];

  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  theme: 'system',
  activeModal: null,
  notifications: [],

  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setTheme: (theme) => set({ theme }),

  openModal: (modalId) => set({ activeModal: modalId }),

  closeModal: () => set({ activeModal: null }),

  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: crypto.randomUUID() },
      ],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}));
```

### Project Configuration Store

```typescript
// stores/projectConfigStore.ts
import { create } from 'zustand';

interface ProjectConfig {
  name: string;
  description: string;
  preset: string;
  scrapers: {
    platforms: string[];
    commercial: string | null;
  };
  llm: {
    provider: string;
    model: string;
    apiKey: string;
  };
  targets: Target[];
  schedule: ScheduleConfig;
}

interface ProjectConfigState {
  config: Partial<ProjectConfig>;
  currentStep: number;

  setConfig: (config: Partial<ProjectConfig>) => void;
  updateConfig: (updates: Partial<ProjectConfig>) => void;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  reset: () => void;
}

const initialConfig: Partial<ProjectConfig> = {
  name: '',
  description: '',
  preset: 'standard',
  scrapers: { platforms: [], commercial: null },
  targets: [],
};

export const useProjectConfigStore = create<ProjectConfigState>((set) => ({
  config: initialConfig,
  currentStep: 0,

  setConfig: (config) => set({ config }),

  updateConfig: (updates) =>
    set((state) => ({
      config: { ...state.config, ...updates },
    })),

  setStep: (step) => set({ currentStep: step }),

  nextStep: () =>
    set((state) => ({ currentStep: state.currentStep + 1 })),

  prevStep: () =>
    set((state) => ({ currentStep: Math.max(0, state.currentStep - 1) })),

  reset: () => set({ config: initialConfig, currentStep: 0 }),
}));
```

---

## WebSocket State

Real-time updates via WebSocket.

```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { useQueryClient } from '@tanstack/react-query';

interface WebSocketMessage {
  type: string;
  data: unknown;
}

export function useWebSocket(projectId?: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const accessToken = useAuthStore((state) => state.accessToken);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!accessToken) return;

    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_WS_URL}/ws?token=${accessToken}`
    );

    ws.onopen = () => {
      if (projectId) {
        ws.send(JSON.stringify({ type: 'subscribe', project_id: projectId }));
      }
    };

    ws.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'scrape.progress':
          // Update scrape job status
          queryClient.invalidateQueries({ queryKey: ['scrapeJobs'] });
          break;

        case 'scrape.completed':
          // Refresh results
          queryClient.invalidateQueries({ queryKey: ['results', projectId] });
          queryClient.invalidateQueries({ queryKey: ['project', projectId] });
          break;

        case 'analysis.completed':
          // Refresh analysis data
          queryClient.invalidateQueries({ queryKey: ['results', projectId] });
          break;
      }
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [accessToken, projectId, queryClient]);

  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return { send };
}
```

---

## Form State

Form state management with React Hook Form.

```typescript
// Example: Project creation form
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCreateProject } from '@/hooks/useProjects';

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
  preset: z.enum(['starter', 'standard', 'advanced', 'budget']),
  platforms: z.array(z.string()).min(1, 'Select at least one platform'),
});

type FormData = z.infer<typeof schema>;

export function CreateProjectForm() {
  const createProject = useCreateProject();

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      description: '',
      preset: 'standard',
      platforms: [],
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      await createProject.mutateAsync(data);
      // Success handling
    } catch (error) {
      // Error handling
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

---

## State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Components                             │
├─────────────────────────────────────────────────────────────┤
│                           │                                  │
│    ┌──────────────────────┼──────────────────────┐          │
│    │                      │                      │          │
│    ▼                      ▼                      ▼          │
│ ┌──────────┐        ┌──────────┐          ┌──────────┐     │
│ │ Zustand  │        │  React   │          │   Form   │     │
│ │  Store   │        │  Query   │          │  State   │     │
│ │          │        │          │          │          │     │
│ │ UI State │        │  Server  │          │  Local   │     │
│ │ Auth     │        │  State   │          │  Input   │     │
│ └──────────┘        └──────────┘          └──────────┘     │
│       │                   │                     │           │
│       │                   │                     │           │
│       │                   ▼                     │           │
│       │            ┌──────────┐                │           │
│       │            │   API    │                │           │
│       │            │  Client  │                │           │
│       │            └──────────┘                │           │
│       │                   │                     │           │
│       │                   ▼                     │           │
│       │            ┌──────────┐                │           │
│       │            │  Backend │                │           │
│       │            │   API    │                │           │
│       │            └──────────┘                │           │
│       │                   │                     │           │
│       │                   │                     │           │
│       ▼                   ▼                     ▼           │
│ ┌─────────────────────────────────────────────────────┐    │
│ │              WebSocket (Real-time Updates)          │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
