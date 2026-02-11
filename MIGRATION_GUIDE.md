# Migration Guide: Agent Orchestrator → Generic Orchestrator

This guide helps you migrate from the agent-specific orchestration system to the generic system.

エージェント固有のオーケストレーションシステムから汎用システムへの移行ガイド。

---

## Overview / 概要

### What Changed? / 何が変わりましたか？

The new generic system removes dependencies on agent-specific concepts and makes the orchestration logic reusable across different types of tasks and projects.

新しい汎用システムはエージェント固有の概念への依存を排除し、異なるタイプのタスクやプロジェクト間でオーケストレーションロジックを再利用可能にします。

| Concept / 概念 | Old (Agent-Specific) / 旧（エージェント固有） | New (Generic) / 新（汎用） |
|----------------|-----------------------------------------------|---------------------------|
| Main Class / メインクラス | `AgentOrchestrator` | `GenericOrchestrator` |
| Supervisor / スーパーバイザー | `Supervisor` | `GenericSupervisor` |
| Task Definition / タスク定義 | `(id, name, description, tags)` tuple | `Task` dataclass |
| Worker / ワーカー | Subagent (with agent ID) | `Worker` dataclass |
| Batch Logic / バッチロジック | Fixed batch size | Dynamic batch sizing |
| Dependencies / 依存関係 | None | Full dependency graph |

---

## Step-by-Step Migration / ステップバイステップの移行

### Step 1: Update Imports / インポートを更新

**Old / 旧:**
```python
from orchestrator import AgentOrchestrator
from supervisor import Supervisor
```

**New / 新:**
```python
from generic_orchestrator import GenericOrchestrator, Task, Worker
from generic_supervisor import GenericSupervisor
```

### Step 2: Convert Task Definitions / タスク定義を変換

**Old / 旧:**
```python
ALL_AGENTS = [
    (41, 'reading-agent', '読書記録', 'books, progress, notes'),
    (42, 'sleep-agent', '睡眠記録', 'sleep time, quality, dreams'),
    (43, 'meditation-agent', '瞑想記録', 'duration, technique, notes'),
]
```

**New / 新:**
```python
tasks = [
    Task(
        id='agent_041',
        type='agent',
        name='reading-agent',
        description='読書記録',
        tags=['books', 'progress', 'notes'],
        priority=1,
        metadata={'agent_number': 41}
    ),
    Task(
        id='agent_042',
        type='agent',
        name='sleep-agent',
        description='睡眠記録',
        tags=['sleep', 'time', 'quality', 'dreams'],
        priority=1,
        metadata={'agent_number': 42}
    ),
    Task(
        id='agent_043',
        type='agent',
        name='meditation-agent',
        description='瞑想記録',
        tags=['duration', 'technique', 'notes'],
        priority=1,
        metadata={'agent_number': 43}
    ),
]
```

### Step 3: Update Orchestrator Initialization / オーケストレーター初期化を更新

**Old / 旧:**
```python
orchestrator = AgentOrchestrator()
```

**New / 新:**
```python
orchestrator = GenericOrchestrator('my_project_config.json')
```

### Step 4: Add Tasks / タスクを追加

**Old / 旧:**
```python
# Tasks were predefined in ALL_AGENTS
# Tasks were not explicitly added
```

**New / 新:**
```python
orchestrator.add_tasks(tasks)
```

### Step 5: Register Workers / ワーカーを登録

**Old / 旧:**
```python
supervisor.register_subagent(
    name='dev-subagent-1',
    session_key='agent:main:subagent:xxx',
    task='エージェント41-45の開発'
)
```

**New / 新:**
```python
# Register worker with orchestrator
worker = Worker(
    id='dev-subagent-1',
    name='Development Subagent 1',
    type='agent_development',
    capacity=5,
    max_parallel_tasks=2,
    metadata={'session_key': 'agent:main:subagent:xxx'}
)
orchestrator.register_worker(worker)

# Register worker with supervisor
supervisor.register_worker(
    worker_id='dev-subagent-1',
    name='Development Subagent 1',
    worker_type='agent_development',
    metadata={'session_key': 'agent:main:subagent:xxx'}
)
```

### Step 6: Update Batch Assignment / バッチ割り当てを更新

**Old / 旧:**
```python
batch = orchestrator.get_next_batch()
# Batch was a list of dictionaries
batch_summary = '\n'.join([
    f"{a['id']}. {a['name']} - {a['description']}"
    for a in batch
])
```

**New / 新:**
```python
# Get next batch
batch = orchestrator.get_next_batch(batch_size=5)

# Assign to worker
task_ids = [t.id for t in batch]
worker_id = 'dev-subagent-1'
if orchestrator.assign_tasks(task_ids, worker_id):
    print(f"Assigned {len(task_ids)} tasks to {worker_id}")
```

