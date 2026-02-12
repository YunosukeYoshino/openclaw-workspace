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
