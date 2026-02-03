# UI Components

## Overview

This document describes the reusable UI components used throughout Sentimatrix Studio.

## Common Components

### Button

Primary action button with variants.

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
  onClick?: () => void;
}
```

**Usage:**

```tsx
<Button variant="primary" size="md" onClick={handleClick}>
  Create Project
</Button>

<Button variant="danger" loading={isDeleting}>
  Delete
</Button>
```

---

### Input

Text input with label and error handling.

```typescript
interface InputProps {
  label?: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'url';
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
}
```

**Usage:**

```tsx
<Input
  label="Project Name"
  placeholder="Enter project name"
  error={errors.name?.message}
  required
  {...register('name')}
/>
```

---

### Select

Dropdown select with search support.

```typescript
interface SelectProps {
  label?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
  searchable?: boolean;
  multiple?: boolean;
  error?: string;
}
```

**Usage:**

```tsx
<Select
  label="Platform"
  options={[
    { value: 'amazon', label: 'Amazon' },
    { value: 'steam', label: 'Steam' },
  ]}
  placeholder="Select platform"
/>
```

---

### Card

Container component with header, body, and footer sections.

```typescript
interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}
```

**Usage:**

```tsx
<Card hoverable onClick={() => navigate(`/projects/${id}`)}>
  <Card.Header>
    <h3>Project Name</h3>
    <Badge>Active</Badge>
  </Card.Header>
  <Card.Body>
    <p>Project description</p>
  </Card.Body>
  <Card.Footer>
    <span>150 results</span>
  </Card.Footer>
</Card>
```

---

### Badge

Status indicator component.

```typescript
interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md';
  children: ReactNode;
}
```

**Usage:**

```tsx
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>
```

---

### Modal

Dialog overlay component.

```typescript
interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: ReactNode;
}
```

**Usage:**

```tsx
<Modal open={isOpen} onClose={() => setIsOpen(false)} title="Confirm Delete">
  <Modal.Body>
    <p>Are you sure you want to delete this project?</p>
  </Modal.Body>
  <Modal.Footer>
    <Button variant="ghost" onClick={() => setIsOpen(false)}>
      Cancel
    </Button>
    <Button variant="danger" onClick={handleDelete}>
      Delete
    </Button>
  </Modal.Footer>
</Modal>
```

---

### Table

Data table with sorting and pagination.

```typescript
interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  sortable?: boolean;
  pagination?: PaginationProps;
  onRowClick?: (row: T) => void;
}

interface Column<T> {
  key: keyof T;
  header: string;
  render?: (value: T[keyof T], row: T) => ReactNode;
  sortable?: boolean;
  width?: string;
}
```

**Usage:**

```tsx
<Table
  columns={[
    { key: 'name', header: 'Name', sortable: true },
    { key: 'status', header: 'Status', render: (v) => <Badge>{v}</Badge> },
    { key: 'results', header: 'Results' },
  ]}
  data={projects}
  pagination={{ page: 1, limit: 20, total: 100 }}
  onRowClick={(row) => navigate(`/projects/${row.id}`)}
/>
```

---

### Skeleton

Loading placeholder components for content loading states.

```typescript
interface SkeletonProps {
  className?: string;
  variant?: 'default' | 'circular' | 'text';
  width?: string | number;
  height?: string | number;
}
```

**Pre-built Skeletons:**

```tsx
// Card skeleton
<SkeletonCard />

// Table skeleton
<SkeletonTable rows={5} columns={4} />

// Stats skeleton
<SkeletonStats count={4} />

// Chart skeleton
<SkeletonChart height={300} />

// Form skeleton
<SkeletonForm fields={5} />

// List skeleton
<SkeletonList items={5} />
```

---

### Spinner

Loading spinner with various sizes.

```typescript
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```

**Usage:**

```tsx
<Spinner size="md" />

// Loading overlay for containers
<LoadingOverlay isLoading={loading} text="Processing...">
  <Content />
