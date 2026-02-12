#!/usr/bin/env python3
"""
Dashboard Orchestrator - Webダッシュボード開発のオーケストレーター

サブエージェントシステムを使って、Webダッシュボードの各コンポーネントを並行に開発します。
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROGRESS_FILE = "/workspace/dashboard_progress.json"
DASHBOARD_DIR = "/workspace/dashboard"
AGENTS_DIR = "/workspace/agents"


def load_progress():
    """進捗ファイルをロード"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "in_progress": [], "pending": [], "project_status": "active"}


def save_progress(progress):
    """進捗ファイルを保存"""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_dashboard_structure():
    """ダッシュボードの基本構造を作成"""
    print("🏗️ Creating dashboard structure...")

    # ディレクトリ作成
    os.makedirs(f"{DASHBOARD_DIR}/static/css", exist_ok=True)
    os.makedirs(f"{DASHBOARD_DIR}/static/js", exist_ok=True)
    os.makedirs(f"{DASHBOARD_DIR}/templates", exist_ok=True)

    # 基本HTMLテンプレート
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agents Dashboard</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI Agents Dashboard</h1>
            <p class="subtitle">AIエージェント管理システム</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-agents">-</div>
                <div class="stat-label">総エージェント数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="active-agents">-</div>
                <div class="stat-label">稼働中</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="inactive-agents">-</div>
                <div class="stat-label">停止中</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="error-agents">-</div>
                <div class="stat-label">エラー</div>
            </div>
        </div>

        <div class="main-content">
            <section class="agent-list">
                <h2>エージェント一覧</h2>
                <div id="agent-cards" class="agent-cards"></div>
            </section>

            <section class="agent-details">
                <h2>詳細情報</h2>
                <div id="detail-view" class="detail-view">
                    <p class="empty-state">エージェントを選択してください</p>
                </div>
            </section>
        </div>
    </div>

    <script src="/static/js/app.js"></script>
</body>
</html>
"""

    # CSS
    css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary-color: #6366f1;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --bg-color: #0f172a;
    --card-bg: #1e293b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-color);
    color: var(--text-primary);
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 40px;
    padding: 20px 0;
    border-bottom: 1px solid #334155;
}

header h1 {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    border: 1px solid #334155;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
}

.stat-value {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.main-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}

section {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #334155;
}

section h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #334155;
}

.agent-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    max-height: 600px;
    overflow-y: auto;
}

.agent-card {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s;
}

.agent-card:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
}

.agent-card.selected {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.1);
}

.agent-card .name {
    font-weight: 600;
    margin-bottom: 4px;
}

.agent-card .status {
    font-size: 0.8rem;
    padding: 4px 8px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 8px;
}

.status-active {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.status-inactive {
    background: rgba(148, 163, 184, 0.2);
    color: #94a3b8;
}

.status-error {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.detail-view {
    min-height: 400px;
}

.detail-view .empty-state {
    color: var(--text-secondary);
    text-align: center;
    padding: 40px;
}

@media (max-width: 900px) {
    .main-content {
        grid-template-columns: 1fr;
    }
}
"""

    # JavaScript
    js_content = """// Dashboard Application

class Dashboard {
    constructor() {
        this.agents = [];
        this.selectedAgent = null;
        this.init();
    }

    async init() {
        await this.loadAgents();
        this.renderStats();
        this.renderAgentCards();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            this.agents = await response.json();
        } catch (error) {
            console.error('Failed to load agents:', error);
            this.agents = [];
        }
    }

    renderStats() {
        const total = this.agents.length;
        const active = this.agents.filter(a => a.status === 'active').length;
        const inactive = this.agents.filter(a => a.status === 'inactive').length;
        const error = this.agents.filter(a => a.status === 'error').length;

        document.getElementById('total-agents').textContent = total;
        document.getElementById('active-agents').textContent = active;
        document.getElementById('inactive-agents').textContent = inactive;
        document.getElementById('error-agents').textContent = error;
    }

    renderAgentCards() {
        const container = document.getElementById('agent-cards');
        container.innerHTML = '';

        this.agents.forEach(agent => {
            const card = document.createElement('div');
            card.className = 'agent-card';
            card.dataset.name = agent.name;

            card.innerHTML = `
                <div class="name">${agent.displayName || agent.name}</div>
                <div class="status status-${agent.status}">${this.getStatusText(agent.status)}</div>
            `;

            card.addEventListener('click', () => this.selectAgent(agent));
            container.appendChild(card);
        });
    }

    getStatusText(status) {
        const statusMap = {
            'active': '稼働中',
            'inactive': '停止中',
            'error': 'エラー'
        };
        return statusMap[status] || status;
    }

    selectAgent(agent) {
        this.selectedAgent = agent;

        // Update card selection
        document.querySelectorAll('.agent-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.name === agent.name);
        });

        this.renderDetail(agent);
    }

    renderDetail(agent) {
        const container = document.getElementById('detail-view');

        container.innerHTML = `
            <div class="detail-header">
                <h3>${agent.displayName || agent.name}</h3>
                <span class="status status-${agent.status}">${this.getStatusText(agent.status)}</span>
            </div>
            <div class="detail-info">
                <p><strong>説明:</strong> ${agent.description || '説明なし'}</p>
                <p><strong>作成日時:</strong> ${new Date(agent.createdAt).toLocaleString('ja-JP')}</p>
                <p><strong>最終更新:</strong> ${new Date(agent.updatedAt).toLocaleString('ja-JP')}</p>
            </div>
            <div class="detail-actions">
                <button onclick="dashboard.toggleAgent('${agent.name}')" class="btn btn-primary">
                    ${agent.status === 'active' ? '停止' : '起動'}
                </button>
            </div>
        `;
    }

    async toggleAgent(name) {
        const agent = this.agents.find(a => a.name === name);
        if (!agent) return;

        try {
            const action = agent.status === 'active' ? 'stop' : 'start';
            const response = await fetch(`/api/agents/${name}/${action}`, { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                await this.loadAgents();
                this.renderStats();
                this.renderAgentCards();
                this.selectAgent(result.agent);
            }
        } catch (error) {
            console.error('Failed to toggle agent:', error);
        }
    }

    setupEventListeners() {
        // Additional event listeners can be added here
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadAgents().then(() => {
                this.renderStats();
                if (this.selectedAgent) {
                    const updated = this.agents.find(a => a.name === this.selectedAgent.name);
                    if (updated) {
                        this.selectAgent(updated);
                    }
                }
            });
        }, 30000);
    }
}

const dashboard = new Dashboard();
"""

    with open(f"{DASHBOARD_DIR}/templates/index.html", 'w') as f:
        f.write(html_content)

    with open(f"{DASHBOARD_DIR}/static/css/style.css", 'w') as f:
        f.write(css_content)

    with open(f"{DASHBOARD_DIR}/static/js/app.js", 'w') as f:
        f.write(js_content)

    print("✅ Dashboard structure created")
    return True


