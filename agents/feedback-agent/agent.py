#!/usr/bin/env python3
"""
Feedback Agent - Discord Integration
Natural Language Processing for Feedback Collection and Analysis
"""

import re
from db import *

def parse_message(message):
    """Parse message and determine action"""
    # Add feedback
    add_match = re.match(r'(?:フィードバック|feedback)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add_feedback', 'content': add_match.group(1)}

    # List feedback
    list_match = re.match(r'(?:一覧|list|feedbacks)[：:]?\s*(.+)?', message, re.IGNORECASE)
    if list_match:
        filter_str = list_match.group(1) or ''
        return {'action': 'list_feedback', 'filter': filter_str}

    # View feedback
    view_match = re.match(r'(?:表示|view|show)[：:]\s*フィードバック\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_feedback', 'feedback_id': int(view_match.group(1))}

    # Update feedback
    update_match = re.match(r'(?:更新|update)[：:]\s*フィードバック\s*(\d+)', message, re.IGNORECASE)
    if update_match:
        remaining = message[update_match.end():].strip()
        return {'action': 'update_feedback', 'feedback_id': int(update_match.group(1)), 'content': remaining}

    # Analyze
    analyze_match = re.match(r'(?:分析|analyze|analysis)[：:]?\s*(\d+)?', message, re.IGNORECASE)
    if analyze_match:
        days = int(analyze_match.group(1)) if analyze_match.group(1) else 30
        return {'action': 'analyze', 'days': days}

    # Report
    report_match = re.match(r'(?:レポート|report|generate report)[：:]?\s*(\d+)?', message, re.IGNORECASE)
    if report_match:
        days = int(report_match.group(1)) if report_match.group(1) else 30
        return {'action': 'generate_report', 'days': days}

    # Comment
    comment_match = re.match(r'(?:コメント|comment)[：:]\s*フィードバック\s*(\d+)[：:]\s*(.+)', message, re.IGNORECASE)
    if comment_match:
        return {'action': 'add_comment', 'feedback_id': int(comment_match.group(1)), 'comment': comment_match.group(2)}

    return None

