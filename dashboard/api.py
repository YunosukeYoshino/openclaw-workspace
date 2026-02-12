#!/usr/bin/env python3
"""
Dashboard API - Webダッシュボード用のバックエンドAPI

FastAPIを使って、エージェントのステータス管理と操作を提供します。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 設定
AGENTS_DIR = "/workspace/agents"
PROGRESS_FILE = "/workspace/dashboard_progress.json"

app = FastAPI(title="AI Agents Dashboard API", version="1.0.0")

# 静的ファイルとテンプレートのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")


# モデル
class Agent(BaseModel):
    name: str
    displayName: Optional[str] = None
    description: Optional[str] = None
    status: str = "inactive"
    createdAt: str
    updatedAt: str


class AgentResponse(BaseModel):
    success: bool
    agent: Optional[Agent] = None
    message: Optional[str] = None


# エージェント情報のロード
def load_agents() -> List[Agent]:
    """エージェント情報をロード"""
    agents = []

    if not os.path.exists(AGENTS_DIR):
        return agents

    for agent_dir in sorted(Path(AGENTS_DIR).iterdir()):
        if not agent_dir.is_dir():
            continue

        name = agent_dir.name

        # README.mdから情報を取得
        readme_path = agent_dir / "README.md"
        description = None
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
                # 最初の段落を説明として使用
                lines = readme_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        description = line
                        break

        # 表示名を作成
        display_name = name.replace('-agent', '').replace('-', ' ').title()
        display_name = display_name.replace(' ', '')  # 英語風に
        display_name = display_name[0].lower() + display_name[1:]  # 小文字開始

        agents.append(Agent(
            name=name,
            displayName=display_name,
            description=description,
            status="active",  # デフォルトは稼働中と仮定
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        ))

    return agents


# エンドポイント
@app.get("/", response_class=HTMLResponse)
async def index():
    """ダッシュボードトップページ"""
    template_path = Path("templates/index.html")
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse(content="<h1>Dashboard</h1>", status_code=200)


@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    """全エージェントのリスト"""
    return load_agents()


@app.get("/api/agents/{agent_name}", response_model=Agent)
async def get_agent(agent_name: str):
    """特定のエージェントの情報"""
    agents = load_agents()
    for agent in agents:
        if agent.name == agent_name:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")


@app.post("/api/agents/{agent_name}/start", response_model=AgentResponse)
async def start_agent(agent_name: str):
    """エージェントを起動"""
    # 実際のエージェント起動ロジックはここに実装
    # とりあえずステータス更新のみ
    return AgentResponse(
        success=True,
        message=f"Agent {agent_name} started"
    )


@app.post("/api/agents/{agent_name}/stop", response_model=AgentResponse)
async def stop_agent(agent_name: str):
    """エージェントを停止"""
    # 実際のエージェント停止ロジックはここに実装
    # とりあえずステータス更新のみ
    return AgentResponse(
        success=True,
        message=f"Agent {agent_name} stopped"
    )


@app.get("/api/stats")
async def get_stats():
    """統計情報"""
    agents = load_agents()
    return {
        "total": len(agents),
        "active": len([a for a in agents if a.status == "active"]),
        "inactive": len([a for a in agents if a.status == "inactive"]),
        "error": len([a for a in agents if a.status == "error"]),
        "last_updated": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ============================================
# エージェント制御エンドポイント
# ============================================

class AgentManager:
    def __init__(self):
        self.agents_dir = "/workspace/agents"
        self.active_agents = {}

    def list_agents(self):
        agents = []
        agents_dir = Path(self.agents_dir)
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir():
                    agent_file = agent_dir / "agent.py"
                    if agent_file.exists():
                        agents.append({
                            "name": agent_dir.name,
                            "status": "running" if agent_dir.name in self.active_agents else "stopped",
                            "path": str(agent_dir)
                        })
        return agents

    def start_agent(self, agent_name):
        if agent_name in self.active_agents:
            return {"status": "error", "message": f"{agent_name} is already running"}

        agent_file = Path(self.agents_dir) / agent_name / "agent.py"
        if not agent_file.exists():
            return {"status": "error", "message": f"Agent {agent_name} not found"}

        self.active_agents[agent_name] = {
            "started_at": datetime.now().isoformat(),
            "pid": len(self.active_agents) + 1000
        }

        return {"status": "success", "message": f"{agent_name} started"}

    def stop_agent(self, agent_name):
        if agent_name not in self.active_agents:
            return {"status": "error", "message": f"{agent_name} is not running"}

        del self.active_agents[agent_name]

        return {"status": "success", "message": f"{agent_name} stopped"}

agent_manager = AgentManager()

@app.get("/api/agents/list")
async def list_agents():
    return agent_manager.list_agents()

@app.post("/api/agents/{agent_name}/start")
async def start_agent(agent_name: str):
    return agent_manager.start_agent(agent_name)

@app.post("/api/agents/{agent_name}/stop")
async def stop_agent(agent_name: str):
    return agent_manager.stop_agent(agent_name)

# ============================================
# ログ管理エンドポイント
# ============================================

class LogManager:
    def __init__(self):
        self.logs = []

    def add_log(self, level, message, agent="system"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "agent": agent,
            "message": message
        }
        self.logs.append(log_entry)
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

    def get_logs(self, limit=50):
        return self.logs[-limit:]

log_manager = LogManager()

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    return log_manager.get_logs(limit)

# ============================================
# アクティビティ追跡エンドポイント
# ============================================

class ActivityTracker:
    def __init__(self):
        self.activities = []
        for i in range(24):
            self.activities.append({
                "hour": i,
                "count": int(5 + 3 * (i % 6) + (i // 4)),
                "type": "agent_start" if i % 2 == 0 else "agent_stop"
            })

    def get_activity_chart_data(self):
        return self.activities

activity_tracker = ActivityTracker()

@app.get("/api/activity/chart")
async def get_activity_chart():
    return activity_tracker.get_activity_chart_data()

# ============================================
# エージェントグラフエンドポイント
# ============================================

@app.get("/api/agents/graph")
async def get_agent_graph():
    return {
        "nodes": [
            {"id": "orchestrator", "label": "Orchestrator", "type": "controller"},
            {"id": "monitor-agent", "label": "Monitor Agent", "type": "agent"},
            {"id": "deploy-agent", "label": "Deploy Agent", "type": "agent"},
            {"id": "notification-agent", "label": "Notification Agent", "type": "agent"},
            {"id": "calendar-integration-agent", "label": "Calendar Agent", "type": "agent"},
        ],
        "edges": [
            {"source": "orchestrator", "target": "monitor-agent", "type": "controls"},
            {"source": "orchestrator", "target": "deploy-agent", "type": "controls"},
            {"source": "monitor-agent", "target": "notification-agent", "type": "notifies"},
            {"source": "deploy-agent", "target": "notification-agent", "type": "notifies"},
            {"source": "orchestrator", "target": "calendar-integration-agent", "type": "uses"},
        ]
    }

# ============================================
# 認証エンドポイント
# ============================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.valid_tokens = {
            "dev-token-12345": {"user": "admin", "role": "admin"},
            "dev-token-67890": {"user": "viewer", "role": "viewer"}
        }

    def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        if token not in self.valid_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return self.valid_tokens[token]

auth_manager = AuthManager()

@app.get("/api/auth/me")
async def get_current_user(user = Depends(auth_manager.verify_token)):
    return user

# ============================================
# 設定管理エンドポイント
# ============================================

from pydantic import BaseModel

class SettingItem(BaseModel):
    key: str
    value: str

class SettingsManager:
    def __init__(self):
        self.settings = {
            "theme": "dark",
            "refresh_interval": "30",
            "log_level": "info",
            "notifications_enabled": "true"
        }

    def get_settings(self):
        return self.settings

    def update_setting(self, key, value):
        if key in self.settings:
            self.settings[key] = value
            return {"status": "success", "key": key, "value": value}
        return {"status": "error", "message": f"Setting {key} not found"}

    def update_multiple(self, settings_list):
        results = []
        for item in settings_list:
            result = self.update_setting(item.key, item.value)
            results.append(result)
        return {"results": results}

settings_manager = SettingsManager()

@app.get("/api/settings")
async def get_settings():
    return settings_manager.get_settings()

@app.post("/api/settings")
async def update_setting(setting: SettingItem):
    return settings_manager.update_setting(setting.key, setting.value)

@app.post("/api/settings/batch")
async def update_multiple_settings(settings: list[SettingItem]):
    return settings_manager.update_multiple(settings)
