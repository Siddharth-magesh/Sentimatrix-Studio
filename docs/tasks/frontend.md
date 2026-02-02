# Frontend Tasks

## Overview

Frontend development tasks for Sentimatrix Studio web application.

**Technology:** Next.js 14, React, TypeScript, Tailwind CSS, Zustand

---

## Phase 1: Project Setup (COMPLETED)

### 1.1 Initialize Project [P0] - COMPLETED

- [x] Create Next.js project with App Router
- [x] Configure TypeScript
- [x] Set up path aliases (@/components, @/lib)
- [x] Configure ESLint
- [ ] Set up Husky pre-commit hooks

### 1.2 Tailwind Configuration [P0] - COMPLETED

- [x] Configure tailwind.config.ts
- [x] Define color palette (primary, neutral, success, warning, error)
- [x] Define typography scale
- [x] Define spacing scale
- [ ] Set up dark mode (optional)

### 1.3 Dependencies [P0] - COMPLETED

- [x] Install and configure React Query
- [x] Install and configure Zustand
- [x] Install and configure React Hook Form
- [x] Install and configure Zod
- [ ] Install Recharts for charts
- [x] Install Lucide React for icons

---

## Phase 2: Common Components (COMPLETED)

### 2.1 Base Components [P0] - COMPLETED

- [x] Button (variants: primary, secondary, outline, ghost, destructive)
- [x] Input (text, email, password, with error state)
- [ ] Select (single, multi, searchable)
- [ ] Textarea
- [ ] Checkbox
- [ ] Radio
- [ ] Switch/Toggle

### 2.2 Layout Components [P0] - COMPLETED

- [x] Card (header, title, description, content, footer)
- [ ] Modal (sizes, close button)
- [ ] Drawer (side panel)
- [ ] Tabs
- [ ] Accordion

### 2.3 Feedback Components [P0] - PARTIAL

- [x] Alert (info, success, warning, error)
- [ ] Toast notifications
- [x] Loading spinner (Loader2 from lucide)
- [ ] Skeleton loader
- [ ] Progress bar
- [ ] Badge

### 2.4 Data Components [P1]

- [ ] Table (sortable, selectable)
- [ ] Pagination
- [ ] Empty state
- [ ] Error state

---

## Phase 3: Layout (COMPLETED)

### 3.1 App Shell [P0] - COMPLETED

- [x] Root layout
- [x] Auth layout (centered card)
- [x] Dashboard layout (sidebar + main)

### 3.2 Navigation [P0] - COMPLETED

- [x] Sidebar component
- [x] Sidebar navigation items
- [x] Sidebar collapse state (mobile)
- [x] Header component
- [x] User dropdown/logout
- [ ] Breadcrumbs

### 3.3 Responsive [P1] - COMPLETED

- [x] Mobile sidebar (drawer with overlay)
- [x] Mobile navigation
- [ ] Responsive table views

---

## Phase 4: State Management (COMPLETED)

### 4.1 Zustand Stores [P0] - COMPLETED

- [x] Auth store (user, tokens, auth state)
- [ ] UI store (sidebar, modals, theme)
- [ ] Project config store (wizard state)

### 4.2 React Query [P0] - COMPLETED

- [x] Configure QueryClient
- [x] Set up query defaults
- [x] Create API client (axios wrapper)

### 4.3 Custom Hooks [P0] - PARTIAL

- [x] useAuthGuard (protected routes)
- [ ] useProjects (list, create, update, delete)
- [ ] useProject (single project)
- [ ] useResults (paginated results)
- [ ] useWebSocket (real-time updates)

---

## Phase 5: Authentication Pages (COMPLETED)

### 5.1 Login Page [P0] - COMPLETED

- [x] Login form component
- [x] Email/password validation (Zod)
- [x] Error handling
- [ ] Forgot password link
- [ ] OAuth buttons

### 5.2 Register Page [P0] - COMPLETED

- [x] Registration form component
- [x] Name/email/password fields
- [x] Password validation rules
- [x] Confirm password
- [x] Error handling

### 5.3 Password Reset [P1]

- [ ] Forgot password page
- [ ] Reset password page

### 5.4 OAuth [P1]

- [ ] OAuth callback page
- [ ] Account linking UI

---

## Phase 6: Dashboard (PARTIAL)

### 6.1 Main Dashboard [P0] - PARTIAL

- [x] Stats cards (placeholder)
- [ ] Sentiment trend chart (line/area)
- [ ] Recent activity list
- [x] Quick actions panel

### 6.2 Analytics Page [P2]

- [ ] Date range picker
- [ ] Sentiment distribution chart
- [ ] Emotion breakdown chart
- [ ] Topics word cloud (optional)
- [ ] Trend comparison

---

## Phase 7: Projects

### 7.1 Projects List [P0]

- [ ] Projects table/grid view
- [ ] Search and filter
- [ ] Status badge
- [ ] Create project button
- [ ] Project row actions (edit, delete)

