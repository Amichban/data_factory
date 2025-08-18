import { Config } from '@/types';

/**
 * Application configuration
 * Centralizes all environment variables and configuration settings
 */

// Helper function to get environment variable with fallback
function getEnvVar(key: string, fallback?: string): string {
  const value = process.env[key];
  if (value === undefined && fallback === undefined) {
    throw new Error(`Environment variable ${key} is required but not set`);
  }
  return value || fallback || '';
}

// Helper function to get boolean environment variable
function getBoolEnvVar(key: string, fallback: boolean = false): boolean {
  const value = process.env[key];
  if (value === undefined) return fallback;
  return value.toLowerCase() === 'true' || value === '1';
}

// Helper function to get number environment variable
function getNumberEnvVar(key: string, fallback: number): number {
  const value = process.env[key];
  if (value === undefined) return fallback;
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? fallback : parsed;
}

/**
 * Main configuration object
 */
export const config: Config = {
  // API Configuration
  apiUrl: getEnvVar('NEXT_PUBLIC_API_URL', 'http://localhost:3001/api'),
  
  // Environment
  environment: (getEnvVar('NODE_ENV', 'development') as Config['environment']),
  
  // Health Check Configuration
  enableHealthChecks: getBoolEnvVar('NEXT_PUBLIC_ENABLE_HEALTH_CHECKS', true),
  healthCheckInterval: getNumberEnvVar('NEXT_PUBLIC_HEALTH_CHECK_INTERVAL', 30000), // 30 seconds
};

/**
 * Additional configuration objects for specific features
 */

export const apiConfig = {
  baseUrl: config.apiUrl,
  timeout: getNumberEnvVar('NEXT_PUBLIC_API_TIMEOUT', 10000), // 10 seconds
  retries: getNumberEnvVar('NEXT_PUBLIC_API_RETRIES', 3),
  retryDelay: getNumberEnvVar('NEXT_PUBLIC_API_RETRY_DELAY', 1000), // 1 second
} as const;

export const healthConfig = {
  enabled: config.enableHealthChecks,
  interval: config.healthCheckInterval,
  endpoints: {
    frontend: '/api/health',
    backend: `${config.apiUrl}/health`,
  },
  services: [
    'database',
    'cache',
    'external-api',
    'message-queue',
  ],
} as const;

export const appConfig = {
  name: getEnvVar('NEXT_PUBLIC_APP_NAME', 'QuantX Platform'),
  version: getEnvVar('NEXT_PUBLIC_APP_VERSION', '1.0.0'),
  description: getEnvVar('NEXT_PUBLIC_APP_DESCRIPTION', 'A comprehensive quantitative analysis platform'),
  url: getEnvVar('NEXT_PUBLIC_APP_URL', 'http://localhost:3000'),
} as const;

export const featureFlags = {
  enableDarkMode: getBoolEnvVar('NEXT_PUBLIC_ENABLE_DARK_MODE', true),
  enableAnalytics: getBoolEnvVar('NEXT_PUBLIC_ENABLE_ANALYTICS', false),
  enableHealthMonitoring: getBoolEnvVar('NEXT_PUBLIC_ENABLE_HEALTH_MONITORING', true),
  enableDebugMode: getBoolEnvVar('NEXT_PUBLIC_DEBUG', config.environment === 'development'),
} as const;

/**
 * Runtime configuration validation
 */
export function validateConfig(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Validate required environment variables
  const requiredVars = [
    'NODE_ENV',
  ];

  for (const varName of requiredVars) {
    if (!process.env[varName]) {
      errors.push(`Required environment variable ${varName} is not set`);
    }
  }

  // Validate environment values
  const validEnvironments = ['development', 'production', 'test'];
  if (!validEnvironments.includes(config.environment)) {
    errors.push(`Invalid NODE_ENV: ${config.environment}. Must be one of: ${validEnvironments.join(', ')}`);
  }

  // Validate API URL format
  try {
    new URL(config.apiUrl);
  } catch {
    errors.push(`Invalid NEXT_PUBLIC_API_URL: ${config.apiUrl}`);
  }

  // Validate numeric values
  if (config.healthCheckInterval < 1000) {
    errors.push('Health check interval must be at least 1000ms');
  }

  if (apiConfig.timeout < 1000) {
    errors.push('API timeout must be at least 1000ms');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Utility functions
 */
export const isDevelopment = config.environment === 'development';
export const isProduction = config.environment === 'production';
export const isTest = config.environment === 'test';

/**
 * Export individual configurations for easier importing
 */
export default config;