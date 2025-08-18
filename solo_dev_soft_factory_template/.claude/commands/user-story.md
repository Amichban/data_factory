---
name: user-story
description: Generate well-formed user stories with acceptance criteria and test scenarios
tools: [Read, Write, Edit]
---

# User Story Generator

Creates comprehensive user stories following the standard format with acceptance criteria, test scenarios, and technical specifications.

## Usage

```bash
/user-story "As a [role], I want to [action] so that [benefit]"
/user-story --epic "Data Analytics"       # Create story within an epic
/user-story --template                    # Show story template
/user-story --from-issue #5              # Generate from GitHub issue
```

## What It Generates

### 1. User Story Document

```markdown
# US-[NUMBER]: [Title]

## Story Statement
**As a** [role/persona]  
**I want to** [capability/action]  
**So that** [business value/benefit]

## Story Details
- **Epic**: [Parent epic if applicable]
- **Priority**: P0/P1/P2/P3
- **Points**: 1/2/3/5/8/13
- **Type**: Feature/Enhancement/Bug/Technical Debt

## Acceptance Criteria
✅ **AC1**: Given [context], When [action], Then [outcome]
✅ **AC2**: Given [context], When [action], Then [outcome]
✅ **AC3**: Performance: [metric] must be [threshold]
✅ **AC4**: Error handling: [scenario] shows [message]

## Test Scenarios
### Happy Path
- **Scenario**: Normal usage flow
- **Steps**: [1, 2, 3]
- **Expected**: Success with valid data

### Edge Cases
- **Empty data**: System handles gracefully
- **Maximum values**: System remains performant
- **Concurrent access**: No data corruption

### Error Cases
- **Invalid input**: Clear error message
- **Network failure**: Retry with backoff
- **Permission denied**: Appropriate 403 response

## Debug UI Requirements
- **Route**: `/debug/[feature]`
- **Components**: 
  - Data viewer
  - API tester
  - State inspector
- **Actions**:
  - Manual refresh
  - Clear cache
  - Export data

## Production UI Requirements
- **Route**: `/[feature]`
- **Components**:
  - [List components]
- **Interactions**:
  - [User actions]
- **Responsive**: Mobile, tablet, desktop

## Technical Specifications

### API Endpoints
```yaml
- method: GET
  path: /api/v1/[resource]
  response: { data: [], pagination: {} }
  
- method: POST
  path: /api/v1/[resource]
  request: { field1: string, field2: number }
  response: { id: string, created_at: datetime }
