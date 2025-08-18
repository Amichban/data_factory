# US-009: Store Events Transaction

**Epic**: Data Storage & Management  
**Priority**: P0 (Core)  
**Estimate**: 3 points  
**Dependencies**: US-003, US-004  

## User Story

**As a** System  
**I want to** persist detected events with transactional integrity  
**So that** no events are lost and data remains consistent

## Acceptance Criteria

- [ ] Insert events into new_resistance_events table
- [ ] Insert corresponding entry in master table
- [ ] Implement transaction for atomicity
- [ ] Handle duplicate event detection
- [ ] Implement batch insert for performance (1000 records/batch)
- [ ] Add retry logic for transient failures
- [ ] Log all database operations
- [ ] Maintain referential integrity

## Technical Requirements

### Transaction Implementation
```python
async def store_events(events: List[Event]):
    async with database.transaction():
        # Insert into events table
        event_ids = await bulk_insert_events(events)
        
        # Insert into master table
        await bulk_insert_master(event_ids)
        
        # Update statistics
        await update_statistics(len(events))
```

## Definition of Done

- [ ] Transaction rollback tested
- [ ] Bulk insert optimized
- [ ] Duplicate handling verified
- [ ] Performance benchmarks met
- [ ] Error recovery tested