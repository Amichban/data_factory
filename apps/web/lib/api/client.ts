import { ApiClientConfig, ApiError, ApiResponse, FetchOptions } from '@/types';

class ApiClient {
  private baseUrl: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout || 10000; // Default 10 seconds
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...config.headers,
    };
  }

  private async fetchWithTimeout(
    url: string,
    options: FetchOptions = {}
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      options.timeout || this.timeout
    );

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...this.defaultHeaders,
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return data;
      } else {
        const text = await response.text();
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return {
          success: true,
          data: text as T,
        };
      }
    } catch (error) {
      if (error instanceof Error) {
        throw new ApiError(error.message, response.status);
      }
      throw new ApiError('Unknown error occurred', response.status);
    }
  }

  private buildUrl(endpoint: string): string {
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${this.baseUrl}/${cleanEndpoint}`;
  }

  async get<T>(endpoint: string, options: FetchOptions = {}): Promise<ApiResponse<T>> {
    try {
      const response = await this.fetchWithTimeout(this.buildUrl(endpoint), {
        ...options,
        method: 'GET',
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Network error occurred'
      );
    }
  }

  async post<T>(
    endpoint: string,
    data?: unknown,
    options: FetchOptions = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.fetchWithTimeout(this.buildUrl(endpoint), {
        ...options,
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Network error occurred'
      );
    }
  }

  async put<T>(
    endpoint: string,
    data?: unknown,
    options: FetchOptions = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.fetchWithTimeout(this.buildUrl(endpoint), {
        ...options,
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Network error occurred'
      );
    }
  }

  async delete<T>(endpoint: string, options: FetchOptions = {}): Promise<ApiResponse<T>> {
    try {
      const response = await this.fetchWithTimeout(this.buildUrl(endpoint), {
        ...options,
        method: 'DELETE',
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        error instanceof Error ? error.message : 'Network error occurred'
      );
    }
  }
}

// Custom error class for API errors
class ApiError extends Error {
  public status?: number;
  public code?: string;

  constructor(message: string, status?: number, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

// Export the ApiError class
export { ApiError };

// Create and export a default instance
export const apiClient = new ApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  timeout: 10000,
});

export default ApiClient;