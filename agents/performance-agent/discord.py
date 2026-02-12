"""
Performance Agent Discord Module
Natural language processing for performance metrics and optimization management
"""

import re
from typing import Optional, Dict, List
from db import PerformanceDB


class PerformanceDiscord:
    """Discord interface for performance agent with NLP"""

    def __init__(self, db_path: str = "performance.db"):
        self.db = PerformanceDB(db_path)

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "add_metric":
            return self._handle_add_metric(entities)
        elif intent == "list_metrics":
            return self._handle_list_metrics(entities)
        elif intent == "show_trend":
            return self._handle_show_trend(entities)
        elif intent == "add_benchmark":
            return self._handle_add_benchmark(entities)
        elif intent == "list_benchmarks":
            return self._handle_list_benchmarks(entities)
        elif intent == "update_benchmark":
            return self._handle_update_benchmark(entities)
        elif intent == "add_optimization":
            return self._handle_add_optimization(entities)
        elif intent == "list_optimizations":
            return self._handle_list_optimizations(entities)
        elif intent == "update_optimization":
            return self._handle_update_optimization(entities)
        elif intent == "add_alert":
            return self._handle_add_alert(entities)
        elif intent == "list_alerts":
            return self._handle_list_alerts(entities)
        elif intent == "resolve_alert":
            return self._handle_resolve_alert(entities)
        elif intent == "add_report":
            return self._handle_add_report(entities)
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

        # Add metric
        if re.search(r'(metric.*add|add.*metric|メトリクス追加|メトリクス記録|パフォーマンス記録|add.*performance)', lower_msg):
            entities['metric_name'] = self._extract_metric_name(message)
            entities['metric_value'] = self._extract_value(message)
            entities['unit'] = self._extract_unit(message)
            entities['component'] = self._extract_component(message)
            entities['environment'] = self._extract_environment(message)
            return "add_metric", entities

        # List metrics
        if re.search(r'(metric.*list|list.*metric|メトリクス一覧|メトリクス表示|show.*metrics)', lower_msg):
            entities['metric_name'] = self._extract_metric_name(message)
            entities['component'] = self._extract_component(message)
            return "list_metrics", entities

        # Show trend
        if re.search(r'(trend|トレンド|傾向|推移|chart|グラフ)', lower_msg):
            entities['metric_name'] = self._extract_metric_name(message)
            entities['hours'] = self._extract_hours(message)
            return "show_trend", entities

        # Add benchmark
        if re.search(r'(benchmark.*add|add.*benchmark|ベンチマーク追加|ベンチマーク作成|create.*benchmark)', lower_msg):
            entities['benchmark_name'] = self._extract_name(message)
            entities['benchmark_type'] = self._extract_type(message)
            entities['baseline'] = self._extract_value(message)
            entities['target'] = self._extract_target(message)
            entities['unit'] = self._extract_unit(message)
            return "add_benchmark", entities

        # List benchmarks
        if re.search(r'(benchmark.*list|list.*benchmark|ベンチマーク一覧|ベンチマーク表示|show.*benchmark)', lower_msg):
            entities['benchmark_type'] = self._extract_type(message)
            entities['status'] = self._extract_status(message)
            return "list_benchmarks", entities

        # Update benchmark
        if re.search(r'(benchmark.*update|update.*benchmark|ベンチマーク更新|ベンチマーク実行|run.*benchmark)', lower_msg):
            entities['benchmark_id'] = self._extract_id(message)
            entities['current_value'] = self._extract_value(message)
            entities['status'] = self._extract_status(message)
            return "update_benchmark", entities

        # Add optimization
        if re.search(r'(optimization.*add|add.*optimization|最適化追加|最適化作成|改善計画|create.*optimization)', lower_msg):
            entities['optimization_name'] = self._extract_name(message)
            entities['component'] = self._extract_component(message)
            entities['before_value'] = self._extract_before(message)
            entities['after_value'] = self._extract_after(message)
            entities['unit'] = self._extract_unit(message)
            return "add_optimization", entities

        # List optimizations
        if re.search(r'(optimization.*list|list.*optimization|最適化一覧|最適化表示|show.*optimization|改善.*一覧)', lower_msg):
            entities['status'] = self._extract_status(message)
            return "list_optimizations", entities

        # Update optimization
        if re.search(r'(optimization.*update|update.*optimization|最適化更新|最適化完了|complete.*optimization)', lower_msg):
            entities['opt_id'] = self._extract_id(message)
            entities['after_value'] = self._extract_after(message)
            entities['status'] = self._extract_status(message)
            return "update_optimization", entities

        # Add alert
        if re.search(r'(alert.*add|add.*alert|アラート追加|アラート作成|create.*alert)', lower_msg):
            entities['alert_type'] = self._extract_type(message)
            entities['severity'] = self._extract_severity(message)
            entities['metric_name'] = self._extract_metric_name(message)
            entities['threshold'] = self._extract_value(message)
            return "add_alert", entities

        # List alerts
        if re.search(r'(alert.*list|list.*alert|アラート一覧|アラート表示|show.*alert)', lower_msg):
            entities['severity'] = self._extract_severity(message)
            return "list_alerts", entities

        # Resolve alert
        if re.search(r'(alert.*resolve|resolve.*alert|アラート解決|アラート完了|close.*alert)', lower_msg):
            entities['alert_id'] = self._extract_id(message)
            return "resolve_alert", entities

        # Add report
        if re.search(r'(report.*add|add.*report|レポート追加|レポート作成|generate.*report)', lower_msg):
            entities['report_name'] = self._extract_name(message)
            entities['report_type'] = self._extract_type(message)
            return "add_report", entities

        # Show summary
        if re.search(r'(summary|要約|サマリー|概要|summary.*performance)', lower_msg):
            return "show_summary", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_metric_name(self, message: str) -> Optional[str]:
        """Extract metric name"""
        patterns = [
            r'メトリクス[:\s]+([^\s,]+)',
            r'metric[:\s]+([^\s,]+)',
            r'指標[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_value(self, message: str) -> Optional[float]:
        """Extract numeric value"""
        patterns = [
            r'値[:\s]+([\d.]+)',
            r'value[:\s]+([\d.]+)',
            r'(\d+\.?\d*)\s*(ms|s|mb|%)?$',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_target(self, message: str) -> Optional[float]:
        """Extract target value"""
        patterns = [
            r'目標[:\s]+([\d.]+)',
            r'target[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_unit(self, message: str) -> Optional[str]:
        """Extract unit"""
        patterns = [
            r'単位[:\s]+([^\s,]+)',
            r'unit[:\s]+([^\s,]+)',
            r'(ms|s|mb|gb|%|requests|bytes)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_component(self, message: str) -> Optional[str]:
        """Extract component name"""
        patterns = [
            r'コンポーネント[:\s]+([^\s,]+)',
            r'component[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_environment(self, message: str) -> Optional[str]:
        """Extract environment"""
        envs = ['production', 'staging', 'development', 'prod', 'stage', 'dev']
        lower_msg = message.lower()
        for env in envs:
            if env in lower_msg:
                return env
        return 'production'

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

    def _extract_type(self, message: str) -> Optional[str]:
        """Extract type"""
        patterns = [
            r'タイプ[:\s]+([^\s,]+)',
            r'type[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_before(self, message: str) -> Optional[float]:
        """Extract before value"""
        patterns = [
            r'前[:\s]+([\d.]+)',
            r'before[:\s]+([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_after(self, message: str) -> Optional[float]:
        """Extract after value"""
        patterns = [
            r'後[:\s]+([\d.]+)',
            r'after[:\s]+([\d.]+)',
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
            'active': 'active',
            'completed': 'completed',
            'planned': 'planned',
            'in_progress': 'in_progress',
            'failed': 'failed',
            '保留': 'pending',
            '有効': 'active',
            '完了': 'completed',
            '計画中': 'planned',
            '実行中': 'in_progress',
            '失敗': 'failed',
        }
        lower_msg = message.lower()
        for key, value in status_map.items():
            if key in lower_msg:
                return value
        return None

    def _extract_severity(self, message: str) -> Optional[str]:
        """Extract severity"""
        severity_map = {
            'info': 'info',
            'warning': 'warning',
            'error': 'error',
            'critical': 'critical',
            '情報': 'info',
            '警告': 'warning',
            'エラー': 'error',
            '重大': 'critical',
        }
        lower_msg = message.lower()
        for key, value in severity_map.items():
            if key in lower_msg:
                return value
        return 'warning'

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

    def _extract_hours(self, message: str) -> int:
        """Extract hours"""
        match = re.search(r'(\d+)\s*(hour|時間|h)', message, re.IGNORECASE)
        return int(match.group(1)) if match else 24

    # Handlers

    def _handle_add_metric(self, entities: Dict) -> str:
        """Handle adding metric"""
        metric_name = entities.get('metric_name')
        metric_value = entities.get('metric_value')

        if not metric_name or metric_value is None:
            return "メトリクス名と値を指定してください。例: メトリクス追加 メトリクス:response_time 値:150"

        metric_id = self.db.add_metric(
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=entities.get('unit'),
            component=entities.get('component'),
            environment=entities.get('environment', 'production')
        )

        return f"✅ メトリクスを記録しました (ID: {metric_id})\n名前: {metric_name}\n値: {metric_value}"

    def _handle_list_metrics(self, entities: Dict) -> str:
        """Handle listing metrics"""
        metrics = self.db.get_metrics(
            metric_name=entities.get('metric_name'),
            component=entities.get('component'),
            limit=30
        )

        if not metrics:
            return "メトリクスが見つかりません"

        response = f"📊 **メトリクス一覧** ({len(metrics)}件):\n\n"
        for m in metrics[:15]:
            unit = f" {m['metric_unit']}" if m['metric_unit'] else ""
            response += f"• {m['metric_name']}: {m['metric_value']}{unit}"
            if m['component']:
                response += f" ({m['component']})"
            response += f" - {m['timestamp']}\n"

        if len(metrics) > 15:
            response += f"\n...他 {len(metrics) - 15}件"

        return response

    def _handle_show_trend(self, entities: Dict) -> str:
        """Handle showing trend"""
        metric_name = entities.get('metric_name')

        if not metric_name:
            return "メトリクス名を指定してください"

        hours = entities.get('hours', 24)
        trends = self.db.get_metric_trend(metric_name, hours)

        if not trends:
            return f"{metric_name} のトレンドデータが見つかりません"

        if len(trends) < 2:
            return "トレンドを表示するには最低2つのデータポイントが必要です"

        # Calculate change
        first_val = trends[0]['metric_value']
        last_val = trends[-1]['metric_value']
        change = ((last_val - first_val) / first_val) * 100 if first_val != 0 else 0
        trend_icon = "📈" if change >= 0 else "📉"

        response = f"{trend_icon} **{metric_name} トレンド** (過去{hours}時間)\n\n"
        response += f"開始: {first_val}\n"
        response += f"終了: {last_val}\n"
        response += f"変化: {change:+.1f}%\n\n"
        response += f"データポイント: {len(trends)}件"

        return response

    def _handle_add_benchmark(self, entities: Dict) -> str:
        """Handle adding benchmark"""
        benchmark_name = entities.get('benchmark_name')
        benchmark_type = entities.get('benchmark_type')

        if not benchmark_name or not benchmark_type:
            return "ベンチマーク名とタイプを指定してください"

        benchmark_id = self.db.add_benchmark(
            benchmark_name=benchmark_name,
            benchmark_type=benchmark_type,
            baseline_value=entities.get('baseline'),
            target_value=entities.get('target'),
            unit=entities.get('unit')
        )

        return f"✅ ベンチマークを追加しました (ID: {benchmark_id})\n名前: {benchmark_name}\nタイプ: {benchmark_type}"

    def _handle_list_benchmarks(self, entities: Dict) -> str:
        """Handle listing benchmarks"""
        benchmarks = self.db.get_benchmarks(
            benchmark_type=entities.get('benchmark_type'),
            status=entities.get('status')
        )

        if not benchmarks:
            return "ベンチマークが見つかりません"

        status_icons = {'pending': '⏳', 'active': '🔄', 'completed': '✅', 'failed': '❌'}

        response = f"🎯 **ベンチマーク一覧** ({len(benchmarks)}件):\n\n"
        for b in benchmarks:
            icon = status_icons.get(b['status'], '📌')
            unit = f" {b['unit']}" if b['unit'] else ""
            target = f" / 目標: {b['target_value']}{unit}" if b['target_value'] else ""
            current = f"現在: {b['current_value']}{unit}" if b['current_value'] else "未実行"
            response += f"{icon} #{b['id']} {b['benchmark_name']} ({b['benchmark_type']})\n"
            response += f"   {current}{target}\n\n"

        return response

    def _handle_update_benchmark(self, entities: Dict) -> str:
        """Handle updating benchmark"""
        benchmark_id = entities.get('benchmark_id')

        if not benchmark_id:
            return "ベンチマークIDを指定してください"

        success = self.db.update_benchmark(
            benchmark_id=benchmark_id,
            current_value=entities.get('current_value'),
            status=entities.get('status')
        )

        if success:
            return f"✅ ベンチマーク {benchmark_id} を更新しました"
        else:
            return "更新に失敗しました"

    def _handle_add_optimization(self, entities: Dict) -> str:
        """Handle adding optimization"""
        optimization_name = entities.get('optimization_name')

        if not optimization_name:
            return "最適化名を指定してください"

        opt_id = self.db.add_optimization(
            optimization_name=optimization_name,
            component=entities.get('component'),
            before_value=entities.get('before_value'),
            after_value=entities.get('after_value'),
            unit=entities.get('unit'),
            status=entities.get('status', 'planned')
        )

        return f"✅ 最適化を追加しました (ID: {opt_id})\n名前: {optimization_name}"

    def _handle_list_optimizations(self, entities: Dict) -> str:
        """Handle listing optimizations"""
        optimizations = self.db.get_optimizations(status=entities.get('status'))

        if not optimizations:
            return "最適化が見つかりません"

        status_icons = {'planned': '📝', 'in_progress': '🔄', 'completed': '✅', 'failed': '❌'}
        status_labels = {'planned': '計画中', 'in_progress': '実行中', 'completed': '完了', 'failed': '失敗'}

        response = f"⚡ **最適化一覧** ({len(optimizations)}件):\n\n"
        for o in optimizations:
            icon = status_icons.get(o['status'], '📌')
            status_label = status_labels.get(o['status'], o['status'])
            response += f"{icon} #{o['id']} {o['optimization_name']} - {status_label}\n"

            if o['component']:
                response += f"   コンポーネント: {o['component']}\n"

            if o['before_value']:
                unit = f" {o['unit']}" if o['unit'] else ""
                response += f"   変化: {o['before_value']}{unit}"
                if o['after_value']:
                    response += f" → {o['after_value']}{unit}"
                    if o['improvement_percent']:
                        response += f" ({o['improvement_percent']:+.1f}%)"
                response += "\n"

            response += "\n"

        return response

    def _handle_update_optimization(self, entities: Dict) -> str:
        """Handle updating optimization"""
        opt_id = entities.get('opt_id')

        if not opt_id:
            return "最適化IDを指定してください"

        success = self.db.update_optimization(
            opt_id=opt_id,
            after_value=entities.get('after_value'),
            status=entities.get('status')
        )

        if success:
            return f"✅ 最適化 {opt_id} を更新しました"
        else:
            return "更新に失敗しました"

    def _handle_add_alert(self, entities: Dict) -> str:
        """Handle adding alert"""
        alert_type = entities.get('alert_type')

        if not alert_type:
            return "アラートタイプを指定してください"

        alert_id = self.db.add_alert(
            alert_type=alert_type,
            severity=entities.get('severity', 'warning'),
            metric_name=entities.get('metric_name'),
            threshold=entities.get('threshold'),
            message=entities.get('message')
        )

        return f"🚨 アラートを追加しました (ID: {alert_id})\nタイプ: {alert_type}"

    def _handle_list_alerts(self, entities: Dict) -> str:
        """Handle listing alerts"""
        resolved = None
        if '未解決' in entities.values() or 'unresolved' in [str(v).lower() for v in entities.values()]:
            resolved = False
        elif '解決済み' in entities.values() or 'resolved' in [str(v).lower() for v in entities.values()]:
            resolved = True

        alerts = self.db.get_alerts(resolved=resolved, severity=entities.get('severity'))

        if not alerts:
            return "アラートが見つかりません"

        severity_icons = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'critical': '💀'}
        response = f"🚨 **アラート一覧** ({len(alerts)}件):\n\n"
        for a in alerts:
            icon = severity_icons.get(a['severity'], '🚨')
            status = "✓解決済み" if a['resolved'] == 1 else "⏳未解決"
            response += f"{icon} #{a['id']} {a['alert_type']} ({status})\n"
            if a['message']:
                response += f"   {a['message']}\n"
            response += f"   {a['created_at']}\n\n"

        return response

    def _handle_resolve_alert(self, entities: Dict) -> str:
        """Handle resolving alert"""
        alert_id = entities.get('alert_id')

        if not alert_id:
            return "アラートIDを指定してください"

        self.db.resolve_alert(alert_id)
        return f"✅ アラート {alert_id} を解決済みにしました"

    def _handle_add_report(self, entities: Dict) -> str:
        """Handle adding report"""
        report_name = entities.get('report_name')
        report_type = entities.get('report_type')

        if not report_name or not report_type:
            return "レポート名とタイプを指定してください"

        report_id = self.db.add_report(
            report_name=report_name,
            report_type=report_type,
            start_date=entities.get('start_date'),
            end_date=entities.get('end_date'),
            summary=entities.get('summary'),
            insights=entities.get('insights')
        )

        return f"📊 レポートを追加しました (ID: {report_id})\n名前: {report_name}\nタイプ: {report_type}"

    def _handle_show_summary(self, entities: Dict) -> str:
        """Handle showing summary"""
        summary = self.db.get_performance_summary()

        response = f"📊 **パフォーマンスサマリー**\n\n"
        response += f"総メトリクス数: {summary['total_metrics']}件\n"
        response += f"アクティブなベンチマーク: {summary['active_benchmarks']}件\n"
        response += f"完了した最適化: {summary['completed_optimizations']}件\n"

        if summary['average_improvement']:
            response += f"平均改善率: {summary['average_improvement']:.1f}%\n"

        response += f"未解決のアラート: {summary['unresolved_alerts']}件"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
📊 **Performance Agent ヘルプ**

**メトリクス管理:**
• メトリクス追加 メトリクス:response_time 値:150 単位:ms
• メトリクス一覧
• response_timeのトレンドを表示

**ベンチマーク:**
• ベンチマーク追加 名前:API Response タイプ:response_time 目標:100
• ベンチマーク一覧
• ベンチマーク更新 ID:1 値:120

**最適化:**
• 最適化追加 名前:DBインデックス 前:500 後:200
• 最適化一覧
• 最適化更新 ID:1 後:200 ステータス:完了

**アラート:**
• アラート追加 タイプ:high_response 重要度:警告
• アラート一覧
• アラート解決 ID:1

**サマリー:**
• サマリー表示

**English support:**
• Add metric metric: response_time value: 150 unit: ms
• List metrics
• Show trend for response_time
• Add benchmark name: API Response type: response_time target: 100
• List benchmarks
• Show summary
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return "すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = PerformanceDiscord(":memory:")

    # Test adding metric
    print("--- Add Metric ---")
    print(agent.process_message("メトリクス追加 メトリクス:response_time 値:150 単位:ms"))

    # Test listing metrics
    print("\n--- List Metrics ---")
    print(agent.process_message("メトリクス一覧"))

    # Test adding benchmark
    print("\n--- Add Benchmark ---")
    print(agent.process_message("ベンチマーク追加 名前:API Response タイプ:response_time 目標:100"))

    # Test showing summary
    print("\n--- Summary ---")
    print(agent.process_message("サマリー表示"))