def parse_feedback_content(content, user_id):
    """Parse feedback addition content"""
    result = {'user_id': user_id, 'type': 'other', 'title': None, 'description': None, 'rating': None, 'sentiment': None, 'category': None, 'tags': None}

    # Type
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(bug|feature|improvement|compliment|complaint|other|バグ|機能|改善|称賛|不満|その他)', content, re.IGNORECASE)
    if type_match:
        t = type_match.group(1).lower()
        type_map = {'バグ': 'bug', 'bug': 'bug', '機能': 'feature', 'feature': 'feature', '改善': 'improvement', 'improvement': 'improvement', '称賛': 'compliment', 'compliment': 'compliment', '不満': 'complaint', 'complaint': 'complaint', 'その他': 'other', 'other': 'other'}
        result['type'] = type_map.get(t, 'other')

    # Rating
    rating_match = re.search(r'(?:評価|rating|rate)[：:]\s*(\d)', content, re.IGNORECASE)
    if rating_match:
        result['rating'] = int(rating_match.group(1))

    # Sentiment
    sentiment_match = re.search(r'(?:感情|sentiment|positive|negative|neutral|ポジティブ|ネガティブ|ニュートラル)[：:]?\s*(positive|negative|neutral|ポジティブ|ネガティブ|ニュートラル)?', content, re.IGNORECASE)
    if sentiment_match:
        s = sentiment_match.group(1) if sentiment_match.group(1) else sentiment_match.group(0).split(':')[0].strip().lower()
        sentiment_map = {'positive': 'positive', 'ポジティブ': 'positive', 'negative': 'negative', 'ネガティブ': 'negative', 'neutral': 'neutral', 'ニュートラル': 'neutral'}
        result['sentiment'] = sentiment_map.get(s, 'neutral')

    # Category
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,\n]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # Tags
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*([^、,\n]+)', content, re.IGNORECASE)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # Description
    desc_match = re.search(r'(?:説明|description|詳細|detail)[：:]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()
        # Title is before description
        idx = content.find(desc_match.group(0))
        title = content[:idx].strip()
        for key in ['タイプ', 'type', '評価', 'rating', '感情', 'sentiment', 'カテゴリ', 'category', 'タグ', 'tags']:
            match = re.search(rf'{key}[×:：]', title)
            if match:
                title = title[:match.start()].strip()
        result['title'] = title or 'No title'
    else:
        # Everything is the title
        for key in ['タイプ', 'type', '評価', 'rating', '感情', 'sentiment', 'カテゴリ', 'category', 'タグ', 'tags']:
            match = re.search(rf'{key}[×:：]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()
        result['description'] = None

    return result

def parse_feedback_update(content):
    """Parse feedback update content"""
    result = {}

    status_match = re.search(r'(?:ステータス|status)[：:]\s*(new|reviewed|in_progress|resolved|dismissed|新規|確認中|進行中|解決済み|却下)', content, re.IGNORECASE)
    if status_match:
        s = status_match.group(1).lower()
        status_map = {'new': 'new', '新規': 'new', 'reviewed': 'reviewed', '確認中': 'reviewed', 'in_progress': 'in_progress', '進行中': 'in_progress', 'resolved': 'resolved', '解決済み': 'resolved', 'dismissed': 'dismissed', '却下': 'dismissed'}
        result['status'] = status_map.get(s)

    sentiment_match = re.search(r'(?:感情|sentiment)[：:]\s*(positive|negative|neutral|ポジティブ|ネガティブ|ニュートラル)', content, re.IGNORECASE)
    if sentiment_match:
        s = sentiment_match.group(1).lower()
        sentiment_map = {'positive': 'positive', 'ポジティブ': 'positive', 'negative': 'negative', 'ネガティブ': 'negative', 'neutral': 'neutral', 'ニュートラル': 'neutral'}
        result['sentiment'] = sentiment_map.get(s)

    return result

def parse_feedback_filter(filter_str):
    """Parse feedback list filter"""
    result = {'status': None, 'type': None, 'sentiment': None}

    f = filter_str.lower()

    if 'new' in f or '新規' in f:
        result['status'] = 'new'
    elif 'reviewed' in f or '確認中' in f:
        result['status'] = 'reviewed'
    elif 'in_progress' in f or '進行中' in f:
        result['status'] = 'in_progress'
    elif 'resolved' in f or '解決済み' in f:
        result['status'] = 'resolved'

    if 'bug' in f or 'バグ' in f:
        result['type'] = 'bug'
    elif 'feature' in f or '機能' in f:
        result['type'] = 'feature'
    elif 'compliment' in f or '称賛' in f:
        result['type'] = 'compliment'

    if 'positive' in f or 'ポジティブ' in f:
        result['sentiment'] = 'positive'
    elif 'negative' in f or 'ネガティブ' in f:
        result['sentiment'] = 'negative'

    return result

def process_action(parsed, user_id):
    """Process the parsed action and return response"""
    try:
        if parsed['action'] == 'add_feedback':
            feedback_data = parse_feedback_content(parsed['content'], user_id)
            feedback_id = add_feedback(**feedback_data)
            return {
                'status': 'success',
                'message_ja': f'フィードバック #{feedback_id} を追加しました',
                'message_en': f'Feedback #{feedback_id} added',
                'feedback_id': feedback_id
            }

        elif parsed['action'] == 'list_feedback':
            filters = parse_feedback_filter(parsed['filter'])
            feedback_list = list_feedback(**filters)
            items = '\n'.join([f"#{f[0]}: {f[3]} ({f[2]}, {f[5]})" for f in feedback_list])
            return {
                'status': 'success',
                'message_ja': f'フィードバック一覧:\n{items}',
                'message_en': f'Feedback list:\n{items}'
            }

        elif parsed['action'] == 'view_feedback':
            feedback, comments = get_feedback(parsed['feedback_id'])
            if feedback:
                comments_text = '\n'.join([f"{c[0]}: {c[1]}" for c in comments])
                return {
                    'status': 'success',
                    'message_ja': f'フィードバック #{feedback[0]}: {feedback[3]}\nタイプ: {feedback[2]}\n感情: {feedback[5]}\n評価: {feedback[6]}\n\nコメント:\n{comments_text}',
                    'message_en': f'Feedback #{feedback[0]}: {feedback[3]}\nType: {feedback[2]}\nSentiment: {feedback[5]}\nRating: {feedback[6]}\n\nComments:\n{comments_text}'
                }
            else:
                return {
                    'status': 'not_found',
                    'message_ja': 'フィードバックが見つかりません',
                    'message_en': 'Feedback not found'
                }

        elif parsed['action'] == 'update_feedback':
            update_data = parse_feedback_update(parsed['content'])
            if update_data:
                update_feedback(parsed['feedback_id'], **update_data)
                return {
                    'status': 'success',
                    'message_ja': f'フィードバック #{parsed["feedback_id"]} を更新しました',
                    'message_en': f'Feedback #{parsed["feedback_id"]} updated'
                }
            else:
                return {
                    'status': 'error',
                    'message_ja': '更新内容が無効です',
                    'message_en': 'Invalid update content'
                }

        elif parsed['action'] == 'analyze':
            analysis = analyze_feedback(parsed['days'])
            return {
                'status': 'success',
                'message_ja': f'分析結果 (過去{parsed["days"]}日):\n総数: {analysis["total"]}\n感情分布: {analysis["sentiment_distribution"]}\nタイプ分布: {analysis["type_distribution"]}',
                'message_en': f'Analysis (last {parsed["days"]} days):\nTotal: {analysis["total"]}\nSentiment: {analysis["sentiment_distribution"]}\nType: {analysis["type_distribution"]}',
                'analysis': analysis
            }

        elif parsed['action'] == 'generate_report':
            report_id, analysis = generate_report(parsed['days'])
            return {
                'status': 'success',
                'message_ja': f'レポート #{report_id} を生成しました (過去{parsed["days"]}日)',
                'message_en': f'Report #{report_id} generated (last {parsed["days"]} days)',
                'report_id': report_id,
                'analysis': analysis
            }

        elif parsed['action'] == 'add_comment':
            comment_id = add_comment(parsed['feedback_id'], user_id, parsed['comment'])
            return {
                'status': 'success',
                'message_ja': f'フィードバック #{parsed["feedback_id"]} にコメントを追加しました',
                'message_en': f'Comment added to feedback #{parsed["feedback_id"]}'
            }

        return {
            'status': 'error',
            'message_ja': '不明なアクションです',
            'message_en': 'Unknown action'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message_ja': f'エラーが発生しました: {str(e)}',
            'message_en': f'Error occurred: {str(e)}'
        }

if __name__ == '__main__':
    init_db()
