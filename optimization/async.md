# Async Processing

## FastAPI Async

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/agents")
async def get_agents():
    # Use async database operations
    results = await agent_db.fetch_all()
    return results
```

## Task Queue

```python
import asyncio

async def process_task(task_id):
    # Background task processing
    result = await heavy_operation(task_id)
    await save_result(task_id, result)
    return result
```