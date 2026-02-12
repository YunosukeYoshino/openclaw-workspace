# クイックスタートガイド / Quick Start Guide

## 5分で始めよう / Get Started in 5 Minutes

### ステップ1: インストール / Step 1: Installation

```bash
git clone https://github.com/YunosukeYoshino/openclaw-workspace.git
cd openclaw-workspace
pip install -r requirements.txt
```

### ステップ2: エージェント起動 / Step 2: Start Agent

```bash
python3 agents/debug-agent/agent.py
```

### ステップ3: ダッシュボードアクセス / Step 3: Access Dashboard

```bash
cd dashboard
python3 api.py
```

ブラウザで http://localhost:8000 にアクセス

### ステップ4: エージェント操作 / Step 4: Use Agent

ダッシュボードからエージェントを選択して操作開始

**🎉 これで準備完了！ / Ready to go!**
