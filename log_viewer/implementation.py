#!/usr/bin/env python3
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
        match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line)
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
