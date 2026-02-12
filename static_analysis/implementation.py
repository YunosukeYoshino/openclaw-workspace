#!/usr/bin/env python3
"""
Static Analysis - 静的解析

コードの静的解析・エラー検出
"""

import ast
import json
from pathlib import Path
from typing import List, Dict, Any


class StaticAnalyzer:
    """静的解析クラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.issues = []

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイルを解析"""
        self.issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                self._check_node(node, file_path)

        except Exception as e:
            self.issues.append({
                "file": file_path,
                "line": 0,
                "type": "error",
                "message": f"Parse error: {e}"
            })

        return self.issues

    def _check_node(self, node, file_path: str):
        """ノードをチェック"""
        if isinstance(node, ast.FunctionDef):
            self._check_function(node, file_path)
        elif isinstance(node, ast.ClassDef):
            self._check_class(node, file_path)
        elif isinstance(node, ast.Import):
            self._check_import(node, file_path)

    def _check_function(self, node, file_path: str):
        """関数をチェック"""
        # 関数名のチェック
        if not node.name.islower():
            self.issues.append({
                "file": file_path,
                "line": node.lineno,
                "type": "warning",
                "message": f"Function name should be lowercase: {node.name}"
            })

        # 関数の長さをチェック
        if hasattr(node, 'end_lineno'):
            length = node.end_lineno - node.lineno
            if length > 50:
                self.issues.append({
                    "file": file_path,
                    "line": node.lineno,
                    "type": "warning",
                    "message": f"Function too long ({length} lines): {node.name}"
                })

    def _check_class(self, node, file_path: str):
        """クラスをチェック"""
        # クラス名のチェック
        if not node.name[0].isupper():
            self.issues.append({
                "file": file_path,
                "line": node.lineno,
                "type": "warning",
                "message": f"Class name should be PascalCase: {node.name}"
            })

    def _check_import(self, node, file_path: str):
        """インポートをチェック"""
        for alias in node.names:
            if alias.asname and not alias.asname.islower():
                self.issues.append({
                    "file": file_path,
                    "line": node.lineno,
                    "type": "warning",
                    "message": f"Import alias should be lowercase: {alias.asname}"
                })


def main():
    analyzer = StaticAnalyzer()
    issues = analyzer.analyze_file("implementation.py")

    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  [{issue['type']}] {issue['file']}:{issue['line']} - {issue['message']}")


if __name__ == "__main__":
    main()
