#!/usr/bin/env python3
"""
メンテナンス自動化スクリプト

自動バックアップ、ヘルスチェック、クリーンアップタスクを実行する。
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# 設定
WORKSPACE = Path("/workspace")
BACKUP_DIR = WORKSPACE / "backups"
LOG_DIR = WORKSPACE / "maintenance_logs"
AGENTS_DIR = WORKSPACE / "agents"
MEMORY_DIR = WORKSPACE / "memory"

# ログ設定
LOG_FILE = LOG_DIR / f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(message):
    """ログを出力"""
    print(message)
    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def backup_important_files():
    """重要なファイルをバックアップ"""
    log("=" * 60)
    log("📦 自動バックアップ")
    log("=" * 60)

    BACKUP_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    # 本日のバックアップディレクトリを作成
    today_backup = BACKUP_DIR / datetime.now().strftime("%Y%m%d")
    today_backup.mkdir(exist_ok=True)

    # バックアップ対象ファイル
    backup_targets = [
        MEMORY_DIR,
        WORKSPACE / "MEMORY.md",
        WORKSPACE / "Plan.md",
        WORKSPACE / "TOOL.md",
        WORKSPACE / "AGENTS.md",
    ]

    backup_count = 0
    for target in backup_targets:
        if target.exists():
            if target.is_dir():
                target_dir = today_backup / target.name
                shutil.copytree(target, target_dir, dirs_exist_ok=True)
                log(f"  ✅ バックアップ完了: {target.name}/")
                backup_count += 1
            else:
                shutil.copy2(target, today_backup / target.name)
                log(f"  ✅ バックアップ完了: {target.name}")
                backup_count += 1
        else:
            log(f"  ⚠️  ファイルが存在しません: {target.name}")

    log(f"\n📊 バックアップサマリー: {backup_count}個のファイル/ディレクトリをバックアップ")

    # 古いバックアップを削除（30日分だけ残す）
    cleanup_old_backups(today_backup)
    log(f"  🗑️  古いバックアップをクリーンアップ完了")

    return backup_count

def cleanup_old_backups(keep_backup):
    """古いバックアップを削除"""
    all_backups = sorted(BACKUP_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)

    # 最新の30個のバックアップを残す
    for old_backup in all_backups[30:]:
        if old_backup.is_dir() and old_backup != keep_backup:
            shutil.rmtree(old_backup)
            log(f"    削除: {old_backup.name}")

def health_check_agents():
    """エージェントのヘルスチェック"""
    log("=" * 60)
    log("🏥 エージェントヘルスチェック")
    log("=" * 60)

    agent_dirs = sorted([d for d in AGENTS_DIR.iterdir() if d.is_dir()])
    required_files = ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]

    healthy_agents = []
    unhealthy_agents = []

    for agent_dir in agent_dirs:
        missing_files = []
        for filename in required_files:
            if not (agent_dir / filename).exists():
                missing_files.append(filename)

        if missing_files:
            unhealthy_agents.append({
                "name": agent_dir.name,
                "missing": missing_files,
            })
        else:
            healthy_agents.append(agent_dir.name)

    log(f"\n📊 ヘルスチェック結果:")
    log(f"  総エージェント数: {len(agent_dirs)}")
    log(f"  ヘルシー: {len(healthy_agents)}")
    log(f"  アンヘルシー: {len(unhealthy_agents)}")

    if unhealthy_agents:
        log(f"\n❌ アンヘルシーエージェント一覧 ({len(unhealthy_agents)}個):")
        for agent in unhealthy_agents[:10]:  # Show first 10
            log(f"  - {agent['name']}: 欠損 {', '.join(agent['missing'])}")
        if len(unhealthy_agents) > 10:
            log(f"  ... さらに {len(unhealthy_agents) - 10} 個")

    # 結果を保存
    health_result = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(agent_dirs),
        "healthy_agents": len(healthy_agents),
        "unhealthy_agents": len(unhealthy_agents),
        "unhealthy_list": unhealthy_agents,
    }

    health_file = WORKSPACE / "health_check_result.json"
    with open(health_file, "w", encoding="utf-8") as f:
        json.dump(health_result, f, indent=2, ensure_ascii=False)
    log(f"\n📁 ヘルスチェック結果を保存: {health_file}")

    return {
        "total": len(agent_dirs),
        "healthy": len(healthy_agents),
        "unhealthy": len(unhealthy_agents),
    }

def cleanup_temp_files():
    """一時ファイルをクリーンアップ"""
    log("=" * 60)
    log("🧹 クリーンアップ")
    log("=" * 60)

    # クリーンアップ対象のパターン
    cleanup_patterns = [
        "*.pyc",
        "__pycache__",
        ".DS_Store",
        "Thumbs.db",
        "*.tmp",
        "*.temp",
    ]

    cleaned_count = 0
    cleaned_size = 0

    for root, dirs, files in os.walk(WORKSPACE):
        # ディレクトリのクリーンアップ
        for d in dirs[:]:
            if d in cleanup_patterns:
                dir_path = Path(root) / d
                if dir_path.exists():
                    size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
                    shutil.rmtree(dir_path)
                    log(f"  ✅ 削除: {dir_path.relative_to(WORKSPACE)} ({size:,} bytes)")
                    cleaned_count += 1
                    cleaned_size += size
                    dirs.remove(d)

        # ファイルのクリーンアップ
        for f in files:
            for pattern in cleanup_patterns:
                if f.endswith(pattern.replace("*", "")):
                    file_path = Path(root) / f
                    if file_path.exists():
                        size = file_path.stat().st_size
                        file_path.unlink()
                        log(f"  ✅ 削除: {file_path.relative_to(WORKSPACE)} ({size:,} bytes)")
                        cleaned_count += 1
                        cleaned_size += size
                        break

    log(f"\n📊 クリーンアップサマリー:")
    log(f"  削除したファイル/ディレクトリ: {cleaned_count}個")
    log(f"  解放した容量: {cleaned_size:,} bytes ({cleaned_size / 1024 / 1024:.2f} MB)")

    return {
        "cleaned_count": cleaned_count,
        "cleaned_size": cleaned_size,
    }

def check_git_status():
    """Gitステータスをチェック"""
    log("=" * 60)
    log("📝 Gitステータスチェック")
    log("=" * 60)

    import subprocess

    # 変更があるかチェック
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        log(f"\n⚠️  未コミットの変更があります:")
        log(result.stdout)
    else:
        log(f"\n✅ Gitワークスペースはクリーンです")

    return result.stdout.strip() != ""

def generate_maintenance_report(results):
    """メンテナンスレポートを生成"""
    log("=" * 60)
    log("📊 メンテナンスレポート")
    log("=" * 60)

    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }

    report_file = WORKSPACE / f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"\n📁 メンテナンスレポートを保存: {report_file}")

    return report_file

def main():
    """メイン関数"""
    log("🚀 メンテナンス自動化開始")
    log(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 1. 自動バックアップ
    results["backup"] = backup_important_files()
    log("")

    # 2. ヘルスチェック
    results["health_check"] = health_check_agents()
    log("")

    # 3. クリーンアップ
    results["cleanup"] = cleanup_temp_files()
    log("")

    # 4. Gitステータスチェック
    results["git_status"] = check_git_status()
    log("")

    # 5. レポート生成
    report_file = generate_maintenance_report(results)

    end_time = datetime.now()
    duration = (end_time - datetime.now()).total_seconds()

    log("=" * 60)
    log(f"✅ メンテナンス完了")
    log(f"終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"レポート: {report_file}")
    log("=" * 60)

if __name__ == "__main__":
    main()
