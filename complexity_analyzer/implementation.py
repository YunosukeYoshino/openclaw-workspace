#!/usr/bin/env python3
"""
Complexity Analyzer - 複雑度解析

コード複雑度の分析・可視化
"""

import ast
import json
from pathlib import Path
from typing import List, Dict, Any


class ComplexityAnalyzer:
    """複雑度解析クラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.complexity_results = []

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"max_complexity": 10}

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """ファイルを解析"""
        self.complexity_results = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    self.complexity_results.append({
                        "name": node.name,
                        "type": "function",
                        "line": node.lineno,
                        "complexity": complexity
                    })
                elif isinstance(node, ast.ClassDef):
                    complexity = self._calculate_class_complexity(node)
                    self.complexity_results.append({
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                        "complexity": complexity
                    })

        except Exception as e:
            print(f"Error analyzing file: {e}")

        return self.complexity_results

    def _calculate_cyclomatic_complexity(self, node) -> int:
        """循環的複雑度を計算"""
        complexity = 1  # 基本複雑度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _calculate_class_complexity(self, node) -> int:
        """クラスの複雑度を計算"""
        complexity = 0

        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                complexity += self._calculate_cyclomatic_complexity(child)

        return complexity

    def generate_report(self) -> str:
        """レポートを生成"""
        total_complexity = sum(r["complexity"] for r in self.complexity_results)
        avg_complexity = total_complexity / len(self.complexity_results) if self.complexity_results else 0

        high_complexity = [r for r in self.complexity_results if r["complexity"] > self.config.get("max_complexity", 10)]

        report = "Complexity Analysis Report\n"
        report += "=" * 40 + "\n\n"
        report += f"Total Complexity: {total_complexity}\n"
        report += f"Average Complexity: {avg_complexity:.2f}\n"
        report += f"Functions/Classes: {len(self.complexity_results)}\n"
        report += f"High Complexity Items: {len(high_complexity)}\n\n"

        if high_complexity:
            report += "High Complexity Items:\n"
            for item in high_complexity:
                report += f"  - {item['name']} ({item['type']}): {item['complexity']}\n"

        return report


def main():
    analyzer = ComplexityAnalyzer()
    results = analyzer.analyze_file("implementation.py")

    print(f"Analyzed {len(results)} items")
    print(analyzer.generate_report())


if __name__ == "__main__":
    main()
