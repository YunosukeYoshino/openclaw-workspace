#!/usr/bin/env python3
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
