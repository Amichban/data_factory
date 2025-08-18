# US-020: Operations Monitoring Page

**Epic**: User Interface  
**Priority**: P1 (Important)  
**Estimate**: 3 points  
**Dependencies**: US-006, US-007  

## User Story

**As a** System Administrator  
**I want to** monitor system operations and performance  
**So that** I can ensure reliable event detection and processing

## Acceptance Criteria

- [ ] Add "Operations" to sidebar menu
- [ ] Display last run times for batch/spike modes
- [ ] Show table statistics (row counts, last update)
- [ ] Display processing performance metrics
- [ ] Show error logs and alerts
- [ ] Add manual trigger buttons for processes
- [ ] Include system health indicators
- [ ] Display resource usage (CPU, memory, storage)

## Technical Requirements

### Monitoring Metrics
```typescript
interface OperationsMetrics {
  processing: {
    batchLastRun: Date;
    spikeLastRun: { [granularity: string]: Date };
    avgProcessingTime: number;
    errorRate: number;
  };
  
  data: {
    totalEvents: number;
    totalFeatures: number;
    storageUsedGB: number;
    oldestData: Date;
  };
  
  health: {
    status: 'healthy' | 'degraded' | 'critical';
    activeAlerts: Alert[];
    uptime: number;
  };
}
```

## Definition of Done

- [ ] Operations page created
- [ ] All metrics displayed
- [ ] Manual triggers working
- [ ] Error logs accessible
- [ ] Health indicators accurate
- [ ] Auto-refresh implemented