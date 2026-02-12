"""
Backup Schedule Agent Discord Module
Natural language processing for scheduled backup management
"""

import re
from typing import Optional, Dict, List
from db import BackupScheduleDB


class BackupScheduleDiscord:
    """Discord interface for backup schedule agent with NLP"""

    def __init__(self, db_path: str = "backup_schedule.db"):
        self.db = BackupScheduleDB(db_path)

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "add_schedule":
            return self._handle_add_schedule(entities)
        elif intent == "list_schedules":
            return self._handle_list_schedules(entities)
        elif intent == "show_schedule":
            return self._handle_show_schedule(entities)
        elif intent == "update_schedule":
            return self._handle_update_schedule(entities)
        elif intent == "toggle_schedule":
            return self._handle_toggle_schedule(entities)
        elif intent == "delete_schedule":
            return self._handle_delete_schedule(entities)
        elif intent == "add_backup_job":
            return self._handle_add_backup_job(entities)
        elif intent == "list_backup_jobs":
            return self._handle_list_backup_jobs(entities)
        elif intent == "update_backup_job":
            return self._handle_update_backup_job(entities)
        elif intent == "add_backup_target":
            return self._handle_add_backup_target(entities)
        elif intent == "list_backup_targets":
            return self._handle_list_backup_targets(entities)
        elif intent == "delete_backup_target":
            return self._handle_delete_backup_target(entities)
        elif intent == "show_logs":
            return self._handle_show_logs(entities)
        elif intent == "add_retention_policy":
            return self._handle_add_retention_policy(entities)
        elif intent == "list_retention_policies":
            return self._handle_list_retention_policies(entities)
        elif intent == "show_summary":
            return self._handle_show_summary(entities)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_unknown(message)

    def _parse_intent(self, message: str) -> tuple:
        """Parse intent and entities from message"""
        entities = {}
        lower_msg = message.lower()

        # Add schedule
        if re.search(r'(schedule.*add|add.*schedule|スケジュール追加|バックアップスケジュール追加|create.*schedule)', lower_msg):
            entities['name'] = self._extract_name(message)
            entities['target_type'] = self._extract_target_type(message)
            entities['target_path'] = self._extract_path(message)
            entities['schedule_type'] = self._extract_schedule_type(message)
            entities['schedule_value'] = self._extract_schedule_value(message)
            return "add_schedule", entities

        # List schedules
        if re.search(r'(schedule.*list|list.*schedule|スケジュール一覧|スケジュール表示|show.*schedule)', lower_msg):
            entities['target_type'] = self._extract_target_type(message)
            entities['enabled'] = self._extract_enabled(message)
            return "list_schedules", entities

        # Show schedule
        if re.search(r'(schedule.*show|show.*schedule|スケジュール詳細|schedule.*get|get.*schedule)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            return "show_schedule", entities

        # Update schedule
        if re.search(r'(schedule.*update|update.*schedule|スケジュール更新|schedule.*edit)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            entities['schedule_type'] = self._extract_schedule_type(message)
            entities['schedule_value'] = self._extract_schedule_value(message)
            entities['retention_days'] = self._extract_retention(message)
            entities['enabled'] = self._extract_enabled(message)
            return "update_schedule", entities

        # Toggle schedule
        if re.search(r'(schedule.*enable|schedule.*disable|schedule.*toggle|スケジュール有効|スケジュール無効)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            return "toggle_schedule", entities

        # Delete schedule
        if re.search(r'(schedule.*delete|delete.*schedule|スケジュール削除|remove.*schedule)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            return "delete_schedule", entities

        # Add backup job
        if re.search(r'(backup.*job.*add|add.*backup.*job|バックアップジョブ追加|run.*backup|execute.*backup)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            return "add_backup_job", entities

        # List backup jobs
        if re.search(r'(backup.*job.*list|list.*backup.*job|バックアップジョブ一覧|バックアップ履歴|show.*job)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            entities['status'] = self._extract_status(message)
            return "list_backup_jobs", entities

        # Update backup job
        if re.search(r'(backup.*job.*update|update.*backup.*job|バックアップジョブ更新|complete.*job)', lower_msg):
            entities['job_id'] = self._extract_id(message)
            entities['status'] = self._extract_status(message)
            entities['success'] = self._extract_success(message)
            return "update_backup_job", entities

        # Add backup target
        if re.search(r'(target.*add|add.*target|ターゲット追加|バックアップターゲット追加|create.*target)', lower_msg):
            entities['target_type'] = self._extract_target_type(message)
            entities['target_name'] = self._extract_name(message)
            entities['target_path'] = self._extract_path(message)
            return "add_backup_target", entities

        # List backup targets
        if re.search(r'(target.*list|list.*target|ターゲット一覧|ターゲット表示|show.*target)', lower_msg):
            entities['target_type'] = self._extract_target_type(message)
            return "list_backup_targets", entities

        # Delete backup target
        if re.search(r'(target.*delete|delete.*target|ターゲット削除|remove.*target)', lower_msg):
            entities['target_id'] = self._extract_id(message)
            return "delete_backup_target", entities

        # Show logs
        if re.search(r'(log.*show|show.*log|ログ表示|ログ一覧|view.*log)', lower_msg):
            entities['schedule_id'] = self._extract_id(message)
            entities['log_level'] = self._extract_log_level(message)
            return "show_logs", entities

        # Add retention policy
        if re.search(r'(retention.*add|add.*retention|リテンション追加|リテンションポリシー追加|create.*retention)', lower_msg):
            entities['policy_name'] = self._extract_name(message)
            entities['backup_type'] = self._extract_backup_type(message)
            return "add_retention_policy", entities

        # List retention policies
        if re.search(r'(retention.*list|list.*retention|リテンション一覧|ポリシー一覧|show.*retention)', lower_msg):
            entities['backup_type'] = self._extract_backup_type(message)
            return "list_retention_policies", entities

        # Show summary
        if re.search(r'(summary|要約|サマリー|概要|backup.*summary)', lower_msg):
            return "show_summary", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_name(self, message: str) -> Optional[str]:
        """Extract name"""
        patterns = [
            r'名前[:\s]+([^\s,]+)',
            r'name[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_target_type(self, message: str) -> Optional[str]:
        """Extract target type"""
        types = ['database', 'file', 'directory', 'system', 'config', 'db']
        lower_msg = message.lower()
        for t in types:
            if t in lower_msg:
                return t
        return None

    def _extract_path(self, message: str) -> Optional[str]:
        """Extract path"""
        patterns = [
            r'パス[:\s]+([^\s]+)',
            r'path[:\s]+([^\s]+)',
            r'(/[^\s]+)',
            r'(/[a-zA-Z0-9_./-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_schedule_type(self, message: str) -> Optional[str]:
        """Extract schedule type"""
        types = ['daily', 'weekly', 'monthly', 'hourly', 'cron']
        lower_msg = message.lower()
        for t in types:
            if t in lower_msg:
                return t
        return 'daily'

    def _extract_schedule_value(self, message: str) -> Optional[str]:
        """Extract schedule value"""
        patterns = [
            r'時間[:\s]+([^\s,]+)',
            r'time[:\s]+([^\s,]+)',
            r'曜日[:\s]+([^\s,]+)',
            r'(day|night|morning|evening|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_retention(self, message: str) -> Optional[int]:
        """Extract retention days"""
        patterns = [
            r'保存期間[:\s]+(\d+)',
            r'retention[:\s]+(\d+)',
            r'(\d+)\s*(day|日)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_enabled(self, message: str) -> Optional[bool]:
        """Extract enabled status"""
        if re.search(r'(有効|enabled|enable|active|on)', message.lower()):
            return True
        if re.search(r'(無効|disabled|disable|inactive|off)', message.lower()):
            return False
        return None

    def _extract_id(self, message: str) -> Optional[int]:
        """Extract ID"""
        patterns = [
            r'ID[:\s]*(\d+)',
            r'id[:\s]*(\d+)',
            r'#(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_status(self, message: str) -> Optional[str]:
        """Extract status"""
        status_map = {
            'pending': 'pending',
            'running': 'running',
            'completed': 'completed',
            'failed': 'failed',
            '保留中': 'pending',
            '実行中': 'running',
            '完了': 'completed',
            '失敗': 'failed',
        }
        lower_msg = message.lower()
        for key, value in status_map.items():
            if key in lower_msg:
                return value
        return None

    def _extract_success(self, message: str) -> Optional[bool]:
        """Extract success flag"""
        if re.search(r'(成功|success|succeeded)', message.lower()):
            return True
        if re.search(r'(失敗|failed|error)', message.lower()):
            return False
        return None

    def _extract_log_level(self, message: str) -> Optional[str]:
        """Extract log level"""
        levels = ['info', 'warning', 'error', 'debug']
        lower_msg = message.lower()
        for level in levels:
            if level in lower_msg:
                return level
        return None

    def _extract_backup_type(self, message: str) -> Optional[str]:
        """Extract backup type"""
        types = ['full', 'incremental', 'differential']
        lower_msg = message.lower()
        for t in types:
            if t in lower_msg:
                return t
        return 'full'

    # Handlers

    def _handle_add_schedule(self, entities: Dict) -> str:
        """Handle adding backup schedule"""
        name = entities.get('name')
        target_type = entities.get('target_type')
        target_path = entities.get('target_path')
        schedule_type = entities.get('schedule_type', 'daily')

        if not name or not target_path:
            return "名前とパスを指定してください。例: スケジュール追加 名前:DB Daily タイプ:database パス:/data/db"

        schedule_id = self.db.add_backup_schedule(
            name=name,
            target_type=target_type or 'file',
            target_path=target_path,
            schedule_type=schedule_type,
            schedule_value=entities.get('schedule_value') or '00:00'
        )

        return f"✅ バックアップスケジュールを追加しました (ID: {schedule_id})\n名前: {name}\nタイプ: {schedule_type}"

    def _handle_list_schedules(self, entities: Dict) -> str:
        """Handle listing backup schedules"""
        schedules = self.db.get_backup_schedules(
            target_type=entities.get('target_type'),
            enabled=entities.get('enabled')
        )

        if not schedules:
            return "バックアップスケジュールが見つかりません"

        response = f"📅 **バックアップスケジュール一覧** ({len(schedules)}件):\n\n"
        for s in schedules:
            status_icon = "🟢" if s['enabled'] == 1 else "🔴"
            response += f"{status_icon} #{s['id']} {s['name']}\n"
            response += f"   タイプ: {s['target_type']} | {s['schedule_type']} {s['schedule_value']}\n"
            response += f"   パス: {s['target_path']}\n"
            if s['retention_days']:
                response += f"   保存期間: {s['retention_days']}日\n"
            response += "\n"

        return response

    def _handle_show_schedule(self, entities: Dict) -> str:
        """Handle showing schedule details"""
        schedule_id = entities.get('schedule_id')

        if not schedule_id:
            return "スケジュールIDを指定してください"

        schedule = self.db.get_backup_schedule(schedule_id)
        if not schedule:
            return f"スケジュールID {schedule_id} が見つかりません"

        status = "有効" if schedule['enabled'] == 1 else "無効"
        response = f"📅 **バックアップスケジュール詳細**\n\n"
        response += f"ID: {schedule['id']}\n"
        response += f"名前: {schedule['name']}\n"
        response += f"ターゲットタイプ: {schedule['target_type']}\n"
        response += f"パス: {schedule['target_path']}\n"
        response += f"スケジュール: {schedule['schedule_type']} {schedule['schedule_value']}\n"
        response += f"バックアップタイプ: {schedule['backup_type']}\n"
        response += f"圧縮: {'有効' if schedule['compression'] == 1 else '無効'}\n"
        response += f"保存期間: {schedule['retention_days']}日\n"
        response += f"状態: {status}\n"
        response += f"作成日: {schedule['created_at']}"

        return response

    def _handle_update_schedule(self, entities: Dict) -> str:
        """Handle updating schedule"""
        schedule_id = entities.get('schedule_id')

        if not schedule_id:
            return "スケジュールIDを指定してください"

        success = self.db.update_backup_schedule(
            schedule_id=schedule_id,
            schedule_type=entities.get('schedule_type'),
            schedule_value=entities.get('schedule_value'),
            retention_days=entities.get('retention_days'),
            enabled=entities.get('enabled')
        )

        if success:
            return f"✅ スケジュール {schedule_id} を更新しました"
        else:
            return "更新に失敗しました"

    def _handle_toggle_schedule(self, entities: Dict) -> str:
        """Handle toggling schedule enabled status"""
        schedule_id = entities.get('schedule_id')

        if not schedule_id:
            return "スケジュールIDを指定してください"

        is_enabled = self.db.toggle_schedule_enabled(schedule_id)
        status = "有効" if is_enabled else "無効"
        return f"🔘 スケジュール {schedule_id} を「{status}」にしました"

    def _handle_delete_schedule(self, entities: Dict) -> str:
        """Handle deleting schedule"""
        schedule_id = entities.get('schedule_id')

        if not schedule_id:
            return "スケジュールIDを指定してください"

        self.db.delete_backup_schedule(schedule_id)
        return f"🗑️ スケジュール {schedule_id} を削除しました"

    def _handle_add_backup_job(self, entities: Dict) -> str:
        """Handle adding backup job"""
        schedule_id = entities.get('schedule_id')

        if not schedule_id:
            return "スケジュールIDを指定してください"

        job_id = self.db.add_backup_job(schedule_id)
        return f"✅ バックアップジョブを追加しました (ID: {job_id})"

    def _handle_list_backup_jobs(self, entities: Dict) -> str:
        """Handle listing backup jobs"""
        jobs = self.db.get_backup_jobs(
            schedule_id=entities.get('schedule_id'),
            status=entities.get('status'),
            limit=30
        )

        if not jobs:
            return "バックアップジョブが見つかりません"

        status_icons = {'pending': '⏳', 'running': '🔄', 'completed': '✅', 'failed': '❌'}
        response = f"🔄 **バックアップジョブ一覧** ({len(jobs)}件):\n\n"
        for j in jobs[:15]:
            icon = status_icons.get(j['status'], '📌')
            size = f" ({j['backup_size_bytes']:,} bytes)" if j['backup_size_bytes'] else ""
            response += f"{icon} #{j['id']} スケジュール:#{j['schedule_id']} - {j['status']}{size}\n"
            if j['backup_path']:
                response += f"   パス: {j['backup_path']}\n"
            if j['error_message']:
                response += f"   エラー: {j['error_message']}\n"
            response += f"   {j['created_at']}\n\n"

        if len(jobs) > 15:
            response += f"\n...他 {len(jobs) - 15}件"

        return response

    def _handle_update_backup_job(self, entities: Dict) -> str:
        """Handle updating backup job"""
        job_id = entities.get('job_id')

        if not job_id:
            return "ジョブIDを指定してください"

        success = self.db.update_backup_job(
            job_id=job_id,
            status=entities.get('status'),
            success=entities.get('success')
        )

        if success:
            return f"✅ ジョブ {job_id} を更新しました"
        else:
            return "更新に失敗しました"

    def _handle_add_backup_target(self, entities: Dict) -> str:
        """Handle adding backup target"""
        target_type = entities.get('target_type') or 'file'
        target_name = entities.get('target_name')
        target_path = entities.get('target_path')

        if not target_name or not target_path:
            return "名前とパスを指定してください"

        target_id = self.db.add_backup_target(
            target_type=target_type,
            target_name=target_name,
            target_path=target_path
        )

        return f"✅ バックアップターゲットを追加しました (ID: {target_id})\n名前: {target_name}"

    def _handle_list_backup_targets(self, entities: Dict) -> str:
        """Handle listing backup targets"""
        targets = self.db.get_backup_targets(target_type=entities.get('target_type'))

        if not targets:
            return "バックアップターゲットが見つかりません"

        response = f"🎯 **バックアップターゲット一覧** ({len(targets)}件):\n\n"
        for t in targets:
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(t['priority'], '📌')
            response += f"{priority_icon} #{t['id']} {t['target_name']} ({t['target_type']})\n"
            response += f"   パス: {t['target_path']}\n"
            if t['description']:
                response += f"   説明: {t['description']}\n"
            response += "\n"

        return response

    def _handle_delete_backup_target(self, entities: Dict) -> str:
        """Handle deleting backup target"""
        target_id = entities.get('target_id')

        if not target_id:
            return "ターゲットIDを指定してください"

        self.db.delete_backup_target(target_id)
        return f"🗑️ ターゲット {target_id} を削除しました"

    def _handle_show_logs(self, entities: Dict) -> str:
        """Handle showing logs"""
        logs = self.db.get_logs(
            schedule_id=entities.get('schedule_id'),
            log_level=entities.get('log_level'),
            limit=30
        )

        if not logs:
            return "ログが見つかりません"

        level_icons = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'debug': '🔍'}
        response = f"📜 **バックアップログ** ({len(logs)}件):\n\n"
        for log in logs[:20]:
            icon = level_icons.get(log['log_level'], '📝')
            response += f"{icon} [{log['log_level']}] {log['message']}\n"
            if log['details']:
                response += f"   {log['details']}\n"
            response += f"   {log['timestamp']}\n\n"

        if len(logs) > 20:
            response += f"\n...他 {len(logs) - 20}件"

        return response

    def _handle_add_retention_policy(self, entities: Dict) -> str:
        """Handle adding retention policy"""
        policy_name = entities.get('policy_name')
        backup_type = entities.get('backup_type', 'full')

        if not policy_name:
            return "ポリシー名を指定してください"

        policy_id = self.db.add_retention_policy(
            policy_name=policy_name,
            backup_type=backup_type
        )

        return f"✅ リテンションポリシーを追加しました (ID: {policy_id})\n名前: {policy_name}"

    def _handle_list_retention_policies(self, entities: Dict) -> str:
        """Handle listing retention policies"""
        policies = self.db.get_retention_policies(backup_type=entities.get('backup_type'))

        if not policies:
            return "リテンションポリシーが見つかりません"

        response = f"📋 **リテンションポリシー一覧** ({len(policies)}件):\n\n"
        for p in policies:
            response += f"#{p['id']} {p['policy_name']} ({p['backup_type']})\n"
            if p['daily_retention']:
                response += f"   日次: {p['daily_retention']}日\n"
            if p['weekly_retention']:
                response += f"   週次: {p['weekly_retention']}週\n"
            if p['monthly_retention']:
                response += f"   月次: {p['monthly_retention']}ヶ月\n"
            if p['yearly_retention']:
                response += f"   年次: {p['yearly_retention']}年\n"
            response += "\n"

        return response

    def _handle_show_summary(self, entities: Dict) -> str:
        """Handle showing summary"""
        summary = self.db.get_backup_summary()

        total_size_gb = summary['total_backup_size_bytes'] / (1024 ** 3) if summary['total_backup_size_bytes'] else 0

        response = f"📊 **バックアップサマリー**\n\n"
        response += f"総スケジュール数: {summary['total_schedules']}件\n"
        response += f"有効なスケジュール: {summary['enabled_schedules']}件\n"
        response += f"過去24時間のジョブ: {summary['recent_jobs_24h']}件\n"
        response += f"成功したジョブ: {summary['successful_jobs']}件\n"
        response += f"失敗したジョブ: {summary['failed_jobs']}件\n"
        response += f"総バックアップサイズ: {total_size_gb:.2f} GB"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
💾 **Backup Schedule Agent ヘルプ**

**スケジュール管理:**
• スケジュール追加 名前:DB Daily タイプ:database パス:/data/db
• スケジュール一覧
• スケジュール詳細 ID:1
• スケジュール更新 ID:1 保存期間:60
• スケジュール有効 ID:1
• スケジュール削除 ID:1

**バックアップジョブ:**
• バックアップ実行 ID:1
• バックアップ履歴
• ジョブ更新 ID:1 ステータス:完了 成功:はい

**ターゲット管理:**
• ターゲット追加 タイプ:database 名前:Main DB パス:/data/db
• ターゲット一覧
• ターゲット削除 ID:1

**ログ・ポリシー:**
• ログ表示
• リテンション追加 名前:Standard タイプ:full
• リテンション一覧

**サマリー:**
• サマリー表示

**English support:**
• Add schedule name: DB Daily type: database path: /data/db
• List schedules
• Show schedule ID:1
• Run backup ID:1
• Show backup jobs
• Add target type: database name: Main DB path: /data/db
• Show summary
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return "すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = BackupScheduleDiscord(":memory:")

    # Test adding schedule
    print("--- Add Schedule ---")
    print(agent.process_message("スケジュール追加 名前:DB Daily タイプ:database パス:/data/db"))

    # Test listing schedules
    print("\n--- List Schedules ---")
    print(agent.process_message("スケジュール一覧"))

    # Test adding backup target
    print("\n--- Add Target ---")
    print(agent.process_message("ターゲット追加 タイプ:database 名前:Main DB パス:/data/db"))

    # Test showing summary
    print("\n--- Summary ---")
    print(agent.process_message("サマリー表示"))
