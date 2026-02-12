#!/usr/bin/env python3
"""
Dependency Checker - 依存関係チェック

依存パッケージの脆弱性チェック
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class DependencyChecker:
    """依存関係チェッカークラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.vulnerabilities = []

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def check_requirements(self, requirements_path: str) -> List[Dict[str, Any]]:
        """requirements.txtをチェック"""
        self.vulnerabilities = []

        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    self._check_package_vulnerability(package)

        except Exception as e:
            print(f"Error reading requirements: {e}")

        return self.vulnerabilities

    def _check_package_vulnerability(self, package: str):
        """パッケージの脆弱性をチェック"""
        # 既知の脆弱性データベース（簡易版）
        known_vulnerabilities = {
            "requests": ["CVE-2023-32681"],
            "pillow": ["CVE-2023-44271"],
            "django": ["CVE-2023-41916"]
        }

        if package.lower() in known_vulnerabilities:
            for cve in known_vulnerabilities[package.lower()]:
                self.vulnerabilities.append({
                    "package": package,
                    "cve": cve,
                    "severity": "medium",
                    "message": f"Known vulnerability found: {cve}"
                })

    def check_pyproject(self, pyproject_path: str) -> List[Dict[str, Any]]:
        """pyproject.tomlをチェック"""
        self.vulnerabilities = []

        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                import tomli
                data = tomli.load(f)

            if "project" in data and "dependencies" in data["project"]:
                for dep in data["project"]["dependencies"]:
                    package = dep.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    self._check_package_vulnerability(package)

        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")

        return self.vulnerabilities


def main():
    checker = DependencyChecker()
    vulnerabilities = checker.check_requirements("requirements.txt")

    print(f"Found {len(vulnerabilities)} vulnerabilities:")
    for vuln in vulnerabilities:
        print(f"  [{vuln['severity']}] {vuln['package']}: {vuln['cve']} - {vuln['message']}")


if __name__ == "__main__":
    main()
