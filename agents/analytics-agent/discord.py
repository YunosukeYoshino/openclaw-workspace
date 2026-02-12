#!/usr/bin/env python3
"""
Analytics Agent - Discord Integration
"""

import re
from datetime import datetime, timedelta
from db import AnalyticsDB

db = AnalyticsDB()

def parse_message(message):
    """Parse message"""
    # Store data
    store_match = re.match(r'(?:保存|save|store)[:：]\s*(.+)', message, re.IGNORECASE)
    if store_match:
        return parse_store(store_match.group(1))

    # Create report
    report_match = re.match(r'(?:レポート|report)[:：]\s*(.+)', message, re.IGNORECASE)
    if report_match:
        return {'action': 'create_report', 'title': report_match.group(1).strip()}

    # Save visualization
    viz_match = re.match(r'(?:可視化|visualization|viz|chart)[:：]\s*(.+)', message, re.IGNORECASE)
    if viz_match:
        return parse_visualization(viz_match.group(1))

    # List data
    list_data_match = re.match(r'(?:データ一覧|data|list)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_data_match:
        source = list_data_match.group(1) if list_data_match.group(1) else None
        return {'action': 'list_data', 'source': source}

    # List reports
    if message.strip() in ['レポート一覧', 'reports']:
        return {'action': 'list_reports'}

    # List visualizations
    if message.strip() in ['可視化一覧', 'visualizations', 'charts']:
        return {'action': 'list_visualizations'}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_store(content):
    """Parse store content"""
    result = {'action': 'store', 'source': None, 'data_type': None, 'data': {}, 'tags': None}

    # Source
    source_match = re.search(r'ソース|source[:：]\s*(.+?)(?:[,，]|$)', content)
    if source_match:
        result['source'] = source_match.group(1).strip()

    # Data type
    type_match = re.search(r'タイプ|type[:：]\s*(.+?)(?:[,，]|$)', content)
    if type_match:
        result['data_type'] = type_match.group(1).strip()

    # Tags
    tags_match = re.search(r'タグ|tags[:：]\s*(.+)', content)
    if tags_match:
        result['tags'] = [t.strip() for t in tags_match.group(1).split(',')]

    # Data (everything else)
    if not result['source']:
        parts = content.split(',')
        if parts:
            result['source'] = parts[0].strip()

    return result

def parse_visualization(content):
    """Parse visualization content"""
    result = {'action': 'create_viz', 'title': None, 'chart_type': None, 'data': {}}

    # Title
    title_match = re.match(r'^([^,、]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # Chart type
    chart_match = re.search(r'(?:タイプ|type|chart)[:：]\s*(.+?)(?:[,，]|$)', content)
    if chart_match:
        result['chart_type'] = chart_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'store':
        data_id = db.store_data(
            parsed.get('source') or 'manual',
            parsed.get('data_type') or 'custom',
            parsed.get('data', {}),
            parsed.get('tags')
        )

        response = f"✅ データ #{data_id} 保存完了\n"
        response += f"ソース: {parsed.get('source', 'manual')}\n"
        if parsed.get('data_type'):
            response += f"タイプ: {parsed['data_type']}"
        if parsed.get('tags'):
            response += f"\nタグ: {', '.join(parsed['tags'])}"

        return response

    elif action == 'create_report':
        import json
        report_id = db.create_report(
            parsed['title'],
            json.dumps({'generated_at': datetime.now().isoformat()}),
            f"Report created on {datetime.now().strftime('%Y-%m-%d')}"
        )

        return f"✅ レポート #{report_id} 作成完了: {parsed['title']}"

    elif action == 'create_viz':
        import json
        viz_id = db.save_visualization(
            parsed.get('title') or 'Untitled',
            parsed.get('chart_type') or 'bar',
            parsed.get('data', {}),
            {'created_at': datetime.now().isoformat()}
        )

        return f"✅ 可視化 #{viz_id} 作成完了: {parsed.get('title', 'Untitled')}"

    elif action == 'list_data':
        data_list = db.get_data(source=parsed.get('source'), limit=20)

        if not data_list:
            source_text = f" ({parsed['source']})" if parsed.get('source') else ""
            return f"📊 データ{source_text} がありません"

        source_text = f" ({parsed['source']})" if parsed.get('source') else ""
        response = f"📊 データ一覧{source_text} ({len(data_list)}件):\n"
        for i, item in enumerate(data_list[:10], 1):
            response += f"\n{i}. [{item['id']}] {item['source']} - {item['data_type']}"

        return response

    elif action == 'list_reports':
        reports = db.get_reports()

        if not reports:
            return "📋 レポートがありません"

        response = f"📋 レポート一覧 ({len(reports)}件):\n"
        for i, report in enumerate(reports[:10], 1):
            response += f"\n{i}. [{report['id']}] {report['title']} ({report['status']})"

        return response

    elif action == 'list_visualizations':
        vizs = db.get_visualizations()

        if not vizs:
            return "📈 可視化がありません"

        response = f"📈 可視化一覧 ({len(vizs)}件):\n"
        for i, viz in enumerate(vizs[:10], 1):
            response += f"\n{i}. [{viz['id']}] {viz['title']} ({viz['chart_type']})"

        return response

    elif action == 'stats':
        response = "📊 分析統計:\n"
        response += "データの統計情報はデータベースを確認してください"

        return response

    return None

if __name__ == '__main__':
    db.init_db()

    test_messages = [
        "保存: sales, タイプ:revenue",
        "レポート: Monthly Sales Report",
        "可視化: Sales Chart, タイプ:bar",
        "データ一覧",
        "レポート一覧",
        "可視化一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
