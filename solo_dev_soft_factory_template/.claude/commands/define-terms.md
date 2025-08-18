---
name: define-terms
description: Generate glossary of technical terms with precise definitions
tools: [Read, Write]
---

# Term Definition Generator

Extracts all technical terms from your specification and creates precise, unambiguous definitions.

## Usage

```bash
/define-terms                  # Generate glossary from current scope
/define-terms --domain finance # Include domain-specific definitions
/define-terms --formulas       # Include mathematical definitions
```

## What It Generates

### 1. Technical Glossary
```yaml
glossary:
  terms:
    active_user:
      definition: "User with last_activity_timestamp < 7 days from current_time"
      type: boolean
      formula: "now() - user.last_activity < 604800"
      examples:
        - "User logged in 3 days ago: active_user = true"
        - "User logged in 10 days ago: active_user = false"
    
    session_timeout:
      definition: "Duration in seconds before session expires"
      type: integer
      default: 1800
      constraints: "Must be between 300 and 86400"
      formula: "last_activity + timeout_duration < current_time"
```

### 2. Mathematical Definitions
```yaml
formulas:
  percentage_change:
    definition: "Relative change between two values"
    formula: "(new_value - old_value) / old_value * 100"
    edge_cases:
      - condition: "old_value == 0"
        result: "return 0 or NULL based on business logic"
      - condition: "new_value == NULL"
        result: "return NULL"
    precision: "Round to 2 decimal places"
    
  moving_average:
    definition: "Simple moving average over N periods"
    formula: "sum(values[-N:]) / N"
    parameters:
      N: "Number of periods (typically 20, 50, or 200)"
    requirements: "Minimum N values required before calculation"
```

### 3. State Definitions
```yaml
states:
  order_status:
    pending:
      definition: "Order created but not yet processed"
      transitions: ["processing", "cancelled"]
      timeout: "Cancel if pending > 24 hours"
    
    processing:
      definition: "Payment verified, preparing shipment"
      transitions: ["shipped", "failed", "refunded"]
      sla: "Must transition within 4 hours"
    
    shipped:
      definition: "Package handed to carrier"
      transitions: ["delivered", "returned"]
      tracking: "Required carrier tracking number"
```

### 4. Data Type Definitions
```yaml
data_types:
  price:
    type: "decimal"
    precision: 5
    scale: 2
    constraints: "Must be > 0"
    example: "123.45"
    
  timestamp:
    type: "datetime"
    timezone: "UTC"
    format: "ISO 8601"
    example: "2024-01-15T14:30:00Z"
    
  currency_pair:
    type: "string"
    pattern: "^[A-Z]{3}/[A-Z]{3}$"
    example: "EUR/USD"
    validation: "Must be in supported_pairs list"
```

### 5. Business Rules
```yaml
business_rules:
  minimum_order_value:
    definition: "Smallest acceptable order amount"
    value: 10.00
    currency: "USD"
    applies_to: "All orders except samples"
    
  spike_threshold:
    definition: "Price movement to trigger spike detection"
    formula: "abs(price_change) > ATR(14) * 2"
    components:
      - ATR: "Average True Range over 14 periods"
      - multiplier: "2 (configurable)"
```

## Common Patterns

### Time-Related Terms
```yaml
business_hours:
  definition: "Active trading hours"
  timezone: "America/New_York"
  schedule:
    monday-friday: "09:30-16:00"
    saturday-sunday: "closed"
  holidays: "NYSE calendar"
  
end_of_day:
  definition: "Daily settlement time"
  time: "17:00"
  timezone: "America/New_York"
  note: "16:00 during DST"
```

### Calculation Terms
```yaml
compound_interest:
  definition: "Interest calculated on principal and accumulated interest"
  formula: "A = P(1 + r/n)^(nt)"
  variables:
    A: "Final amount"
    P: "Principal"
    r: "Annual rate (decimal)"
    n: "Compounds per year"
    t: "Time in years"
```

### Event Terms
```yaml
green_candle:
  definition: "Trading period where close > open"
  formula: "candle.close > candle.open + epsilon"
  epsilon: 0.00001
  note: "Epsilon prevents floating point equality issues"
  
resistance_level:
  definition: "Price level where upward movement historically stalls"
  calculation: "Local maximum over N periods"
  validation: "Must be tested at least twice"
```

## Output Files

### Generated Glossary
```markdown
# Project Glossary

## A

**Active User**: User with activity within last 7 days
- Formula: `now() - last_activity < 604800`
- Type: Boolean
- See also: Inactive User, Session

**ATR (Average True Range)**: Volatility indicator
- Formula: `EMA(TR, period)`
- Default Period: 14
- Range: [0, ∞)

## B

**Business Day**: Monday-Friday excluding holidays
- Hours: 09:00-17:00 ET
- Holidays: NYSE calendar
- See also: Settlement Day
```

### Decision Log
```yaml
decisions:
  - id: TERM-001
    term: "spike"
    options:
      - "Price change > 2 * ATR"
      - "Price change > 3% in 5 minutes"
      - "Volume > 2 * average volume"
    decision: "Price change > 2 * ATR"
    rationale: "ATR adapts to volatility"
    decided_by: "PM"
    date: "2024-01-15"
```

## Integration with Spec Process

```bash
# Workflow
/scope #1                      # Generate initial scope
/define-terms                  # Extract and define all terms
/spec-lint                     # Check for undefined terms
/spec-enhance --add-glossary  # Add glossary to spec
/accept-scope                  # Proceed with clear definitions
```

## Best Practices

1. **Define Early**: Create glossary before implementation
2. **Be Precise**: Use mathematical notation where applicable
3. **Include Examples**: Show edge cases and normal cases
4. **Version Control**: Track term changes over time
5. **Cross-Reference**: Link related terms
6. **Domain Alignment**: Use industry-standard definitions
7. **Avoid Ambiguity**: Each term should have single interpretation