</LoadingOverlay>

// Full page loader
<PageLoader text="Loading dashboard..." />

// Inline loader
<InlineLoader text="Saving..." size="sm" />
```

---

### Alert

Notification banner component.

```typescript
interface AlertProps {
  variant: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  children: ReactNode;
}
```

**Usage:**

```tsx
<Alert variant="success" title="Success" dismissible>
  Project created successfully.
</Alert>
```

---

### Tabs

Tab navigation component.

```typescript
interface TabsProps {
  tabs: { id: string; label: string; content: ReactNode }[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
}
```

**Usage:**

```tsx
<Tabs
  tabs={[
    { id: 'overview', label: 'Overview', content: <OverviewTab /> },
    { id: 'results', label: 'Results', content: <ResultsTab /> },
    { id: 'settings', label: 'Settings', content: <SettingsTab /> },
  ]}
  defaultTab="overview"
/>
```

---

## Dashboard Components

### StatsCard

Metric display card.

```typescript
interface StatsCardProps {
  title: string;
  value: string | number;
  change?: { value: number; trend: 'up' | 'down' };
  icon?: ReactNode;
}
```

**Usage:**

```tsx
<StatsCard
  title="Total Results"
  value={12500}
  change={{ value: 15, trend: 'up' }}
  icon={<ChartIcon />}
/>
```

---

### SentimentChart

Sentiment visualization chart.

```typescript
interface SentimentChartProps {
  data: { date: string; positive: number; neutral: number; negative: number }[];
  type?: 'line' | 'bar' | 'area';
  height?: number;
}
```

**Usage:**

```tsx
<SentimentChart data={trendData} type="area" height={300} />
```

---

### EmotionBreakdown

Emotion distribution visualization.

```typescript
interface EmotionBreakdownProps {
  data: { emotion: string; count: number }[];
  type?: 'pie' | 'bar' | 'radar';
}
```

**Usage:**

```tsx
<EmotionBreakdown data={emotionData} type="radar" />
```

---

## Form Components

### FormField

Form field wrapper with label and error.

```typescript
interface FormFieldProps {
  label: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  children: ReactNode;
}
```

**Usage:**

```tsx
<FormField label="API Key" error={errors.apiKey?.message} required>
  <Input type="password" {...register('apiKey')} />
</FormField>
```

---

### Stepper

Multi-step form navigation.

```typescript
interface StepperProps {
  steps: { id: string; label: string }[];
  currentStep: number;
  onChange?: (step: number) => void;
}
```

**Usage:**

```tsx
<Stepper
  steps={[
    { id: 'account', label: 'Account' },
    { id: 'preset', label: 'Preset' },
    { id: 'config', label: 'Configuration' },
    { id: 'review', label: 'Review' },
  ]}
  currentStep={2}
/>
```

---

## Configuration Components

### PresetCard

Configuration preset selection card.

```typescript
interface PresetCardProps {
  preset: {
    id: string;
    name: string;
    description: string;
    features: string[];
    price?: string;
    recommended?: boolean;
  };
  selected?: boolean;
  onSelect: () => void;
}
```

**Usage:**

```tsx
<PresetCard
  preset={{
    id: 'standard',
    name: 'Standard',
    description: 'Full analysis capabilities',
    features: ['Sentiment', 'Emotions', 'Summaries'],
    recommended: true,
  }}
  selected={selectedPreset === 'standard'}
  onSelect={() => setSelectedPreset('standard')}
/>
```

---

### PlatformSelector

Scraping platform selection.

```typescript
interface PlatformSelectorProps {
  platforms: Platform[];
  selected: string[];
  onChange: (selected: string[]) => void;
  multiple?: boolean;
}
```

**Usage:**

```tsx
<PlatformSelector
  platforms={availablePlatforms}
  selected={['amazon', 'steam']}
  onChange={setSelectedPlatforms}
  multiple
/>
```

---

### TargetInput

URL target input with validation.

```typescript
interface TargetInputProps {
  targets: Target[];
  onChange: (targets: Target[]) => void;
  maxTargets?: number;
}
```

**Usage:**

```tsx
<TargetInput
  targets={targets}
  onChange={setTargets}
  maxTargets={50}
/>
```

---

## Layout Components

### Sidebar

Navigation sidebar.

```typescript
interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}
```

---

### Header

Application header with user menu.

```typescript
interface HeaderProps {
  title?: string;
  breadcrumbs?: { label: string; href: string }[];
}
```

---

### PageHeader

Page title with actions.

```typescript
interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  breadcrumbs?: { label: string; href: string }[];
}
```

**Usage:**

```tsx
<PageHeader
  title="Projects"
  description="Manage your sentiment analysis projects"
  actions={<Button>New Project</Button>}