```

### Database Changes
```sql
-- New table or modifications
CREATE TABLE IF NOT EXISTS [table_name] (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Performance Requirements
- Response time: < 200ms P95
- Throughput: > 100 req/sec
- Data volume: Handle 10K records

### Security Considerations
- Authentication: Required/Optional
- Authorization: Role-based/Resource-based
- Data sensitivity: PII/Confidential/Public

## Dependencies
- **Blocked by**: [US-XXX]
- **Blocks**: [US-YYY]
- **Related**: [US-ZZZ]

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Debug UI functional
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Acceptance tests automated
- [ ] API documented
- [ ] Performance requirements met
- [ ] Security review completed
- [ ] Code reviewed and approved
- [ ] Deployed to staging
```

### 2. Acceptance Test Stub

```python
# tests/acceptance/test_us_[number].py
"""
Acceptance tests for US-[NUMBER]: [Title]
Generated from user story
"""
import pytest
from tests.fixtures import TestDataFactory

class TestUS[Number][Title]:
    """
    As a [role]
    I want to [action]
    So that [benefit]
    """
    
    @pytest.fixture
    def story_context(self):
        """Setup data specific to this user story"""
        return TestDataFactory.create_story_context("US-[NUMBER]")
    
    @pytest.mark.acceptance
    @pytest.mark.story("US-[NUMBER]")
    async def test_ac1_[description](self, client, story_context):
        """AC1: Given [context], When [action], Then [outcome]"""
        # Given
        await story_context.setup_preconditions()
        
        # When
        response = await client.[method]("[endpoint]")
        
        # Then
        assert response.status_code == 200
        assert response.json()["result"] == "expected"
    
    @pytest.mark.acceptance
    @pytest.mark.performance
    async def test_performance_requirement(self, client, story_context):
        """Performance: Response time < 200ms"""
        response = await client.get("[endpoint]")
        assert response.elapsed.total_seconds() < 0.2
```

### 3. Debug UI Component

```typescript
// apps/web/app/debug/[feature]/page.tsx
/**
 * Debug UI for US-[NUMBER]: [Title]
 * Auto-generated from user story
 */
import { DebugLayout } from '@/components/debug/DebugLayout';
import { useDebugData } from '@/hooks/useDebugData';

export default function Debug[Feature]() {
  const { data, error, isLoading, refetch } = useDebugData('/api/v1/[endpoint]');
  
  return (
    <DebugLayout
      title="US-[NUMBER]: [Title]"
      description="Debug interface for [feature]"
    >
      {/* Story Info */}
      <div className="bg-blue-50 p-4 rounded mb-4">
        <h3 className="font-bold">User Story</h3>
        <p>As a [role], I want to [action] so that [benefit]</p>
      </div>
      
      {/* Acceptance Criteria Checklist */}
      <div className="bg-green-50 p-4 rounded mb-4">
        <h3 className="font-bold">Acceptance Criteria</h3>
        <ul className="space-y-2">
          <li>✅ AC1: [Description]</li>
          <li>✅ AC2: [Description]</li>
        </ul>
      </div>
      
      {/* Data Display */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="font-bold mb-2">Raw Data</h3>
          <pre className="bg-gray-100 p-2 rounded text-xs">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
        
        <div>
          <h3 className="font-bold mb-2">Test Actions</h3>
          <div className="space-y-2">
            <button onClick={refetch} className="btn">Refresh Data</button>
            <button onClick={() => testScenario('happy')} className="btn">Test Happy Path</button>
            <button onClick={() => testScenario('error')} className="btn">Test Error Case</button>
          </div>
        </div>
      </div>
    </DebugLayout>
  );
}
```

## Story Patterns

### CRUD Operations
```yaml
pattern: crud
stories:
  - "As a user, I want to create [resource] so that I can [benefit]"
  - "As a user, I want to view [resource] so that I can [benefit]"
  - "As a user, I want to update [resource] so that I can [benefit]"
  - "As a user, I want to delete [resource] so that I can [benefit]"
  - "As a user, I want to list [resources] so that I can [benefit]"
  - "As a user, I want to search [resources] so that I can [benefit]"
```

### Data Analysis
```yaml
pattern: analytics
stories:
  - "As an analyst, I want to view metrics so that I can track performance"
  - "As an analyst, I want to filter data so that I can focus on specifics"
  - "As an analyst, I want to export data so that I can share insights"
  - "As an analyst, I want to compare periods so that I can identify trends"
```

### Real-time Features
```yaml
pattern: realtime
stories:
  - "As a user, I want to see live updates so that I have current information"
  - "As a user, I want to receive notifications so that I'm informed of changes"
  - "As a user, I want to collaborate in real-time so that we stay synchronized"
```

## Story Quality Checklist

### Good User Story Criteria (INVEST)
- **I**ndependent: Can be developed separately
- **N**egotiable: Details can be discussed
- **V**aluable: Provides clear business value
- **E**stimable: Can be sized/pointed
- **S**mall: Fits in a sprint
- **T**estable: Has clear acceptance criteria

### Acceptance Criteria Quality
- [ ] Written in Given-When-Then format
- [ ] Measurable and specific
- [ ] Includes performance requirements
- [ ] Covers error scenarios
- [ ] Testable through automation

### Technical Completeness
- [ ] API contracts defined
- [ ] Database changes specified
- [ ] Security requirements clear
- [ ] Performance targets set
- [ ] Dependencies identified

## Integration with Other Commands

```bash
# Complete workflow
/user-story "As a user, I want to view dashboard"
# Creates: US-001

/story-to-slice US-001 US-002 US-003
# Creates: VS-001 linked to stories

/debug-ui US-001
# Generates: Debug interface

/acceptance-test US-001
# Generates: Test suite

/issue --from-story US-001
# Creates: GitHub issue
```

## Story Templates

### Feature Story
```markdown
As a [user type]
I want to [perform action]
So that [achieve goal]
```

### Bug Story
```markdown
As a [user type]
I want [issue] to be fixed
So that I can [complete task without issue]
```

### Technical Story
```markdown
As a [developer/system]
I want to [technical improvement]
So that [technical benefit]
```

### Performance Story
```markdown
As a [user type]
I want [action] to be faster
So that [improved experience]
```

## Best Practices

1. **Start with the user**: Always identify the persona first
2. **Focus on value**: The "so that" clause must be clear
3. **Keep it simple**: One capability per story
4. **Make it testable**: Each AC should be verifiable
5. **Size appropriately**: 1-8 story points ideal
6. **Link to UI**: Always specify both debug and production UI
7. **Include examples**: Concrete scenarios help understanding
8. **Define done**: Clear completion criteria

## Output Files

### Generated Files
```
user-stories/
├── active/
│   └── US-001-view-dashboard.md
├── tests/
│   └── acceptance/
│       └── test_us_001.py
└── apps/
    └── web/
        └── app/
            └── debug/
                └── dashboard/
                    └── page.tsx
```

## Metrics Tracking

The command automatically updates story metrics:
```yaml
# .claude/metrics/stories.yaml
total_stories: 25
by_status:
  backlog: 10
  in_progress: 5
  completed: 10
by_size:
  small: 8
  medium: 12
  large: 5
test_coverage:
  with_acceptance_tests: 20
  with_debug_ui: 18
  fully_automated: 15
```