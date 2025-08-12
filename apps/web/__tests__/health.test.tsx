/**
 * Tests for the Health page component
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import HealthPage from '@/app/health/page';
import { checkFrontendHealth, checkHealth } from '@/lib/api/health';
import { HealthStatus } from '@/types';

// Mock the health API functions
jest.mock('@/lib/api/health');

const mockCheckFrontendHealth = checkFrontendHealth as jest.MockedFunction<typeof checkFrontendHealth>;
const mockCheckHealth = checkHealth as jest.MockedFunction<typeof checkHealth>;

describe('HealthPage', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockCheckFrontendHealth.mockReset();
    mockCheckHealth.mockReset();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Initial Loading State', () => {
    it('should display loading state initially', () => {
      // Mock pending promises
      mockCheckFrontendHealth.mockImplementation(() => new Promise(() => {}));
      mockCheckHealth.mockImplementation(() => new Promise(() => {}));

      render(<HealthPage />);

      expect(screen.getByText('Loading health data...')).toBeInTheDocument();
      expect(screen.getByRole('progressbar', { hidden: true })).toBeInTheDocument();
    });
  });

  describe('Successful Health Data Loading', () => {
    it('should display health data when both frontend and backend are healthy', async () => {
      const frontendHealth: HealthStatus = testUtils.createMockHealthStatus({
        services: [
          {
            name: 'Frontend API',
            status: 'healthy',
            responseTime: 50,
          },
        ],
      });

      const backendHealth: HealthStatus = testUtils.createMockHealthStatus({
        services: [
          {
            name: 'Database',
            status: 'healthy',
            responseTime: 100,
          },
          {
            name: 'Cache',
            status: 'healthy',
            responseTime: 25,
          },
        ],
      });

      mockCheckFrontendHealth.mockResolvedValue(frontendHealth);
      mockCheckHealth.mockResolvedValue(backendHealth);

      render(<HealthPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading health data...')).not.toBeInTheDocument();
      });

      // Check that both health sections are displayed
      expect(screen.getByText('Frontend Health')).toBeInTheDocument();
      expect(screen.getByText('Backend Health')).toBeInTheDocument();

      // Check that all services are displayed
      expect(screen.getByText('Frontend API')).toBeInTheDocument();
      expect(screen.getByText('Database')).toBeInTheDocument();
      expect(screen.getByText('Cache')).toBeInTheDocument();

      // Check status indicators
      const healthyStatuses = screen.getAllByText('HEALTHY');
      expect(healthyStatuses.length).toBeGreaterThan(0);

      // Check response times are displayed
      expect(screen.getByText('Response Time: 50ms')).toBeInTheDocument();
      expect(screen.getByText('Response Time: 100ms')).toBeInTheDocument();
      expect(screen.getByText('Response Time: 25ms')).toBeInTheDocument();
    });

    it('should display degraded status correctly', async () => {
      const degradedHealth: HealthStatus = testUtils.createMockHealthStatus({
        status: 'degraded',
        services: [
          {
            name: 'Slow Service',
            status: 'degraded',
            responseTime: 5000,
            message: 'Service is responding slowly',
          },
        ],
      });

      mockCheckFrontendHealth.mockResolvedValue(degradedHealth);
      mockCheckHealth.mockResolvedValue(testUtils.createMockHealthStatus());

      render(<HealthPage />);

      await waitFor(() => {
        expect(screen.getByText('DEGRADED')).toBeInTheDocument();
      });

      expect(screen.getByText('Slow Service')).toBeInTheDocument();
      expect(screen.getByText('Service is responding slowly')).toBeInTheDocument();
      expect(screen.getByText('Response Time: 5000ms')).toBeInTheDocument();
    });

    it('should display unhealthy status correctly', async () => {
      const unhealthyHealth: HealthStatus = testUtils.createMockHealthStatus({
        status: 'unhealthy',
        services: [
          {
            name: 'Failed Service',
            status: 'unhealthy',
            message: 'Service connection failed',
          },
        ],
      });

      mockCheckFrontendHealth.mockResolvedValue(unhealthyHealth);
      mockCheckHealth.mockResolvedValue(testUtils.createMockHealthStatus());

      render(<HealthPage />);

      await waitFor(() => {
        expect(screen.getByText('UNHEALTHY')).toBeInTheDocument();
      });

      expect(screen.getByText('Failed Service')).toBeInTheDocument();
      expect(screen.getByText('Service connection failed')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when both API calls fail', async () => {
      mockCheckFrontendHealth.mockRejectedValue(new Error('Frontend API failed'));
      mockCheckHealth.mockRejectedValue(new Error('Backend API failed'));

      render(<HealthPage />);

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument();
        expect(screen.getByText('Failed to fetch health data')).toBeInTheDocument();
      });
    });

    it('should handle partial failures gracefully', async () => {
      const frontendHealth: HealthStatus = testUtils.createMockHealthStatus();
      
      mockCheckFrontendHealth.mockResolvedValue(frontendHealth);
      mockCheckHealth.mockRejectedValue(new Error('Backend failed'));

      render(<HealthPage />);

      await waitFor(() => {
        expect(screen.getByText('Frontend Health')).toBeInTheDocument();
        expect(screen.getByText('Backend Health')).toBeInTheDocument();
      });

      // Frontend should show data
      expect(screen.getByText('Test Service')).toBeInTheDocument();

      // Backend should show no data message
      expect(screen.getByText('No health data available')).toBeInTheDocument();
    });
  });

  describe('Refresh Functionality', () => {
    it('should refresh health data when refresh button is clicked', async () => {
      const initialHealth = testUtils.createMockHealthStatus();
      mockCheckFrontendHealth.mockResolvedValue(initialHealth);
      mockCheckHealth.mockResolvedValue(initialHealth);

      render(<HealthPage />);

      await waitFor(() => {
        expect(screen.getByText('HEALTHY')).toBeInTheDocument();
      });

      // Click refresh button
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      fireEvent.click(refreshButton);

      // Should show loading state
      expect(screen.getByText('Refreshing...')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.queryByText('Refreshing...')).not.toBeInTheDocument();
      });

      // API functions should be called twice (initial load + refresh)
      expect(mockCheckFrontendHealth).toHaveBeenCalledTimes(2);
      expect(mockCheckHealth).toHaveBeenCalledTimes(2);
    });

    it('should disable refresh button while loading', async () => {
      mockCheckFrontendHealth.mockImplementation(() => new Promise(() => {}));
      mockCheckHealth.mockImplementation(() => new Promise(() => {}));

      render(<HealthPage />);

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      expect(refreshButton).toBeDisabled();
    });
  });

  describe('Auto-refresh', () => {
    it('should automatically refresh health data every 30 seconds', async () => {
      const mockHealth = testUtils.createMockHealthStatus();
      mockCheckFrontendHealth.mockResolvedValue(mockHealth);
      mockCheckHealth.mockResolvedValue(mockHealth);

      render(<HealthPage />);

      // Wait for initial load
      await waitFor(() => {
        expect(mockCheckFrontendHealth).toHaveBeenCalledTimes(1);
      });

      // Fast-forward 30 seconds
      jest.advanceTimersByTime(30000);

      await waitFor(() => {
        expect(mockCheckFrontendHealth).toHaveBeenCalledTimes(2);
        expect(mockCheckHealth).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Uptime Display', () => {
    it('should format uptime correctly for different durations', async () => {
      const testCases = [
        { uptime: 1000, expected: '1s' },
        { uptime: 61000, expected: '1m 1s' },
        { uptime: 3661000, expected: '1h 1m' },
        { uptime: 90061000, expected: '1d 1h 1m' },
      ];

      for (const { uptime, expected } of testCases) {
        const health = testUtils.createMockHealthStatus({ uptime });
        mockCheckFrontendHealth.mockResolvedValue(health);
        mockCheckHealth.mockResolvedValue(health);

        const { unmount } = render(<HealthPage />);

        await waitFor(() => {
          expect(screen.getByText(expected)).toBeInTheDocument();
        });

        unmount();
      }
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', async () => {
      const mockHealth = testUtils.createMockHealthStatus();
      mockCheckFrontendHealth.mockResolvedValue(mockHealth);
      mockCheckHealth.mockResolvedValue(mockHealth);

      render(<HealthPage />);

      await waitFor(() => {
        const mainHeading = screen.getByRole('heading', { level: 1 });
        expect(mainHeading).toHaveTextContent('System Health');

        const subHeadings = screen.getAllByRole('heading', { level: 2 });
        expect(subHeadings).toHaveLength(2);
        expect(subHeadings[0]).toHaveTextContent('Frontend Health');
        expect(subHeadings[1]).toHaveTextContent('Backend Health');
      });
    });

    it('should have accessible button labels', async () => {
      const mockHealth = testUtils.createMockHealthStatus();
      mockCheckFrontendHealth.mockResolvedValue(mockHealth);
      mockCheckHealth.mockResolvedValue(mockHealth);

      render(<HealthPage />);

      await waitFor(() => {
        const refreshButton = screen.getByRole('button', { name: /refresh/i });
        expect(refreshButton).toBeInTheDocument();
      });
    });
  });
});