#!/usr/bin/env python3
"""
Webhook Agent - Discord連携 (Webhook URL Management & Event Logging)
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # Webhook追加
    add_match = re.match(r'(?:webhook|フック|フック追加)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Webhook一覧
    list_match = re.match(r'(?:(?:webhook|フック)(?:一覧|list)|list_webhooks)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 有効Webhook一覧
    if message.strip() in ['有効webhook', 'active_webhooks', 'enabled_webhooks']:
        return {'action': 'list_enabled'}

    # タイプ別一覧
    type_match = re.match(r'(?:webhook|フック)(?:一覧|list)[:：]\s*(discord|slack|telegram|custom|generic)', message, re.IGNORECASE)
    if type_match:
        return {'action': 'list_type', 'webhook_type': type_match.group(1).lower()}

    # Webhook詳細
    detail_match = re.match(r'(?:詳細|detail|show)[:：]\s*(\d+)', message, re.IGNORECASE)
    if detail_match:
        return {'action': 'detail', 'webhook_id': int(detail_match.group(1))}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'webhook_id': int(delete_match.group(1))}

    # 有効/無効切り替え
    toggle_match = re.match(r'(?:切り替え|toggle|enable|disable)[:：]\s*(\d+)', message, re.IGNORECASE)
    if toggle_match:
        return {'action': 'toggle', 'webhook_id': int(toggle_match.group(1))}

    # イベント履歴
    history_match = re.match(r'(?:履歴|history|log)[:：]?\s*(\d+)?', message, re.IGNORECASE)
    if history_match:
        limit = int(history_match.group(1)) if history_match.group(1) else 10
        return {'action': 'history', 'limit': limit}

    # 特定Webhookの履歴
    webhook_history_match = re.match(r'(?:履歴|history|log)[:：]?\s*webhook[:：]?\s*(\d+)', message, re.IGNORECASE)
    if webhook_history_match:
        return {'action': 'webhook_history', 'webhook_id': int(webhook_history_match.group(1))}

    # 統計
    stats_match = re.match(r'(?:統計|stats|statistics)[:：]?\s*(\d+)?(日|days?)?', message, re.IGNORECASE)
    if stats_match:
        days = 7  # デフォルト7日
        if stats_match.group(1):
            try:
                days = int(stats_match.group(1))
            except:
                pass
        return {'action': 'stats', 'days': days}

    # 接続テスト
    test_match = re.match(r'(?:テスト|test|ping)[:：]?\s*(\d+)?', message, re.IGNORECASE)
    if test_match:
        if test_match.group(1):
            return {'action': 'test', 'webhook_id': int(test_match.group(1))}
        return {'action': 'test_all'}

    # 古いイベント削除
    cleanup_match = re.match(r'(?:クリーンアップ|cleanup|cleanup_events)[:：]?\s*(\d+)?', message, re.IGNORECASE)
    if cleanup_match:
        days = int(cleanup_match.group(1)) if cleanup_match.group(1) else 30
        return {'action': 'cleanup', 'days': days}

    # Webhook更新
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+),\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return parse_update(int(update_match.group(1)), update_match.group(2))

    # サマリー
    if message.strip() in ['サマリー', 'summary', 'overview']:
        return {'action': 'summary'}

    return None

def parse_add(content):
    """Webhook追加を解析"""
    result = {'action': 'add', 'name': None, 'url': None, 'webhook_type': 'generic',
              'description': None, 'secret': None, 'enabled': 1, 'rate_limit': 60,
              'timeout_seconds': 10, 'headers': None}

    # URL (http/httpsで始まるもの)
    url_match = re.search(r'(https?://[^\s,，]+)', content)
    if url_match:
        result['url'] = url_match.group(1).strip()

    # Webhookタイプ
    type_match = re.search(r'タイプ[:：]\s*(discord|slack|telegram|custom|generic)', content, re.IGNORECASE)
    if type_match:
        result['webhook_type'] = type_match.group(1).lower()

    # URLからタイプを推測
    if not type_match and result['url']:
        if 'discord.com' in result['url'] or 'discordapp.com' in result['url']:
            result['webhook_type'] = 'discord'
        elif 'hooks.slack.com' in result['url']:
            result['webhook_type'] = 'slack'
        elif 'api.telegram.org' in result['url']:
            result['webhook_type'] = 'telegram'

    # 名前 (URLより前の部分)
    if result['url']:
        url_pos = content.find(result['url'])
        if url_pos > 0:
            result['name'] = content[:url_pos].strip(' ,，')
    else:
        result['name'] = content.strip()

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # シークレット/トークン
    secret_match = re.search(r'(?:secret|token|シークレット|トークン)[:：]\s*(\S+)', content, re.IGNORECASE)
    if secret_match:
        result['secret'] = secret_match.group(1)

    # レート制限
    rate_match = re.search(r'(?:rate_limit|レート)[:：]\s*(\d+)', content, re.IGNORECASE)
    if rate_match:
        result['rate_limit'] = int(rate_match.group(1))

    # タイムアウト
    timeout_match = re.search(r'(?:timeout|タイムアウト)[:：]\s*(\d+)', content, re.IGNORECASE)
    if timeout_match:
        result['timeout_seconds'] = int(timeout_match.group(1))

    # 無効フラグ
    if re.search(r'(?:disabled|無効)', content, re.IGNORECASE):
        result['enabled'] = 0

    return result

def parse_update(webhook_id, content):
    """Webhook更新を解析"""
    result = {'action': 'update', 'webhook_id': webhook_id}

    # URL
    url_match = re.search(r'(https?://[^\s,，]+)', content)
    if url_match:
        result['url'] = url_match.group(1).strip()

    # タイプ
    type_match = re.search(r'タイプ[:：]\s*(discord|slack|telegram|custom|generic)', content, re.IGNORECASE)
    if type_match:
        result['webhook_type'] = type_match.group(1).lower()

    # 名前
    name_match = re.search(r'名前[:：]\s*([^,，]+)', content, re.IGNORECASE)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # シークレット
    secret_match = re.search(r'(?:secret|token|シークレット|トークン)[:：]\s*(\S+)', content, re.IGNORECASE)
    if secret_match:
        result['secret'] = secret_match.group(1)

    # レート制限
    rate_match = re.search(r'(?:rate_limit|レート)[:：]\s*(\d+)', content, re.IGNORECASE)
    if rate_match:
        result['rate_limit'] = int(rate_match.group(1))

    # タイムアウト
    timeout_match = re.search(r'(?:timeout|タイムアウト)[:：]\s*(\d+)', content, re.IGNORECASE)
    if timeout_match:
        result['timeout_seconds'] = int(timeout_match.group(1))

    # 有効/無効
    if re.search(r'(?:enable|有効)', content, re.IGNORECASE):
        result['enabled'] = 1
    elif re.search(r'(?:disable|無効)', content, re.IGNORECASE):
        result['enabled'] = 0

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['url']:
            return "❌ Webhook URLを入力してください (https://... の形式)"

        webhook_id = add_webhook(
            parsed['name'] or 'Unnamed Webhook',
            parsed['url'],
            parsed['webhook_type'],
            parsed['description'],
            parsed['secret'],
            parsed['enabled'],
            parsed['rate_limit'],
            parsed['timeout_seconds'],
            parsed['headers']
        )

        response = f"✅ Webhook #{webhook_id} 追加完了\n"
        response += f"名前: {parsed['name'] or 'Unnamed Webhook'}\n"
        response += f"URL: {parsed['url']}\n"
        if parsed['webhook_type'] != 'generic':
            response += f"タイプ: {parsed['webhook_type']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['rate_limit'] != 60:
            response += f"レート制限: {parsed['rate_limit']}/分\n"
        if parsed['timeout_seconds'] != 10:
            response += f"タイムアウト: {parsed['timeout_seconds']}秒\n"
        response += f"状態: {'有効' if parsed['enabled'] else '無効'}"

        return response

    elif action == 'list':
        webhooks = list_webhooks()

        if not webhooks:
            return "📋 Webhookが登録されていません"

        response = f"📋 Webhook一覧 ({len(webhooks)}件):\n"
        for webhook in webhooks:
            response += format_webhook(webhook)

        return response

    elif action == 'list_enabled':
        webhooks = list_webhooks(enabled_only=True)

        if not webhooks:
            return "📋 有効なWebhookはありません"

        response = f"📋 有効なWebhook ({len(webhooks)}件):\n"
        for webhook in webhooks:
            response += format_webhook(webhook)

        return response

    elif action == 'list_type':
        webhooks = list_webhooks(webhook_type=parsed['webhook_type'])

        if not webhooks:
            return f"📋 {parsed['webhook_type']} タイプのWebhookはありません"

        response = f"📋 {parsed['webhook_type']} Webhook一覧 ({len(webhooks)}件):\n"
        for webhook in webhooks:
            response += format_webhook(webhook)

        return response

    elif action == 'detail':
        webhook = get_webhook(parsed['webhook_id'])

        if not webhook:
            return f"❌ Webhook #{parsed['webhook_id']} が見つかりません"

        return format_webhook_detail(webhook)

    elif action == 'history':
        limit = parsed.get('limit', 10)
        events = get_webhook_events(limit=limit)

        if not events:
            return "📜 イベント履歴がありません"

        response = f"📜 イベント履歴 (直近{limit}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'webhook_history':
        events = get_webhook_events(webhook_id=parsed['webhook_id'], limit=20)

        if not events:
            return f"📜 Webhook #{parsed['webhook_id']} のイベント履歴はありません"

        webhook = get_webhook(parsed['webhook_id'])
        webhook_name = webhook[1] if webhook else "Unknown"

        response = f"📜 {webhook_name} (#{parsed['webhook_id']}) の履歴:\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'delete':
        delete_webhook(parsed['webhook_id'])
        return f"🗑️ Webhook #{parsed['webhook_id']} 削除完了"

    elif action == 'toggle':
        toggle_webhook(parsed['webhook_id'])
        return f"🔄 Webhook #{parsed['webhook_id']} 有効/無効切り替え"

    elif action == 'update':
        webhook_id = parsed.pop('webhook_id')
        success = update_webhook(webhook_id, **parsed)

        if success:
            return f"✅ Webhook #{webhook_id} 更新完了"
        else:
            return f"❌ Webhook #{webhook_id} の更新に失敗しました"

    elif action == 'stats':
        days = parsed.get('days', 7)
        stats = get_webhook_stats(days=days)

        if not stats:
            return f"📊 過去{days}日間の統計データはありません"

        response = f"📊 過去{days}日間の統計:\n"
        response += format_stats(stats)

        return response

    elif action == 'test':
        webhook_id = parsed['webhook_id']
        test_result = test_webhook_connection(webhook_id)

        if test_result['success']:
            response = f"✅ Webhook #{webhook_id} 接続テスト: 成功\n"
            response += f"URL: {test_result['url']}\n"
            response += f"タイプ: {test_result['webhook_type']}\n"
            response += test_result.get('message', 'Valid webhook configuration')
        else:
            response = f"❌ Webhook #{webhook_id} 接続テスト: 失敗\n"
            response += f"エラー: {test_result.get('error', 'Unknown error')}"

        return response

    elif action == 'test_all':
        webhooks = list_webhooks(enabled_only=True)

        if not webhooks:
            return "📋 有効なWebhookがありません"

        response = f"🧪 全Webhook接続テスト:\n"
        for webhook in webhooks:
            webhook_id = webhook[0]
            test_result = test_webhook_connection(webhook_id)

            if test_result['success']:
                response += f"✅ #{webhook_id} {webhook[1]}\n"
            else:
                response += f"❌ #{webhook_id} {webhook[1]} - {test_result.get('error', 'Error')}\n"

        return response

    elif action == 'cleanup':
        days = parsed.get('days', 30)
        deleted_count = cleanup_old_events(days)

        response = f"🧹 クリーンアップ完了\n"
        response += f"削除したイベント: {deleted_count}件\n"
        response += f"対象: {days}日以上前のイベント"

        return response

    elif action == 'summary':
        summary = get_webhook_summary()

        response = "📊 Webhookサマリー:\n"
        response += f"Webhook数: {summary['total_webhooks']}件 (有効: {summary['enabled_webhooks']}件)\n"

        if summary['by_type']:
            response += "\nタイプ別:\n"
            for webhook_type, count in summary['by_type'].items():
                response += f"  • {webhook_type}: {count}件\n"

        response += f"\nイベント: {summary['total_events']}件 (成功: {summary['success_events']} / 失敗: {summary['failed_events']})\n"
        response += f"平均送信時間: {summary['avg_duration_ms']}ms\n"
        response += f"今日のイベント: {summary['today_events']}件"

        if summary['last_event']:
            response += f"\n最後のイベント: {summary['last_event']}"

        return response

    return None

def format_webhook(webhook):
    """Webhookをフォーマット"""
    id, name, url, webhook_type, description, enabled, created_at, updated_at = webhook

    # ステータス表示
    status_icon = "✅" if enabled else "⏸️"

    # タイプアイコン
    type_icons = {
        'discord': '🎮',
        'slack': '💬',
        'telegram': '✈️',
        'custom': '⚙️',
        'generic': '🔗'
    }
    type_icon = type_icons.get(webhook_type, '🔗')

    # URLを短縮表示
    short_url = url[:40] + "..." if len(url) > 40 else url

    response = f"\n{status_icon} [{id}] {type_icon} {name}\n"
    response += f"    URL: {short_url}\n"
    if webhook_type != 'generic':
        response += f"    タイプ: {webhook_type}\n"

    return response

def format_webhook_detail(webhook):
    """Webhook詳細をフォーマット"""
    id, name, url, webhook_type, description, secret, enabled, \
    rate_limit, timeout, headers, created_at, updated_at = webhook

    response = f"📋 Webhook詳細 #{id}:\n"
    response += f"名前: {name}\n"
    response += f"URL: {url}\n"
    response += f"タイプ: {webhook_type}\n"
    if description:
        response += f"説明: {description}\n"
    if secret:
        masked_secret = secret[:4] + "*" * (len(secret) - 8) + secret[-4:] if len(secret) > 8 else "****"
        response += f"シークレット: {masked_secret}\n"
    response += f"レート制限: {rate_limit}/分\n"
    response += f"タイムアウト: {timeout}秒\n"
    if headers:
        import json
        headers_dict = json.loads(headers)
        response += f"ヘッダー: {len(headers_dict)}件設定\n"
    response += f"状態: {'有効' if enabled else '無効'}\n"
    response += f"作成日時: {created_at}\n"
    response += f"更新日時: {updated_at}"

    return response

def format_event(event):
    """イベントをフォーマット"""
    id, webhook_id, webhook_name, event_type, status, duration, success, error, created_at = event

    # ステータス表示
    status_icon = "✅" if success else "❌"

    # ステータスコード
    status_text = f"[{status}]" if status else "[No Response]"

    response = f"{status_icon} [{id}] {webhook_name} - {created_at}\n"
    response += f"    イベント: {event_type}\n"
    response += f"    {status_text}  "
    if duration > 0:
        response += f"時間: {duration}ms"
    response += "\n"
    if error:
        response += f"    エラー: {error}\n"

    return response

def format_stats(stats):
    """統計をフォーマット"""
    from collections import defaultdict

    # 日付・Webhook別に集計
    by_date = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})

    for stat in stats:
        webhook_id, webhook_name, date, total, success, failed, avg_duration = stat
        by_date[date]['total'] += total
        by_date[date]['success'] += success
        by_date[date]['failed'] += failed

    response = ""
    for date in sorted(by_date.keys(), reverse=True):
        data = by_date[date]
        success_rate = (data['success'] / data['total'] * 100) if data['total'] > 0 else 0
        response += f"\n📅 {date}:\n"
        response += f"    合計: {data['total']}件 (成功: {data['success']}, 失敗: {data['failed']})\n"
        response += f"    成功率: {success_rate:.1f}%\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "webhook: discord通知, https://discord.com/api/webhooks/xxx, タイプ: discord",
        "webhook: slack通知, https://hooks.slack.com/services/xxx, タイプ: slack, 説明: エラー通知",
        "webhook: 通知, https://example.com/webhook",
        "list_webhooks",
        "detail: 1",
        "履歴",
        "統計",
        "サマリー",
        "test: 1",
        "toggle: 1",
        "削除: 2",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
