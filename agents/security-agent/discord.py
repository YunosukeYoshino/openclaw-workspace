"""
Security Agent Discord Module

Natural language processing for security management commands.
"""

import re
from typing import Dict, Optional, List
from .db import SecurityDB

class SecurityDiscordHandler:
    """Handle Discord messages for Security Agent"""

    def __init__(self, db: SecurityDB):
        self.db = db

    def process_message(self, content: str) -> str:
        """
        Process a Discord message and execute appropriate action.

        Supported commands:
        - "threat add <type> <severity> [description]" - Add new threat
        - "threat list [status] [severity]" - List threats
        - "threat resolve <id>" - Mark threat as resolved
        - "incident add <title> <severity> [description]" - Add incident
        - "incident list [status]" - List incidents
        - "incident update <id> <status>" - Update incident status
        - "measure add <name> <type> [description]" - Add security measure
        - "measure list" - List measures
        - "stats" - Show security statistics
        """
        content_lower = content.lower().strip()

        # Threat commands
        if "threat add" in content_lower:
            return self._add_threat(content)
        elif "threat list" in content_lower or "list threat" in content_lower:
            return self._list_threats(content_lower)
        elif "threat resolve" in content_lower:
            return self._resolve_threat(content)

        # Incident commands
        elif "incident add" in content_lower:
            return self._add_incident(content)
        elif "incident list" in content_lower or "list incident" in content_lower:
            return self._list_incidents(content_lower)
        elif "incident update" in content_lower:
            return self._update_incident(content)

        # Measure commands
        elif "measure add" in content_lower:
            return self._add_measure(content)
        elif "measure list" in content_lower or "list measure" in content_lower:
            return self._list_measures()

        # Stats
        elif "stat" in content_lower:
            return self._show_stats()

        # Help
        elif "help" in content_lower:
            return self._show_help()

        else:
            return self._show_help()

    def _add_threat(self, content: str) -> str:
        """Parse and add a new threat"""
        # Extract severity (high/medium/low/critical)
        severity = None
        for sev in ['critical', 'high', 'medium', 'low']:
            if sev.lower() in content.lower():
                severity = sev
                break

        if not severity:
            return "❌ 重大度 (critical/high/medium/low) を指定してください"

        # Extract type
        type_match = re.search(r'(?:threat add|add threat)\s+(\w+)', content, re.IGNORECASE)
        threat_type = type_match.group(1) if type_match else 'unknown'

        # Extract description (everything after type+severity)
        desc_match = re.search(rf'{threat_type}\s+{severity}\s+(.+)', content, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else None

        threat_id = self.db.add_threat(
            type=threat_type,
            severity=severity,
            title=description[:50] if description else f"{threat_type} threat",
            description=description
        )

        return f"✅ 脅威を登録しました (ID: {threat_id})\n" \
               f"   タイプ: {threat_type}\n" \
               f"   重大度: {severity}\n" \
               f"   説明: {description or 'なし'}"

    def _list_threats(self, content: str) -> str:
        """List threats with optional filters"""
        status = None
        severity = None

        if "open" in content or "active" in content:
            status = "open"
        elif "resolved" in content:
            status = "resolved"

        for sev in ['critical', 'high', 'medium', 'low']:
            if sev in content:
                severity = sev
                break

        threats = self.db.get_threats(status=status, severity=severity, limit=10)

        if not threats:
            return "📭 脅威は見つかりませんでした"

        output = f"🔒 **脅威一覧** (フィルター: {status or '全て'}/{severity or '全て'})\n\n"
        for t in threats:
            emoji = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '⚡',
                'low': '🔵'
            }.get(t['severity'], '📋')

            status_emoji = '🟢' if t['status'] == 'resolved' else '🔴'

            output += f"{emoji} **#{t['id']}** {status_emoji} {t['type']} - {t['severity']}\n"
            output += f"   状態: {t['status']} | 検知: {t['detected_at']}\n"
            if t['description']:
                output += f"   {t['description'][:100]}...\n"
            output += "\n"

        return output

    def _resolve_threat(self, content: str) -> str:
        """Mark a threat as resolved"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ 脅威IDを指定してください (例: threat resolve 123)"

        threat_id = int(id_match.group(1))
        success = self.db.update_threat_status(threat_id, 'resolved')

        if success:
            return f"✅ 脅威 #{threat_id} を解決済みにしました"
        else:
            return f"❌ 脅威 #{threat_id} が見つかりません"

    def _add_incident(self, content: str) -> str:
        """Parse and add a new incident"""
        severity = None
        for sev in ['critical', 'high', 'medium', 'low']:
            if sev.lower() in content.lower():
                severity = sev
                break

        if not severity:
            return "❌ 重大度 (critical/high/medium/low) を指定してください"

        # Extract title (between "incident add" and severity)
        title_match = re.search(r'(?:incident add)\s+(.+?)\s+{}'.format(severity), content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else f"Incident"

        # Extract description
        desc_match = re.search(rf'{severity}\s+(.+)', content, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else None

        incident_id = self.db.add_incident(
            title=title,
            severity=severity,
            description=description
        )

        return f"✅ インシデントを登録しました (ID: {incident_id})\n" \
               f"   タイトル: {title}\n" \
               f"   重大度: {severity}"

    def _list_incidents(self, content: str) -> str:
        """List incidents with optional filters"""
        status = None

        if "active" in content:
            status = "active"
        elif "resolved" in content or "closed" in content:
            status = "resolved"

        incidents = self.db.get_incidents(status=status, limit=10)

        if not incidents:
            return "📭 インシデントは見つかりませんでした"

        output = f"🚨 **インシデント一覧** (フィルター: {status or '全て'})\n\n"
        for i in incidents:
            emoji = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '⚡',
                'low': '🔵'
            }.get(i['severity'], '📋')

            status_emoji = '🟢' if i['status'] in ('resolved', 'closed') else '🔴'

            output += f"{emoji} **#{i['id']}** {status_emoji} {i['title']}\n"
            output += f"   状態: {i['status']} | 重大度: {i['severity']} | 作成: {i['created_at']}\n"
            if i['description']:
                output += f"   {i['description'][:100]}...\n"
            output += "\n"

        return output

    def _update_incident(self, content: str) -> str:
        """Update incident status"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ インシデントIDを指定してください (例: incident update 123 resolved)"

        incident_id = int(id_match.group(1))

        status = None
        if "resolved" in content.lower():
            status = "resolved"
        elif "contained" in content.lower():
            status = "contained"
        elif "closed" in content.lower():
            status = "closed"
        elif "investigating" in content.lower():
            status = "investigating"

        if not status:
            return "❌ ステータスを指定してください (resolved/contained/closed/investigating)"

        success = self.db.update_incident_status(incident_id, status)

        if success:
            return f"✅ インシデント #{incident_id} のステータスを {status} に更新しました"
        else:
            return f"❌ インシデント #{incident_id} が見つかりません"

    def _add_measure(self, content: str) -> str:
        """Parse and add a new security measure"""
        type_match = re.search(r'(?:measure add)\s+(\w+)', content, re.IGNORECASE)
        measure_type = type_match.group(1).lower() if type_match else 'preventive'

        valid_types = ['preventive', 'detective', 'corrective', 'deterrent']
        if measure_type not in valid_types:
            # Try to find type in content
            for vt in valid_types:
                if vt in content.lower():
                    measure_type = vt
                    break

        # Extract name (between type and description)
        name_match = re.search(rf'{measure_type}\s+(.+?)(?:\s+(?:{valid_types[1:]}|$))', content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else f"Security measure"

        # Extract description
        desc_match = re.search(rf'{name}\s+(.+)', content, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else None

        measure_id = self.db.add_measure(
            name=name,
            type=measure_type,
            description=description
        )

        return f"✅ セキュリティ対策を登録しました (ID: {measure_id})\n" \
               f"   名称: {name}\n" \
               f"   タイプ: {measure_type}"

    def _list_measures(self) -> str:
        """List security measures"""
        measures = self.db.get_measures()

        if not measures:
            return "📭 セキュリティ対策は見つかりませんでした"

        output = f"🛡️ **セキュリティ対策一覧**\n\n"
        type_emojis = {
            'preventive': '🚫',
            'detective': '🔍',
            'corrective': '🔧',
            'deterrent': '⚡'
        }

        for m in measures:
            emoji = type_emojis.get(m['type'], '🛡️')
            status_emoji = '🟢' if m['status'] == 'active' else '⚪'

            output += f"{emoji} **#{m['id']}** {status_emoji} {m['name']}\n"
            output += f"   タイプ: {m['type']} | 状態: {m['status']}\n"
            if m['description']:
                output += f"   {m['description'][:80]}...\n"
            output += "\n"

        return output

    def _show_stats(self) -> str:
        """Show security statistics"""
        stats = self.db.get_stats()

        output = "📊 **セキュリティ統計**\n\n"

        # Active threats
        active_threats = stats.get('active_threats_by_severity', {})
        total_threats = sum(active_threats.values())
        output += f"🔒 **アクティブ脅威**: {total_threats} 件\n"
        for severity, count in active_threats.items():
            emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': '🔵'}.get(severity, '📋')
            output += f"   {emoji} {severity}: {count}\n"
        output += "\n"

        # Incidents
        incidents = stats.get('incidents_by_status', {})
        output += f"🚨 **インシデント**\n"
        for status, count in incidents.items():
            emoji = '🟢' if status in ('resolved', 'closed') else '🔴'
            output += f"   {emoji} {status}: {count}\n"
        output += "\n"

        # Critical alerts
        critical = stats.get('critical_threats', 0)
        if critical > 0:
            output += f"🚨 **要注意**: {critical} 件のクリティカルな脅威が未解決です！\n"

        return output

    def _show_help(self) -> str:
        """Show help message"""
        return """
🛡️ **Security Agent ヘルプ**

**脅威管理**
- `threat add <タイプ> <重大度> [説明]` - 脅威を追加
- `threat list [status] [severity]` - 脅威一覧
- `threat resolve <ID>` - 脅威を解決済みにする

**インシデント管理**
- `incident add <タイトル> <重大度> [説明]` - インシデントを追加
- `incident list [status]` - インシデント一覧
- `incident update <ID> <status>` - ステータス更新

**セキュリティ対策**
- `measure add <タイプ> <名称> [説明]` - 対策を追加
- `measure list` - 対策一覧

**統計**
- `stats` - セキュリティ統計を表示

**重大度**: critical, high, medium, low
**タイプ**: preventive, detective, corrective, deterrent
"""
