'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useAuthStore } from '@/stores/auth';
import { useToast } from '@/components/ui';
import { useQueryClient } from '@tanstack/react-query';
import { scrapeKeys } from './use-scrape';
import { resultKeys } from './use-results';
import { projectKeys } from './use-projects';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface JobProgressEvent {
  type: 'job.progress';
  project_id: string;
  job_id: string;
  progress: number;
  status: string;
  message?: string;
  stats?: {
    targets_processed: number;
    results_scraped: number;
    errors: number;
  };
}

export interface JobCompletedEvent {
  type: 'job.completed';
  project_id: string;
  job_id: string;
  stats: {
    targets_processed: number;
    results_scraped: number;
    errors: number;
  };
}

export interface JobFailedEvent {
  type: 'job.failed';
  project_id: string;
  job_id: string;
  error: string;
}

export type WebSocketEvent = JobProgressEvent | JobCompletedEvent | JobFailedEvent;

export interface UseWebSocketOptions {
  onProgress?: (event: JobProgressEvent) => void;
  onCompleted?: (event: JobCompletedEvent) => void;
  onFailed?: (event: JobFailedEvent) => void;
  autoConnect?: boolean;
}

export function useWebSocket(projectId?: string, options: UseWebSocketOptions = {}) {
  const { accessToken } = useAuthStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!accessToken) {
      console.warn('Cannot connect WebSocket: No access token');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');

    const wsUrl = projectId
      ? `${WS_BASE_URL}/api/v1/ws/jobs/${projectId}?token=${accessToken}`
      : `${WS_BASE_URL}/api/v1/ws?token=${accessToken}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      reconnectAttempts.current = 0;
      console.log('WebSocket connected');

      // Subscribe to project if not using project-specific endpoint
      if (projectId && !wsUrl.includes('/jobs/')) {
        ws.send(JSON.stringify({ action: 'subscribe', project_id: projectId }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketEvent | { type: string };

        switch (data.type) {
          case 'job.progress':
            options.onProgress?.(data as JobProgressEvent);
            // Invalidate scrape job query
            const progressEvent = data as JobProgressEvent;
            queryClient.invalidateQueries({
              queryKey: scrapeKeys.job(progressEvent.project_id, progressEvent.job_id),
            });
            break;

          case 'job.completed':
            const completedEvent = data as JobCompletedEvent;
            options.onCompleted?.(completedEvent);
            toast.success(`Scrape job completed: ${completedEvent.stats.results_scraped} results`);
            // Invalidate queries
            queryClient.invalidateQueries({
              queryKey: scrapeKeys.jobs(completedEvent.project_id),
            });
            queryClient.invalidateQueries({
              queryKey: resultKeys.lists(),
            });
            queryClient.invalidateQueries({
              queryKey: projectKeys.detail(completedEvent.project_id),
            });
            break;

          case 'job.failed':
            const failedEvent = data as JobFailedEvent;
            options.onFailed?.(failedEvent);
            toast.error(`Scrape job failed: ${failedEvent.error}`);
            queryClient.invalidateQueries({
              queryKey: scrapeKeys.jobs(failedEvent.project_id),
            });
            break;

          case 'pong':
          case 'connected':
          case 'subscribed':
          case 'unsubscribed':
            // Acknowledgment messages, no action needed
            break;

          default:
            console.log('Unknown WebSocket message:', data);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('error');
    };

    ws.onclose = (event) => {
      setStatus('disconnected');
      wsRef.current = null;

      // Auto-reconnect with exponential backoff
      if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;
        console.log(`WebSocket closed, reconnecting in ${delay}ms...`);
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      }
    };
  }, [accessToken, projectId, options, queryClient, toast]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  const subscribe = useCallback((newProjectId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', project_id: newProjectId }));
    }
  }, []);

  const unsubscribe = useCallback((existingProjectId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'unsubscribe', project_id: existingProjectId }));
    }
  }, []);

  const ping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'ping' }));
    }
  }, []);

  // Auto-connect on mount if requested
  useEffect(() => {
    if (options.autoConnect !== false && accessToken) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect, options.autoConnect, accessToken]);

  // Keep-alive ping
  useEffect(() => {
    if (status !== 'connected') return;

    const pingInterval = setInterval(ping, 30000);
    return () => clearInterval(pingInterval);
  }, [status, ping]);

  return {
    status,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    ping,
    isConnected: status === 'connected',
  };
}

// Simple hook for job progress tracking
export function useJobProgress(projectId: string, jobId: string) {
  const [progress, setProgress] = useState(0);
  const [status, setJobStatus] = useState<string>('pending');
  const [stats, setStats] = useState<JobProgressEvent['stats'] | null>(null);

  useWebSocket(projectId, {
    onProgress: (event) => {
      if (event.job_id === jobId) {
        setProgress(event.progress);
        setJobStatus(event.status);
        if (event.stats) setStats(event.stats);
      }
    },
    onCompleted: (event) => {
      if (event.job_id === jobId) {
        setProgress(100);
        setJobStatus('completed');
        setStats(event.stats);
      }
    },
    onFailed: (event) => {
      if (event.job_id === jobId) {
        setJobStatus('failed');
      }
    },
  });

  return { progress, status, stats };
}
