---
name: review-agents
description: Review and edit agent allocations proposed by PM for each slice
tools: [Read, Edit, TodoWrite]
---

# Review Agent Allocations

After running `/scope` to generate slices, use this command to review and edit the proposed agent allocations.

## Process

1. Read the current scope.json file
2. Display the proposed agent sequences for each slice
3. Allow user to confirm or edit allocations
4. Update scope.json with final allocations
5. Create a task list with agent assignments

## Usage

```bash
/review-agents
```

This will:
1. Show each slice with its proposed agent sequence
2. Ask for confirmation or edits
3. Update the scope file
4. Generate a development todo list

## Example Output

```
Slice: User Login
Current agent sequence:
1. architect - Design authentication flow
2. dba - Create user tables
3. backend - Implement login endpoint
4. frontend - Create login form
5. security - Review implementation

Do you want to:
[A]ccept this sequence
[E]dit the sequence
[R]emove an agent
[A]dd an agent
```

## Integration with /accept-scope

Once agent allocations are reviewed and confirmed:
- The `/accept-scope` command will include agent assignments in issue descriptions
- Each issue will have a "Development Sequence" section with assigned agents
- This provides clear guidance on which agents to use for each task