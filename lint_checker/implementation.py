#!/usr/bin/env python3
"""
Lint Checker - リントチェック

コード品質チェック・ベストプラクティス
"""

import ast
import json
from pathlib import Path
from typing import List, Dict, Any


class LintChecker:
    """リントチェッカークラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.violations = []

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイルをチェック"""
        self.violations = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                self._check_node(node, file_path)

        except Exception as e:
            self.violations.append({
                "file": file_path,
                "line": 0,
                "rule": "parse-error",
                "message": f"Parse error: {e}"
            })

        return self.violations

    def _check_node(self, node, file_path: str):
        """ノードをチェック"""
        if isinstance(node, ast.FunctionDef):
            self._check_function(node, file_path)
        elif isinstance(node, ast.ClassDef):
            self._check_class(node, file_path)

    def _check_function(self, node, file_path: str):
        """関数をチェック"""
        # ドキュメント文字列のチェック
        docstring = ast.get_docstring(node)
        if not docstring and not node.name.startswith('_'):
            self.violations.append({
                "file": file_path,
                "line": node.lineno,
                "rule": "missing-docstring",
                "message": f"Missing docstring for function: {node.name}"
            })

        # 引数の数をチェック
        arg_count = len(node.args.args)
        if arg_count > 7:
            self.violations.append({
                "file": file_path,
                "line": node.lineno,
                "rule": "too-many-arguments",
                "message": f"Too many arguments ({arg_count}) in function: {node.name}"
            })

    def _check_class(self, node, file_path: str):
        """クラスをチェック"""
        # ドキュメント文字列のチェック
        docstring = ast.get_docstring(node)
        if not docstring:
            self.violations.append({
                "file": file_path,
                "line": node.lineno,
                "rule": "missing-docstring",
                "message": f"Missing docstring for class: {node.name}"
            })

        # メソッドの数をチェック
        method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
        if method_count > 20:
            self.violations.append({
                "file": file_path,
                "line": node.lineno,
                "rule": "too-many-methods",
                "message": f"Too many methods ({method_count}) in class: {node.name}"
            })


def main():
    checker = LintChecker()
    violations = checker.check_file("implementation.py")

    print(f"Found {len(violations)} violations:")
    for violation in violations:
        print(f"  [{violation['rule']}] {violation['file']}:{violation['line']} - {violation['message']}")


if __name__ == "__main__":
    main()
