"""
Scale Agent Discord Module
Natural language processing for scaling and capacity planning
"""

import re
from typing import Optional, Dict, List
from db import ScaleDB


class ScaleDiscord:
    """Discord interface for scale agent with NLP"""

    def __init__(self, db_path: str = "scale.db"):
        self.db = ScaleDB(db_path)

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "add_resource":
            return self._handle_add_resource(entities)
        elif intent == "list_resources":
            return self._handle_list_resources(entities)
        elif intent == "update_usage":
            return self._handle_update_usage(entities)
        elif intent == "show_usage_history":
            return self._handle_show_usage_history(entities)
        elif intent == "add_scaling_event":
            return self._handle_add_scaling_event(entities)
        elif intent == "list_scaling_events":
            return self._handle_list_scaling_events(entities)
        elif intent == "complete_scaling":
            return self._handle_complete_scaling(entities)
        elif intent == "add_capacity_plan":
            return self._handle_add_capacity_plan(entities)
        elif intent == "list_capacity_plans":
            return self._handle_list_capacity_plans(entities)
        elif intent == "update_capacity_plan":
            return self._handle_update_capacity_plan(entities)
        elif intent == "set_thresholds":
            return self._handle_set_thresholds(entities)
        elif intent == "show_thresholds":
            return self._handle_show_thresholds(entities)
        elif intent == "check_scaling":
            return self._handle_check_scaling(entities)
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

        # Add resource
        if re.search(r'(resource.*add|add.*resource|リソース追加|リソース作成|create.*resource)', lower_msg):
            entities['resource_type'] = self._extract_resource_type(message)
            entities['resource_name'] = self._extract_name(message)
            entities['capacity'] = self._extract_capacity(message)
            entities['environment'] = self._extract_environment(message)
            return "add_resource", entities

        # List resources
        if re.search(r'(resource.*list|list.*resource|リソース一覧|リソース表示|show.*resource)', lower_msg):
            entities['resource_type'] = self._extract_resource_type(message)
            entities['environment'] = self._extract_environment(message)
            return "list_resources", entities

        # Update usage
        if re.search(r'(usage.*update|update.*usage|使用量更新|使用量記録|record.*usage)', lower_msg):
            entities['resource_id'] = self._extract_id(message)
            entities['usage_value'] = self._extract_value(message)
            return "update_usage", entities

        # Show usage history
        if re.search(r'(usage.*history|history.*usage|使用量履歴|使用量履歴表示)', lower_msg):
            entities['resource_id'] = self._extract_id(message)
            return "show_usage_history", entities

        # Add scaling event
        if re.search(r'(scaling.*add|add.*scaling|スケーリング追加|スケーリング記録|scale.*event)', lower_msg):
            entities['resource_id'] = self._extract_id(message)
            entities['event_type'] = self._extract_event_type(message)
            entities['from_capacity'] = self._extract_from(message)
            entities['to_capacity'] = self._extract_to(message)
            return "add_scaling_event", entities

        # List scaling events
        if re.search(r'(scaling.*list|list.*scaling|スケーリング一覧|スケーリング表示|show.*scaling)', lower_msg):
            entities['status'] = self._extract_status(message)
            return "list_scaling_events", entities

        # Complete scaling
        if re.search(r'(scaling.*complete|complete.*scaling|スケーリング完了|finish.*scaling)', lower_msg):
            entities['event_id'] = self._extract_id(message)
            return "complete_scaling", entities

        # Add capacity plan
        if re.search(r'(capacity.*plan.*add|add.*capacity.*plan|キャパシティプラン追加|キャパシティ計画|create.*plan)', lower_msg):
            entities['plan_name'] = self._extract_name(message)
            entities['resource_type'] = self._extract_resource_type(message)
            entities['forecast_days'] = self._extract_days(message)
            entities['growth'] = self._extract_growth(message)
            entities['recommended_capacity'] = self._extract_capacity(message)
            entities['estimated_date'] = self._extract_date(message)
            return "add_capacity_plan", entities

        # List capacity plans
        if re.search(r'(capacity.*plan.*list|list.*capacity.*plan|キャパシティプラン一覧|計画一覧|show.*plan)', lower_msg):
            entities['status'] = self._extract_status(message)
            entities['priority'] = self._extract_priority(message)
            return "list_capacity_plans", entities

        # Update capacity plan
        if re.search(r'(capacity.*plan.*update|update.*capacity.*plan|キャパシティプラン更新|計画更新)', lower_msg):
            entities['plan_id'] = self._extract_id(message)
            entities['status'] = self._extract_status(message)
            return "update_capacity_plan", entities

        # Set thresholds
        if re.search(r'(threshold.*set|set.*threshold|しきい値設定|閾値設定)', lower_msg):
            entities['resource_id'] = self._extract_id(message)
            entities['scale_up'] = self._extract_scale_up(message)
            entities['scale_down'] = self._extract_scale_down(message)
            entities['min_capacity'] = self._extract_min(message)
            entities['max_capacity'] = self._extract_max(message)
            entities['auto_scale'] = self._extract_auto_scale(message)
            return "set_thresholds", entities

        # Show thresholds
        if re.search(r'(threshold.*list|list.*threshold|しきい値一覧|閾値一覧|show.*threshold)', lower_msg):
            entities['resource_id'] = self._extract_id(message)
            return "show_thresholds", entities

        # Check scaling
        if re.search(r'(check.*scaling|scale.*check|スケーリング確認|auto.*scale|自動スケール)', lower_msg):
            return "check_scaling", entities

        # Show summary
        if re.search(r'(summary|要約|サマリー|概要|capacity.*summary)', lower_msg):
            return "show_summary", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_resource_type(self, message: str) -> Optional[str]:
        """Extract resource type"""
        types = ['cpu', 'memory', 'storage', 'database', 'server', 'container', 'worker', 'queue']
        lower_msg = message.lower()
        for t in types:
            if t in lower_msg:
                return t
        return None

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

    def _extract_capacity(self, message: str) -> Optional[float]:
        """Extract capacity value"""
        patterns = [
            r'容量[:\s]+([\d.]+)',
            r'capacity[:\s]+([\d.]+)',
            r'(\d+\.?\d*)\s*(gb|mb|gb|cpu|core)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_value(self, message: str) -> Optional[float]:
        """Extract value"""
        patterns = [
            r'値[:\s]+([\d.]+)',
            r'value[:\s]+([\d.]+)',
            r'使用量[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_environment(self, message: str) -> Optional[str]:
        """Extract environment"""
        envs = ['production', 'staging', 'development', 'prod', 'stage', 'dev']
        lower_msg = message.lower()
        for env in envs:
            if env in lower_msg:
                return env
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

    def _extract_event_type(self, message: str) -> str:
        """Extract event type"""
        if re.search(r'(scale.*up|up|増加|拡張)', message.lower()):
            return 'scale_up'
        elif re.search(r'(scale.*down|down|減少|縮小)', message.lower()):
            return 'scale_down'
        return 'scale_up'

    def _extract_from(self, message: str) -> Optional[float]:
        """Extract from value"""
        patterns = [
            r'前[:\s]+([\d.]+)',
            r'from[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_to(self, message: str) -> Optional[float]:
        """Extract to value"""
        patterns = [
            r'後[:\s]+([\d.]+)',
            r'to[:\s]+([\d.]+)',
            r'目標[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_status(self, message: str) -> Optional[str]:
        """Extract status"""
        status_map = {
            'pending': 'pending',
            'completed': 'completed',
            'planned': 'planned',
            'active': 'active',
            'in_progress': 'in_progress',
            '保留中': 'pending',
            '完了': 'completed',
            '計画中': 'planned',
            'アクティブ': 'active',
            '実行中': 'in_progress',
        }
        lower_msg = message.lower()
        for key, value in status_map.items():
            if key in lower_msg:
                return value
        return None

    def _extract_days(self, message: str) -> int:
        """Extract days"""
        match = re.search(r'(\d+)\s*(day|日)', message, re.IGNORECASE)
        return int(match.group(1)) if match else 30

    def _extract_growth(self, message: str) -> Optional[float]:
        """Extract growth percentage"""
        match = re.search(r'成長[:\s]+([\d.]+)%', message, re.IGNORECASE)
        return float(match.group(1)) if match else None

    def _extract_date(self, message: str) -> Optional[str]:
        """Extract date"""
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'日付[:\s]+([^\s,]+)',
            r'date[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_priority(self, message: str) -> Optional[str]:
        """Extract priority"""
        priorities = ['high', 'medium', 'low', 'high', '中', '低']
        lower_msg = message.lower()
        for p in priorities:
            if p in lower_msg:
                return 'high' if p == 'high' or p == '高' else ('medium' if p == 'medium' or p == '中' else 'low')
        return None

    def _extract_scale_up(self, message: str) -> Optional[float]:
        """Extract scale up threshold"""
        patterns = [
            r'up[:\s]+([\d.]+)%',
            r'増加[:\s]+([\d.]+)%',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_scale_down(self, message: str) -> Optional[float]:
        """Extract scale down threshold"""
        patterns = [
            r'down[:\s]+([\d.]+)%',
            r'減少[:\s]+([\d.]+)%',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_min(self, message: str) -> Optional[float]:
        """Extract minimum capacity"""
        patterns = [
            r'min[:\s]+([\d.]+)',
            r'最小[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_max(self, message: str) -> Optional[float]:
        """Extract maximum capacity"""
        patterns = [
            r'max[:\s]+([\d.]+)',
            r'最大[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_auto_scale(self, message: str) -> bool:
        """Extract auto scale flag"""
        return bool(re.search(r'(auto|自動)', message.lower()))

    # Handlers

    def _handle_add_resource(self, entities: Dict) -> str:
        """Handle adding resource"""
        resource_type = entities.get('resource_type')
        resource_name = entities.get('resource_name')
        capacity = entities.get('capacity')

        if not resource_type or not resource_name or capacity is None:
            return "リソースタイプ、名前、容量を指定してください。例: リソース追加 タイプ:CPU 名前:server-1 容量:100"

        resource_id = self.db.add_resource(
            resource_type=resource_type,
            resource_name=resource_name,
            capacity=capacity,
            environment=entities.get('environment', 'production')
        )

        return f"✅ リソースを追加しました (ID: {resource_id})\nタイプ: {resource_type}\n名前: {resource_name}\n容量: {capacity}"

    def _handle_list_resources(self, entities: Dict) -> str:
        """Handle listing resources"""
        resources = self.db.get_resources(
            resource_type=entities.get('resource_type'),
            environment=entities.get('environment')
        )

        if not resources:
            return "リソースが見つかりません"

        response = f"📦 **リソース一覧** ({len(resources)}件):\n\n"
        for r in resources:
            util = r['utilization_percent'] or 0
            status_icon = "🟢" if r['status'] == 'active' else "🔴"
            response += f"{status_icon} #{r['id']} {r['resource_name']} ({r['resource_type']})\n"
            response += f"   容量: {r['capacity']} | 使用量: {r['current_usage']} | 利用率: {util:.1f}%\n\n"

        return response

    def _handle_update_usage(self, entities: Dict) -> str:
        """Handle updating usage"""
        resource_id = entities.get('resource_id')
        usage_value = entities.get('usage_value')

        if not resource_id or usage_value is None:
            return "リソースIDと使用量を指定してください"

        success = self.db.update_resource_usage(resource_id, usage_value)
        if success:
            return f"✅ リソース {resource_id} の使用量を更新しました: {usage_value}"
        else:
            return "更新に失敗しました"

    def _handle_show_usage_history(self, entities: Dict) -> str:
        """Handle showing usage history"""
        resource_id = entities.get('resource_id')

        if not resource_id:
            return "リソースIDを指定してください"

        history = self.db.get_usage_history(resource_id, limit=20)

        if not history:
            return f"リソース {resource_id} の使用量履歴が見つかりません"

        response = f"📊 **使用量履歴** (リソース #{resource_id}):\n\n"
        for h in history[:10]:
            response += f"• {h['usage_value']} - {h['timestamp']}\n"
            if h['notes']:
                response += f"  ({h['notes']})\n"

        if len(history) > 10:
            response += f"\n...他 {len(history) - 10}件"

        return response

    def _handle_add_scaling_event(self, entities: Dict) -> str:
        """Handle adding scaling event"""
        resource_id = entities.get('resource_id')
        event_type = entities.get('event_type', 'scale_up')

        if not resource_id:
            return "リソースIDを指定してください"

        event_id = self.db.add_scaling_event(
            resource_id=resource_id,
            event_type=event_type,
            from_capacity=entities.get('from_capacity'),
            to_capacity=entities.get('to_capacity')
        )

        return f"✅ スケーリングイベントを追加しました (ID: {event_id})\nタイプ: {event_type}"

    def _handle_list_scaling_events(self, entities: Dict) -> str:
        """Handle listing scaling events"""
        events = self.db.get_scaling_events(status=entities.get('status'))

        if not events:
            return "スケーリングイベントが見つかりません"

        type_icons = {'scale_up': '📈', 'scale_down': '📉'}
        status_icons = {'pending': '⏳', 'completed': '✅', 'failed': '❌'}

        response = f"📊 **スケーリングイベント一覧** ({len(events)}件):\n\n"
        for e in events:
            type_icon = type_icons.get(e['event_type'], '📊')
            status_icon = status_icons.get(e['status'], '📌')
            response += f"{type_icon} #{e['id']} {e['event_type']} - {status_icon}\n"

            if e['from_capacity'] and e['to_capacity']:
                response += f"   {e['from_capacity']} → {e['to_capacity']}\n"

            if e['reason']:
                response += f"   理由: {e['reason']}\n"

            response += f"   {e['created_at']}\n\n"

        return response

    def _handle_complete_scaling(self, entities: Dict) -> str:
        """Handle completing scaling"""
        event_id = entities.get('event_id')

        if not event_id:
            return "イベントIDを指定してください"

        self.db.complete_scaling_event(event_id)
        return f"✅ スケーリングイベント {event_id} を完了しました"

    def _handle_add_capacity_plan(self, entities: Dict) -> str:
        """Handle adding capacity plan"""
        plan_name = entities.get('plan_name')
        resource_type = entities.get('resource_type')

        if not plan_name:
            return "プラン名を指定してください"

        plan_id = self.db.add_capacity_plan(
            plan_name=plan_name,
            resource_type=resource_type,
            forecast_period_days=entities.get('forecast_days', 30),
            projected_growth=entities.get('growth'),
            recommended_capacity=entities.get('recommended_capacity'),
            estimated_date=entities.get('estimated_date')
        )

        return f"✅ キャパシティプランを追加しました (ID: {plan_id})\n名前: {plan_name}"

    def _handle_list_capacity_plans(self, entities: Dict) -> str:
        """Handle listing capacity plans"""
        plans = self.db.get_capacity_plans(
            status=entities.get('status'),
            priority=entities.get('priority')
        )

        if not plans:
            return "キャパシティプランが見つかりません"

        priority_icons = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        status_icons = {'planned': '📝', 'in_progress': '🔄', 'completed': '✅'}

        response = f"📋 **キャパシティプラン一覧** ({len(plans)}件):\n\n"
        for p in plans:
            priority_icon = priority_icons.get(p['priority'], '📌')
            status_icon = status_icons.get(p['status'], '📌')
            response += f"{priority_icon} #{p['id']} {p['plan_name']} - {status_icon}\n"

            if p['resource_type']:
                response += f"   リソースタイプ: {p['resource_type']}\n"

            if p['projected_growth']:
                response += f"   予測成長: {p['projected_growth']}%\n"

            if p['recommended_capacity']:
                response += f"   推奨容量: {p['recommended_capacity']}\n"

            if p['estimated_date']:
                response += f"   予定日: {p['estimated_date']}\n"

            response += "\n"

        return response

    def _handle_update_capacity_plan(self, entities: Dict) -> str:
        """Handle updating capacity plan"""
        plan_id = entities.get('plan_id')

        if not plan_id:
            return "プランIDを指定してください"

        success = self.db.update_capacity_plan(
            plan_id=plan_id,
            status=entities.get('status'),
            recommended_capacity=entities.get('recommended_capacity')
        )

        if success:
            return f"✅ キャパシティプラン {plan_id} を更新しました"
        else:
            return "更新に失敗しました"

    def _handle_set_thresholds(self, entities: Dict) -> str:
        """Handle setting thresholds"""
        resource_id = entities.get('resource_id')

        if not resource_id:
            return "リソースIDを指定してください"

        self.db.set_thresholds(
            resource_id=resource_id,
            scale_up_threshold=entities.get('scale_up'),
            scale_down_threshold=entities.get('scale_down'),
            min_capacity=entities.get('min_capacity'),
            max_capacity=entities.get('max_capacity'),
            auto_scale_enabled=entities.get('auto_scale', False)
        )

        return f"✅ リソース {resource_id} のしきい値を設定しました"

    def _handle_show_thresholds(self, entities: Dict) -> str:
        """Handle showing thresholds"""
        resource_id = entities.get('resource_id')
        thresholds = self.db.get_thresholds(resource_id)

        if not thresholds:
            if resource_id:
                return f"リソース {resource_id} のしきい値設定が見つかりません"
            else:
                return "しきい値設定が見つかりません"

        response = f"⚡ **しきい値設定** ({len(thresholds)}件):\n\n"
        for t in thresholds:
            auto_status = "🟢 有効" if t['auto_scale_enabled'] == 1 else "🔴 無効"
            response += f"リソース #{t['resource_id']}\n"
            response += f"   スケールアップ: {t['scale_up_threshold']}%\n"
            response += f"   スケールダウン: {t['scale_down_threshold']}%\n"
            if t['min_capacity']:
                response += f"   最小容量: {t['min_capacity']}\n"
            if t['max_capacity']:
                response += f"   最大容量: {t['max_capacity']}\n"
            response += f"   自動スケール: {auto_status}\n\n"

        return response

    def _handle_check_scaling(self, entities: Dict) -> str:
        """Handle checking scaling triggers"""
        triggers = self.db.check_scale_triggers()

        if not triggers:
            return "✅ スケーリングが必要なリソースはありません"

        response = f"⚠️ **スケーリングが必要なリソース** ({len(triggers)}件):\n\n"
        for t in triggers:
            action_icon = "📈" if t['action'] == 'scale_up' else "📉"
            response += f"{action_icon} #{t['resource_id']} {t['resource_name']}\n"
            response += f"   アクション: {t['action']}\n"
            response += f"   現在の利用率: {t['current_utilization']:.1f}% (しきい値: {t['threshold']}%)\n"
            response += f"   推奨容量: {t['recommended_capacity']}\n\n"

        return response

    def _handle_show_summary(self, entities: Dict) -> str:
        """Handle showing summary"""
        summary = self.db.get_capacity_summary()

        response = f"📊 **キャパシティサマリー**\n\n"
        response += f"総リソース数: {summary['total_resources']}件\n"
        response += f"総容量: {summary['total_capacity']}\n"
        response += f"総使用量: {summary['total_usage']}\n"
        response += f"平均利用率: {summary['average_utilization']:.1f}%\n"
        response += f"保留中のスケーリング: {summary['pending_scaling_events']}件\n"
        response += f"アクティブなプラン: {summary['active_capacity_plans']}件"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
📊 **Scale Agent ヘルプ**

**リソース管理:**
• リソース追加 タイプ:CPU 名前:server-1 容量:100
• リソース一覧
• 使用量更新 ID:1 値:50
• 使用量履歴 ID:1

**スケーリング:**
• スケーリング追加 ID:1 スケールアップ 前:100 後:150
• スケーリング一覧
• スケーリング完了 ID:1
• スケーリング確認

**キャパシティプラン:**
• キャパシティプラン追加 名前:Q4 Plan タイプ:CPU 成長:20%
• キャパシティプラン一覧
• キャパシティプラン更新 ID:1 ステータス:完了

**しきい値設定:**
• しきい値設定 ID:1 up:80% down:30% 最小:50 最大:200 自動:オン

**サマリー:**
• サマリー表示

**English support:**
• Add resource type: CPU name: server-1 capacity: 100
• List resources
• Update usage ID:1 value: 50
• Show usage history ID:1
• Add scaling event ID:1 scale up from: 100 to: 150
• Check scaling triggers
• Show summary
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return "すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = ScaleDiscord(":memory:")

    # Test adding resource
    print("--- Add Resource ---")
    print(agent.process_message("リソース追加 タイプ:CPU 名前:server-1 容量:100"))

    # Test listing resources
    print("\n--- List Resources ---")
    print(agent.process_message("リソース一覧"))

    # Test adding capacity plan
    print("\n--- Add Capacity Plan ---")
    print(agent.process_message("キャパシティプラン追加 名前:Q4 Plan タイプ:CPU 成長:20%"))

    # Test showing summary
    print("\n--- Summary ---")
    print(agent.process_message("サマリー表示"))
