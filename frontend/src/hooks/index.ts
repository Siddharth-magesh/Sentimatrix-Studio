// Auth
export { useAuthGuard } from './use-auth-guard';

// Projects
export {
  useProjects,
  useProject,
  useProjectStats,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  projectKeys,
} from './use-projects';

// Targets
export {
  useTargets,
  useAddTarget,
  useAddTargetsBulk,
  useDeleteTarget,
  targetKeys,
} from './use-targets';

// Results
export {
  useResults,
  useResult,
  useAnalyticsSummary,
  useSentimentTimeline,
  useGlobalSentimentTimeline,
  useDeleteResult,
  useExportResults,
  resultKeys,
} from './use-results';

// Scrape
export {
  useScrapeJobs,
  useScrapeJob,
  useStartScrape,
  useCancelScrape,
  scrapeKeys,
} from './use-scrape';

// Settings
export {
  // API Keys
  useApiKeys,
  useAddApiKey,
  useDeleteApiKey,
  useTestApiKey,
  apiKeyKeys,
  // Presets
  usePresets,
  usePreset,
  useCreatePreset,
  useUpdatePreset,
  useDeletePreset,
  presetKeys,
  // LLM
  useLLMProviders,
  llmKeys,
  // Webhooks
  useWebhooks,
  useCreateWebhook,
  useUpdateWebhook,
  useDeleteWebhook,
  useTestWebhook,
  webhookKeys,
  // Schedules
  useSchedules,
  useProjectSchedule,
  useSetProjectSchedule,
  useToggleSchedule,
  useDeleteSchedule,
  scheduleKeys,
} from './use-settings';

// Dashboard
export { useDashboard, useDashboardSummary, dashboardKeys } from './use-dashboard';

// Billing
export {
  useSubscription,
  useUsageStats,
  usePlans,
  useInvoices,
  useCreateCheckoutSession,
  useCancelSubscription,
  useResumeSubscription,
  useCustomerPortal,
  billingKeys,
} from './use-billing';

// WebSocket
export {
  useWebSocket,
  useJobProgress,
  type WebSocketStatus,
  type JobProgressEvent,
  type JobCompletedEvent,
  type JobFailedEvent,
  type WebSocketEvent,
} from './use-websocket';
