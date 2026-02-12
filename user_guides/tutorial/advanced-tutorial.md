# 上級チュートリアル / Advanced Tutorial

## 高度な機能とカスタマイズ / Advanced Features & Customization

### カスタムエージェント作成 / Creating Custom Agents

```python
# my-agent/agent.py
from db import Database
from discord import DiscordParser

class MyAgent:
    def __init__(self):
        self.db = Database("my_agent.db")
        self.parser = DiscordParser()

    def process(self, text: str):
        # 自然言語解析
        intent = self.parser.parse(text)

        # 処理実行
        if intent.action == "create":
            return self.create_item(intent.data)
        elif intent.action == "list":
            return self.list_items()

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

### エージェント間連携 / Agent Integration

```python
from event_bus import EventBus

# イベント発行
bus = EventBus()
bus.publish("task.created", {"task": "example"})

# イベント購読
@bus.subscribe("task.created")
def on_task_created(data):
    print(f"Task created: {data['task']}")
```

### ワークフローの作成 / Creating Workflows

```python
from workflow_engine import WorkflowEngine

engine = WorkflowEngine()

workflow = engine.create_workflow("daily-report")
workflow.add_step("collect_data", data_collector)
workflow.add_step("analyze", analyzer)
workflow.add_step("send_report", sender)

engine.execute(workflow)
```
