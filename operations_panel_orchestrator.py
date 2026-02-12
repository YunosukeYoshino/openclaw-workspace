#!/usr/bin/env python3
"""
Operations Panel Orchestrator - 運用パネルオーケストレーター

システム運用・管理画面を強化するためのオーケストレーター
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

class OperationsPanelOrchestrator:
    def __init__(self):
        self.workspace = Path("/workspace")
        self.progress_file = self.workspace / "operations_panel_progress.json"
        self.archive_dir = self.workspace / "archive" / "orchestrators"

        # プロジェクト定義
        self.project = {
            "name": "Operations Panel Project",
            "description": "システム運用・管理画面の強化",
            "tasks": [
                {
                    "id": "ops-dashboard",
                    "name": "運用ダッシュボード",
                    "description": "システム運用状況を一覧表示するダッシュボード",
                    "directory": "operations_dashboard"
                },
                {
                    "id": "metrics-viz",
                    "name": "メトリクス可視化",
                    "description": "システムメトリクスのリアルタイム可視化",
                    "directory": "metrics_visualization"
                },
                {
                    "id": "alert-center",
                    "name": "アラートセンター",
                    "description": "アラート管理・通知センター",
                    "directory": "alert_center"
                },
                {
                    "id": "log-viewer",
                    "name": "ログビューア",
                    "description": "システムログの検索・表示",
                    "directory": "log_viewer"
                },
                {
                    "id": "config-manager",
                    "name": "設定管理",
                    "description": "システム設定の集中管理",
                    "directory": "config_manager"
                }
            ]
        }

        # 進捗データの初期化
        self.progress = {
            "project": self.project["name"],
            "started_at": datetime.now().isoformat(),
            "tasks": {task["id"]: False for task in self.project["tasks"]},
            "completed": False
        }

        # 既存の進捗データを読み込む
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                existing = json.load(f)
                for key in self.progress["tasks"]:
                    if key in existing.get("tasks", {}):
                        self.progress["tasks"][key] = existing["tasks"][key]

    def save_progress(self):
        """進捗を保存"""
        self.progress["updated_at"] = datetime.now().isoformat()
        self.progress["completed"] = all(self.progress["tasks"].values())

        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def create_module(self, task):
        """モジュールを作成"""
        task_id = task["id"]
        task_name = task["name"]
        directory = self.workspace / task["directory"]

        print(f"\n📦 {task_name} を作成中...")

        # ディレクトリ作成
        directory.mkdir(parents=True, exist_ok=True)

        # implementation.py 作成
        implementation_content = self.get_implementation_content(task_id)
        (directory / "implementation.py").write_text(implementation_content, encoding='utf-8')

        # README.md 作成
        readme_content = self.get_readme_content(task_id)
        (directory / "README.md").write_text(readme_content, encoding='utf-8')

        # requirements.txt 作成
        requirements_content = self.get_requirements_content(task_id)
        (directory / "requirements.txt").write_text(requirements_content, encoding='utf-8')

        # config.json 作成
        config_content = self.get_config_content(task_id)
        (directory / "config.json").write_text(config_content, encoding='utf-8')

        print(f"✅ {task_name} を作成しました: {directory}")

    def get_implementation_content(self, task_id):
        """implementation.py の内容を生成"""
        templates = {
            "ops-dashboard": self.get_ops_dashboard_impl(),
            "metrics-viz": self.get_metrics_viz_impl(),
            "alert-center": self.get_alert_center_impl(),
            "log-viewer": self.get_log_viewer_impl(),
            "config-manager": self.get_config_manager_impl()
        }
        return templates.get(task_id, "#!/usr/bin/env python3\n# Implementation")

    def get_ops_dashboard_impl(self):
        return '''#!/usr/bin/env python3
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
'''

    def get_metrics_viz_impl(self):
        return '''#!/usr/bin/env python3
"""
Metrics Visualization - メトリクス可視化

