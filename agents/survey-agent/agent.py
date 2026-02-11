#!/usr/bin/env python3
"""
Survey Agent - Discord Integration
Natural Language Processing for Survey Creation and Analysis
"""

import re
import json
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """Parse message and determine action"""
    # Create survey
    create_match = re.match(r'(?:アンケート|survey)[：:]\s*(?:作成|create|new)[：:]\s*(.+)', message, re.IGNORECASE)
    if create_match:
        return {'action': 'create_survey', 'content': create_match.group(1)}

    # Add question
    question_match = re.match(r'(?:質問|question)[：:]\s*(?:追加|add)[：:]\s*アンケート\s*(\d+)[：:]\s*(.+)', message, re.IGNORECASE)
    if question_match:
        return {'action': 'add_question', 'survey_id': int(question_match.group(1)), 'content': question_match.group(2)}

    # Activate survey
    activate_match = re.match(r'(?:開始|start|activate)[：:]\s*アンケート\s*(\d+)', message, re.IGNORECASE)
    if activate_match:
        return {'action': 'activate_survey', 'survey_id': int(activate_match.group(1))}

    # Close survey
    close_match = re.match(r'(?:終了|close|end)[：:]\s*アンケート\s*(\d+)', message, re.IGNORECASE)
    if close_match:
        return {'action': 'close_survey', 'survey_id': int(close_match.group(1))}

    # Submit response
    response_match = re.match(r'(?:回答|respond|submit)[：:]\s*アンケート\s*(\d+)[：:]\s*(.+)', message, re.IGNORECASE)
    if response_match:
        return {'action': 'submit_response', 'survey_id': int(response_match.group(1)), 'content': response_match.group(2)}

    # List surveys
    if re.match(r'(?:一覧|list|surveys|アンケート一覧)', message, re.IGNORECASE):
        return {'action': 'list_surveys'}

    # View survey
    view_match = re.match(r'(?:表示|view|show)[：:]\s*アンケート\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_survey', 'survey_id': int(view_match.group(1))}

    # View responses
    responses_match = re.match(r'(?:回答|responses)[：:]\s*アンケート\s*(\d+)', message, re.IGNORECASE)
    if responses_match:
        return {'action': 'view_responses', 'survey_id': int(responses_match.group(1))}

    # Analyze
    analyze_match = re.match(r'(?:分析|analyze)[：:]\s*アンケート\s*(\d+)', message, re.IGNORECASE)
    if analyze_match:
        return {'action': 'analyze', 'survey_id': int(analyze_match.group(1))}

    return None

