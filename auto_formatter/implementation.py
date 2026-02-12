#!/usr/bin/env python3
"""
Auto Formatter - 自動フォーマット

コードの自動フォーマット・スタイル統一
"""

import re
from pathlib import Path
from typing import List


class AutoFormatter:
    """自動フォーマットクラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)
        return {"indent_size": 4, "max_line_length": 100}

    def format_file(self, file_path: str) -> str:
        """ファイルをフォーマット"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        formatted_lines = []

        for line in lines:
            # 行末の空白を削除
            line = line.rstrip()

            # タブをスペースに置換
            line = line.replace('\t', ' ' * 4)

            formatted_lines.append(line)

        # 空行の連続を1行に
        result = self._remove_consecutive_blank_lines(formatted_lines)

        return '\n'.join(result)

    def _remove_consecutive_blank_lines(self, lines: List[str]) -> List[str]:
        """連続する空行を削除"""
        result = []
        blank_count = 0

        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)

        return result

    def save_formatted(self, file_path: str, content: str):
        """フォーマット済みの内容を保存"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    formatter = AutoFormatter()
    content = formatter.format_file("implementation.py")
    print("Formatted content:")
    print(content)


if __name__ == "__main__":
    main()
