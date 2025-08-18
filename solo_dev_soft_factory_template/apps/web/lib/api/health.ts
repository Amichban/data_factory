import { apiClient } from './client';
import { HealthStatus, ServiceHealth, ApiResponse } from '@/types';

/**
 * Health check API functions
 */
export class HealthApi {
  /**
   * Check the overall health of the application
   */
  static async checkHealth(): Promise<HealthStatus> {
    try {
      const response = await apiClient.get<HealthStatus>('/health');
      
      if (response.success && response.data) {
        return response.data;
      }
      
      throw new Error(response.message || 'Health check failed');
    } catch (error) {
      // Return unhealthy status if the API call fails
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        uptime: 0,
        services: [],
      };
    }
  }

  /**
   * Check the health of a specific service
   */
  static async checkServiceHealth(serviceName: string): Promise<ServiceHealth> {
    try {
      const response = await apiClient.get<ServiceHealth>(`/health/${serviceName}`);
      
      if (response.success && response.data) {
        return response.data;
      }
      
      throw new Error(response.message || `Health check for ${serviceName} failed`);
    } catch (error) {
      return {
        name: serviceName,
        status: 'unhealthy',
        message: error instanceof Error ? error.message : 'Service health check failed',
      };
    }
  }

  /**
   * Check the health of multiple services
   */
  static async checkMultipleServices(serviceNames: string[]): Promise<ServiceHealth[]> {
    try {
      const promises = serviceNames.map(serviceName => 
        this.checkServiceHealth(serviceName)
      );
      
      const results = await Promise.allSettled(promises);
      
      return results.map((result, index) => {
        if (result.status === 'fulfilled') {
          return result.value;
        } else {
          return {
            name: serviceNames[index],
            status: 'unhealthy' as const,
            message: 'Failed to check service health',
          };
        }
      });
    } catch (error) {
      return serviceNames.map(name => ({
        name,
        status: 'unhealthy' as const,
        message: 'Batch health check failed',
      }));
    }
  }

  /**
   * Perform a lightweight health check (ping)
   */
  static async ping(): Promise<{ success: boolean; responseTime: number }> {
    const startTime = Date.now();
    
    try {
      await apiClient.get('/ping');
      const responseTime = Date.now() - startTime;
      
      return {
        success: true,
        responseTime,
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      return {
        success: false,
        responseTime,
      };
    }
  }

  /**
   * Get detailed system information
   */
  static async getSystemInfo(): Promise<{
    version: string;
    uptime: number;
    memory: {
      used: number;
      total: number;
      percentage: number;
    };
    cpu: {
      usage: number;
    };
  }> {
    try {
      const response = await apiClient.get<{
        version: string;
        uptime: number;
        memory: { used: number; total: number; percentage: number };
        cpu: { usage: number };
      }>('/health/system');
      
      if (response.success && response.data) {
        return response.data;
      }
      
      throw new Error('Failed to get system information');
    } catch (error) {
      return {
        version: 'unknown',
        uptime: 0,
        memory: { used: 0, total: 0, percentage: 0 },
        cpu: { usage: 0 },
      };
    }
  }

  /**
   * Frontend-specific health check
   */
  static async checkFrontendHealth(): Promise<HealthStatus> {
    const timestamp = new Date().toISOString();
    const startTime = Date.now();
    
    try {
      // Check if we can reach our own API
      const response = await fetch('/api/health');
      const responseTime = Date.now() - startTime;
      
      if (response.ok) {
        const data = await response.json();
        return {
          status: 'healthy',
          timestamp,
          uptime: Date.now() - (performance.timeOrigin || 0),
          version: data.version || process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
          services: [
            {
              name: 'Frontend API',
              status: 'healthy',
              responseTime,
            },
          ],
        };
      } else {
        throw new Error(`Frontend API returned ${response.status}`);
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        timestamp,
        uptime: Date.now() - (performance.timeOrigin || 0),
        version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
        services: [
          {
            name: 'Frontend API',
            status: 'unhealthy',
            message: error instanceof Error ? error.message : 'Unknown error',
          },
        ],
      };
    }
  }
}

// Convenience functions for direct usage
export const checkHealth = HealthApi.checkHealth;
export const checkServiceHealth = HealthApi.checkServiceHealth;
export const checkMultipleServices = HealthApi.checkMultipleServices;
export const ping = HealthApi.ping;
export const getSystemInfo = HealthApi.getSystemInfo;
export const checkFrontendHealth = HealthApi.checkFrontendHealth;