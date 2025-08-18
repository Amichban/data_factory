# US-005: Events Dashboard UI

**Epic**: User Interface  
**Priority**: P1 (Important)  
**Estimate**: 5 points  
**Dependencies**: US-003, US-004  

## User Story

**As a** Trader/Analyst  
**I want to** view resistance events in a web interface  
**So that** I can monitor market structure changes and identify trading opportunities

## Acceptance Criteria

- [ ] Add "Events" as collapsible menu item in sidebar
- [ ] Create events table page with filters
- [ ] Instrument selector dropdown (29 instruments)
- [ ] Granularity selector (H1, H4, D, W)
- [ ] Event type selector (initially just new_resistance)
- [ ] Display events in sortable table
- [ ] Show all event properties as columns
- [ ] Implement pagination (50 records per page)
- [ ] Add export to CSV functionality
- [ ] Real-time updates when new events detected
- [ ] Load time < 2 seconds for 1000 records

## Technical Requirements

### UI Components
```typescript
// Event Table Columns
interface EventTableColumns {
  eventId: string;
  timestamp: Date;
  instrument: string;
  granularity: string;
  priceLevel: number;
  rebound: number;
  reboundInATR: number;
  volume?: number;
  dayOfWeek: string;
  hourOfDay: number;
}

// Filters
interface EventFilters {
  instrument: string;
  granularity: 'H1' | 'H4' | 'D' | 'W';
  dateRange: { start: Date; end: Date };
  eventType: 'new_resistance';
}
```

### Incremental UI Development
1. **Step 1**: Display raw JSON data from API
2. **Step 2**: Add basic table with sorting
3. **Step 3**: Implement filters and pagination
4. **Step 4**: Apply design system and polish

### Performance Requirements
- Initial load: <2 seconds
- Filter application: <500ms
- Sort operation: <200ms
- Export to CSV: <5 seconds for 10k records

## Test Scenarios

1. **Load Events**: Display 100 events correctly
2. **Filter by Instrument**: Show only EUR_USD events
3. **Filter by Granularity**: Show only H1 events
4. **Date Range**: Filter last 7 days
5. **Sorting**: Sort by price level, timestamp
6. **Pagination**: Navigate through pages
7. **Export**: Download CSV with filters applied
8. **Real-time Update**: New event appears without refresh
9. **Empty State**: Handle no events gracefully

## Definition of Done

- [ ] Events table component created
- [ ] All filters working correctly
- [ ] Sorting implemented for all columns
- [ ] Pagination with page size options
- [ ] Export functionality tested
- [ ] Real-time updates via WebSocket
- [ ] Responsive design for mobile
- [ ] Loading states implemented
- [ ] Error handling for API failures
- [ ] Unit tests for components
- [ ] E2E tests for user flows

## UI/UX Notes

### Design Requirements
- Use DataGrid component from design system
- Highlight recent events (< 1 hour old)
- Color code by instrument groups (majors, minors, exotics)
- Show loading skeleton while fetching
- Sticky header for table
- Tooltips for technical terms

### Mobile Considerations
- Horizontal scroll for table
- Collapsible filters on mobile
- Touch-friendly pagination

## Related Stories

- US-003: Event Detection (provides data)
- US-006: Features Dashboard (similar UI pattern)
- US-007: Operations Dashboard (navigation structure)