### Step 7: Update Task Completion / タスク完了を更新

**Old / 旧:**
```python
orchestrator.update_completion(
    agent_ids=[41, 42, 43],
    subagent_name='dev-subagent-1'
)
```

**New / 新:**
```python
# Mark individual tasks as complete
for task_id in task_ids:
    orchestrator.complete_task(task_id, success=True)

# Or mark as failed with error
orchestrator.complete_task(task_id, success=False,
                          error_message='Network timeout')

# Update progress during execution
orchestrator.update_task_progress(task_id, 0.5)  # 50% complete
```

### Step 8: Update Status Display / ステータス表示を更新

**Old / 旧:**
```python
orchestrator.display_status()
supervisor_status = supervisor.get_status()
print(f"Running: {supervisor_status['running']}")
```

**New / 新:**
```python
# Orchestrator status
orchestrator.display_status()

# Supervisor status
supervisor.display_status()

# Get summary data
summary = orchestrator.get_summary()
print(f"Progress: {summary['progress_percent']:.1f}%")
```

### Step 9: Update Worker Heartbeat / ワーカーハートビートを更新

**Old / 旧:**
```python
supervisor.update_heartbeat(subagent_name)
```

**New / 新:**
```python
# Update heartbeat with optional current task
supervisor.update_heartbeat(
    worker_id='dev-subagent-1',
    current_task='agent_041'
)
```

### Step 10: Update Monitoring / 監視を更新

**Old / 旧:**
```python
supervisor.monitor_loop()
```

**New / 新:**
```python
# With optional callback
def monitor_callback():
    summary = orchestrator.get_summary()
    print(f"Progress: {summary['progress_percent']:.1f}%")

supervisor.monitor_loop(callback=monitor_callback)
```

---

## Complete Migration Example / 完全な移行例

### Before (Agent-Specific) / 以前（エージェント固有）

```python
from orchestrator import AgentOrchestrator
from supervisor import Supervisor

# Initialize
orchestrator = AgentOrchestrator()
supervisor = Supervisor()

# Register subagent
supervisor.register_subagent(
    'dev-subagent-1',
    'agent:main:subagent:xxx',
    'エージェント41-45の開発'
)

# Get batch
batch = orchestrator.get_next_batch()
if batch:
    orchestrator.assign_batch(batch)

# Update completion
orchestrator.update_completion([41, 42, 43], 'dev-subagent-1')

# Display status
orchestrator.display_status()
```

### After (Generic) / その後（汎用）

```python
from generic_orchestrator import GenericOrchestrator, Task, Worker
from generic_supervisor import GenericSupervisor

# Initialize
orchestrator = GenericOrchestrator()
supervisor = GenericSupervisor()

# Define tasks
tasks = [
    Task(id='agent_041', type='agent', name='reading-agent',
         description='読書記録', tags=['books', 'progress']),
    Task(id='agent_042', type='agent', name='sleep-agent',
         description='睡眠記録', tags=['sleep', 'time']),
    Task(id='agent_043', type='agent', name='meditation-agent',
         description='瞑想記録', tags=['meditation', 'duration']),
]
orchestrator.add_tasks(tasks)

# Register worker
worker = Worker(id='dev-subagent-1', name='Development Subagent 1',
                type='agent_development', capacity=5)
orchestrator.register_worker(worker)
supervisor.register_worker('dev-subagent-1', 'Development Subagent 1',
                           'agent_development')

# Get and assign batch
batch = orchestrator.get_next_batch()
if batch:
    task_ids = [t.id for t in batch]
    if orchestrator.assign_tasks(task_ids, 'dev-subagent-1'):
        print(f"Assigned {len(task_ids)} tasks")

# Mark tasks complete
for task_id in task_ids:
    orchestrator.complete_task(task_id, success=True)

# Display status
orchestrator.display_status()
supervisor.display_status()
```

---

## New Features to Explore / 探索すべき新機能

The generic system adds several new features that weren't available before:

汎用システムには、以前にはなかったいくつかの新機能が追加されています：

### 1. Task Dependencies / タスク依存関係

```python
tasks = [
    Task(id='task1', type='extract', name='Extract'),
    Task(id='task2', type='process', name='Process',
         dependencies=['task1']),
    Task(id='task3', type='load', name='Load',
         dependencies=['task2']),
]
```

### 2. Priority System / 優先度システム

```python
Task(id='urgent', name='Urgent', priority=10)
Task(id='normal', name='Normal', priority=1)
```

### 3. Task Filtering / タスクフィルタリング

```python
# Get tasks by type
data_tasks = orchestrator.get_tasks_by_type('data')

# Get tasks by tag
important_tasks = orchestrator.get_tasks_by_tag('critical')
```

### 4. Dynamic Batch Sizing / 動的バッチサイジング

