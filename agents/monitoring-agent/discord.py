"""
Monitoring Agent Discord Module
Natural language processing for system monitoring commands
"""

import re
from db import MonitoringDB
from typing import Optional, Dict, List


class MonitoringDiscord:
    """Discord interface for monitoring agent with NLP"""

    def __init__(self, db_path: str = "monitoring.db"):
        self.db = MonitoringDB(db_path)

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip().lower()

        # Parse intent and entities
        intent, entities = self._parse_intent(message)

        # Route to appropriate handler
        if intent == "record_metric":
            return self._handle_record_metric(entities)
        elif intent == "get_metrics":
            return self._handle_get_metrics(entities)
        elif intent == "create_alert":
            return self._handle_create_alert(entities)
        elif intent == "get_alerts":
            return self._handle_get_alerts(entities)
        elif intent == "resolve_alert":
            return self._handle_resolve_alert(entities)
        elif intent == "log_performance":
            return self._handle_log_performance(entities)
        elif intent == "get_performance":
            return self._handle_get_performance(entities)
        elif intent == "set_threshold":
            return self._handle_set_threshold(entities)
        elif intent == "check_thresholds":
            return self._handle_check_thresholds(entities)
        elif intent == "list":
            return self._handle_list(entities)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_unknown(message)

    def _parse_intent(self, message: str) -> tuple:
        """Parse intent and entities from message"""
        entities = {}

        # Metric recording patterns
        if re.search(r'(記録|記録して|記録する|record|log|add.*metric)', message):
            entities['metric_name'] = self._extract_metric_name(message)
            entities['value'] = self._extract_value(message)
            entities['unit'] = self._extract_unit(message)
            entities['source'] = self._extract_source(message) or "user"
            return "record_metric", entities

        # Get metrics patterns
        if re.search(r'(メトリクス|指標|metrics|get.*metric|show.*metric)', message):
            entities['metric_name'] = self._extract_metric_name(message)
            entities['limit'] = self._extract_limit(message) or 10
            return "get_metrics", entities

        # Create alert patterns
        if re.search(r'(アラート|警告|alert|create.*alert|raise.*alert)', message):
            entities['alert_type'] = self._extract_alert_type(message)
            entities['severity'] = self._extract_severity(message)
            entities['message'] = self._extract_alert_message(message)
            entities['source'] = self._extract_source(message)
            return "create_alert", entities

        # Get alerts patterns
        if re.search(r'(アラート一覧|警告一覧|アラート表示|alerts|show.*alert|list.*alert)', message):
            entities['resolved'] = self._extract_resolved(message)
            entities['severity'] = self._extract_severity(message)
            return "get_alerts", entities

        # Resolve alert patterns
        if re.search(r'(解決|解決する|resolve|resolve.*alert)', message):
            entities['alert_id'] = self._extract_id(message)
            return "resolve_alert", entities

        # Log performance patterns
        if re.search(r'(パフォーマンス|performance|log.*perf|record.*perf)', message):
            entities['service_name'] = self._extract_service_name(message)
            entities['response_time'] = self._extract_value(message)
            entities['status_code'] = self._extract_status_code(message)
            entities['success'] = not re.search(r'(失敗|エラー|error|failed)', message)
            entities['error_message'] = self._extract_error_message(message)
            return "log_performance", entities

        # Get performance logs patterns
        if re.search(r'(パフォーマンスログ|perf.*log|show.*perf|get.*perf)', message):
            entities['service_name'] = self._extract_service_name(message)
            entities['limit'] = self._extract_limit(message) or 10
            return "get_performance", entities

        # Set threshold patterns
        if re.search(r'(閾値|しきい値|threshold|set.*threshold|define.*threshold)', message):
            entities['metric_name'] = self._extract_metric_name(message)
            entities['warning'] = self._extract_warning(message)
            entities['critical'] = self._extract_critical(message)
            return "set_threshold", entities

        # Check thresholds patterns
        if re.search(r'(閾値チェック|しきい値チェック|threshold.*check|check.*threshold)', message):
            return "check_thresholds", entities

        # List patterns
        if re.search(r'(一覧|リスト|list|show.*all)', message):
            return "list", entities

        # Help patterns
        if re.search(r'(ヘルプ|使い方|help|使い道|使い方教えて)', message):
            return "help", entities

        return "unknown", entities

    def _extract_metric_name(self, message: str) -> Optional[str]:
        """Extract metric name from message"""
        patterns = [
            r'メトリクス[:\s]+([^\s,]+)',
            r'指標[:\s]+([^\s,]+)',
            r'metric[:\s]+([^\s,]+)',
            r'([^,\s]+)\s*(?:is|was|現在)'
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_value(self, message: str) -> Optional[float]:
        """Extract numeric value from message"""
        match = re.search(r'(\d+\.?\d*)', message)
        return float(match.group(1)) if match else None

    def _extract_unit(self, message: str) -> Optional[str]:
        """Extract unit from message"""
        patterns = [
            r'([a-zA-Z]+)(?:で|at)?$',  # e.g., "ms", "CPU"
            r'(パーセント|%|percent)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_source(self, message: str) -> Optional[str]:
        """Extract source from message"""
        patterns = [
            r'ソース[:\s]+([^\s,]+)',
            r'from\s+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_alert_type(self, message: str) -> Optional[str]:
        """Extract alert type from message"""
        patterns = [
            r'タイプ[:\s]+([^\s,]+)',
            r'type[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return "custom"

    def _extract_severity(self, message: str) -> Optional[str]:
        """Extract severity from message"""
        severity_map = {
            '情報': 'info', 'info': 'info',
            '警告': 'warning', 'warn': 'warning',
            'エラー': 'error', 'error': 'error',
            '重大': 'critical', 'critical': 'critical', 'crucial': 'critical'
        }
        for key, value in severity_map.items():
            if key in message:
                return value
        return 'info'

    def _extract_alert_message(self, message: str) -> str:
        """Extract alert message from message"""
        # Remove command keywords and extract the message part
        cleaned = re.sub(r'(アラート|警告|alert|create.*alert)', '', message, flags=re.IGNORECASE)
        cleaned = re.sub(r'(タイプ|type|重要度|severity|info|warning|error|critical)', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip() or "アラートが発生しました"

    def _extract_resolved(self, message: str) -> Optional[bool]:
        """Extract resolved filter from message"""
        if re.search(r'(解決済み|resolved|closed)', message):
            return True
        if re.search(r'(未解決|open|active|pending)', message):
            return False
        return None

    def _extract_id(self, message: str) -> Optional[int]:
        """Extract ID from message"""
        match = re.search(r'(\d+)', message)
        return int(match.group(1)) if match else None

    def _extract_service_name(self, message: str) -> Optional[str]:
        """Extract service name from message"""
        patterns = [
            r'サービス[:\s]+([^\s,]+)',
            r'service[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_status_code(self, message: str) -> Optional[int]:
        """Extract HTTP status code from message"""
        patterns = [
            r'ステータス[:\s]+(\d+)',
            r'status[:\s]+(\d+)',
            r'status[:\s]+code[:\s]+(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_error_message(self, message: str) -> Optional[str]:
        """Extract error message from message"""
        patterns = [
            r'エラー[:\s]+(.+?)(?:\n|$)',
            r'error[:\s]+(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_warning(self, message: str) -> Optional[float]:
        """Extract warning threshold value"""
        patterns = [
            r'警告[:\s]+(\d+\.?\d*)',
            r'warning[:\s]+(\d+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_critical(self, message: str) -> Optional[float]:
        """Extract critical threshold value"""
        patterns = [
            r'重大[:\s]+(\d+\.?\d*)',
            r'critical[:\s]+(\d+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_limit(self, message: str) -> Optional[int]:
        """Extract limit value"""
        patterns = [
            r'(\d+)個',
            r'last\s+(\d+)',
            r'latest\s+(\d+)',
            r'top\s+(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    # Handler methods

    def _handle_record_metric(self, entities: Dict) -> str:
        """Handle metric recording"""
        if not entities.get('metric_name') or entities.get('value') is None:
            return "メトリクス名と値を指定してください。例: CPU使用率50%を記録"

        metric_id = self.db.record_metric(
            metric_name=entities['metric_name'],
            value=entities['value'],
            unit=entities.get('unit'),
            source=entities.get('source', 'user')
        )
        return f"✅ メトリクスを記録しました (ID: {metric_id})"

    def _handle_get_metrics(self, entities: Dict) -> str:
        """Handle get metrics"""
        metrics = self.db.get_metrics(
            metric_name=entities.get('metric_name'),
            limit=entities.get('limit', 10)
        )

        if not metrics:
            return "メトリクスが見つかりません"

        response = f"📊 メトリクス ({len(metrics)}件):\n"
        for m in metrics:
            unit = f" {m['unit']}" if m['unit'] else ""
            response += f"  • {m['metric_name']}: {m['value']}{unit} ({m['timestamp']})\n"
        return response

    def _handle_create_alert(self, entities: Dict) -> str:
        """Handle alert creation"""
        alert_id = self.db.create_alert(
            alert_type=entities.get('alert_type', 'custom'),
            severity=entities.get('severity', 'info'),
            message=entities.get('message', 'アラートが発生しました'),
            source=entities.get('source')
        )
        return f"🚨 アラートを作成しました (ID: {alert_id})"

    def _handle_get_alerts(self, entities: Dict) -> str:
        """Handle get alerts"""
        alerts = self.db.get_alerts(
            resolved=entities.get('resolved'),
            severity=entities.get('severity')
        )

        if not alerts:
            return "アラートが見つかりません"

        response = f"🚨 アラート ({len(alerts)}件):\n"
        for a in alerts:
            status = "✅ 解決済み" if a['resolved'] else "🔴 未解決"
            severity_icon = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'critical': '💀'}.get(a['severity'], '📢')
            response += f"  {status} [{severity_icon} {a['severity']}] ID:{a['id']} - {a['message']} ({a['created_at']})\n"
        return response

    def _handle_resolve_alert(self, entities: Dict) -> str:
        """Handle alert resolution"""
        if not entities.get('alert_id'):
            return "アラートIDを指定してください。例: アラート123を解決"

        success = self.db.resolve_alert(entities['alert_id'])
        if success:
            return f"✅ アラート {entities['alert_id']} を解決済みにしました"
        else:
            return f"❌ アラート {entities['alert_id']} が見つかりません"

    def _handle_log_performance(self, entities: Dict) -> str:
        """Handle performance logging"""
        if not entities.get('service_name'):
            return "サービス名を指定してください。例: APIのパフォーマンスを記録"

        log_id = self.db.log_performance(
            service_name=entities['service_name'],
            response_time=entities.get('response_time'),
            status_code=entities.get('status_code'),
            success=entities.get('success', True),
            error_message=entities.get('error_message')
        )
        status = "成功" if entities.get('success', True) else "失敗"
        return f"📈 パフォーマンスログを記録しました (ID: {log_id}, ステータス: {status})"

    def _handle_get_performance(self, entities: Dict) -> str:
        """Handle get performance logs"""
        logs = self.db.get_performance_logs(
            service_name=entities.get('service_name'),
            limit=entities.get('limit', 10)
        )

        if not logs:
            return "パフォーマンスログが見つかりません"

        response = f"📈 パフォーマンスログ ({len(logs)}件):\n"
        for log in logs:
            status_icon = "✅" if log['success'] else "❌"
            rt = f", {log['response_time']:.0f}ms" if log['response_time'] else ""
            sc = f", ステータス{log['status_code']}" if log['status_code'] else ""
            response += f"  {status_icon} {log['service_name']}{rt}{sc} ({log['timestamp']})\n"
        return response

    def _handle_set_threshold(self, entities: Dict) -> str:
        """Handle threshold setting"""
        if not entities.get('metric_name'):
            return "メトリクス名を指定してください。例: CPUの閾値を警告80、重大90に設定"

        threshold_id = self.db.set_threshold(
            metric_name=entities['metric_name'],
            warning=entities.get('warning'),
            critical=entities.get('critical')
        )
        return f"⚙️ 閾値を設定しました (ID: {threshold_id})"

    def _handle_check_thresholds(self, entities: Dict) -> str:
        """Handle threshold checking"""
        results = self.db.check_thresholds()

        if not results:
            return "閾値設定が見つかりません"

        response = f"🔍 閾値チェック:\n"
        for r in results:
            current = r.get('current_value', 'N/A')
            warning = r.get('warning_threshold', 'N/A')
            critical = r.get('critical_threshold', 'N/A')
            status = "✅ 正常"
            if critical != 'N/A' and current != 'N/A' and current >= critical:
                status = "💀 重大"
            elif warning != 'N/A' and current != 'N/A' and current >= warning:
                status = "⚠️ 警告"
            response += f"  {status} {r['metric_name']}: {current} (警告: {warning}, 重大: {critical})\n"
        return response

    def _handle_list(self, entities: Dict) -> str:
        """Handle list command"""
        return self._handle_help()

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
📊 **Monitoring Agent ヘルプ**

**メトリクス管理:**
• メトリクスを記録 - CPU使用率50%を記録
• メトリクスを表示 - CPUのメトリクスを表示

**アラート管理:**
• アラートを作成 - アラートを作成 高いCPU usage 重要度error
• アラート一覧 - 未解決のアラートを表示
• アラートを解決 - アラート123を解決

**パフォーマンス監視:**
• パフォーマンスを記録 - APIのパフォーマンスを記録 200ms
• パフォーマンスログを表示 - APIのパフォーマンスを表示

**閾値管理:**
• 閾値を設定 - CPUの閾値を警告80、重大90に設定
• 閾値をチェック - 現在の閾値をチェック

**English support:**
• Record CPU usage 50%
• Show CPU metrics
• Create alert high CPU usage severity warning
• Show unresolved alerts
• Check thresholds
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return f"すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = MonitoringDiscord(":memory:")

    # Test metric recording
    print(agent.process_message("CPU使用率50%を記録"))
    print(agent.process_message("メモリ使用率 60% を記録"))

    # Test getting metrics
    print(agent.process_message("CPUのメトリクスを表示"))

    # Test alert creation
    print(agent.process_message("アラートを作成 高いCPU usage 重要度error"))

    # Test getting alerts
    print(agent.process_message("アラート一覧"))

    # Test performance logging
    print(agent.process_message("APIのパフォーマンスを記録 200ms"))

    # Test setting threshold
    print(agent.process_message("CPUの閾値を警告80、重大90に設定"))

    # Test checking thresholds
    print(agent.process_message("閾値をチェック"))

    # Test help
    print(agent.process_message("ヘルプ"))