### 7.2 New Project Wizard [P0]

- [ ] Stepper component
- [ ] Basic info step (name, description)
- [ ] Preset selection step
- [ ] Scraper config step
- [ ] LLM config step
- [ ] Targets input step
- [ ] Schedule config step (optional)
- [ ] Review step
- [ ] Form validation
- [ ] Submit handling

### 7.3 Project Detail [P0]

- [ ] Project header (name, status, actions)
- [ ] Stats overview cards
- [ ] Sentiment chart
- [ ] Targets list
- [ ] Recent results preview
- [ ] Action buttons (Scrape, Analyze, Export)

### 7.4 Project Results [P0]

- [ ] Results table
- [ ] Sentiment filter
- [ ] Date range filter
- [ ] Search
- [ ] Pagination
- [ ] Result detail modal
- [ ] Export button

### 7.5 Project Settings [P1]

- [ ] Edit project form
- [ ] Configuration editor
- [ ] Danger zone (delete)

---

## Phase 8: Configuration

### 8.1 Presets Page [P1]

- [ ] Preset cards display
- [ ] Preset detail view
- [ ] Create custom preset

### 8.2 Scrapers Page [P1]

- [ ] Platform list
- [ ] Commercial providers list
- [ ] Configuration panel

### 8.3 LLM Page [P1]

- [ ] Provider list
- [ ] Configuration form
- [ ] Connection test button
- [ ] API key input (masked)

---

## Phase 9: Settings

### 9.1 Profile Settings [P0]

- [ ] Profile form (name, company)
- [ ] Password change form
- [ ] Preferences form

### 9.2 API Keys [P1]

- [ ] API keys list
- [ ] Add key modal
- [ ] Test key button
- [ ] Delete confirmation

### 9.3 Webhooks [P2]

- [ ] Webhooks list
- [ ] Create webhook form
- [ ] Edit webhook form
- [ ] Test webhook button
- [ ] Delivery logs

### 9.4 Billing [P3]

- [ ] Usage stats
- [ ] Plan comparison
- [ ] Upgrade CTA

---

## Phase 10: Real-time Features

### 10.1 WebSocket Integration [P1]

- [ ] WebSocket connection hook
- [ ] Connection status indicator
- [ ] Auto-reconnection
- [ ] Event handling

### 10.2 Live Updates [P1]

- [ ] Scrape progress indicator
- [ ] Analysis progress indicator
- [ ] Results live update
- [ ] Notification toasts

---

## Phase 11: Forms

### 11.1 Form Components [P0] - PARTIAL

- [x] FormField wrapper (via react-hook-form)
- [x] FormError display
- [ ] FormSection grouping
- [x] Form submit button (with loading)

### 11.2 Complex Inputs [P0]

- [ ] PresetSelector
- [ ] PlatformSelector (multi-select with icons)
- [ ] ProviderSelector
- [ ] TargetInput (URL list with validation)
- [ ] ScheduleConfig (frequency, time, days)
- [ ] ApiKeyInput (masked, with validation)

---

## Phase 12: Charts

### 12.1 Chart Components [P0]

- [ ] SentimentLineChart
- [ ] SentimentAreaChart
- [ ] SentimentPieChart
- [ ] EmotionBarChart
- [ ] EmotionRadarChart
- [ ] TrendComparisonChart

### 12.2 Chart Utilities [P1]

- [ ] Chart color palette
- [ ] Responsive sizing
- [ ] Tooltips
- [ ] Legends

---

## Phase 13: Polish

### 13.1 UX Improvements [P1]

- [x] Loading states for async operations
- [ ] Error boundaries
- [ ] Empty states with CTAs
- [ ] Confirmation dialogs for destructive actions
- [ ] Success feedback messages

### 13.2 Accessibility [P1]

- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Focus management
- [ ] Screen reader testing

### 13.3 Performance [P2]

- [ ] Code splitting
- [ ] Image optimization
- [ ] Bundle size analysis
- [ ] Lazy loading

---

## Dependencies

```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "react-hook-form": "^7.49.3",
    "@hookform/resolvers": "^3.3.3",
    "zod": "^3.22.4",
    "lucide-react": "^0.309.0",
    "tailwindcss": "^3.4.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "axios": "^1.6.5"
  }
}
```

---

## Code Quality

- [x] TypeScript strict mode
- [x] All props typed
- [ ] All components documented
- [ ] Storybook for key components (optional)
- [x] ESLint configured
- [x] Component tests (Button, Input, Card, Alert)

---

## Implementation Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Project Setup | COMPLETED | 100% |
| Phase 2: Common Components | PARTIAL | 60% |
| Phase 3: Layout | COMPLETED | 90% |
| Phase 4: State Management | COMPLETED | 70% |
| Phase 5: Auth Pages | COMPLETED | 80% |
| Phase 6-13 | Not Started | 0% |

**Last Updated:** Phase 1 Foundation frontend complete with auth functionality.