def parse_survey_content(content, created_by):
    """Parse survey creation content"""
    result = {'title': None, 'description': None, 'created_by': created_by, 'starts_at': None, 'ends_at': None}

    # Description
    desc_match = re.search(r'(?:説明|description|概要)[：:]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()
        # Title is before description
        idx = content.find(desc_match.group(0))
        result['title'] = content[:idx].strip()
    else:
        result['title'] = content.strip()

    # Start date
    start_match = re.search(r'(?:開始|start|starts_at)[：:]\s*(.+)', content, re.IGNORECASE)
    if start_match and '説明' not in start_match.group(0):
        result['starts_at'] = parse_date(start_match.group(1).strip())

    # End date
    end_match = re.search(r'(?:終了|end|ends_at)[：:]\s*(.+)', content, re.IGNORECASE)
    if end_match and '説明' not in end_match.group(0):
        result['ends_at'] = parse_date(end_match.group(1).strip())

    return result

def parse_question_content(content):
    """Parse question content"""
    result = {'question_text': None, 'question_type': 'text', 'options': None, 'required': False, 'order_num': 0}

    # Type
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(text|multiple_choice|rating|yes_no|checkbox|テキスト|選択|評価|yes/no|チェック)', content, re.IGNORECASE)
    if type_match:
        t = type_match.group(1).lower()
        type_map = {'text': 'text', 'テキスト': 'text', 'multiple_choice': 'multiple_choice', '選択': 'multiple_choice', 'rating': 'rating', '評価': 'rating', 'yes_no': 'yes_no', 'yes/no': 'yes_no', 'checkbox': 'checkbox', 'チェック': 'checkbox'}
        result['question_type'] = type_map.get(t, 'text')

    # Required
    required_match = re.search(r'(?:必須|required|必須項目)', content, re.IGNORECASE)
    if required_match:
        result['required'] = True

    # Options
    options_match = re.search(r'(?:選択肢|options|choices)[：:]\s*(.+)', content, re.IGNORECASE)
    if options_match:
        opts = [o.strip() for o in options_match.group(1).split(',')]
        result['options'] = ','.join(opts)

    # Order
    order_match = re.search(r'(?:順序|order)[：:]\s*(\d+)', content, re.IGNORECASE)
    if order_match:
        result['order_num'] = int(order_match.group(1))

    # Question text (everything before type/options)
    for key in ['タイプ', 'type', '選択肢', 'options', 'choices', '必須', 'required', '順序', 'order']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['question_text'] = content[:match.start()].strip()
            break
    else:
        result['question_text'] = content.strip()

    return result

def parse_response_content(content):
    """Parse response submission content"""
    # Parse format: "Q1: answer1, Q2: answer2" or "1: answer1, 2: answer2"
    answers = []
    parts = re.split(r',\s*', content)

    for part in parts:
        match = re.match(r'(?:Q|question)?(\d+)[：:]\s*(.+)', part, re.IGNORECASE)
        if match:
            question_num = int(match.group(1))
            answer = match.group(2).strip()
            answers.append((question_num, answer))

    return answers

def parse_date(date_str):
    """Parse date string"""
    try:
        # Try common formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(date_str.split()[0], fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

        # Handle relative dates
        if 'tomorrow' in date_str.lower() or '明日' in date_str:
            dt = datetime.now() + timedelta(days=1)
            return dt.strftime("%Y-%m-%d 00:00:00")
        elif 'next week' in date_str.lower() or '来週' in date_str:
            dt = datetime.now() + timedelta(days=7)
            return dt.strftime("%Y-%m-%d 00:00:00")

        return None
    except:
        return None

def process_action(parsed, user_id):
    """Process the parsed action and return response"""
    try:
        if parsed['action'] == 'create_survey':
            survey_data = parse_survey_content(parsed['content'], user_id)
            survey_id = create_survey(**survey_data)
            return {
                'status': 'success',
                'message_ja': f'アンケート #{survey_id} を作成しました',
                'message_en': f'Survey #{survey_id} created',
                'survey_id': survey_id
            }

        elif parsed['action'] == 'add_question':
            q_data = parse_question_content(parsed['content'])
            question_id = add_question(parsed['survey_id'], **q_data)
            return {
                'status': 'success',
                'message_ja': f'アンケート #{parsed["survey_id"]} に質問 #{question_id} を追加しました',
                'message_en': f'Question #{question_id} added to survey #{parsed["survey_id"]}',
                'question_id': question_id
            }

        elif parsed['action'] == 'activate_survey':
            update_survey(parsed['survey_id'], status='active')
            return {
                'status': 'success',
                'message_ja': f'アンケート #{parsed["survey_id"]} を開始しました',
                'message_en': f'Survey #{parsed["survey_id"]} activated'
            }

        elif parsed['action'] == 'close_survey':
            update_survey(parsed['survey_id'], status='closed')
            return {
                'status': 'success',
                'message_ja': f'アンケート #{parsed["survey_id"]} を終了しました',
                'message_en': f'Survey #{parsed["survey_id"]} closed'
            }

        elif parsed['action'] == 'submit_response':
            answers = parse_response_content(parsed['content'])
            response_id = submit_response(parsed['survey_id'], user_id, answers)
            return {
                'status': 'success',
                'message_ja': f'アンケート #{parsed["survey_id"]} に回答しました',
                'message_en': f'Response submitted to survey #{parsed["survey_id"]}',
                'response_id': response_id
            }

        elif parsed['action'] == 'list_surveys':
            surveys = list_surveys()
            survey_list = '\n'.join([f"#{s[0]}: {s[1]} ({s[2]})" for s in surveys])
            return {
                'status': 'success',
                'message_ja': f'アンケート一覧:\n{survey_list}',
                'message_en': f'Survey list:\n{survey_list}'
            }

        elif parsed['action'] == 'view_survey':
            survey, questions = get_survey(parsed['survey_id'])
            if survey:
                q_list = '\n'.join([f"Q{q[0]}: {q[1]} ({q[2]})" for q in questions])
                return {
                    'status': 'success',
                    'message_ja': f'アンケート #{survey[0]}: {survey[1]}\nステータス: {survey[3]}\n\n質問:\n{q_list}',
                    'message_en': f'Survey #{survey[0]}: {survey[1]}\nStatus: {survey[3]}\n\nQuestions:\n{q_list}'
                }
            else:
                return {
                    'status': 'not_found',
                    'message_ja': 'アンケートが見つかりません',
                    'message_en': 'Survey not found'
                }

        elif parsed['action'] == 'view_responses':
            responses = get_responses(parsed['survey_id'])
            resp_summary = f'全{len(responses)}件の回答\n'
            for i, (resp, answers) in enumerate(responses[:10], 1):
                resp_summary += f'\n回答{i}: {resp[1]} ({resp[2]})\n'
                for q, a in answers:
                    resp_summary += f'  {q}: {a}\n'

            return {
                'status': 'success',
                'message_ja': resp_summary,
                'message_en': resp_summary
            }

        elif parsed['action'] == 'analyze':
            analysis = analyze_survey(parsed['survey_id'])
            result = f'分析結果 (回答数: {analysis["total_responses"]})\n'
            for q in analysis['questions']:
                result += f'\nQ{q["id"]}: {q["question"]}\n'
                if q['type'] == 'rating':
                    result += f'  平均: {q["stats"].get("average", "N/A")}\n'
                elif q['type'] in ['multiple_choice', 'yes_no']:
                    result += f'  分布: {q["stats"].get("distribution", {})}\n'

            return {
                'status': 'success',
                'message_ja': result,
                'message_en': result,
                'analysis': analysis
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