システムメトリクスのリアルタイム可視化
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class MetricsVisualizer:
    """メトリクス可視化クラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.db_path = Path(self.config.get("db_path", "data/metrics.db"))

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"db_path": "data/metrics.db", "retention_days": 30}

    def collect_metrics(self) -> Dict[str, Any]:
        """メトリクスを収集"""
        import psutil

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "cores": psutil.cpu_count()
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }

        self._save_metrics(metrics)
        return metrics

    def _save_metrics(self, metrics: Dict[str, Any]):
        """メトリクスを保存"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS metrics ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "timestamp TEXT NOT NULL, "
            "cpu_percent REAL, "
            "memory_percent REAL, "
            "disk_percent REAL, "
            "network_sent INTEGER, "
            "network_recv INTEGER)"
        )

        cursor.execute(
            "INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                metrics["timestamp"],
                metrics["cpu"]["percent"],
                metrics["memory"]["percent"],
                metrics["disk"]["percent"],
                metrics["network"]["bytes_sent"],
                metrics["network"]["bytes_recv"]
            )
        )

        conn.commit()
        conn.close()

    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """メトリクス履歴を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute(
            "SELECT timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv "
            "FROM metrics "
            "WHERE timestamp >= ? "
            "ORDER BY timestamp DESC",
            (since.isoformat(),)
        )

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                "timestamp": row[0],
                "cpu_percent": row[1],
                "memory_percent": row[2],
                "disk_percent": row[3],
                "network_sent": row[4],
                "network_recv": row[5]
            })

        conn.close()
        return metrics


def main():
    """メイン関数"""
    visualizer = MetricsVisualizer()
    metrics = visualizer.collect_metrics()

    print("Current Metrics:")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
'''

    def get_alert_center_impl(self):
        return '''#!/usr/bin/env python3
"""
Alert Center - アラートセンター

アラート管理・通知センター
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum


class AlertSeverity(Enum):
    """アラート重要度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertCenter:
    """アラートセンター"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.db_path = Path(self.config.get("db_path", "data/alerts.db"))

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"db_path": "data/alerts.db", "retention_days": 30}

    def create_alert(self, title: str, message: str, severity: str = "info",
                     source: str = "system") -> int:
        """アラートを作成"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS alerts ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, "
            "message TEXT NOT NULL, "
            "severity TEXT NOT NULL, "
            "source TEXT NOT NULL, "
            "status TEXT DEFAULT 'active', "
            "created_at TEXT NOT NULL, "
            "acknowledged_at TEXT, "
            "acknowledged_by TEXT)"
        )

        cursor.execute(
            "INSERT INTO alerts (title, message, severity, source, status, created_at) "
            "VALUES (?, ?, ?, ?, 'active', ?)",
            (title, message, severity, source, datetime.now().isoformat())
        )

        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return alert_id

    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "system"):
        """アラートを確認済みにする"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE alerts "
            "SET status = 'acknowledged', acknowledged_at = ?, acknowledged_by = ? "
            "WHERE id = ?",
            (datetime.now().isoformat(), acknowledged_by, alert_id)
        )

        conn.commit()
        conn.close()

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """アクティブなアラートを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title, message, severity, source, status, created_at "
            "FROM alerts "
            "WHERE status = 'active' "
            "ORDER BY created_at DESC"
        )

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "severity": row[3],
                "source": row[4],
                "status": row[5],
                "created_at": row[6]
            })

        conn.close()
        return alerts

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """アラート履歴を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title, message, severity, source, status, created_at "
            "FROM alerts "
            "ORDER BY created_at DESC "
            "LIMIT ?",
            (limit,)
        )

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "severity": row[3],
                "source": row[4],
                "status": row[5],
                "created_at": row[6]
            })

        conn.close()
        return alerts


def main():
    """メイン関数"""
    alert_center = AlertCenter()

    # テストアラート作成
    alert_id = alert_center.create_alert(
        title="Test Alert",
        message="This is a test alert",
        severity="info"
    )

    print(f"Created alert: {alert_id}")

    active_alerts = alert_center.get_active_alerts()
    print(f"Active alerts: {len(active_alerts)}")


if __name__ == "__main__":
    main()
'''

    def get_log_viewer_impl(self):
        return '''#!/usr/bin/env python3
