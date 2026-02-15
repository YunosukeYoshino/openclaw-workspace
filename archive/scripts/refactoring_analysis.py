#!/usr/bin/env python3
"""
リファクタリング分析スクリプト
ワークスペースの整理とコードの最適化を分析
"""
import os
import re
from pathlib import Path
from collections import Counter

def analyze_orchestrators():
    """オーケストレーターファイルの分析"""
    workspace = Path("/workspace")
    orchestrators = sorted(workspace.glob("orchestrate_v*.py"))

    print(f"## オーケストレーター分析 ({len(orchestrators)}個のファイル)")
    print()

    # 行数カウント
    for orch in orchestrators[:20]:
        lines = len(orch.read_text().splitlines())
        print(f"  {orch.name}: {lines}行")

    # 共通importの分析
    imports = Counter()
    for orch in orchestrators:
        content = orch.read_text()
        for line in content.splitlines():
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                imports[line.strip()] += 1

    print("\n### よく使われるimport (上位20)")
    for imp, count in imports.most_common(20):
        print(f"  ({count}回) {imp}")

def analyze_duplicate_progress_files():
    """progress.jsonファイルの重複分析"""
    workspace = Path("/workspace")
    progress_files = sorted(workspace.glob("*_progress.json"))

    print(f"\n## progress.jsonファイル分析 ({len(progress_files)}個)")
    print()

    # 重複するファイル名の検出
    v_progress = [f for f in progress_files if f.stem.startswith("v")]
    print(f"  Vシリーズのprogress.json: {len(v_progress)}個")
    print(f"  その他のprogress.json: {len(progress_files) - len(v_progress)}個")

def analyze_temporary_files():
    """一時ファイルの分析"""
    workspace = Path("/workspace")

    print("\n## 一時ファイル・ゴミファイル分析")
    print()

    # ログファイル
    log_files = list(workspace.glob("**/*.log"))
    print(f"  ログファイル: {len(log_files)}個")
    for log in log_files[:5]:
        size = log.stat().st_size
        print(f"    - {log.name}: {size}バイト")

    # データベースファイル
    db_files = list(workspace.glob("**/*.db"))
    print(f"  データベースファイル: {len(db_files)}個")
    for db in db_files[:10]:
        size = db.stat().st_size
        print(f"    - {db.relative_to(workspace)}: {size:,}バイト")

    # クリーンアップ候補
    print("\n### クリーンアップ候補")
    if log_files:
        print(f"  古いログファイル: {len(log_files)}個 (maintenance_logs/内)")
    if db_files:
        print(f"  テスト用データベース: {len(db_files)}個 (各エージェント内)")

def analyze_agent_files():
    """エージェントファイルの分析"""
    workspace = Path("/workspace")
    agents_dir = workspace / "agents"

    print(f"\n## エージェントファイル分析")
    print()

    if not agents_dir.exists():
        print("  agents/ディレクトリが存在しません")
        return

    agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir()]
    print(f"  エージェントディレクトリ数: {len(agent_dirs)}")

    # 各エージェントの標準ファイル
    standard_files = {"agent.py", "db.py", "discord.py", "README.md", "requirements.txt"}
    missing = []
    extra = []

    for agent_dir in agent_dirs[:100]:  # 最初の100個のみ
        files = {f.name for f in agent_dir.iterdir() if f.is_file()}
        missing_std = standard_files - files
        extra_files = files - standard_files

        if missing_std:
            missing.append(f"{agent_dir.name}: {', '.join(missing_std)}")
        if extra_files:
            extra.append(f"{agent_dir.name}: {', '.join(extra_files)}")

    print(f"\n### 標準ファイルが欠けているエージェント (最初の100個のチェック)")
    for m in missing[:10]:
        print(f"  ⚠️  {m}")

    print(f"\n### 標準以外のファイルを持つエージェント (最初の100個のチェック)")
    for e in extra[:10]:
        print(f"  ℹ️  {e}")

def analyze_large_files():
    """大きなファイルの分析"""
    workspace = Path("/workspace")

    print(f"\n## 大きなファイル分析 (700行超)")
    print()

    large_files = []
    for py_file in workspace.glob("*.py"):
        lines = len(py_file.read_text().splitlines())
        if lines > 700:
            large_files.append((py_file.name, lines))

    large_files.sort(key=lambda x: x[1], reverse=True)

    for fname, lines in large_files[:20]:
        print(f"  {fname}: {lines}行")

def analyze_workspace_structure():
    """ワークスペース構造の分析（認知負荷）"""
    workspace = Path("/workspace")

    print(f"\n## ワークスペース構造分析（認知負荷）")
    print()

    # ルートディレクトリのアイテム数
    root_items = [i for i in workspace.iterdir() if not i.name.startswith(".")]
    print(f"  ルートディレクトリのアイテム数: {len(root_items)}")

    # カテゴリ別カウント
    py_files = list(workspace.glob("*.py"))
    json_files = list(workspace.glob("*.json"))
    md_files = list(workspace.glob("*.md"))
    txt_files = list(workspace.glob("*.txt"))

    print(f"    - Pythonファイル: {len(py_files)}個")
    print(f"    - JSONファイル: {len(json_files)}個")
    print(f"    - Markdownファイル: {len(md_files)}個")
    print(f"    - テキストファイル: {len(txt_files)}個")

    # エージェントディレクトリ数
    agents_dir = workspace / "agents"
    if agents_dir.exists():
        agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir()]
        print(f"\n  エージェント数: {len(agent_dirs)}個")

    # 認知負荷の評価
    print("\n### 認知負荷の評価")
    if len(root_items) > 100:
        print("  ⚠️  ルートディレクトリのアイテムが多すぎます（>100）")
        print("     提案: サブディレクトリで整理（orchestrators/, scripts/, docs/等）")
    elif len(root_items) > 50:
        print("  ⚠️  ルートディレクトリのアイテムが多いです（>50）")
        print("     提案: 部分的に整理を検討")
    else:
        print("  ✅ ルートディレクトリの構造は妥当です")

    if len(py_files) > 50:
        print("\n  ⚠️  ルート直下のPythonファイルが多いです（>50）")
        print("     提案: orchestrators/ディレクトリに移動")

def main():
    """メイン分析"""
    print("=" * 70)
    print("ワークスペース リファクタリング分析")
    print("=" * 70)

    analyze_large_files()
    analyze_orchestrators()
    analyze_duplicate_progress_files()
    analyze_temporary_files()
    analyze_agent_files()
    analyze_workspace_structure()

    print("\n" + "=" * 70)
    print("分析完了")
    print("=" * 70)

if __name__ == "__main__":
    main()