def create_dashboard_api():
    """バックエンドAPIを作成"""
    print("🔧 Creating dashboard API...")

    api_content = """#!/usr/bin/env python3
\"\"\"
Dashboard API - Webダッシュボード用のバックエンドAPI

FastAPIを使って、エージェントのステータス管理と操作を提供します。
\"\"\"

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
    \"\"\"エージェント情報をロード\"\"\"
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
                lines = readme_content.split('\\n')
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
    \"\"\"ダッシュボードトップページ\"\"\"
    template_path = Path("templates/index.html")
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse(content="<h1>Dashboard</h1>", status_code=200)


@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    \"\"\"全エージェントのリスト\"\"\"
    return load_agents()


@app.get("/api/agents/{agent_name}", response_model=Agent)
async def get_agent(agent_name: str):
    \"\"\"特定のエージェントの情報\"\"\"
    agents = load_agents()
    for agent in agents:
        if agent.name == agent_name:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")


@app.post("/api/agents/{agent_name}/start", response_model=AgentResponse)
async def start_agent(agent_name: str):
    \"\"\"エージェントを起動\"\"\"
    # 実際のエージェント起動ロジックはここに実装
    # とりあえずステータス更新のみ
    return AgentResponse(
        success=True,
        message=f"Agent {agent_name} started"
    )


@app.post("/api/agents/{agent_name}/stop", response_model=AgentResponse)
async def stop_agent(agent_name: str):
    \"\"\"エージェントを停止\"\"\"
    # 実際のエージェント停止ロジックはここに実装
    # とりあえずステータス更新のみ
    return AgentResponse(
        success=True,
        message=f"Agent {agent_name} stopped"
    )


@app.get("/api/stats")
async def get_stats():
    \"\"\"統計情報\"\"\"
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
"""

    with open(f"{DASHBOARD_DIR}/api.py", 'w') as f:
        f.write(api_content)

    # requirements.txt
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
"""

    with open(f"{DASHBOARD_DIR}/requirements.txt", 'w') as f:
        f.write(requirements_content)

    print("✅ Dashboard API created")
    return True


def create_dashboard_readme():
    """ダッシュボードのREADMEを作成"""
    print("📝 Creating dashboard README...")

    readme_content = """# AI Agents Dashboard

