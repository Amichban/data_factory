// Base API response interface
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Health check interfaces
export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  uptime: number;
  version?: string;
  services?: ServiceHealth[];
}

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  responseTime?: number;
  message?: string;
}

// API client configuration
export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

// Request/Response types
export interface FetchOptions extends RequestInit {
  timeout?: number;
}

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

// Navigation types
export interface NavItem {
  href: string;
  label: string;
  external?: boolean;
}

// Component props
export interface LayoutProps {
  children: React.ReactNode;
}

export interface PageProps {
  params: Record<string, string>;
  searchParams: Record<string, string>;
}

// Environment configuration
export interface Config {
  apiUrl: string;
  environment: 'development' | 'production' | 'test';
  enableHealthChecks: boolean;
  healthCheckInterval: number;
}