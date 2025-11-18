# Agent Coordination Protocol

This document describes how multiple agents coordinate their work in the Data Analytics V5 project.

## Overview

The project uses 4 specialized agents working in parallel:
- **Agent 1**: Frontend Specialist
- **Agent 2**: Backend Specialist
- **Agent 3**: Database/Scripts Specialist
- **Agent 4**: UI/UX Design Specialist

## Agent Identification

Each agent identifies itself by reading its agent ID from a dedicated file:
- Agent 1 reads `.agent-1.id` (contains: `1`)
- Agent 2 reads `.agent-2.id` (contains: `2`)
- Agent 3 reads `.agent-3.id` (contains: `3`)
- Agent 4 reads `.agent-4.id` (contains: `4`)

## Agent Configuration

All agents load their configuration from `.agent-config.json`, which defines:
- Agent role and responsibilities
- Allowed and forbidden directories
- Coordination methods
- Which other agents they can coordinate with

## Coordination Method: Code Comments/TODOs

Agents coordinate through code comments using a standardized TODO format.

### TODO Comment Format

```
TODO: [Agent N] description
```

Where:
- `N` is the agent number (1-4)
- `description` is a clear, actionable description of what needs to be done

### Examples

**Frontend requesting backend endpoint:**
```typescript
// TODO: [Agent 2] Add GET /api/customers/demographics endpoint
// Expected response: { data: CustomerDemographics[], metadata: {...} }
const { data } = useQuery({
  queryKey: ["customers", "demographics"],
  queryFn: () => customersAPI.demographics(), // This endpoint doesn't exist yet
});
```

**Backend requesting frontend component:**
```python
# TODO: [Agent 1] Create customer list component that displays:
# - Customer name, email, phone
# - Uses /api/v1/customers endpoint
# - Supports filtering by branch_id
@router.get("/customers", response_model=AnalyticsResponse)
async def get_customers(...):
    # Endpoint is ready, waiting for frontend component
```

**Database requesting backend update:**
```sql
-- TODO: [Agent 2] Update API to use new 'customer_status' column
-- Column added in migration 20240101_add_customer_status.sql
-- Values: 'active', 'inactive', 'pending'
```

**UI/UX requesting frontend implementation:**
```typescript
// TODO: [Agent 1] Implement data fetching for CustomerCard component
// Design is complete, needs API integration
export function CustomerCard() {
  // Component structure ready, needs data
}
```

## Coordination Workflow

### 1. Agent Startup
1. Read agent ID from `.agent-[N].id` file
2. Load configuration from `.agent-config.json`
3. Identify role and boundaries
4. Load role-specific rules from `.cursorrules-[role].md`

### 2. Before Starting Work
1. Search codebase for `TODO: [Agent N]` comments addressed to you
2. Check if other agents are working on related files
3. Review any coordination comments in files you plan to modify
4. Verify you're working within your allowed directories

### 3. During Work
1. Follow role-specific rules strictly
2. Stay within your allowed directories
3. Never modify forbidden directories
4. If you need something from another agent, leave a TODO comment

### 4. After Completing Work
1. Mark completed TODOs as resolved (remove or update comment)
2. Create new TODOs if follow-up work is needed
3. Document API changes in commit messages
4. Update API documentation when endpoints change

## Inter-Agent Communication Patterns

### Frontend ↔ Backend
**Frontend to Backend:**
```typescript
// TODO: [Agent 2] Add POST /api/customers endpoint
// Request body: { name: string, email: string, phone: string }
// Response: { id: number, ...customer }
```

**Backend to Frontend:**
```python
# TODO: [Agent 1] Create customer creation form component
# Endpoint ready: POST /api/v1/customers
# Uses CustomerCreate schema for validation
```

### Backend ↔ Database/Scripts
**Backend to Database:**
```python
# TODO: [Agent 3] Add index on customers.email for faster lookups
# Query performance issue in get_customer_by_email()
```

**Database to Backend:**
```sql
-- TODO: [Agent 2] Update Customer model to include 'last_login_at' timestamp
-- Column added in migration 20240102_add_last_login.sql
```

