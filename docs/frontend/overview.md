# Frontend Overview

## Introduction

Sentimatrix Studio frontend is built with Next.js 14 using the App Router, providing a modern, performant user interface for managing sentiment analysis projects.

## Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.x | React framework with App Router |
| React | 18.x | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Utility-first styling |
| Zustand | 4.x | State management |
| React Query | 5.x | Server state management |
| Recharts | 2.x | Data visualization |
| React Hook Form | 7.x | Form handling |
| Zod | 3.x | Schema validation |

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/              # Auth group (login, register)
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/         # Dashboard group
│   │   │   ├── dashboard/
│   │   │   ├── projects/
│   │   │   ├── config/
│   │   │   ├── settings/
│   │   │   └── layout.tsx
│   │   ├── api/                 # API routes (if needed)
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Landing page
│   ├── components/              # React components
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── config/
│   │   ├── results/
│   │   ├── forms/
│   │   ├── layout/
│   │   └── common/
│   ├── hooks/                   # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useProjects.ts
│   │   └── useWebSocket.ts
│   ├── lib/                     # Utilities
│   │   ├── api.ts              # API client
│   │   ├── utils.ts            # Helper functions
│   │   └── constants.ts        # Constants
│   ├── stores/                  # Zustand stores
│   │   ├── authStore.ts
│   │   ├── projectStore.ts
│   │   └── uiStore.ts
│   ├── types/                   # TypeScript types
│   │   ├── api.ts
│   │   ├── project.ts
│   │   └── user.ts
│   └── styles/                  # Global styles
│       └── globals.css
├── public/                      # Static assets
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

## Key Concepts

### App Router

Using Next.js 14 App Router with:

- **Route Groups**: `(auth)` and `(dashboard)` for different layouts
- **Server Components**: Default for optimal performance
- **Client Components**: Used only when needed (interactivity)
- **Parallel Routes**: For modals and side panels
- **Intercepting Routes**: For seamless navigation

### Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │────>│   API Call  │────>│  Store JWT  │
│   Page      │     │   /login    │     │  in Memory  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Dashboard  │<────│  Redirect   │
                    │   Page      │     │             │
                    └─────────────┘     └─────────────┘
```

### State Management

**Server State (React Query):**
- API responses
- Project data
- Analysis results
- User profile

**Client State (Zustand):**
- UI state (sidebar, modals)
- Authentication state
- Form state
- WebSocket connection

### Data Fetching

```typescript
// Server Component (default)
async function ProjectsPage() {
  const projects = await getProjects();
  return <ProjectList projects={projects} />;
}

// Client Component with React Query
'use client';
function ProjectDetails({ id }: { id: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => api.getProject(id),
  });

  if (isLoading) return <Loading />;
  return <ProjectView project={data} />;
}
```

## Design System

### Colors

```css
/* Primary */
--primary-50: #f0f9ff;
--primary-500: #0ea5e9;
--primary-900: #0c4a6e;

/* Neutral */
--gray-50: #f9fafb;
--gray-500: #6b7280;
--gray-900: #111827;

/* Semantic */
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;

/* Sentiment */
--sentiment-positive: #22c55e;
--sentiment-neutral: #6b7280;
--sentiment-negative: #ef4444;
```

### Typography

```css
/* Font Family */
font-family: 'Inter', system-ui, sans-serif;

/* Sizes */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 1.875rem;
```

### Spacing

Tailwind default spacing scale (4px base):
- `1`: 4px
- `2`: 8px
- `4`: 16px
- `6`: 24px
- `8`: 32px

## Component Guidelines

### Component Structure

```typescript
// components/projects/ProjectCard.tsx

import { type FC } from 'react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { type Project } from '@/types/project';

interface ProjectCardProps {
  project: Project;
  onSelect?: (id: string) => void;
}

export const ProjectCard: FC<ProjectCardProps> = ({ project, onSelect }) => {
  return (
    <Card onClick={() => onSelect?.(project.id)}>
      <Card.Header>
        <h3>{project.name}</h3>
        <Badge variant={project.status}>{project.status}</Badge>
      </Card.Header>
      <Card.Body>
        <p>{project.description}</p>
      </Card.Body>
      <Card.Footer>
        <span>{project.results_count} results</span>
      </Card.Footer>
    </Card>
  );
};
```

### Form Handling

```typescript
// Using React Hook Form with Zod
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export function ProjectForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    // Handle submission
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('name')} error={errors.name?.message} />
      <Textarea {...register('description')} />
      <Button type="submit">Create</Button>
    </form>
  );
}
```

## Performance Optimization

### Code Splitting

- Automatic route-based splitting with App Router
- Dynamic imports for heavy components
- Lazy loading for modals and dialogs

### Caching

- React Query caching for API responses
- Next.js data cache for static data
- Browser caching for assets

### Image Optimization

- Next.js Image component for automatic optimization
- WebP format with fallbacks
- Lazy loading for below-fold images

## Accessibility

### ARIA Labels

All interactive elements include appropriate ARIA attributes.

### Keyboard Navigation

Full keyboard support for all interactive elements.

### Focus Management

Proper focus management for modals and navigation.

### Screen Reader Support

Semantic HTML and ARIA live regions for dynamic content.
