import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import {
  useProjects,
  useProject,
  useProjectStats,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  projectKeys,
} from '@/hooks/use-projects';
import { api } from '@/lib/api';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    getProjects: jest.fn(),
    getProject: jest.fn(),
    getProjectStats: jest.fn(),
    createProject: jest.fn(),
    updateProject: jest.fn(),
    deleteProject: jest.fn(),
  },
}));

// Mock toast
jest.mock('@/components/ui', () => ({
  useToast: () => ({
    toast: {
      success: jest.fn(),
      error: jest.fn(),
    },
  }),
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

describe('projectKeys', () => {
  it('generates correct key for all projects', () => {
    expect(projectKeys.all).toEqual(['projects']);
  });

  it('generates correct key for lists', () => {
    expect(projectKeys.lists()).toEqual(['projects', 'list']);
  });

  it('generates correct key for list with filters', () => {
    const filters = { page: 1, search: 'test' };
    expect(projectKeys.list(filters)).toEqual(['projects', 'list', filters]);
  });

  it('generates correct key for details', () => {
    expect(projectKeys.details()).toEqual(['projects', 'detail']);
  });

  it('generates correct key for specific detail', () => {
    expect(projectKeys.detail('123')).toEqual(['projects', 'detail', '123']);
  });

  it('generates correct key for stats', () => {
    expect(projectKeys.stats('123')).toEqual(['projects', 'detail', '123', 'stats']);
  });
});

describe('useProjects', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches projects successfully', async () => {
    const mockProjects = {
      items: [
        { id: '1', name: 'Project 1' },
        { id: '2', name: 'Project 2' },
      ],
      total: 2,
      page: 1,
      pages: 1,
    };

    mockApi.getProjects.mockResolvedValueOnce(mockProjects);

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockProjects);
    expect(mockApi.getProjects).toHaveBeenCalledWith(undefined);
  });

  it('passes params to API', async () => {
    const params = { page: 2, limit: 10, search: 'test' };
    mockApi.getProjects.mockResolvedValueOnce({ items: [], total: 0, page: 2, pages: 0 });

    const { result } = renderHook(() => useProjects(params), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.getProjects).toHaveBeenCalledWith(params);
  });

  it('handles error state', async () => {
    mockApi.getProjects.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
  });
});

describe('useProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches single project successfully', async () => {
    const mockProject = { id: '123', name: 'Test Project' };
    mockApi.getProject.mockResolvedValueOnce(mockProject);

    const { result } = renderHook(() => useProject('123'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockProject);
    expect(mockApi.getProject).toHaveBeenCalledWith('123');
  });

  it('does not fetch when id is empty', () => {
    renderHook(() => useProject(''), {
      wrapper: createWrapper(),
    });

    expect(mockApi.getProject).not.toHaveBeenCalled();
  });
});

describe('useProjectStats', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches project stats successfully', async () => {
    const mockStats = {
      total_results: 100,
      sentiment_distribution: { positive: 60, negative: 20, neutral: 20 },
    };
    mockApi.getProjectStats.mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useProjectStats('123'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockStats);
    expect(mockApi.getProjectStats).toHaveBeenCalledWith('123');
  });

  it('does not fetch when id is empty', () => {
    renderHook(() => useProjectStats(''), {
      wrapper: createWrapper(),
    });

    expect(mockApi.getProjectStats).not.toHaveBeenCalled();
  });
});

describe('useCreateProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('creates project successfully', async () => {
    const newProject = { name: 'New Project', description: 'Test' };
    const createdProject = { id: '456', ...newProject };
    mockApi.createProject.mockResolvedValueOnce(createdProject);

    const { result } = renderHook(() => useCreateProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate(newProject);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.createProject).toHaveBeenCalledWith(newProject);
  });

  it('handles creation error', async () => {
    mockApi.createProject.mockRejectedValueOnce(new Error('Validation failed'));

    const { result } = renderHook(() => useCreateProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ name: '' });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useUpdateProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('updates project successfully', async () => {
    const updateData = { name: 'Updated Name' };
    const updatedProject = { id: '123', name: 'Updated Name' };
    mockApi.updateProject.mockResolvedValueOnce(updatedProject);

    const { result } = renderHook(() => useUpdateProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ id: '123', data: updateData });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.updateProject).toHaveBeenCalledWith('123', updateData);
  });

  it('handles update error', async () => {
    mockApi.updateProject.mockRejectedValueOnce(new Error('Update failed'));

    const { result } = renderHook(() => useUpdateProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ id: '123', data: { name: 'New Name' } });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useDeleteProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deletes project successfully', async () => {
    mockApi.deleteProject.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useDeleteProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('123');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.deleteProject).toHaveBeenCalledWith('123');
  });

  it('handles delete error', async () => {
    mockApi.deleteProject.mockRejectedValueOnce(new Error('Delete failed'));

    const { result } = renderHook(() => useDeleteProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('123');

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
