#!/usr/bin/env python3
"""
Operations Dashboard - 運用ダッシュボード

システム運用状況を一覧表示するダッシュボード
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class OperationsDashboard:
    """運用ダッシュボード"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.data_dir = Path(self.config.get("data_dir", "data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"data_dir": "data", "refresh_interval": 30}

    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": self._get_agents_status(),
            "services": self._get_services_status(),
            "resources": self._get_resource_usage(),
            "alerts": self._get_active_alerts()
        }

    def _get_agents_status(self) -> List[Dict[str, Any]]:
        """エージェントステータスを取得"""
        agents_dir = Path("/workspace/agents")
        agents = []

        for agent_dir in sorted(agents_dir.iterdir()):
            if agent_dir.is_dir():
                agent_name = agent_dir.name
                agents.append({
                    "name": agent_name,
                    "status": "active" if (agent_dir / "agent.py").exists() else "inactive",
                    "last_updated": self._get_last_modified(agent_dir)
                })

        return agents

    def _get_services_status(self) -> List[Dict[str, Any]]:
        """サービスステータスを取得"""
        services = [
            {"name": "Dashboard", "status": "running"},
            {"name": "API Gateway", "status": "running"},
            {"name": "Message Bus", "status": "running"},
            {"name": "Event System", "status": "running"}
        ]
        return services

    def _get_resource_usage(self) -> Dict[str, Any]:
        """リソース使用状況を取得"""
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """アクティブなアラートを取得"""
        return []

    def _get_last_modified(self, path: Path) -> str:
        """最終更新日時を取得"""
        if path.exists():
            timestamp = path.stat().st_mtime
            return datetime.fromtimestamp(timestamp).isoformat()
        return None


def main():
    """メイン関数"""
    dashboard = OperationsDashboard()
    status = dashboard.get_system_status()

    print("System Status:")
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