```python
orchestrator.config['auto_adjust_batch_size'] = True
batch = orchestrator.get_next_batch()  # Auto-adjusts based on capacity
```

### 5. Progress Tracking / 進捗追跡

```python
orchestrator.update_task_progress('task_001', 0.5)  # 50%
orchestrator.update_task_progress('task_001', 0.8)  # 80%
```

### 6. Critical Path Analysis / クリティカルパス分析

```python
critical_path = orchestrator.get_critical_path()
print(f"Critical path: {critical_path}")
```

### 7. Worker Status Details / ワーカーステータス詳細

```python
status = orchestrator.get_worker_status('worker_001')
print(f"Load: {status['current_load']}/{status['max_parallel_tasks']}")
```

---

## File Structure Changes / ファイル構造の変更

### Old Files / 旧ファイル

```
orchestrator.py
supervisor.py
agent_monitor.py
dev_progress_tracker.py
orchestrator_progress.json
supervisor_config.json
supervisor_log.json
monitor_log.json
dev_progress.json
```

### New Files / 新ファイル

```
generic_orchestrator.py           # ← Replaces orchestrator.py + dev_progress_tracker.py
generic_supervisor.py             # ← Replaces supervisor.py + agent_monitor.py
generic_orchestrator_config.json  # Orchestrator configuration
generic_supervisor_config.json    # Supervisor configuration
orchestrator_state.json           # Combined state file
orchestrator_history.json         # Event history
supervisor_log.json               # Worker event logs (enhanced)
```

---

## Configuration Migration / 設定の移行

### Orchestrator Config / オーケストレーター設定

Create `generic_orchestrator_config.json`:

```json
{
  "default_batch_size": 5,
  "min_batch_size": 1,
  "max_batch_size": 20,
  "auto_adjust_batch_size": true,
  "max_retries": 3,
  "heartbeat_timeout": 600,
  "progress_update_interval": 30
}
```

### Supervisor Config / スーパーバイザー設定

Create `generic_supervisor_config.json`:

```json
{
  "heartbeat_interval": 300,
  "heartbeat_timeout": 600,
  "max_restarts": 3,
  "restart_delay": 5,
  "monitor_interval": 60,
  "log_retention_days": 30,
  "auto_restart": true
}
```

---

## Testing the Migration / 移行のテスト

### Test Checklist / テストチェックリスト

- [ ] All tasks are properly converted
    すべてのタスクが適切に変換されている
- [ ] Tasks can be added and retrieved
    タスクを追加・取得できる
- [ ] Workers can be registered
    ワーカーを登録できる
- [ ] Batch assignment works
    バッチ割り当てが動作する
- [ ] Task completion updates progress
    タスク完了で進捗が更新される
- [ ] Worker heartbeat monitoring works
    ワーカーハートビート監視が動作する
- [ ] Error recovery works
    エラー回復が動作する
- [ ] Status display shows correct information
    ステータス表示が正しい情報を表示する
- [ ] State is persisted and restored
    状態が永続化・復元される

---

## Troubleshooting / トラブルシューティング

### Issue: Tasks not appearing in batch / 問題: タスクがバッチに表示されない

**Solution / 解決策:**
Ensure tasks have `status='pending'` and all dependencies are satisfied.

タスクが `status='pending'` を持ち、すべての依存関係が満たされていることを確認してください。

```python
# Check task status
status = orchestrator.task_status['task_id']
print(status.status)  # Should be 'pending'

# Check dependencies
task = orchestrator.tasks['task_id']
print(task.dependencies)  # All must be completed
```

### Issue: Worker not receiving tasks / 問題: ワーカーがタスクを受け取らない

**Solution / 解決策:**
Check worker capacity and parallel task limits.

ワーカーの容量と並列タスク制限を確認してください。

```python
status = orchestrator.get_worker_status('worker_id')
print(f"Current load: {status['current_load']}")
print(f"Max parallel: {status['max_parallel_tasks']}")
```

### Issue: State not persisting / 問題: 状態が永続化されない

**Solution / 解決策:**
Ensure you're calling `save_state()` or that it's being called automatically.

`save_state()` を呼び出しているか、自動的に呼び出されていることを確認してください。

```python
# Manual save
orchestrator.save_state()
supervisor.save_state()
```

---

## Getting Help / ヘルプの取得

If you encounter issues during migration:

移行中に問題が発生した場合：

1. Check the examples (`example_data_pipeline.py`, `example_web_scraping.py`)
   例を確認する（`example_data_pipeline.py`、`example_web_scraping.py`）
2. Review the API reference in the main README
   メインREADMEのAPIリファレンスを確認する
3. Examine state files for debugging
   デバッグのために状態ファイルを確認する

---

**Happy migrating! / 移行をお楽しみください！** 🚀