/>
```

---

## Error Handling Components

### ErrorBoundary

React error boundary for catching component errors.

```typescript
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}
```

**Usage:**

```tsx
<ErrorBoundary
  fallback={<ErrorDisplay title="Something went wrong" />}
  onError={(error) => logError(error)}
>
  <Dashboard />
</ErrorBoundary>
```

---

### ErrorDisplay

Styled error message display.

```typescript
interface ErrorDisplayProps {
  error?: Error | string;
  title?: string;
  message?: string;
  onRetry?: () => void;
  showDetails?: boolean;
}
```

**Usage:**

```tsx
<ErrorDisplay
  title="Failed to load projects"
  message="Please check your connection and try again"
  onRetry={refetch}
  showDetails
/>
```

---

### ApiError

API-specific error display with status codes.

```typescript
interface ApiErrorProps {
  status: number;
  message?: string;
  onRetry?: () => void;
}
```

**Usage:**

```tsx
<ApiError status={404} message="Project not found" />
<ApiError status={500} onRetry={refetch} />
```

---

## Empty State Components

### EmptyState

Generic empty state with icon, title, and action.

```typescript
interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  size?: 'sm' | 'md' | 'lg';
}
```

**Pre-built Empty States:**

```tsx
// No projects
<EmptyProjects onCreateProject={() => router.push('/projects/new')} />

// No targets
<EmptyTargets onAddTarget={() => setShowAddModal(true)} />

// No results
<EmptyResults onRunScrape={handleRunScrape} />

// No search results
<EmptySearch query={searchQuery} onClear={() => setSearchQuery('')} />

// No webhooks
<EmptyWebhooks onCreateWebhook={() => setShowCreateModal(true)} />

// No schedules
<EmptySchedules onCreateSchedule={() => setShowCreateModal(true)} />
```

---

## Toast Notifications

### Toast System

Global toast notification system.

```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  success: (title: string, message?: string) => string;
  error: (title: string, message?: string) => string;
  warning: (title: string, message?: string) => string;
  info: (title: string, message?: string) => string;
}
```

**Usage:**

```tsx
// Wrap app with provider
<ToastProvider>
  <App />
</ToastProvider>

// Use in components
const { success, error } = useToast();

const handleSave = async () => {
  try {
    await saveProject();
    success('Project saved', 'Your changes have been saved successfully');
  } catch (err) {
    error('Save failed', 'Unable to save project. Please try again.');
  }
};
```

---

## Component Location

All UI components are located in:

```
frontend/src/components/
├── ui/
│   ├── button.tsx
│   ├── input.tsx
│   ├── card.tsx
│   ├── skeleton.tsx
│   ├── spinner.tsx
│   ├── error-boundary.tsx
│   ├── empty-state.tsx
│   ├── toast.tsx
│   └── index.ts
├── forms/
├── features/
└── layout/
```

Import from the barrel file:

```tsx
import {
  Button,
  Input,
  Card,
  Skeleton,
  Spinner,
  ErrorBoundary,
  EmptyState,
  useToast
} from '@/components/ui';
```
