#!/usr/bin/env python3
"""
Support Agent - Discord Integration
Natural Language Processing for Customer Support
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """Parse message and determine action"""
    # Create ticket
    add_match = re.match(r'(?:チケット|ticket|問い合わせ|inquiry|support)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'create_ticket', 'content': add_match.group(1)}

    # FAQ search
    faq_match = re.match(r'(?:FAQ|faq|faq検索|faq search)[：:]\s*(.+)', message, re.IGNORECASE)
    if faq_match:
        return {'action': 'search_faq', 'keyword': faq_match.group(1)}

    # Add FAQ
    add_faq_match = re.match(r'(?:FAQ追加|add faq|faq add)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_faq_match:
        return {'action': 'add_faq', 'content': add_faq_match.group(1)}

    # Update ticket
    update_match = re.match(r'(?:更新|update)[：:]\s*チケット\s*(\d+)', message, re.IGNORECASE)
    if update_match:
        remaining = message[update_match.end():].strip()
        return {'action': 'update_ticket', 'ticket_id': int(update_match.group(1)), 'content': remaining}

    # Add response
    response_match = re.match(r'(?:返信|reply|respond)[：:]\s*チケット\s*(\d+)[：:]\s*(.+)', message, re.IGNORECASE)
    if response_match:
        return {'action': 'add_response', 'ticket_id': int(response_match.group(1)), 'message': response_match.group(2)}

    # View ticket
    view_match = re.match(r'(?:表示|view|show)[：:]\s*チケット\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_ticket', 'ticket_id': int(view_match.group(1))}

    # List tickets
    list_match = re.match(r'(?:一覧|list|tickets)[：:]?\s*(.+)?', message, re.IGNORECASE)
    if list_match:
        filter_str = list_match.group(1) or ''
        return {'action': 'list_tickets', 'filter': filter_str}

    # Stats
    if re.match(r'(?:統計|stats|統計情報)', message, re.IGNORECASE):
        return {'action': 'stats'}

    # Close ticket
    close_match = re.match(r'(?:クローズ|close|解決|resolve)[：:]\s*チケット\s*(\d+)', message, re.IGNORECASE)
    if close_match:
        return {'action': 'close_ticket', 'ticket_id': int(close_match.group(1))}

    return None

def parse_ticket_content(content, user_id):
    """Parse ticket creation content"""
    result = {'user_id': user_id, 'subject': None, 'description': None, 'category': None, 'priority': 'normal'}

    # Priority
    priority_match = re.search(r'(?:優先|priority)[：:]\s*(low|normal|high|urgent|低|通常|高|緊急)', content, re.IGNORECASE)
    if priority_match:
        p = priority_match.group(1).lower()
        priority_map = {'low': 'low', '通常': 'normal', 'normal': 'normal', '高': 'high', 'high': 'high', '緊急': 'urgent', 'urgent': 'urgent'}
        result['priority'] = priority_map.get(p, 'normal')

    # Category
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,\n]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # Subject (everything before description or at the start)
    desc_match = re.search(r'(?:説明|description|本文)[：:]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()
        # Subject is before description
        idx = content.find(desc_match.group(0))
        subject = content[:idx].strip()
        for key in ['優先', 'priority', 'カテゴリ', 'category']:
            match = re.search(rf'{key}[×:：]', subject)
            if match:
                subject = subject[:match.start()].strip()
        result['subject'] = subject or 'No subject'
    else:
        # Everything is the subject
        for key in ['優先', 'priority', 'カテゴリ', 'category']:
            match = re.search(rf'{key}[×:：]', content)
            if match:
                result['subject'] = content[:match.start()].strip()
                break
        else:
            result['subject'] = content.strip()
        result['description'] = None

    return result

def parse_faq_content(content):
    """Parse FAQ addition content"""
    result = {'question': None, 'answer': None, 'category': None, 'keywords': None}

    # Category
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,\n]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # Keywords
    keywords_match = re.search(r'(?:キーワード|keywords)[：:]\s*([^、,\n]+)', content, re.IGNORECASE)
    if keywords_match:
        result['keywords'] = keywords_match.group(1).strip()

    # Answer
    answer_match = re.search(r'(?:回答|answer)[：:]\s*(.+)', content, re.IGNORECASE)
    if answer_match:
        result['answer'] = answer_match.group(1).strip()
        # Question is before answer
        idx = content.find(answer_match.group(0))
        question = content[:idx].strip()
        for key in ['カテゴリ', 'category', 'キーワード', 'keywords']:
            match = re.search(rf'{key}[×:：]', question)
            if match:
                question = question[:match.start()].strip()
        result['question'] = question or 'No question'
    else:
        result['answer'] = content.strip()
        result['question'] = 'No question'

    return result

def parse_ticket_update(content):
    """Parse ticket update content"""
    result = {}

    status_match = re.search(r'(?:ステータス|status)[：:]\s*(open|in_progress|resolved|closed|open|進行中|解決済み|クローズ)', content, re.IGNORECASE)
    if status_match:
        s = status_match.group(1).lower()
        status_map = {'open': 'open', '進行中': 'in_progress', 'in_progress': 'in_progress', '解決済み': 'resolved', 'resolved': 'resolved', 'クローズ': 'closed', 'closed': 'closed'}
        result['status'] = status_map.get(s)

    priority_match = re.search(r'(?:優先|priority)[：:]\s*(low|normal|high|urgent|低|通常|高|緊急)', content, re.IGNORECASE)
    if priority_match:
        p = priority_match.group(1).lower()
        priority_map = {'low': 'low', '通常': 'normal', 'normal': 'normal', '高': 'high', 'high': 'high', '緊急': 'urgent', 'urgent': 'urgent'}
        result['priority'] = priority_map.get(p, 'normal')

    assigned_match = re.search(r'(?:担当|assign|assigned_to)[：:]\s*(.+)', content, re.IGNORECASE)
    if assigned_match:
        result['assigned_to'] = assigned_match.group(1).strip()

    return result

def process_action(parsed, user_id):
    """Process the parsed action and return response"""
    try:
        if parsed['action'] == 'create_ticket':
            ticket_data = parse_ticket_content(parsed['content'], user_id)
            ticket_id = create_ticket(**ticket_data)
            return {
                'status': 'success',
                'message_ja': f'チケット #{ticket_id} を作成しました',
                'message_en': f'Ticket #{ticket_id} created',
                'ticket_id': ticket_id
            }

        elif parsed['action'] == 'search_faq':
            faqs = search_faqs(parsed['keyword'])
            if faqs:
                faq_list = '\n'.join([f"Q: {q[1]}\nA: {q[2][:100]}..." for q in faqs])
                return {
                    'status': 'success',
                    'message_ja': f'FAQ検索結果:\n{faq_list}',
                    'message_en': f'FAQ results:\n{faq_list}',
                    'faqs': faqs
                }
            else:
                return {
                    'status': 'not_found',
                    'message_ja': '該当するFAQが見つかりませんでした',
                    'message_en': 'No matching FAQ found'
                }

        elif parsed['action'] == 'add_faq':
            faq_data = parse_faq_content(parsed['content'])
            faq_id = add_faq(**faq_data)
            return {
                'status': 'success',
                'message_ja': f'FAQ #{faq_id} を追加しました',
                'message_en': f'FAQ #{faq_id} added',
                'faq_id': faq_id
            }

        elif parsed['action'] == 'update_ticket':
            update_data = parse_ticket_update(parsed['content'])
            if update_data:
                update_ticket(parsed['ticket_id'], **update_data)
                return {
                    'status': 'success',
                    'message_ja': f'チケット #{parsed["ticket_id"]} を更新しました',
                    'message_en': f'Ticket #{parsed["ticket_id"]} updated'
                }
            else:
                return {
                    'status': 'error',
                    'message_ja': '更新内容が無効です',
                    'message_en': 'Invalid update content'
                }

        elif parsed['action'] == 'add_response':
            response_id = add_response(parsed['ticket_id'], user_id, parsed['message'])
            return {
                'status': 'success',
                'message_ja': f'チケット #{parsed["ticket_id"]} に返信を追加しました',
                'message_en': f'Reply added to ticket #{parsed["ticket_id"]}'
            }

        elif parsed['action'] == 'view_ticket':
            ticket, responses = get_ticket(parsed['ticket_id'])
            if ticket:
                resp_text = '\n'.join([f"{r[0]}: {r[1]}" for r in responses])
                return {
                    'status': 'success',
                    'message_ja': f'チケット #{ticket[0]}: {ticket[2]}\nステータス: {ticket[3]}\n優先度: {ticket[4]}\n\n返信:\n{resp_text}',
                    'message_en': f'Ticket #{ticket[0]}: {ticket[2]}\nStatus: {ticket[3]}\nPriority: {ticket[4]}\n\nReplies:\n{resp_text}'
                }
            else:
                return {
                    'status': 'not_found',
                    'message_ja': 'チケットが見つかりません',
                    'message_en': 'Ticket not found'
                }

        elif parsed['action'] == 'list_tickets':
            status = None
            priority = None
            f = parsed['filter'].lower()

            if 'open' in f or 'オープン' in f or '未解決' in f:
                status = 'open'
            elif 'resolved' in f or '解決' in f:
                status = 'resolved'
            elif 'high' in f or '高' in f:
                priority = 'high'
            elif 'urgent' in f or '緊急' in f:
                priority = 'urgent'

            tickets = list_tickets(status=status, priority=priority)
            ticket_list = '\n'.join([f"#{t[0]}: {t[2]} ({t[3]}, {t[4]})" for t in tickets])
            return {
                'status': 'success',
                'message_ja': f'チケット一覧:\n{ticket_list}',
                'message_en': f'Ticket list:\n{ticket_list}'
            }

        elif parsed['action'] == 'close_ticket':
            update_ticket(parsed['ticket_id'], status='resolved')
            return {
                'status': 'success',
                'message_ja': f'チケット #{parsed["ticket_id"]} を解決済みにしました',
                'message_en': f'Ticket #{parsed["ticket_id"]} marked as resolved'
            }

        elif parsed['action'] == 'stats':
            stats = get_stats()
            return {
                'status': 'success',
                'message_ja': f'統計: ステータス={stats["status_counts"]}, 優先度={stats["priority_counts"]}, FAQ数={stats["total_faqs"]}',
                'message_en': f'Stats: Status={stats["status_counts"]}, Priority={stats["priority_counts"]}, FAQs={stats["total_faqs"]}',
                'stats': stats
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
