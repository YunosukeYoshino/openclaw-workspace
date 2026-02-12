#!/usr/bin/env python3
"""
天気ログエージェント #61 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 天気ログ追加
    weather_match = re.match(r'(?:天気|weather|weather-log)[：:]\s*(.+)', message, re.IGNORECASE)
    if weather_match:
        return parse_add(weather_match.group(1))

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        parsed = parse_update(update_match.group(2))
        parsed['log_id'] = int(update_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:天気|weather|weather-log)(?:一覧|list)|list|weather-logs)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 日付検索
    date_match = re.match(r'(?:(?:日付|date|日)[：:]\s*(.+)', message, re.IGNORECASE)
    if date_match:
        return {'action': 'by_date', 'date': parse_date(date_match.group(1))}

    # 統計
    if message.strip() in ['統計', 'stats', '天気統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """天気ログ追加を解析"""
    result = {'action': 'add', 'date': None, 'weather': None, 'temperature': None,
              'humidity': None, 'wind_speed': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 天気
    weather_match = re.search(r'(?:天気|weather|晴れ|曇り|雨|雪|雷)[：:]\s*([^、,]+)', content)
    if weather_match:
        result['weather'] = weather_match.group(1).strip()

    # 気温
    temp_match = re.search(r'(?:気温|temperature|temp)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if temp_match:
        result['temperature'] = float(temp_match.group(1))

    # 湿度
    humidity_match = re.search(r'(?:湿度|humidity)[：:]?\s*(\d+)', content)
    if humidity_match:
        result['humidity'] = int(humidity_match.group(1))

    # 風速
    wind_match = re.search(r'(?:風速|wind|風)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if wind_match:
        result['wind_speed'] = float(wind_match.group(1))

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 日付がまだない場合、最初の項目より前を日付とする
    if not result['date']:
        for key in ['日付', 'date', '天気', 'weather', '晴れ', '曇り', '雨', '雪', '雷',
                    '気温', 'temperature', 'temp', '湿度', 'humidity', '風速', 'wind', '風',
                    'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['date'] = content[:match.start()].strip()
                break
        else:
            result['date'] = content.strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {'action': 'update', 'date': None, 'weather': None, 'temperature': None,
              'humidity': None, 'wind_speed': None, 'notes': None}

    # 天気
    weather_match = re.search(r'(?:天気|weather)[：:]\s*([^、,]+)', content)
    if weather_match:
        result['weather'] = weather_match.group(1).strip()

    # 気温
    temp_match = re.search(r'(?:気温|temperature|temp)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if temp_match:
        result['temperature'] = float(temp_match.group(1))

    # 湿度
    humidity_match = re.search(r'(?:湿度|humidity)[：:]?\s*(\d+)', content)
    if humidity_match:
        result['humidity'] = int(humidity_match.group(1))

    # 風速
    wind_match = re.search(r'(?:風速|wind|風)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if wind_match:
        result['wind_speed'] = float(wind_match.group(1))

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 昨日
    if '昨日' in date_str:
        from datetime import timedelta
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    # 数字 + 日前
    days_match = re.match(r'(\d+)日前', date_str)
    if days_match:
        from datetime import timedelta
        days = int(days_match.group(1))
        return (today - timedelta(days=days)).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        log_id = add_log(
            parsed['date'],
            parsed['weather'],
            parsed['temperature'],
            parsed['humidity'],
            parsed['wind_speed'],
            parsed['notes']
        )

        response = f"🌡 天気ログ #{log_id} 追加完了\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['weather']:
            response += f"天気: {parsed['weather']}\n"
        if parsed['temperature']:
            response += f"気温: {parsed['temperature']}°C\n"
        if parsed['humidity']:
            response += f"湿度: {parsed['humidity']}%\n"
        if parsed['wind_speed']:
            response += f"風速: {parsed['wind_speed']}m/s\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update':
        update_log(
            parsed['log_id'],
            date=parsed['date'],
            weather=parsed['weather'],
            temperature=parsed['temperature'],
            humidity=parsed['humidity'],
            wind_speed=parsed['wind_speed'],
            notes=parsed['notes']
        )

        return f"✅ 天気ログ #{parsed['log_id']} 更新完了"

    elif action == 'list':
        logs = list_logs()

        if not logs:
            return "🌡 天気ログがありません"

        response = f"🌡 天気ログ ({len(logs)}件):\n"
        for log in logs:
            response += format_log(log)

        return response

    elif action == 'by_date':
        logs = get_by_date(parsed['date'])

        if not logs:
            return f"🌡 {parsed['date']} の天気ログがありません"

        response = f"🌡 {parsed['date']} の天気ログ ({len(logs)}件):\n"
        for log in logs:
            response += format_log(log)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = f"📊 天気統計:\n"
        response += f"全ログ数: {stats['total']}件\n"

        if stats['avg_temperature']:
            response += f"平均気温: {stats['avg_temperature']:.1f}°C\n"

        if stats['by_weather']:
            response += "\n天気別集計:\n"
            for weather, count in stats['by_weather']:
                response += f"  {weather}: {count}件\n"

        return response

    return None

def format_log(log):
    """天気ログをフォーマット"""
    id, date, weather, temperature, humidity, wind_speed, notes, created_at = log

    # 天気アイコン
    weather_icons = {
        'sunny': '☀️', '晴れ': '☀️', '快晴': '☀️',
        'cloudy': '☁️', '曇り': '☁️', '曇天': '☁️',
        'rain': '🌧', '雨': '🌧', '小雨': '🌦',
        'snow': '❄️', '雪': '❄️',
        'thunder': '⛈', '雷': '⛈',
        'fog': '🌫', '霧': '🌫'
    }

    weather_icon = '🌡'

    for key, icon in weather_icons.items():
        if weather and key.lower() in weather.lower():
            weather_icon = icon
            break

    response = f"{weather_icon} [{id}] {date}"

    parts = []
    if weather:
        parts.append(f"🌡 {weather}")
    if temperature:
        parts.append(f"🌡 {temperature}°C")
    if humidity:
        parts.append(f"💧 {humidity}%")
    if wind_speed:
        parts.append(f"💨 {wind_speed}m/s")

    if parts:
        response += f" - {' '.join(parts)}\n"

    if notes:
        response += f"  📝 {notes[:50]}{'...' if len(notes) > 50 else ''}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "天気: 晴れ, 気温: 22, 湿度: 45",
        "天気: 曇り, 気温: 18, 湿度: 65, 風速: 3.5",
        "天気一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
