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

### Loading

Loading indicator variants.

```typescript
interface LoadingProps {
  variant?: 'spinner' | 'skeleton' | 'dots';
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}
```

**Usage:**

```tsx
<Loading variant="spinner" size="md" text="Loading projects..." />

// Skeleton for table
<Loading.Skeleton rows={5} columns={4} />
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
