# Agent Coordination Protocol

This document describes how multiple agents coordinate their work in the Data Analytics V5 project.

## Overview

The project uses 4 specialized agents working in parallel:
- **Agent 1**: Frontend UI/UX Design Expert
- **Agent 2**: Backend Specialist
- **Agent 3**: Database/Scripts Specialist
- **Agent 4**: Full-Stack Engineer

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

**Full-Stack Engineer coordinating end-to-end implementation:**
```typescript
// TODO: [Agent 2] Add GET /api/v1/customers endpoint
// TODO: [Agent 1] Create CustomerList component using the endpoint
// TODO: [Agent 4] Test complete customer list flow end-to-end
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

### Full-Stack Engineer ↔ All Agents
**Full-Stack Engineer coordinating end-to-end features:**
```typescript
// TODO: [Agent 2] Add POST /api/v1/customers endpoint
// TODO: [Agent 1] Create customer creation form component
// TODO: [Agent 4] Test complete customer creation flow
// TODO: [Agent 3] Add index on customers.email for performance
```

**Full-Stack Engineer requesting integration testing:**
```typescript
// TODO: [Agent 4] Test customer list flow end-to-end
// - Frontend: CustomerList component
// - Backend: GET /api/v1/customers endpoint
// - Database: Verify query performance
```

**Full-Stack Engineer optimizing across stack:**
```python
# TODO: [Agent 4] Optimize customer query performance
# - Database: Add index on customers.created_at
# - Backend: Optimize query to use index
# - Frontend: Implement pagination for large result sets
```

## Full-Stack Engineer Role

Agent 4 (Full-Stack Engineer) has a unique position in the system:

**Responsibilities:**
- End-to-end feature implementation spanning all layers
- Integration and E2E testing across the stack
- System architecture understanding and documentation
- Performance optimization across frontend/backend/database
- Deployment coordination and DevOps considerations

**Coordination Patterns:**
- Can coordinate with all agents (1, 2, 3, 4)
- Orchestrates complex features requiring multiple agents
- Tests complete flows from UI to database
- Optimizes performance holistically across layers
- Documents system architecture and integration points

**Example End-to-End Implementation:**
```typescript
// Frontend: app/customers/page.tsx
// TODO: [Agent 2] Implement GET /api/v1/customers endpoint
// TODO: [Agent 4] Test complete customer list flow
const { data } = useQuery({
  queryKey: ["customers"],
  queryFn: () => customersAPI.list(),
});
```

```python
# Backend: app/api/v1/customers.py
# TODO: [Agent 3] Add index on customers.email
# TODO: [Agent 4] Test API performance with new index
@router.get("/customers", response_model=AnalyticsResponse)
async def get_customers(...):
    # Implementation
```

```sql
-- Database: sql/queries/customers.sql
-- TODO: [Agent 4] Test query performance end-to-end
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
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
- Full-Stack Engineer tests and validates contracts
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

```typescript
// ✅ Good: Full-Stack Engineer coordinating end-to-end
// TODO: [Agent 2] Add GET /api/v1/customers/{id}/jobs endpoint
// TODO: [Agent 1] Display job history in CustomerDetailPage
// TODO: [Agent 4] Test complete customer detail flow
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