### Frontend ↔ UI/UX
**Frontend to UI/UX:**
```typescript
// TODO: [Agent 4] Design loading state for customer list
// Current implementation uses basic spinner, needs better UX
```

**UI/UX to Frontend:**
```typescript
// TODO: [Agent 1] Implement data fetching for CustomerCard
// Component structure and styling complete, needs API integration
```

## Task Splitting: Frontend and UI/UX

Agents 1 (Frontend) and 4 (UI/UX) can split tasks between each other:

**UI/UX handles:**
- Visual design and styling
- Component structure and layout
- Design system consistency
- User experience patterns
- Accessibility implementation

**Frontend handles:**
- Data fetching and API integration
- Business logic and state management
- Route handling and navigation
- Performance optimization
- Error handling for API calls

**Coordination example:**
```typescript
// UI/UX creates the component structure
export function CustomerList() {
  // TODO: [Agent 1] Add data fetching using useQuery
  // TODO: [Agent 1] Add error handling for API failures
  // TODO: [Agent 1] Add loading state management
  
  return (
    <div className="grid gap-4">
      {/* Component structure ready */}
    </div>
  );
}
```

## Conflict Prevention

### Directory Boundaries
- Each agent has strict `allowed_directories` and `forbidden_directories`
- Agents must never modify files outside their allowed directories
- If changes are needed in forbidden directories, use TODO comments

### File-Level Coordination
- Before modifying a file, check for existing TODOs
- If another agent is working on the same file, coordinate via comments
- Avoid simultaneous modifications to the same file

### API Contract Coordination
- Backend defines API contracts first
- Frontend implements against contracts
- Changes to contracts require coordination via TODOs

## Best Practices

### Writing Effective TODOs
1. **Be specific**: Include exact endpoint paths, component names, file paths
2. **Provide context**: Explain why the change is needed
3. **Include examples**: Show expected data formats, component props, etc.
4. **Set expectations**: Mention if this blocks other work

### Good TODO Examples
```typescript
// ✅ Good: Specific, actionable, includes context
// TODO: [Agent 2] Add GET /api/customers/{id}/jobs endpoint
// Needed for: Customer detail page job history
// Expected response: { data: Job[], metadata: { total: number } }
```

```python
# ✅ Good: Clear requirement with context
# TODO: [Agent 1] Create CustomerDetailPage component
# Endpoint ready: GET /api/v1/customers/{id}
# Should display: name, email, phone, job history
```

### Bad TODO Examples
```typescript
// ❌ Bad: Too vague, no context
// TODO: [Agent 2] Add endpoint
```

```python
# ❌ Bad: Missing important details
# TODO: [Agent 1] Make component
```

## Resolving TODOs

When you complete a TODO:
1. Remove the TODO comment if work is complete
2. Update the TODO if partial work is done: `// TODO: [Agent 2] Add pagination to endpoint`
3. Add a new TODO if follow-up is needed: `// TODO: [Agent 1] Add pagination UI to component`

## Emergency Coordination

If urgent coordination is needed:
1. Leave a prominent TODO comment at the top of the relevant file
2. Include `[URGENT]` tag: `// TODO: [Agent 2] [URGENT] Fix API endpoint breaking production`
3. Document the issue clearly with steps to reproduce

## Documentation Updates

When making changes that affect other agents:
- Update API documentation if endpoints change
- Update component documentation if props change
- Document schema changes in migration comments
- Update this coordination doc if processes change

## Troubleshooting

### What if I find a TODO that's already been addressed?
- Remove the TODO comment
- Verify the implementation is correct
- Leave a note if you made improvements

### What if I need to modify a forbidden directory?
- Leave a TODO comment for the appropriate agent
- Explain why the change is needed
- Never modify it directly

### What if multiple agents need the same file?
- Coordinate via TODO comments
- One agent should take the lead
- Others should wait or work on related files
- Use version control to track changes

## Summary

- **Identify**: Read `.agent-[N].id` to know your role
- **Configure**: Load `.agent-config.json` for boundaries
- **Coordinate**: Use `TODO: [Agent N]` comments
- **Respect**: Stay within your allowed directories
- **Communicate**: Be specific and provide context in TODOs

