# Database Query Optimization

## Index Strategies

```sql
-- Add indexes to frequently queried columns
CREATE INDEX idx_agent_status ON agents(status);
CREATE INDEX idx_agent_type ON agents(type);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
```

## Query Optimization

```python
# Use select_related/prefetch_related for joins
agents = Agent.objects.select_related('owner').filter(status='active')

# Use only() to limit fields
agents = Agent.objects.only('id', 'name', 'status')

# Use bulk operations
Agent.objects.bulk_create(agent_list)
```