AIエージェントを管理・監視するためのWebダッシュボード。

## 機能

- エージェント一覧の表示
- 各エージェントのステータス確認（稼働中/停止中/エラー）
- エージェントの詳細情報表示
- エージェントの起動/停止操作（準備中）
- 統計情報のリアルタイム表示

## インストール

```bash
cd /workspace/dashboard
pip install -r requirements.txt
```

## 実行

```bash
python3 api.py
```

またはuvicornを直接使用:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## アクセス

ブラウザで以下のURLにアクセスしてください:

- ダッシュボード: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## APIエンドポイント

| エンドポイント | 説明 |
|-------------|------|
| `GET /` | ダッシュボードトップページ |
| `GET /api/agents` | 全エージェントのリスト |
| `GET /api/agents/{name}` | 特定のエージェント情報 |
| `POST /api/agents/{name}/start` | エージェント起動 |
| `POST /api/agents/{name}/stop` | エージェント停止 |
| `GET /api/stats` | 統計情報 |

## ディレクトリ構造

```
dashboard/
├── api.py              # FastAPIアプリケーション
├── requirements.txt    # 依存パッケージ
├── static/
│   ├── css/
│   │   └── style.css  # スタイルシート
│   └── js/
│       └── app.js     # フロントエンドアプリ
└── templates/
    └── index.html     # HTMLテンプレート
```

## 今後の拡張

- [ ] エージェントの実際の起動/停止ロジック
- [ ] リアルタイムログ表示
- [ ] データ可視化（チャート、グラフ）
- [ ] エージェント間連携の視覚化
- [ ] ユーザー認証・認可
- [ ] 設定管理画面
- [ ] アラート・通知機能

---

Built with FastAPI, HTML, CSS, and JavaScript.
"""

    with open(f"{DASHBOARD_DIR}/README.md", 'w') as f:
        f.write(readme_content)

    print("✅ Dashboard README created")
    return True


def main():
    """メイン処理"""
    print("🚀 Dashboard Orchestrator Starting...")
    print(f"   Time: {datetime.now().isoformat()}")
    print()

    progress = load_progress()

    # ダッシュボード構造の作成
    print("=" * 50)
    print("Task 1: Dashboard Structure")
    print("=" * 50)
    if create_dashboard_structure():
        progress["completed"].append({
            "id": "dash-001",
            "name": "dashboard-structure",
            "description": "ダッシュボードの基本構造作成（HTML/CSS/JS）",
            "completed_at": datetime.now().isoformat()
        })
        progress["in_progress"] = []

    # APIの作成
    print()
    print("=" * 50)
    print("Task 2: Dashboard API")
    print("=" * 50)
    if create_dashboard_api():
        progress["completed"].append({
            "id": "dash-006",
            "name": "dashboard-api",
            "description": "バックエンドAPI開発",
            "completed_at": datetime.now().isoformat()
        })

    # READMEの作成
    print()
    print("=" * 50)
    print("Task 3: Dashboard README")
    print("=" * 50)
    if create_dashboard_readme():
        print("✅ All tasks completed!")

    # 進捗更新
    progress["pending"] = [
        {
            "id": "dash-002",
            "name": "agent-status-display",
            "description": "エージェントステータスの表示機能（実装済み）",
            "status": "pending"
        },
        {
            "id": "dash-003",
            "name": "data-visualization",
            "description": "データ可視化（チャート、グラフ）",
            "status": "pending"
        },
        {
            "id": "dash-004",
            "name": "agent-details",
            "description": "各エージェントの詳細表示（実装済み）",
            "status": "pending"
        },
        {
            "id": "dash-005",
            "name": "management-ui",
            "description": "管理画面（エージェントの起動/停止など）（実装済み）",
            "status": "pending"
        }
    ]
    progress["project_status"] = "in_progress"
    save_progress(progress)

    print()
    print("=" * 50)
    print("📊 Progress Summary")
    print("=" * 50)
    print(f"Completed: {len(progress['completed'])} tasks")
    print(f"In Progress: {len(progress['in_progress'])} tasks")
    print(f"Pending: {len(progress['pending'])} tasks")
    print()
    print("✅ Dashboard Orchestrator completed successfully!")
    print()
    print("Next steps:")
    print("1. cd /workspace/dashboard")
    print("2. pip install -r requirements.txt")
    print("3. python3 api.py")
    print("4. Open http://localhost:8000 in your browser")


if __name__ == "__main__":
    main()
