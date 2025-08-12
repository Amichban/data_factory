import { NextRequest, NextResponse } from 'next/server';
import { HealthStatus } from '@/types';

export async function GET(request: NextRequest) {
  try {
    const startTime = Date.now();
    
    // Basic health check information
    const healthData: HealthStatus = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime() * 1000, // Convert to milliseconds
      version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
      services: [
        {
          name: 'Next.js Server',
          status: 'healthy',
          responseTime: Date.now() - startTime,
        },
        {
          name: 'Node.js Runtime',
          status: 'healthy',
          responseTime: 0,
          message: `Node.js ${process.version}`,
        },
      ],
    };

    // Check memory usage
    const memoryUsage = process.memoryUsage();
    const memoryUsageMB = Math.round(memoryUsage.heapUsed / 1024 / 1024);
    const memoryLimitMB = Math.round(memoryUsage.heapTotal / 1024 / 1024);
    
    // Add memory service health
    healthData.services!.push({
      name: 'Memory Usage',
      status: memoryUsageMB > memoryLimitMB * 0.8 ? 'degraded' : 'healthy',
      responseTime: 0,
      message: `${memoryUsageMB}MB / ${memoryLimitMB}MB`,
    });

    // Check if any environment variables are missing
    const requiredEnvVars = ['NODE_ENV'];
    const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);
    
    if (missingEnvVars.length > 0) {
      healthData.services!.push({
        name: 'Environment Configuration',
        status: 'degraded',
        responseTime: 0,
        message: `Missing: ${missingEnvVars.join(', ')}`,
      });
    } else {
      healthData.services!.push({
        name: 'Environment Configuration',
        status: 'healthy',
        responseTime: 0,
        message: `Environment: ${process.env.NODE_ENV}`,
      });
    }

    // Determine overall status based on service health
    const hasUnhealthyServices = healthData.services!.some(service => service.status === 'unhealthy');
    const hasDegradedServices = healthData.services!.some(service => service.status === 'degraded');
    
    if (hasUnhealthyServices) {
      healthData.status = 'unhealthy';
    } else if (hasDegradedServices) {
      healthData.status = 'degraded';
    }

    // Set appropriate HTTP status code
    const httpStatus = healthData.status === 'healthy' ? 200 : 
                      healthData.status === 'degraded' ? 200 : 503;

    return NextResponse.json({
      success: true,
      data: healthData,
    }, { status: httpStatus });

  } catch (error) {
    // Return unhealthy status if there's an error
    const errorHealthData: HealthStatus = {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      uptime: 0,
      services: [
        {
          name: 'Health Check',
          status: 'unhealthy',
          message: error instanceof Error ? error.message : 'Unknown error occurred',
        },
      ],
    };

    return NextResponse.json({
      success: false,
      data: errorHealthData,
      error: 'Health check failed',
    }, { status: 503 });
  }
}

// Add OPTIONS method for CORS preflight
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}