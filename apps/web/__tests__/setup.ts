/**
 * Jest setup file for QuantX Platform tests
 * This file is executed before each test file is run
 */

import '@testing-library/jest-dom';

// Mock Next.js modules
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    };
  },
  useSearchParams() {
    return {
      get: jest.fn(),
      getAll: jest.fn(),
      has: jest.fn(),
      keys: jest.fn(),
      values: jest.fn(),
      entries: jest.fn(),
      forEach: jest.fn(),
      toString: jest.fn(),
    };
  },
  usePathname() {
    return '/';
  },
}));

jest.mock('next/link', () => {
  return ({ children, href, ...props }: any) => {
    return <a href={href} {...props}>{children}</a>;
  };
});

// Mock environment variables
const mockEnv = {
  NODE_ENV: 'test',
  NEXT_PUBLIC_API_URL: 'http://localhost:3001/api',
  NEXT_PUBLIC_APP_NAME: 'QuantX Platform',
  NEXT_PUBLIC_APP_VERSION: '1.0.0',
  NEXT_PUBLIC_ENABLE_HEALTH_CHECKS: 'true',
  NEXT_PUBLIC_HEALTH_CHECK_INTERVAL: '30000',
};

Object.entries(mockEnv).forEach(([key, value]) => {
  process.env[key] = value;
});

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock console methods in test environment to reduce noise
if (process.env.NODE_ENV === 'test') {
  // Only mock console.log, keep error and warn for debugging
  global.console = {
    ...console,
    log: jest.fn(),
  };
}

// Mock performance API
Object.defineProperty(window, 'performance', {
  value: {
    timeOrigin: Date.now(),
    now: jest.fn(() => Date.now()),
  },
  writable: true,
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  thresholds: [],
  root: null,
  rootMargin: '',
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Custom matchers
expect.extend({
  toHaveHealthyStatus(received) {
    const pass = received?.status === 'healthy';
    if (pass) {
      return {
        message: () => `expected ${received} not to have healthy status`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to have healthy status`,
        pass: false,
      };
    }
  },
  
  toBeValidApiResponse(received) {
    const hasSuccess = typeof received?.success === 'boolean';
    const hasData = received?.data !== undefined;
    const pass = hasSuccess && (received.success ? hasData : true);
    
    if (pass) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to be a valid API response`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to be a valid API response with success boolean and data when successful`,
        pass: false,
      };
    }
  },
});

// Global test utilities
global.testUtils = {
  // Helper to create mock health status
  createMockHealthStatus: (overrides = {}) => ({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: 123456,
    version: '1.0.0',
    services: [
      {
        name: 'Test Service',
        status: 'healthy',
        responseTime: 100,
      },
    ],
    ...overrides,
  }),

  // Helper to create mock API response
  createMockApiResponse: (data = {}, success = true) => ({
    success,
    data: success ? data : undefined,
    message: success ? undefined : 'Test error message',
  }),

  // Helper to wait for async operations
  waitFor: (ms = 0) => new Promise(resolve => setTimeout(resolve, ms)),

  // Helper to suppress console errors in specific tests
  suppressConsoleError: () => {
    const originalError = console.error;
    beforeAll(() => {
      console.error = jest.fn();
    });
    afterAll(() => {
      console.error = originalError;
    });
  },
};

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
  // Reset fetch mock
  if (global.fetch) {
    (global.fetch as jest.Mock).mockReset();
  }
});

// Type declarations for TypeScript
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveHealthyStatus(): R;
      toBeValidApiResponse(): R;
    }
  }

  var testUtils: {
    createMockHealthStatus: (overrides?: any) => any;
    createMockApiResponse: (data?: any, success?: boolean) => any;
    waitFor: (ms?: number) => Promise<void>;
    suppressConsoleError: () => void;
  };
}