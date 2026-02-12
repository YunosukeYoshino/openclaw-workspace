"""
Message Agent Discord Module

Natural language processing for message management commands.
"""

import re
from typing import Dict, Optional, List
from .db import MessageDB

class MessageDiscordHandler:
    """Handle Discord messages for Message Agent"""

    def __init__(self, db: MessageDB):
        self.db = db

    def process_message(self, content: str) -> str:
        """
        Process a Discord message and execute appropriate action.

        Supported commands:
        - "message add <sender> <recipient> <content>" - Add message
        - "message list [sender] [recipient]" - List messages
        - "message search <keyword>" - Search messages
        - "contact add <name> <id> <platform>" - Add contact
        - "contact list [platform]" - List contacts
        - "communication start <participants>" - Start communication log
        - "communication end <ID> [summary]" - End communication log
        - "stats" - Show statistics
        """
        content_lower = content.lower().strip()

        # Message commands
        if "message add" in content_lower or "add message" in content_lower:
            return self._add_message(content)
        elif "message list" in content_lower or "list message" in content_lower:
            return self._list_messages(content_lower)
        elif "message search" in content_lower or "search" in content_lower and "message" in content_lower:
            return self._search_messages(content)

        # Contact commands
        elif "contact add" in content_lower:
            return self._add_contact(content)
        elif "contact list" in content_lower or "list contact" in content_lower:
            return self._list_contacts(content_lower)

        # Communication commands
        elif "communication start" in content_lower:
            return self._start_communication(content)
        elif "communication end" in content_lower:
            return self._end_communication(content)
        elif "communication list" in content_lower or "list communication" in content_lower:
            return self._list_communications(content_lower)

        # Stats
        elif "stat" in content_lower:
            return self._show_stats()

        # Help
        elif "help" in content_lower:
            return self._show_help()

        else:
            return self._show_help()

    def _add_message(self, content: str) -> str:
        """Parse and add a new message"""
        # Extract platform
        platform = None
        for plat in ['discord', 'slack', 'email', 'telegram', 'whatsapp', 'line']:
            if plat.lower() in content.lower():
                platform = plat
                break

        # Simple pattern: message add <sender> <recipient> <content>
        # This is a simplified parser - in production you'd want better NLP

        # Try to extract sender and recipient
        parts = content.split()
        if len(parts) < 4:
            return "❌ 送信者、受信者、メッセージ内容を指定してください"

        # Skip "message add"
        idx = 2
        sender = parts[idx]

        # Recipient
        idx += 1
        recipient = parts[idx]

        # Content (rest of message)
        idx += 1
        content_text = ' '.join(parts[idx:])

        message_id = self.db.add_message(
            sender=sender,
            recipient=recipient,
            content=content_text,
            platform=platform
        )

        return f"✅ メッセージを記録しました (ID: {message_id})\n" \
               f"   送信者: {sender}\n" \
               f"   受信者: {recipient}\n" \
               f"   プラットフォーム: {platform or '未指定'}\n" \
               f"   内容: {content_text[:50]}..."

    def _list_messages(self, content: str) -> str:
        """List messages with optional filters"""
        # Try to extract sender/recipient from content
        sender = None
        recipient = None

        # Look for "from <name>" or "to <name>"
        from_match = re.search(r'from\s+(\w+)', content, re.IGNORECASE)
        to_match = re.search(r'to\s+(\w+)', content, re.IGNORECASE)

        if from_match:
            sender = from_match.group(1)
        if to_match:
            recipient = to_match.group(1)

        # Or just look for names in order
        if not sender and not recipient:
            words = content.split()
            if len(words) > 3:
                potential_names = [w for w in words[3:6] if len(w) > 2]
                if len(potential_names) >= 1:
                    sender = potential_names[0]
                if len(potential_names) >= 2:
                    recipient = potential_names[1]

        messages = self.db.get_messages(sender=sender, recipient=recipient, limit=15)

        if not messages:
            return "📭 メッセージは見つかりませんでした"

        output = f"💬 **メッセージ一覧** (送信者: {sender or '全て'} | 受信者: {recipient or '全て'})\n\n"
        platform_emojis = {
            'discord': '🎮',
            'slack': '💼',
            'email': '📧',
            'telegram': '✈️',
            'whatsapp': '💬',
            'line': '💬'
        }

        for m in messages:
            emoji = platform_emojis.get(m['platform'], '💬')
            status_emoji = {'sent': '✉️', 'delivered': '📬', 'read': '📖', 'failed': '❌'}.get(m['status'], '✉️')

            output += f"{emoji} **#{m['id']}** {status_emoji}\n"
            output += f"   {m['sender']} → {m['recipient']}\n"
            output += f"   {m['content'][:80]}...\n"
            output += f"   {m['timestamp']} | {m['platform'] or 'N/A'}\n\n"

        return output

    def _search_messages(self, content: str) -> str:
        """Search messages by keyword"""
        # Extract keyword after "search"
        search_match = re.search(r'(?:message search|search)\s+(.+)', content, re.IGNORECASE)
        if not search_match:
            return "❌ 検索キーワードを指定してください (例: message search important)"

        keyword = search_match.group(1).strip()

        messages = self.db.search_messages(keyword, limit=20)

        if not messages:
            return f"🔍 キーワード '{keyword}' に一致するメッセージは見つかりませんでした"

        output = f"🔍 **検索結果**: '{keyword}' ({len(messages)} 件)\n\n"

        for m in messages:
            output += f"💬 **#{m['id']}**\n"
            output += f"   {m['sender']} → {m['recipient']}\n"
            # Highlight keyword
            highlighted = m['content'].replace(keyword, f"**{keyword}**")
            output += f"   {highlighted[:100]}...\n"
            output += f"   {m['timestamp']}\n\n"

        return output

    def _add_contact(self, content: str) -> str:
        """Parse and add a new contact"""
        # Extract platform
        platform = None
        for plat in ['discord', 'slack', 'email', 'telegram', 'whatsapp', 'line']:
            if plat.lower() in content.lower():
                platform = plat
                break

        # Simple pattern: contact add <name> <id> [platform]
        parts = content.split()
        if len(parts) < 4:
            return "❌ 名前とIDを指定してください"

        # Skip "contact add"
        idx = 2
        name = parts[idx]

        # ID
        idx += 1
        identifier = parts[idx]

        # Platform (optional)
        if not platform and len(parts) > idx + 1:
            platform = parts[idx + 1]

        contact_id = self.db.add_contact(
            name=name,
            identifier=identifier,
            platform=platform
        )

        return f"✅ コンタクトを追加しました (ID: {contact_id})\n" \
               f"   名前: {name}\n" \
               f"   ID: {identifier}\n" \
               f"   プラットフォーム: {platform or '未指定'}"

    def _list_contacts(self, content: str) -> str:
        """List contacts with optional filters"""
        platform = None

        for plat in ['discord', 'slack', 'email', 'telegram', 'whatsapp', 'line']:
            if plat in content.lower():
                platform = plat
                break

        contacts = self.db.get_contacts(platform=platform)

        if not contacts:
            return "📭 コンタクトは見つかりませんでした"

        output = f"👥 **コンタクト一覧** (プラットフォーム: {platform or '全て'})\n\n"
        platform_emojis = {
            'discord': '🎮',
            'slack': '💼',
            'email': '📧',
            'telegram': '✈️',
            'whatsapp': '💬',
            'line': '💬'
        }

        for c in contacts:
            emoji = platform_emojis.get(c['platform'], '👤')
            output += f"{emoji} **{c['name']}** #{c['id']}\n"
            output += f"   ID: {c['identifier']}\n"
            if c['relationship']:
                output += f"   関係: {c['relationship']}\n"
            if c['platform']:
                output += f"   プラットフォーム: {c['platform']}\n"
            output += "\n"

        return output

    def _start_communication(self, content: str) -> str:
        """Start a new communication log"""
        # Extract platform
        platform = None
        for plat in ['discord', 'slack', 'zoom', 'meet', 'teams']:
            if plat.lower() in content.lower():
                platform = plat
                break

        # Extract participants (everything after "start")
        match = re.search(r'(?:communication start)\s+(.+)', content, re.IGNORECASE)
        if not match:
            return "❌ 参加者を指定してください"

        participants = match.group(1).strip()

        log_id = self.db.start_communication(
            participants=participants,
            platform=platform
        )

        return f"✅ 通信ログを開始しました (ID: {log_id})\n" \
               f"   参加者: {participants}\n" \
               f"   プラットフォーム: {platform or '未指定'}"

    def _end_communication(self, content: str) -> str:
        """End a communication log"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ 通信ログIDを指定してください (例: communication end 123)"

        log_id = int(id_match.group(1))

        # Extract summary if provided
        summary_match = re.search(r'\d+\s+(.+)', content)
        summary = summary_match.group(1).strip() if summary_match else None

        success = self.db.end_communication(log_id, summary=summary)

        if success:
            return f"✅ 通信ログ #{log_id} を終了しました"
        else:
            return f"❌ 通信ログ #{log_id} が見つかりません"

    def _list_communications(self, content: str) -> str:
        """List communication logs"""
        comm_type = None

        for ct in ['chat', 'call', 'video', 'email', 'meeting']:
            if ct in content.lower():
                comm_type = ct
                break

        logs = self.db.get_communication_logs(comm_type=comm_type, limit=15)

        if not logs:
            return "📭 通信ログは見つかりませんでした"

        output = f"📞 **通信ログ一覧** (タイプ: {comm_type or '全て'})\n\n"
        type_emojis = {
            'chat': '💬',
            'call': '📞',
            'video': '📹',
            'email': '📧',
            'meeting': '👥'
        }

        for log in logs:
            emoji = type_emojis.get(log['communication_type'], '📞')
            status = '🔴 継続中' if not log['end_time'] else '🟢 完了'

            output += f"{emoji} **#{log['id']}** {status}\n"
            if log['title']:
                output += f"   タイトル: {log['title']}\n"
            output += f"   参加者: {log['participants']}\n"
            output += f"   開始: {log['start_time']}\n"
            if log['end_time']:
                output += f"   終了: {log['end_time']} ({log['duration_minutes']}分)\n"
            if log['summary']:
                output += f"   サマリー: {log['summary'][:80]}...\n"
            output += "\n"

        return output

    def _show_stats(self) -> str:
        """Show message statistics"""
        stats = self.db.get_stats()

        output = "📊 **メッセージ統計**\n\n"

        # Messages by platform
        output += "💬 **メッセージ (プラットフォーム別)**\n"
        messages_by_platform = stats.get('messages_by_platform', {})
        for platform, count in messages_by_platform.items():
            emoji = {'discord': '🎮', 'slack': '💼', 'email': '📧'}.get(platform, '💬')
            output += f"   {emoji} {platform}: {count}\n"

        # Today's messages
        messages_today = stats.get('messages_today', 0)
        output += f"\n📅 今日のメッセージ: {messages_today} 件\n"

        # Communications
        output += "\n📞 **通信ログ (タイプ別)**\n"
        comms_by_type = stats.get('communications_by_type', {})
        type_emojis = {'chat': '💬', 'call': '📞', 'video': '📹', 'meeting': '👥'}
        for comm_type, count in comms_by_type.items():
            emoji = type_emojis.get(comm_type, '📞')
            output += f"   {emoji} {comm_type}: {count}\n"

        avg_duration = stats.get('avg_communication_duration', 0)
        output += f"\n⏱️ 平均通話時間: {avg_duration} 分\n"

        # Contacts
        total_contacts = stats.get('total_contacts', 0)
        output += f"\n👥 登録コンタクト: {total_contacts} 人\n"

        return output

    def _show_help(self) -> str:
        """Show help message"""
        return """
💬 **Message Agent ヘルプ**

**メッセージ管理**
- `message add <送信者> <受信者> <内容>` - メッセージを追加
- `message list [from <name>] [to <name>]` - メッセージ一覧
- `message search <キーワード>` - メッセージを検索

**コンタクト管理**
- `contact add <名前> <ID> [プラットフォーム]` - コンタクト追加
- `contact list [プラットフォーム]` - コンタクト一覧

**通信ログ**
- `communication start <参加者>` - 通信ログ開始
- `communication end <ID> [サマリー]` - 通信ログ終了
- `communication list [タイプ]` - 通信ログ一覧

**統計**
- `stats` - 統計を表示

**プラットフォーム**: discord, slack, email, telegram, whatsapp, line
"""
