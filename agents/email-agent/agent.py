#!/usr/bin/env python3
"""
Email Agent - Natural Language Processing
Supports Japanese and English
"""

import re
from db import *

def detect_language(message):
    """言語を検出 / Detect language"""
    jp_keywords = ['メール', '未読', '重要', '自動返信', '連絡先']
    en_keywords = ['email', 'unread', 'important', 'auto reply', 'contact']

    message_lower = message.lower()
    jp_score = sum(1 for kw in jp_keywords if kw in message)
    en_score = sum(1 for kw in en_keywords if kw in message_lower)
    return 'jp' if jp_score >= en_score else 'en'

def parse_message(message, lang=None):
    """メッセージを解析 / Parse message"""
    lang = lang or detect_language(message)
    message_lower = message.lower()

    # Add email (メール追加)
    if lang == 'jp':
        email_match = re.match(r'(?:メール|email)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        email_match = re.match(r'(?:email|add email)[:：]\s*(.+)', message, re.IGNORECASE)

    if email_match:
        return parse_add_email(email_match.group(1), lang)

    # List emails (メール一覧)
    for kw in ['メール', 'emails', 'list emails', 'inbox']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_emails'}

    # List unread (未読メール)
    for kw in ['未読メール', 'unread', 'unread emails']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_unread'}

    # List important (重要メール)
    for kw in ['重要メール', 'important', 'important emails']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_important'}

    # Mark as read (既読にする)
    if lang == 'jp':
        read_match = re.match(r'(?:既読|mark read|read)[:：]\s*(\d+)', message)
    else:
        read_match = re.match(r'(?:mark read|read)[:：]\s*(\d+)', message, re.IGNORECASE)

    if read_match:
        return {'action': 'mark_read', 'email_id': int(read_match.group(1))}

    # Mark as important (重要にする)
    if lang == 'jp':
        imp_match = re.match(r'(?:重要|mark important)[:：]\s*(\d+)', message)
    else:
        imp_match = re.match(r'(?:mark important)[:：]\s*(\d+)', message, re.IGNORECASE)

    if imp_match:
        return {'action': 'mark_important', 'email_id': int(imp_match.group(1))}

    # Add contact (連絡先追加)
    if lang == 'jp':
        contact_match = re.match(r'(?:連絡先追加|add contact)[:：]\s*(.+)', message)
    else:
        contact_match = re.match(r'(?:add contact|contact)[:：]\s*(.+)', message, re.IGNORECASE)

    if contact_match:
        return parse_add_contact(contact_match.group(1), lang)

    # List contacts (連絡先一覧)
    for kw in ['連絡先', 'contacts', 'list contacts']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_contacts'}

    # Add auto reply (自動返信追加)
    if lang == 'jp':
        reply_match = re.match(r'(?:自動返信|auto reply|auto-reply)[:：]\s*(.+)', message)
    else:
        reply_match = re.match(r'(?:auto reply|auto-reply)[:：]\s*(.+)', message, re.IGNORECASE)

    if reply_match:
        return parse_add_auto_reply(reply_match.group(1), lang)

    # List auto replies (自動返信一覧)
    for kw in ['自動返信', 'auto replies', 'auto-reply rules']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_auto_replies'}

    return None

def parse_add_email(content, lang):
    """メール追加を解析 / Parse add email"""
    result = {'action': 'add_email', 'sender': None, 'subject': None, 'body': None, 'important': False}

    if lang == 'jp':
        # Sender (送信者)
        sender_match = re.search(r'(?:送信者|from|sender)[:：]\s*(.+?)(?:\s|$)', content, re.IGNORECASE)
        if sender_match:
            result['sender'] = sender_match.group(1).strip()
        else:
            # First email-like pattern
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
            if email_match:
                result['sender'] = email_match.group(0)

        # Subject (件名)
        subject_match = re.search(r'(?:件名|subject)[:：]\s*(.+)', content, re.IGNORECASE)
        if subject_match:
            result['subject'] = subject_match.group(1).strip()
        else:
            # Second line or after sender
            if result['sender']:
                temp_content = content.replace(result['sender'], '', 1)
                words = temp_content.strip().split('\n')
                if len(words) > 0:
                    result['subject'] = words[0].strip()

        # Body (本文)
        if result['subject']:
            result['body'] = content.replace(result['sender'], '', 1).replace(result['subject'], '', 1).strip()
        else:
            result['body'] = content

        # Important (重要)
        if '重要' in content:
            result['important'] = True
    else:
        sender_match = re.search(r'(?:from|sender)[:：]\s*(.+?)(?:\s|$)', content, re.IGNORECASE)
        if sender_match:
            result['sender'] = sender_match.group(1).strip()
        else:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
            if email_match:
                result['sender'] = email_match.group(0)

        subject_match = re.search(r'(?:subject)[:：]\s*(.+)', content, re.IGNORECASE)
        if subject_match:
            result['subject'] = subject_match.group(1).strip()
        else:
            if result['sender']:
                temp_content = content.replace(result['sender'], '', 1)
                words = temp_content.strip().split('\n')
                if len(words) > 0:
                    result['subject'] = words[0].strip()

        if result['subject']:
            result['body'] = content.replace(result['sender'], '', 1).replace(result['subject'], '', 1).strip()
        else:
            result['body'] = content

        if 'important' in content_lower(content):
            result['important'] = True

    return result

def content_lower(content):
    return content.lower()

def parse_add_contact(content, lang):
    """連絡先追加を解析 / Parse add contact"""
    result = {'action': 'add_contact', 'email': None, 'name': None, 'important': False}

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
    if email_match:
        result['email'] = email_match.group(0)

    if lang == 'jp':
        name_match = re.search(r'(?:名前|name)[:：]\s*(.+)', content, re.IGNORECASE)
        if name_match:
            result['name'] = name_match.group(1).strip()
        if '重要' in content:
            result['important'] = True
    else:
        name_match = re.search(r'(?:name)[:：]\s*(.+)', content, re.IGNORECASE)
        if name_match:
            result['name'] = name_match.group(1).strip()
        if 'important' in content_lower(content):
            result['important'] = True

    return result

def parse_add_auto_reply(content, lang):
    """自動返信追加を解析 / Parse add auto reply"""
    result = {'action': 'add_auto_reply', 'rule_name': None, 'trigger': None, 'message': None}

    if lang == 'jp':
        # Rule name
        name_match = re.search(r'(?:ルール名|rule name|name)[:：]\s*(.+)', content, re.IGNORECASE)
        if name_match:
            result['rule_name'] = name_match.group(1).strip()

        # Trigger keyword
        trigger_match = re.search(r'(?:トリガー|キーワード|trigger|keyword)[:：]\s*(.+)', content, re.IGNORECASE)
        if trigger_match:
            result['trigger'] = trigger_match.group(1).strip()

        # Reply message
        message_match = re.search(r'(?:返信メッセージ|message|reply)[:：]\s*(.+)', content, re.IGNORECASE)
        if message_match:
            result['message'] = message_match.group(1).strip()
    else:
        name_match = re.search(r'(?:rule name|name)[:：]\s*(.+)', content, re.IGNORECASE)
        if name_match:
            result['rule_name'] = name_match.group(1).strip()

        trigger_match = re.search(r'(?:trigger|keyword)[:：]\s*(.+)', content, re.IGNORECASE)
        if trigger_match:
            result['trigger'] = trigger_match.group(1).strip()

        message_match = re.search(r'(?:message|reply)[:：]\s*(.+)', content, re.IGNORECASE)
        if message_match:
            result['message'] = message_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理 / Handle message"""
    lang = detect_language(message)
    parsed = parse_message(message, lang)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_email':
        if not parsed['sender']:
            return lang_response(lang, '❌ 送信者を入力してください / Please enter sender')

        email_id = add_email(parsed['sender'], parsed['subject'], parsed['body'], parsed['important'])

        response = lang_response(lang, f'📧 メール #{email_id} 追加完了 / Email #{email_id} added\n')
        response += lang_response(lang, f'送信者: {parsed["sender"]} / Sender: {parsed["sender"]}\n')
        if parsed['subject']:
            response += lang_response(lang, f'件名: {parsed["subject"]} / Subject: {parsed["subject"]}')
        return response

    elif action == 'list_emails':
        emails = list_emails()

        if not emails:
            return lang_response(lang, '📧 メールがありません / No emails found')

        response = lang_response(lang, f'📧 メール一覧 ({len(emails)}件) / Emails ({len(emails)} items):\n')
        for email in emails:
            response += format_email(email, lang)

        return response

    elif action == 'list_unread':
        emails = list_emails(is_read=False)

        if not emails:
            return lang_response(lang, '📧 未読メールはありません / No unread emails')

        response = lang_response(lang, f'📧 未読メール ({len(emails)}件) / Unread emails ({len(emails)} items):\n')
        for email in emails:
            response += format_email(email, lang)

        return response

    elif action == 'list_important':
        emails = get_important_unread()

        if not emails:
            return lang_response(lang, '📧 重要な未読メールはありません / No important unread emails')

        response = lang_response(lang, f'📧 重要な未読メール ({len(emails)}件) / Important unread emails ({len(emails)} items):\n')
        for email in emails:
            response += format_email(email, lang)

        return response

    elif action == 'mark_read':
        mark_read(parsed['email_id'])
        return lang_response(lang, f'✅ メール #{parsed["email_id"]} を既読にしました / Marked email #{parsed["email_id"]} as read')

    elif action == 'mark_important':
        mark_important(parsed['email_id'])
        return lang_response(lang, f'⭐ メール #{parsed["email_id"]} を重要にマークしました / Marked email #{parsed["email_id"]} as important')

    elif action == 'add_contact':
        if not parsed['email']:
            return lang_response(lang, '❌ メールアドレスを入力してください / Please enter email address')

        contact_id = add_contact(parsed['email'], parsed['name'], parsed['important'])

        if contact_id:
            response = lang_response(lang, f'👤 連絡先 #{contact_id} 追加完了 / Contact #{contact_id} added\n')
            response += lang_response(lang, f'メール: {parsed["email"]}\n')
            if parsed['name']:
                response += lang_response(lang, f'名前: {parsed["name"]} / Name: {parsed["name"]}')
            return response
        else:
            return lang_response(lang, '❓ その連絡先は既に存在します / That contact already exists')

    elif action == 'list_contacts':
        contacts = list_contacts()

        if not contacts:
            return lang_response(lang, '👤 連絡先がありません / No contacts found')

        response = lang_response(lang, f'👤 連絡先一覧 ({len(contacts)}件) / Contacts ({len(contacts)} items):\n')
        for contact in contacts:
            response += format_contact(contact, lang)

        return response

    elif action == 'add_auto_reply':
        if not parsed['rule_name'] or not parsed['trigger'] or not parsed['message']:
            return lang_response(lang, '❌ ルール名、トリガー、返信メッセージを入力してください / Please enter rule name, trigger, and reply message')

        rule_id = add_auto_reply(parsed['rule_name'], parsed['trigger'], parsed['message'])

        response = lang_response(lang, f'📋 自動返信ルール #{rule_id} 追加完了 / Auto-reply rule #{rule_id} added\n')
        response += lang_response(lang, f'ルール名: {parsed["rule_name"]}\n')
        response += lang_response(lang, f'トリガー: {parsed["trigger"]}\n')
        response += lang_response(lang, f'メッセージ: {parsed["message"]}')
        return response

    elif action == 'list_auto_replies':
        rules = list_auto_replies()

        if not rules:
            return lang_response(lang, '📋 自動返信ルールがありません / No auto-reply rules found')

        response = lang_response(lang, f'📋 自動返信ルール一覧 ({len(rules)}件) / Auto-reply rules ({len(rules)} items):\n')
        for rule in rules:
            response += format_auto_reply(rule, lang)

        return response

    return None

def format_email(email, lang):
    """メールをフォーマット / Format email"""
    id, sender, subject, body, is_read, is_important, received_at = email

    read_mark = '📬' if not is_read else '📭'
    important_mark = '⭐' if is_important else ''

    if lang == 'jp':
        response = f'\n[{id}] {read_mark} {important_mark}\n'
        response += f'    送信者: {sender}\n'
        response += f'    件名: {subject[:40]}...\n' if len(subject) > 40 else f'    件名: {subject}\n'
        response += f'    受信: {received_at}'
    else:
        response = f'\n[{id}] {read_mark} {important_mark}\n'
        response += f'    Sender: {sender}\n'
        response += f'    Subject: {subject[:40]}...\n' if len(subject) > 40 else f'    Subject: {subject}\n'
        response += f'    Received: {received_at}'

    return response

def format_contact(contact, lang):
    """連絡先をフォーマット / Format contact"""
    id, email, name, is_important, created_at = contact

    important_mark = '⭐' if is_important else ''

    if lang == 'jp':
        response = f'\n[{id}] {important_mark} {email}\n'
        if name:
            response += f'    名前: {name}\n'
        response += f'    登録日: {created_at}'
    else:
        response = f'\n[{id}] {important_mark} {email}\n'
        if name:
            response += f'    Name: {name}\n'
        response += f'    Added: {created_at}'

    return response

def format_auto_reply(rule, lang):
    """自動返信ルールをフォーマット / Format auto reply"""
    id, rule_name, trigger, reply_message, is_active, created_at = rule

    if lang == 'jp':
        response = f'\n[{id}] {rule_name}\n'
        response += f'    トリガー: {trigger}\n'
        response += f'    返信: {reply_message[:50]}...\n' if len(reply_message) > 50 else f'    返信: {reply_message}\n'
        response += f'    状態: 有効' if is_active else f'    状態: 無効'
    else:
        response = f'\n[{id}] {rule_name}\n'
        response += f'    Trigger: {trigger}\n'
        response += f'    Reply: {reply_message[:50]}...\n' if len(reply_message) > 50 else f'    Reply: {reply_message}\n'
        response += f'    Status: Active' if is_active else f'    Status: Inactive'

    return response

def lang_response(lang, text):
    return text

if __name__ == '__main__':
    init_db()

    test_messages = [
        "email: from@example.com, subject: Hello, important",
        "unread",
        "important",
        "add contact: test@example.com, name: John",
        "contacts",
        "auto reply: Out of office, trigger: vacation, message: I'm on vacation",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
