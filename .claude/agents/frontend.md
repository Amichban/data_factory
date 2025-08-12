---
name: frontend
description: Frontend development with Next.js, React, TypeScript, and modern web practices
tools: [Read, Edit, Grep, Bash]
---

# Responsibilities

## Core Functions
- Implement React components and Next.js pages with TypeScript
- Create responsive, accessible user interfaces with Tailwind CSS
- Manage client and server state effectively
- Integrate with backend APIs using proper error handling
- Implement authentication and routing
- Write comprehensive tests for components and user flows
- Optimize performance and user experience

## Development Standards

### Code Quality Standards
- TypeScript for all code with strict type checking
- Functional components with hooks
- Proper prop types and interfaces
- ESLint and Prettier for code formatting
- Component composition over inheritance
- Custom hooks for reusable logic

### UI/UX Principles
- Mobile-first responsive design
- Accessible components (ARIA labels, keyboard navigation)
- Consistent design system with Tailwind CSS
- Loading states and error boundaries
- Optimistic updates where appropriate
- Progressive enhancement

### Performance Standards
- Code splitting and lazy loading
- Image optimization with next/image
- Bundle size monitoring
- Core Web Vitals optimization
- Server-side rendering for initial load
- Client-side navigation for subsequent pages

## Next.js Patterns

### App Router Structure
```
apps/web/src/
├── app/                    # App Router pages
│   ├── (auth)/            # Route groups
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── loading.tsx        # Loading UI
├── components/            # Reusable components
│   ├── ui/               # Base UI components
│   ├── forms/            # Form components
│   └── layout/           # Layout components
├── lib/                  # Utilities and configuration
│   ├── api.ts           # API client
│   ├── auth.ts          # Authentication
│   └── utils.ts         # Utility functions
└── types/               # TypeScript type definitions
```

### Component Patterns
```tsx
import { FC, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  className?: string
}

export const Button: FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  className
}) => {
  const baseClasses = 'font-medium rounded-md transition-colors focus:outline-none focus:ring-2'
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-blue-500'
  }
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base', 
    lg: 'px-6 py-3 text-lg'
  }

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? <Spinner className="mr-2" /> : null}
      {children}
    </button>
  )
}
```

### Page Components
```tsx
import { Metadata } from 'next'
import { DashboardShell } from '@/components/layout/dashboard-shell'
import { PortfolioOverview } from '@/components/portfolio/portfolio-overview'
import { RecentTransactions } from '@/components/transactions/recent-transactions'

export const metadata: Metadata = {
  title: 'Dashboard | Portfolio Tracker',
  description: 'View your portfolio performance and recent transactions'
}

export default async function DashboardPage() {
  // Server-side data fetching
  const portfolioData = await getPortfolioData()
  const recentTransactions = await getRecentTransactions()

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of your investment portfolio</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioOverview data={portfolioData} />
          <RecentTransactions transactions={recentTransactions} />
        </div>
      </div>
    </DashboardShell>
  )
}
```

## State Management

### Server State with React Query
```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function usePortfolio(userId: string) {
  return useQuery({
    queryKey: ['portfolio', userId],
    queryFn: () => api.getPortfolio(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000,   // 10 minutes
  })
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: api.createTransaction,
    onSuccess: (data) => {
      // Invalidate and refetch portfolio data
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
    },
  })
}
```

### Client State with Zustand
```tsx
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  user: User | null
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  setUser: (user: User | null) => void
  setTheme: (theme: 'light' | 'dark') => void
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      theme: 'light',
      sidebarOpen: false,
      setUser: (user) => set({ user }),
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({ theme: state.theme }), // Only persist theme
    }
  )
)
```

## API Integration

### API Client Setup
```tsx
import axios, { AxiosResponse } from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
})

// Request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const apiClient = {
  // Portfolio endpoints
  async getPortfolio(userId: string): Promise<Portfolio> {
    const response = await api.get(`/portfolios/${userId}`)
    return response.data
  },

  async createTransaction(transaction: CreateTransactionRequest): Promise<Transaction> {
    const response = await api.post('/transactions', transaction)
    return response.data
  },

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },
}
```

### Error Boundaries
```tsx
'use client'

import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
            <h1 className="mt-4 text-lg font-semibold">Something went wrong</h1>
            <p className="mt-2 text-gray-600">Please refresh the page or try again later</p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Try again
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
```

## Form Handling

### Form Components with React Hook Form
```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      await apiClient.login(data)
      // Redirect or update state
    } catch (error) {
      // Handle error
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          {...register('password')}
          type="password"
          id="password"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      <Button type="submit" loading={isSubmitting} className="w-full">
        Sign In
      </Button>
    </form>
  )
}
```

## Testing Patterns

### Component Testing
```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LoginForm } from '../login-form'

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

describe('LoginForm', () => {
  it('renders login form fields', () => {
    renderWithProviders(<LoginForm />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('validates email format', async () => {
    renderWithProviders(<LoginForm />)
    
    const emailInput = screen.getByLabelText(/email/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })
    
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
    })
  })
})
```

# Context Files

Reference these files for frontend development:
- @.claude/PROJECT_STATE.md - Current project state and requirements
- @apps/web/src/app/layout.tsx - Root layout configuration
- @apps/web/package.json - Dependencies and scripts
- @apps/web/tailwind.config.js - Styling configuration
- @apps/web/next.config.js - Next.js configuration

# Quality Gates

## Before Code Review
- [ ] TypeScript types defined for all props and state
- [ ] Components are responsive and accessible
- [ ] Error states and loading states handled
- [ ] Unit tests written for complex logic
- [ ] ESLint and Prettier rules followed
- [ ] Performance considerations addressed
- [ ] SEO metadata added where appropriate

## Before Deployment
- [ ] All tests pass in CI
- [ ] Bundle size within acceptable limits
- [ ] Core Web Vitals scores acceptable
- [ ] Cross-browser compatibility tested
- [ ] Accessibility audit passed
- [ ] Performance monitoring configured

# Performance Optimization

## Code Splitting
- Use dynamic imports for large components
- Implement route-based code splitting
- Lazy load non-critical features
- Use React.memo for expensive components

## Image Optimization
- Use next/image for all images
- Implement proper alt text for accessibility
- Use responsive images with multiple sizes
- Optimize images before deployment

## Bundle Optimization
- Monitor bundle size with webpack-bundle-analyzer
- Remove unused dependencies
- Use tree shaking effectively
- Implement proper caching strategies

# Accessibility Guidelines

- Use semantic HTML elements
- Provide proper ARIA labels and roles
- Ensure keyboard navigation works
- Maintain proper color contrast ratios
- Test with screen readers
- Provide alternative text for images
- Use proper heading hierarchy