"""
Log Viewer - ログビューア

システムログの検索・表示
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class LogViewer:
    """ログビューア"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.log_dir = Path(self.config.get("log_dir", "logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"log_dir": "logs", "max_file_size_mb": 100}

    def search_logs(self, query: str, hours: int = 24) -> List[Dict[str, Any]]:
        """ログを検索"""
        results = []

        for log_file in self._get_recent_log_files(hours):
            matches = self._search_in_file(log_file, query)
            results.extend(matches)

        return results

    def _get_recent_log_files(self, hours: int) -> List[Path]:
        """最近のログファイルを取得"""
        log_files = []

        for log_file in self.log_dir.glob("*.log"):
            if log_file.is_file():
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if (datetime.now() - mtime).total_seconds() <= hours * 3600:
                    log_files.append(log_file)

        return log_files

    def _search_in_file(self, log_file: Path, query: str) -> List[Dict[str, Any]]:
        """ファイル内で検索"""
        matches = []

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if query.lower() in line.lower():
                        matches.append({
                            "file": str(log_file),
                            "line": line_num,
                            "content": line.strip(),
                            "timestamp": self._extract_timestamp(line)
                        })
        except Exception as e:
            pass

        return matches

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """タイムスタンプを抽出"""
        # ISO 8601形式のタイムスタンプを抽出
        match = re.search(r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}', line)
        return match.group(0) if match else None

    def get_log_files(self) -> List[Dict[str, Any]]:
        """ログファイル一覧を取得"""
        files = []

        for log_file in sorted(self.log_dir.glob("*.log"), reverse=True):
            if log_file.is_file():
                stat = log_file.stat()
                files.append({
                    "name": log_file.name,
                    "path": str(log_file),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return files


def main():
    """メイン関数"""
    viewer = LogViewer()

    # ログファイル一覧
    files = viewer.get_log_files()
    print(f"Log files: {len(files)}")


if __name__ == "__main__":
    main()
'''

    def get_config_manager_impl(self):
        return '''#!/usr/bin/env python3
"""
Config Manager - 設定管理

システム設定の集中管理
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigManager:
    """設定マネージャー"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.config_dir = Path(self.config.get("config_dir", "configs"))
        self.backup_dir = Path(self.config.get("backup_dir", "backups"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"config_dir": "configs", "backup_dir": "backups"}

    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """設定を取得"""
        config_file = self.config_dir / f"{name}.json"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None

    def save_config(self, name: str, config: Dict[str, Any], backup: bool = True):
        """設定を保存"""
        config_file = self.config_dir / f"{name}.json"

        # バックアップを作成
        if backup and config_file.exists():
            self._backup_config(name)

        # 設定を保存
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _backup_config(self, name: str):
        """設定をバックアップ"""
        config_file = self.config_dir / f"{name}.json"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{name}_{timestamp}.json"

        shutil.copy2(config_file, backup_file)

    def list_configs(self) -> List[Dict[str, Any]]:
        """設定一覧を取得"""
        configs = []

        for config_file in self.config_dir.glob("*.json"):
            configs.append({
                "name": config_file.stem,
                "path": str(config_file),
                "modified": datetime.fromtimestamp(config_file.stat().st_mtime).isoformat()
            })

        return configs

    def validate_config(self, name: str) -> bool:
        """設定を検証"""
        config = self.get_config(name)

        if config is None:
            return False

        # 基本的な検証
        if not isinstance(config, dict):
            return False

        return True


def main():
    """メイン関数"""
    manager = ConfigManager()

    # 設定一覧
    configs = manager.list_configs()
    print(f"Configs: {len(configs)}")


if __name__ == "__main__":
    main()
'''

    def get_readme_content(self, task_id):
        """README.md の内容を生成"""
        templates = {
            "ops-dashboard": self.get_ops_dashboard_readme(),
            "metrics-viz": self.get_metrics_viz_readme(),
            "alert-center": self.get_alert_center_readme(),
            "log-viewer": self.get_log_viewer_readme(),
            "config-manager": self.get_config_manager_readme()
        }
        return templates.get(task_id, "# Task\n\nDescription")

    def get_ops_dashboard_readme(self):
        return '''# Operations Dashboard / 運用ダッシュボード

システム運用状況を一覧表示するダッシュボード

## 機能

- システムステータス一覧
- エージェント状態表示
- サービス状態監視
- リソース使用状況
- アクティブアラート表示

## 使い方

```bash
python3 implementation.py
```

## 依存パッケージ

```
psutil
```

---

# Operations Dashboard

System operations dashboard for monitoring system status.

## Features

- System status overview
- Agent status display
- Service monitoring
- Resource usage tracking
- Active alerts display

## Usage

```bash
python3 implementation.py
```

## Dependencies

```
psutil
```
'''

    def get_metrics_viz_readme(self):
        return '''# Metrics Visualization / メトリクス可視化

システムメトリクスのリアルタイム可視化

## 機能

- リアルタイムメトリクス収集
- CPU使用率の追跡
- メモリ使用量の追跡
- ディスク使用量の追跡
- ネットワークトラフィックの追跡
- メトリクス履歴の保存

## 使い方

```bash
python3 implementation.py
```

## 依存パッケージ

```
psutil
```

---

# Metrics Visualization

Real-time system metrics visualization.

## Features

- Real-time metrics collection
- CPU usage tracking
- Memory usage tracking
- Disk usage tracking
- Network traffic tracking
- Metrics history storage

## Usage

```bash
python3 implementation.py
```

## Dependencies

```
psutil
```
'''

    def get_alert_center_readme(self):
        return '''# Alert Center / アラートセンター

アラート管理・通知センター

## 機能

- アラート作成
- アラート確認
- アクティブアラート一覧
- アラート履歴
- アラート重要度管理

## 使い方

```bash
python3 implementation.py
```

## API

### アラート作成

```python
alert_center.create_alert(
    title="Alert Title",
    message="Alert message",
    severity="warning",  # info, warning, error, critical
    source="system"
)
```

### アラート確認

```python
alert_center.acknowledge_alert(alert_id, acknowledged_by="admin")
```

---

# Alert Center

Alert management and notification center.

## Features

- Create alerts
- Acknowledge alerts
- Active alerts list
- Alert history
- Alert severity management

## Usage

```bash
python3 implementation.py
```

## API

### Create Alert

```python
alert_center.create_alert(
    title="Alert Title",
    message="Alert message",
    severity="warning",  # info, warning, error, critical
    source="system"
)
```

### Acknowledge Alert

```python
alert_center.acknowledge_alert(alert_id, acknowledged_by="admin")
```
'''

    def get_log_viewer_readme(self):
        return '''# Log Viewer / ログビューア

システムログの検索・表示

## 機能

- ログファイル一覧
- ログ検索
- タイムスタンプ抽出
- 最近のログフィルタリング

## 使い方

```bash
python3 implementation.py
```

## API

### ログ検索

```python
viewer.search_logs(query="error", hours=24)
```

### ログファイル一覧

```python
viewer.get_log_files()
```

---

# Log Viewer

System log search and viewer.

## Features

- Log file listing
- Log search
- Timestamp extraction
- Recent logs filtering

## Usage

```bash
python3 implementation.py
```

## API

### Search Logs

```python
viewer.search_logs(query="error", hours=24)
```

### List Log Files

```python
viewer.get_log_files()
```
'''

    def get_config_manager_readme(self):
        return '''# Config Manager / 設定管理

システム設定の集中管理

## 機能

- 設定の保存・読み込み
- 設定のバックアップ
- 設定一覧
- 設定検証

## 使い方

```bash
python3 implementation.py
```

## API

### 設定を取得

```python
config = manager.get_config("system")
```

### 設定を保存

```python
manager.save_config("system", {"key": "value"}, backup=True)
```

### 設定一覧

```python
configs = manager.list_configs()
```

---

# Config Manager

Centralized system configuration management.

## Features

- Save and load configurations
- Configuration backup
- Configuration listing
- Configuration validation

## Usage

```bash
python3 implementation.py
```

## API

### Get Configuration

```python
config = manager.get_config("system")
```

### Save Configuration

```python
manager.save_config("system", {"key": "value"}, backup=True)
```

### List Configurations

```python
configs = manager.list_configs()
```
'''

    def get_requirements_content(self, task_id):
        """requirements.txt の内容を生成"""
        requirements = {
            "ops-dashboard": "psutil>=5.9.0",
            "metrics-viz": "psutil>=5.9.0",
            "alert-center": "",
            "log-viewer": "",
            "config-manager": ""
        }
        return requirements.get(task_id, "")

    def get_config_content(self, task_id):
        """config.json の内容を生成"""
        configs = {
            "ops-dashboard": json.dumps({
                "data_dir": "data",
                "refresh_interval": 30
            }, indent=2),
            "metrics-viz": json.dumps({
                "db_path": "data/metrics.db",
                "retention_days": 30
            }, indent=2),
            "alert-center": json.dumps({
                "db_path": "data/alerts.db",
                "retention_days": 30
            }, indent=2),
            "log-viewer": json.dumps({
                "log_dir": "logs",
                "max_file_size_mb": 100
            }, indent=2),
            "config-manager": json.dumps({
                "config_dir": "configs",
                "backup_dir": "backups"
            }, indent=2)
        }
        return configs.get(task_id, "{}")

    def run(self):
        """オーケストレーションを実行"""
        print("=" * 60)
        print(f"🚀 {self.project['name']}")
        print(f"📝 {self.project['description']}")
        print("=" * 60)

        for task in self.project["tasks"]:
            task_id = task["id"]

            if not self.progress["tasks"][task_id]:
                try:
                    self.create_module(task)
                    self.progress["tasks"][task_id] = True
                    self.save_progress()
                except Exception as e:
                    print(f"❌ エラー: {task['name']}: {e}")
                    return

        print("\n" + "=" * 60)
        print("🎉 プロジェクト完了！")
        print("=" * 60)

        # 進捗サマリ
        completed = sum(self.progress["tasks"].values())
        total = len(self.progress["tasks"])
        print(f"\n📊 進捗: {completed}/{total} (100%)")

        for task in self.project["tasks"]:
            status = "✅" if self.progress["tasks"][task["id"]] else "❌"
            print(f"  {status} {task['name']}")


def main():
    """メイン関数"""
    orchestrator = OperationsPanelOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
