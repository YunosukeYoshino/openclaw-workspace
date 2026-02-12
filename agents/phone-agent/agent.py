"""
Phone Agent Discord Module

Natural language processing for call record management commands in Japanese and English.
"""

import re
from typing import Dict, Optional, List
from .db import PhoneDB

class PhoneDiscordHandler:
    """Handle Discord messages for Phone Agent"""

    def __init__(self, db: PhoneDB):
        self.db = db

    def process_message(self, content: str) -> str:
        """
        Process a Discord message and execute appropriate action.

        Supported commands / サポートされるコマンド:
        - "call add <name> <number> <type> [duration] [notes]" - Add call / 通話を追加
        - "call list [type] [name]" - List calls / 通話一覧
        - "call update <id> <field> <value>" - Update call / 通話更新
        - "contact add <name> <number> [email]" - Add contact / 連絡先追加
        - "contact list [name]" - List contacts / 連絡先一覧
        - "contact update <id> <field> <value>" - Update contact / 連絡先更新
        - "stats" - Show statistics / 統計表示
        """
        content_lower = content.lower().strip()

        # Call commands / 通話コマンド
        if "call add" in content_lower or "add call" in content_lower:
            return self._add_call(content)
        elif "call list" in content_lower or "list call" in content_lower:
            return self._list_calls(content_lower)
        elif "call update" in content_lower or "update call" in content_lower:
            return self._update_call(content)

        # Contact commands / 連絡先コマンド
        elif "contact add" in content_lower or "add contact" in content_lower:
            return self._add_contact(content)
        elif "contact list" in content_lower or "list contact" in content_lower:
            return self._list_contacts(content_lower)
        elif "contact update" in content_lower or "update contact" in content_lower:
            return self._update_contact(content)

        # Stats / 統計
        elif "stat" in content_lower or "統計" in content_lower:
            return self._show_stats()

        # Help / ヘルプ
        elif "help" in content_lower or "ヘルプ" in content_lower:
            return self._show_help()

        else:
            return self._show_help()

    def _add_call(self, content: str) -> str:
        """Parse and add a new call record / 新しい通話記録を追加"""
        # Extract call type (incoming/outgoing/missed)
        call_type = None
        for ct in ['incoming', 'outgoing', 'missed']:
            if ct in content.lower():
                call_type = ct
                break

        if not call_type:
            return "❌ Please specify call type (incoming/outgoing/missed)\n通話タイプを指定してください"

        # Extract phone number
        phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,})', content)
        phone_number = phone_match.group(1).strip() if phone_match else None

        if not phone_number:
            return "❌ Please specify phone number / 電話番号を指定してください"

        # Extract contact name (everything before phone number)
        name_match = re.search(r'(?:call add|add call)\s+([^\d]+)', content, re.IGNORECASE)
        contact_name = name_match.group(1).strip() if name_match else "Unknown"

        # Extract duration (in minutes)
        duration_match = re.search(r'(\d+)\s*(?:min|minutes?|分)', content, re.IGNORECASE)
        duration = int(duration_match.group(1)) if duration_match else 0

        # Extract notes (everything after duration or type)
        notes_match = re.search(rf'{call_type}\s+(?:.*?(\d+)\s*min\s+(.+)|(.+))', content, re.IGNORECASE)
        notes = notes_match.group(2) if notes_match and notes_match.group(2) else (notes_match.group(3) if notes_match else None)

        # Extract tags
        tags = []
        if 'urgent' in content.lower():
            tags.append('urgent')
        if 'business' in content.lower():
            tags.append('business')

        call_id = self.db.add_call(
            contact_name=contact_name,
            phone_number=phone_number,
            call_type=call_type,
            duration=duration,
            notes=notes,
            tags=tags
        )

        duration_str = f"{duration} min" if duration > 0 else "N/A"
        return f"✅ Call logged / 通話を記録しました (ID: {call_id})\n" \
               f"   Contact / 連絡先: {contact_name} ({phone_number})\n" \
               f"   Type / タイプ: {call_type}\n" \
               f"   Duration / 期間: {duration_str}\n" \
               f"   Notes / メモ: {notes or 'None / なし'}"

    def _list_calls(self, content: str) -> str:
        """List call records / 通話記録一覧を表示"""
        call_type = None
        contact_name = None

        if "incoming" in content:
            call_type = "incoming"
        elif "outgoing" in content:
            call_type = "outgoing"
        elif "missed" in content:
            call_type = "missed"

        # Extract contact name filter
        name_match = re.search(r'from\s+(\w+)|to\s+(\w+)', content, re.IGNORECASE)
        if name_match:
            contact_name = name_match.group(1) or name_match.group(2)

        calls = self.db.list_calls(limit=20, call_type=call_type, contact_name=contact_name)

        if not calls:
            return "📭 No calls found / 通話記録は見つかりませんでした"

        output = f"📞 **Call History / 通話履歴** (Filter: {call_type or 'All / 全て'})\n\n"
        type_emojis = {'incoming': '📥', 'outgoing': '📤', 'missed': '❌'}

        for call in calls:
            emoji = type_emojis.get(call['call_type'], '📞')
            duration_str = f"{call['duration']} min" if call['duration'] > 0 else "N/A"
            tags_str = f" #{' #'.join(call.get('tags', []))}" if call.get('tags') else ""

            output += f"{emoji} **#{call['id']}** {call['contact_name']} - {call['call_type']}\n"
            output += f"   Phone: {call['phone_number']} | Duration: {duration_str}\n"
            output += f"   Time: {call['call_time']}{tags_str}\n"
            if call['notes']:
                output += f"   Notes: {call['notes'][:50]}...\n"
            output += "\n"

        return output

    def _update_call(self, content: str) -> str:
        """Update a call record / 通話記録を更新"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ Please specify call ID / 通話IDを指定してください (例: call update 123 notes \"Follow up\")"

        call_id = int(id_match.group(1))

        # Extract notes
        notes_match = re.search(r'notes\s+[\"']?([^\"\']+)', content, re.IGNORECASE)
        notes = notes_match.group(1).strip() if notes_match else None

        if not notes:
            return "❌ Please specify field to update / 更新するフィールドを指定してください (例: notes \"Follow up\")"

        success = self.db.update_call(call_id, notes=notes)

        if success:
            return f"✅ Call #{call_id} updated / 通話 #{call_id} を更新しました"
        else:
            return f"❌ Call #{call_id} not found / 通話 #{call_id} が見つかりません"

    def _add_contact(self, content: str) -> str:
        """Parse and add a new contact / 新しい連絡先を追加"""
        # Extract phone number
        phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,})', content)
        phone_number = phone_match.group(1).strip() if phone_match else None

        if not phone_number:
            return "❌ Please specify phone number / 電話番号を指定してください"

        # Extract name (everything before phone number)
        name_match = re.search(r'(?:contact add|add contact)\s+([^\d]+)', content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else "Unknown"

        # Extract email
        email_match = re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', content)
        email = email_match.group(1) if email_match else None

        contact_id = self.db.add_contact(
            name=name,
            phone_number=phone_number,
            email=email
        )

        email_str = f"\n   Email: {email}" if email else ""
        return f"✅ Contact added / 連絡先を追加しました (ID: {contact_id})\n" \
               f"   Name / 名前: {name}\n" \
               f"   Phone / 電話: {phone_number}{email_str}"

    def _list_contacts(self, content: str) -> str:
        """List contacts / 連絡先一覧を表示"""
        name = None
        name_match = re.search(r'(\w+)$', content)
        if name_match:
            name = name_match.group(1)

        contacts = self.db.list_contacts(limit=50, name=name)

        if not contacts:
            return "📭 No contacts found / 連絡先は見つかりませんでした"

        output = f"👥 **Contact List / 連絡先一覧**\n\n"

        for contact in contacts:
            output += f"**#{contact['id']}** {contact['name']}\n"
            output += f"   Phone: {contact['phone_number']}\n"
            if contact['email']:
                output += f"   Email: {contact['email']}\n"
            if contact['notes']:
                output += f"   Notes: {contact['notes'][:30]}...\n"
            output += "\n"

        return output

    def _update_contact(self, content: str) -> str:
        """Update a contact / 連絡先を更新"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ Please specify contact ID / 連絡先IDを指定してください (例: contact update 123 name \"New Name\")"

        contact_id = int(id_match.group(1))

        # Check what to update
        name_match = re.search(r'name\s+[\"']?([^\"\']+)', content, re.IGNORECASE)
        phone_match = re.search(r'phone\s+(\+?\d[\d\s\-\(\)]{7,})', content, re.IGNORECASE)
        email_match = re.search(r'email\s+([\w\.-]+@[\w\.-]+\.\w+)', content, re.IGNORECASE)
        notes_match = re.search(r'notes\s+[\"']?([^\"\']+)', content, re.IGNORECASE)

        updates = {}
        if name_match:
            updates['name'] = name_match.group(1).strip()
        if phone_match:
            updates['phone_number'] = phone_match.group(1).strip()
        if email_match:
            updates['email'] = email_match.group(1)
        if notes_match:
            updates['notes'] = notes_match.group(1).strip()

        if not updates:
            return "❌ Please specify field to update / 更新するフィールドを指定してください (例: name \"New Name\")"

        success = self.db.update_contact(contact_id, **updates)

        if success:
            return f"✅ Contact #{contact_id} updated / 連絡先 #{contact_id} を更新しました"
        else:
            return f"❌ Contact #{contact_id} not found / 連絡先 #{contact_id} が見つかりません"

    def _show_stats(self) -> str:
        """Show phone statistics / 電話統計を表示"""
        stats = self.db.get_stats()

        output = "📊 **Phone Statistics / 電話統計**\n\n"

        # Total calls
        total_calls = stats.get('total_calls', 0)
        output += f"📞 **Total Calls / 総通話数**: {total_calls}\n"

        # By type
        by_type = stats.get('by_type', {})
        type_emojis = {'incoming': '📥', 'outgoing': '📤', 'missed': '❌'}
        for call_type, count in by_type.items():
            emoji = type_emojis.get(call_type, '📞')
            output += f"   {emoji} {call_type}: {count}\n"

        output += "\n"

        # Contacts
        total_contacts = stats.get('total_contacts', 0)
        output += f"👥 **Total Contacts / 総連絡先数**: {total_contacts}\n\n"

        # This month's duration
        month_minutes = stats.get('this_month_minutes', 0)
        hours = int(month_minutes // 60)
        mins = int(month_minutes % 60)
        output += f"⏱️ **This Month / 今月の通話時間**: {hours}h {mins}m ({month_minutes:.1f} min)"

        return output

    def _show_help(self) -> str:
        """Show help message / ヘルプメッセージを表示"""
        return """
📞 **Phone Agent Help / 電話エージェント ヘルプ**

**Call Management / 通話管理**
- `call add <name> <number> <type> [duration] [notes]` - Add call / 通話を追加
- `call list [type] [name]` - List calls / 通話一覧
- `call update <id> notes <text>` - Update call / 通話更新

**Contact Management / 連絡先管理**
- `contact add <name> <number> [email]` - Add contact / 連絡先を追加
- `contact list [name]` - List contacts / 連絡先一覧
- `contact update <id> <field> <value>` - Update contact / 連絡先更新

**Statistics / 統計**
- `stats` - Show statistics / 統計を表示

**Call Types / 通話タイプ**: incoming, outgoing, missed
**Contact Fields / 連絡先フィールド**: name, phone, email, notes
"""
