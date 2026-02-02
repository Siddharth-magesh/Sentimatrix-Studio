# Styling Guide

## Overview

Sentimatrix Studio uses Tailwind CSS for styling with a custom design system.

## Design System

### Color Palette

```css
/* tailwind.config.js colors */
colors: {
  /* Primary - Blue */
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
    950: '#082f49',
  },

  /* Neutral - Gray */
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },

  /* Semantic Colors */
  success: {
    light: '#dcfce7',
    DEFAULT: '#22c55e',
    dark: '#15803d',
  },
  warning: {
    light: '#fef3c7',
    DEFAULT: '#f59e0b',
    dark: '#b45309',
  },
  error: {
    light: '#fee2e2',
    DEFAULT: '#ef4444',
    dark: '#b91c1c',
  },
  info: {
    light: '#dbeafe',
    DEFAULT: '#3b82f6',
    dark: '#1d4ed8',
  },

  /* Sentiment Colors */
  sentiment: {
    positive: '#22c55e',
    neutral: '#6b7280',
    negative: '#ef4444',
  },
}
```

### Typography

```css
/* tailwind.config.js typography */
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
  mono: ['JetBrains Mono', 'monospace'],
},

fontSize: {
  xs: ['0.75rem', { lineHeight: '1rem' }],
  sm: ['0.875rem', { lineHeight: '1.25rem' }],
  base: ['1rem', { lineHeight: '1.5rem' }],
  lg: ['1.125rem', { lineHeight: '1.75rem' }],
  xl: ['1.25rem', { lineHeight: '1.75rem' }],
  '2xl': ['1.5rem', { lineHeight: '2rem' }],
  '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
  '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
},

fontWeight: {
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
},
```

### Spacing

```css
/* Standard Tailwind spacing scale */
/* 1 unit = 4px */
spacing: {
  0: '0px',
  1: '0.25rem',    /* 4px */
  2: '0.5rem',     /* 8px */
  3: '0.75rem',    /* 12px */
  4: '1rem',       /* 16px */
  5: '1.25rem',    /* 20px */
  6: '1.5rem',     /* 24px */
  8: '2rem',       /* 32px */
  10: '2.5rem',    /* 40px */
  12: '3rem',      /* 48px */
  16: '4rem',      /* 64px */
  20: '5rem',      /* 80px */
  24: '6rem',      /* 96px */
}
```

### Border Radius

```css
borderRadius: {
  none: '0',
  sm: '0.125rem',   /* 2px */
  DEFAULT: '0.25rem', /* 4px */
  md: '0.375rem',   /* 6px */
  lg: '0.5rem',     /* 8px */
  xl: '0.75rem',    /* 12px */
  '2xl': '1rem',    /* 16px */
  full: '9999px',
}
```

### Shadows

```css
boxShadow: {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
}
```

---

## Component Styles

### Buttons

```tsx
// Base button styles
const buttonBase = `
  inline-flex items-center justify-center
  font-medium rounded-lg
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
`;

// Size variants
const buttonSizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

// Color variants
const buttonVariants = {
  primary: `
    bg-primary-600 text-white
    hover:bg-primary-700
    focus:ring-primary-500
  `,
  secondary: `
    bg-gray-100 text-gray-700
    hover:bg-gray-200
    focus:ring-gray-500
  `,
  outline: `
    border border-gray-300 bg-white text-gray-700
    hover:bg-gray-50
    focus:ring-primary-500
  `,
  ghost: `
    text-gray-700
    hover:bg-gray-100
    focus:ring-gray-500
  `,
  danger: `
    bg-error text-white
    hover:bg-error-dark
    focus:ring-error
  `,
};
```

### Inputs

```tsx
// Input styles
const inputBase = `
  w-full px-3 py-2
  border border-gray-300 rounded-lg
  text-gray-900 placeholder-gray-400
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
  disabled:bg-gray-50 disabled:text-gray-500
`;

const inputError = `
  border-error
  focus:ring-error focus:border-error
`;
```

### Cards

```tsx
// Card styles
const cardBase = `
  bg-white rounded-xl border border-gray-200
  shadow-sm
`;

const cardHoverable = `
  cursor-pointer
  transition-shadow duration-200
  hover:shadow-md
`;
```

### Tables

```tsx
// Table styles
const tableBase = `
  w-full border-collapse
`;

const tableHeader = `
  bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider
`;

const tableCell = `
  px-6 py-4 whitespace-nowrap text-sm text-gray-900
`;

const tableRowHover = `
  hover:bg-gray-50 transition-colors
`;
```

---

## CSS Utilities

### Custom Utilities

```css
/* globals.css */
@layer utilities {
  /* Text truncation */
  .truncate-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .truncate-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  /* Scrollbar styling */
  .scrollbar-thin {
    scrollbar-width: thin;
  }

  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb {
    background-color: theme('colors.gray.300');
    border-radius: 3px;
  }

  /* Animation utilities */
  .animate-fade-in {
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .animate-slide-up {
    animation: slideUp 0.2s ease-out;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
```

---

## Dark Mode

Dark mode support using Tailwind's dark variant.

```tsx
// Example component with dark mode
<div className="bg-white dark:bg-gray-900">
  <h1 className="text-gray-900 dark:text-white">Title</h1>
  <p className="text-gray-600 dark:text-gray-400">Description</p>
</div>
```

### Dark Mode Colors

```css
/* Dark mode color mappings */
dark: {
  bg: {
    primary: 'gray-900',
    secondary: 'gray-800',
    tertiary: 'gray-700',
  },
  text: {
    primary: 'white',
    secondary: 'gray-300',
    tertiary: 'gray-400',
  },
  border: 'gray-700',
}
```

---

## Responsive Design

### Breakpoints

```css
screens: {
  sm: '640px',   /* Mobile landscape */
  md: '768px',   /* Tablet */
  lg: '1024px',  /* Desktop */
  xl: '1280px',  /* Large desktop */
  '2xl': '1536px', /* Extra large */
}
```

### Responsive Patterns

```tsx
// Stack on mobile, row on desktop
<div className="flex flex-col md:flex-row gap-4">
  <div className="w-full md:w-1/2">Column 1</div>
  <div className="w-full md:w-1/2">Column 2</div>
</div>

// Hide on mobile, show on desktop
<div className="hidden lg:block">Desktop only</div>

// Grid responsive columns
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {items.map(item => <Card key={item.id} />)}
</div>
```

---

## Animation Guidelines

### Transitions

```tsx
// Recommended transition durations
transition-all duration-150  // Fast (hover states)
transition-all duration-200  // Normal (most interactions)
transition-all duration-300  // Slow (modals, panels)
```

### Motion Preferences

```css
/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Best Practices

### Do

- Use semantic color names (primary, error) instead of literal colors
- Use spacing scale consistently (4, 8, 16, 24, 32)
- Use responsive utilities for layout changes
- Keep specificity low with utility classes
- Use component-level CSS for complex styles

### Avoid

- Arbitrary values unless absolutely necessary
- Inline styles
- Important declarations
- Deep nesting of CSS selectors
- Fixed widths/heights without responsive alternatives
