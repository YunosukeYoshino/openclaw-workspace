#!/usr/bin/env python3
"""
Survey Agent - Discord Interface
Natural language processing for survey management
"""

import re
from typing import Optional, Dict, List, Tuple
import json

# Import from db.py
try:
    from db import init_db, create_survey, add_question, update_survey, submit_response, get_survey, list_surveys, get_responses, analyze_survey
except ImportError:
    # Define inline for testing
    def init_db(): pass
    def create_survey(title, description, created_by, starts_at=None, ends_at=None): return 1
    def add_question(survey_id, question_text, question_type, options=None, required=False, order_num=0): return 1
    def update_survey(survey_id, status=None, starts_at=None, ends_at=None): pass
    def submit_response(survey_id, respondent_id, answers): return 1
    def get_survey(survey_id): return None, []
    def list_surveys(status=None): return []
    def get_responses(survey_id): return []
    def analyze_survey(survey_id): return {'total_responses': 0, 'questions': []}


class SurveyDiscord:
    """Discord interface for survey agent with NLP"""

    def __init__(self):
        init_db()

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "create_survey":
            return self._handle_create_survey(entities)
        elif intent == "add_question":
            return self._handle_add_question(entities)
        elif intent == "update_survey":
            return self._handle_update_survey(entities)
        elif intent == "submit_response":
            return self._handle_submit_response(entities)
        elif intent == "show_survey":
            return self._handle_show_survey(entities)
        elif intent == "list_surveys":
            return self._handle_list_surveys(entities)
        elif intent == "show_responses":
            return self._handle_show_responses(entities)
        elif intent == "analyze_survey":
            return self._handle_analyze_survey(entities)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_unknown(message)

    def _parse_intent(self, message: str) -> Tuple[str, Dict]:
        """Parse intent and entities from message"""
        entities = {}
        lower_msg = message.lower()

        # Create survey
        if re.search(r'(アンケートを作成|survey.*create|create.*survey|new.*survey|作成して)', lower_msg):
            entities['title'] = self._extract_title(message)
            entities['description'] = self._extract_description(message)
            entities['created_by'] = self._extract_author(message) or "user"
            return "create_survey", entities

        # Add question
        if re.search(r'(質問を追加|add.*question|question.*add)', lower_msg):
            entities['survey_id'] = self._extract_id(message)
            entities['question'] = self._extract_question_text(message)
            entities['type'] = self._extract_question_type(message)
            entities['options'] = self._extract_options(message)
            entities['required'] = self._extract_required(message)
            return "add_question", entities

        # Update survey
        if re.search(r'(アンケートを更新|update.*survey|survey.*update|start.*survey|close.*survey)', lower_msg):
            entities['survey_id'] = self._extract_id(message)
            entities['status'] = self._extract_status(message)
            return "update_survey", entities

        # Submit response
        if re.search(r'(回答する|submit|answer.*survey|respond)', lower_msg):
            entities['survey_id'] = self._extract_id(message)
            entities['respondent_id'] = self._extract_respondent_id(message) or "anonymous"
            return "submit_response", entities

        # Show survey
        if re.search(r'(アンケートを表示|show.*survey|view.*survey|詳細)', lower_msg):
            entities['survey_id'] = self._extract_id(message)
            return "show_survey", entities

        # List surveys
        if re.search(r'(アンケート一覧|list.*survey|survey.*list|surveys)', lower_msg):
            entities['status'] = self._extract_status(message)
            return "list_surveys", entities

        # Show responses
        if re.search(r'(回答を表示|show.*response|response.*list|answers)', lower_msg):
            entities['survey_id'] = self._extract_id(message)
            return "show_responses", entities

        # Analyze survey
        if re.search(r'(分析|analyze|results|stats)', lower_msg):
            entities['survey_id'] = self._extract_id(message)
            return "analyze_survey", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_title(self, message: str) -> str:
        """Extract survey title"""
        patterns = [
            r'タイトル[:\s]+(.+?)(?:\n|$|説明|description)',
            r'title[:\s]+(.+?)(?:\n|$|description|desc)',
            r'アンケート[:\s]+(.+?)(?:\n|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "新しいアンケート"

    def _extract_description(self, message: str) -> Optional[str]:
        """Extract survey description"""
        patterns = [
            r'説明[:\s]+(.+?)(?:\n|$|質問|question)',
            r'description[:\s]+(.+?)(?:\n|$|question)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_author(self, message: str) -> Optional[str]:
        """Extract author/creator"""
        patterns = [
            r'作成者[:\s]+([^\s,]+)',
            r'by\s+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_id(self, message: str) -> Optional[int]:
        """Extract survey ID"""
        patterns = [
            r'アンケート\s*(\d+)',
            r'survey\s*(\d+)',
            r'ID[:\s]*(\d+)',
            r'no\.?\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_question_text(self, message: str) -> str:
        """Extract question text"""
        patterns = [
            r'質問[:\s]+(.+?)(?:\n|$|タイプ|type|選択肢|option)',
            r'question[:\s]+(.+?)(?:\n|$|type|option)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "新しい質問"

    def _extract_question_type(self, message: str) -> str:
        """Extract question type"""
        type_map = {
            'テキスト': 'text', 'text': 'text',
            '選択': 'multiple_choice', 'multiple': 'multiple_choice', 'choice': 'multiple_choice', '選択肢': 'multiple_choice',
            '評価': 'rating', 'rating': 'rating', 'rate': 'rating',
            'はいいいえ': 'yes_no', 'yes_no': 'yes_no', 'yes/no': 'yes_no',
            'チェックボックス': 'checkbox', 'checkbox': 'checkbox', 'check': 'checkbox',
        }
        lower_msg = message.lower()
        for key, value in type_map.items():
            if key in lower_msg:
                return value
        return 'text'

    def _extract_options(self, message: str) -> Optional[List[str]]:
        """Extract options for multiple choice questions"""
        if not re.search(r'(選択肢|option|multiple|choice)', message.lower()):
            return None

        patterns = [
            r'選択肢[:\s]+(.+)',
            r'options?:\s+(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                options_str = match.group(1)
                # Split by comma or newline
                options = [opt.strip() for opt in re.split(r'[,、\n]', options_str) if opt.strip()]
                return options if options else None
        return None

    def _extract_required(self, message: str) -> bool:
        """Extract whether question is required"""
        required = re.search(r'(必須|required|must)', message.lower())
        return bool(required)

    def _extract_status(self, message: str) -> Optional[str]:
        """Extract survey status"""
        if re.search(r'(開始|activate|start|open)', message.lower()):
            return 'active'
        elif re.search(r'(終了|close|end|stop)', message.lower()):
            return 'closed'
        return None

    def _extract_respondent_id(self, message: str) -> Optional[str]:
        """Extract respondent ID"""
        patterns = [
            r'(from|by)[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(2).strip()
        return None

    def _handle_create_survey(self, entities: Dict) -> str:
        """Handle survey creation"""
        title = entities.get('title', '新しいアンケート')
        description = entities.get('description')
        created_by = entities.get('created_by', 'user')

        survey_id = create_survey(title, description, created_by)
        return f"✅ アンケートを作成しました (ID: {survey_id})\nタイトル: {title}"

    def _handle_add_question(self, entities: Dict) -> str:
        """Handle adding question to survey"""
        survey_id = entities.get('survey_id')
        if not survey_id:
            return "アンケートIDを指定してください。例: アンケート1に質問を追加"

        question = entities.get('question', '新しい質問')
        q_type = entities.get('type', 'text')
        options = entities.get('options')
        required = entities.get('required', False)

        options_str = json.dumps(options) if options else None
        question_id = add_question(survey_id, question, q_type, options_str, required)

        type_display = {
            'text': 'テキスト',
            'multiple_choice': '選択肢',
            'rating': '評価',
            'yes_no': 'はい/いいえ',
            'checkbox': 'チェックボックス'
        }.get(q_type, q_type)

        required_text = " (必須)" if required else ""
        return f"✅ 質問を追加しました (ID: {question_id})\nタイプ: {type_display}{required_text}\n質問: {question}"

    def _handle_update_survey(self, entities: Dict) -> str:
        """Handle survey update"""
        survey_id = entities.get('survey_id')
        if not survey_id:
            return "アンケートIDを指定してください。"

        status = entities.get('status')
        if not status:
            return "ステータスを指定してください (開始/終了)。"

        update_survey(survey_id, status=status)

        status_text = {'active': '公開中', 'closed': '終了', 'draft': '下書き'}.get(status, status)
        return f"✅ アンケート {survey_id} を「{status_text}」にしました"

    def _handle_submit_response(self, entities: Dict) -> str:
        """Handle response submission"""
        survey_id = entities.get('survey_id')
        if not survey_id:
            return "アンケートIDを指定してください。"

        # For this simple implementation, we'll create a placeholder response
        # In a real implementation, you'd parse answers from the message
        survey, questions = get_survey(survey_id)
        if not survey:
            return f"アンケート {survey_id} が見つかりません"

        return f"💬 回答フォームの作成が必要です。\nアンケート: {survey[1]}\n質問数: {len(questions)}"

    def _handle_show_survey(self, entities: Dict) -> str:
        """Handle showing survey details"""
        survey_id = entities.get('survey_id')
        if not survey_id:
            return "アンケートIDを指定してください。"

        survey, questions = get_survey(survey_id)
        if not survey:
            return f"アンケート {survey_id} が見つかりません"

        status_text = {'active': '🟢 公開中', 'closed': '🔴 終了', 'draft': '📝 下書き'}.get(survey[2], survey[2])

        response = f"📋 **アンケート #{survey_id}: {survey[1]}**\n"
        response += f"ステータス: {status_text}\n"
        if survey[3]:
            response += f"説明: {survey[3]}\n"
        response += f"\n質問 ({len(questions)}件):\n"

        for q in questions:
            q_type = {
                'text': 'テキスト',
                'multiple_choice': '選択肢',
                'rating': '評価',
                'yes_no': 'はい/いいえ',
                'checkbox': 'チェックボックス'
            }.get(q[2], q[2])

            options = f"\n    選択肢: {q[3]}" if q[3] else ""
            required = " (必須)" if q[4] else ""
            response += f"  {q[5] + 1}. {q[1]} [{q_type}]{required}{options}\n"

        return response

    def _handle_list_surveys(self, entities: Dict) -> str:
        """Handle listing surveys"""
        surveys = list_surveys(entities.get('status'))

        if not surveys:
            return "アンケートが見つかりません"

        response = f"📊 **アンケート一覧** ({len(surveys)}件):\n\n"
        for s in surveys:
            status_text = {'active': '🟢', 'closed': '🔴', 'draft': '📝'}.get(s[2], s[2])
            response += f"{status_text} #{s[0]} {s[1]}\n"

        return response

    def _handle_show_responses(self, entities: Dict) -> str:
        """Handle showing responses"""
        survey_id = entities.get('survey_id')
        if not survey_id:
            return "アンケートIDを指定してください。"

        responses = get_responses(survey_id)

        if not responses:
            return f"アンケート {survey_id} にはまだ回答がありません"

        response = f"💬 **回答一覧** ({len(responses)}件):\n\n"
        for resp, answers in responses:
            response += f"回答 #{resp[0]} - {resp[1]} ({resp[2]})\n"
            for q, a in answers:
                response += f"  • {q}: {a}\n"
            response += "\n"

        return response

    def _handle_analyze_survey(self, entities: Dict) -> str:
        """Handle survey analysis"""
        survey_id = entities.get('survey_id')
        if not survey_id:
            return "アンケートIDを指定してください。"

        analysis = analyze_survey(survey_id)
        total = analysis['total_responses']

        response = f"📈 **アンケート #{survey_id} の分析**\n\n"
        response += f"総回答数: {total}件\n\n"

        for q in analysis['questions']:
            response += f"**{q['question']}**\n"
            stats = q['stats']

            if q['type'] in ['multiple_choice', 'yes_no']:
                response += "分布:\n"
                for opt, count in stats.get('distribution', {}).items():
                    pct = (count / total * 100) if total > 0 else 0
                    response += f"  • {opt}: {count}件 ({pct:.1f}%)\n"

            elif q['type'] == 'rating':
                avg = stats.get('average')
                response += f"平均: {avg:.1f}\n"

            elif q['type'] == 'text':
                answers = stats.get('answers', [])
                response += f"回答: {len(answers)}件\n"
                for a in answers[:3]:
                    response += f"  • {a}\n"

            response += "\n"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
📋 **Survey Agent ヘルプ**

**アンケート作成:**
• アンケートを作成 タイトル:顧客満足度調査 説明:サービスについてのアンケート
• Create survey title: Customer Satisfaction description: Service feedback

**質問を追加:**
• アンケート1に質問を追加 質問:満足度は？ タイプ:評価
• アンケート1に質問を追加 質問:おすすめ機能 タイプ:選択肢 選択肢:UI,速度,機能,価格 必須

**アンケート管理:**
• アンケート1を開始
• アンケート1を終了

**アンケート表示・回答:**
• アンケート一覧
• アンケート1を表示
• アンケート1の回答を表示

**分析:**
• アンケート1を分析

**English support:**
• Create survey title: Daily Check-in
• Add question to survey 1: How are you feeling? type: rating
• Survey 1 status: active
• Show survey 1
• Analyze survey 1
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return f"すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = SurveyDiscord()

    print(agent.process_message("ヘルプ"))

    # Test creating a survey
    print("\n--- Create Survey ---")
    print(agent.process_message("アンケートを作成 タイトル:毎日チェックイン 説明:1日の気分を記録"))

    # Test adding questions
    print("\n--- Add Questions ---")
    print(agent.process_message("アンケート1に質問を追加 質問:今日の気分は？ タイプ:評価"))
    print(agent.process_message("アンケート1に質問を追加 質問:何に時間を使った？ タイプ:選択肢 選択肢:仕事,勉強,趣味,休息"))

    # Test showing survey
    print("\n--- Show Survey ---")
    print(agent.process_message("アンケート1を表示"))

    # Test listing
    print("\n--- List Surveys ---")
    print(agent.process_message("アンケート一覧"))
