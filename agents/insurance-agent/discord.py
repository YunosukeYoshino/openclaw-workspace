"""
insurance-agent/discord.py
Discord bot for insurance agent with NLP-based message processing
Supports Japanese and English languages
"""

import discord
from discord.ext import commands
import re
import sys
import os
from typing import Optional, Tuple, Dict, List
from db import InsuranceDatabase, get_db


class InsuranceBot(commands.Bot):
    """Insurance Discord bot with NLP-based intent recognition"""

    def __init__(self, db_path: str = "insurance.db", command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = get_db(db_path)

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"{self.user} is ready!")

    async def on_message(self, message: discord.Message):
        """Process incoming messages"""
        if message.author == self.user:
            return

        # Process commands first
        await self.process_commands(message)

        # Process natural language messages
        if message.content and not message.content.startswith(self.command_prefix):
            response = await self.process_message(message.content, str(message.author.id))
            if response:
                await message.channel.send(response)

    async def process_message(self, message: str, user_id: str) -> Optional[str]:
        """
        Process natural language message and return response
        Uses NLP-style pattern matching and keyword analysis
        """
        # Get user's language preference
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings["language"] if user_settings else "en"

        # Detect language from message if not set
        if not user_settings:
            language = self._detect_language(message)
            self.db.set_user_language(user_id, language)

        # Identify intent and extract entities
        intent, entities = self._analyze_intent(message, language)

        # Route to appropriate handler
        response = await self._handle_intent(intent, entities, message, language, user_id)

        # Log conversation
        if response:
            self.db.add_conversation(user_id, message, response, intent)

        return response

    def _detect_language(self, text: str) -> str:
        """Detect language from text (simple heuristic)"""
        # Check for Japanese characters
        japanese_chars = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text)
        if len(japanese_chars) > len(text) * 0.2:
            return "ja"
        return "en"

    def _analyze_intent(self, message: str, language: str) -> Tuple[str, Dict]:
        """
        Analyze message to determine intent and extract entities
        Returns (intent, entities) tuple
        """
        message_lower = message.lower()

        # Define intent patterns for English
        if language == "en":
            intents = {
                "faq": {
                    "keywords": ["what", "how", "why", "when", "help", "question", "explain", "tell me", "faq"],
                    "patterns": [
                        r"what is covered",
                        r"how do i",
                        r"can i",
                        r"should i",
                        r"tell me about",
                        r"explain.*insurance"
                    ]
                },
                "claim_status": {
                    "keywords": ["claim", "status", "check", "where is", "track", "update"],
                    "patterns": [
                        r"check.*claim",
                        r"claim.*status",
                        r"track.*claim",
                        r"where.*is.*claim"
                    ]
                },
                "claim_file": {
                    "keywords": ["file", "submit", "report", "accident", "incident", "lost", "stolen", "damaged"],
                    "patterns": [
                        r"file.*claim",
                        r"submit.*claim",
                        r"report.*claim",
                        r"i need to claim",
                        r"new claim"
                    ]
                },
                "plans_list": {
                    "keywords": ["plans", "insurance", "coverage", "options", "available", "what plans"],
                    "patterns": [
                        r"what.*plans",
                        r"show.*plans",
                        r"list.*plans",
                        r"available.*insurance",
                        r"what.*coverage.*available"
                    ]
                },
                "plans_search": {
                    "keywords": ["health", "auto", "car", "life", "home", "house", "medical", "dental"],
                    "patterns": [
                        r"health.*insurance",
                        r"auto.*insurance",
                        r"car.*insurance",
                        r"life.*insurance",
                        r"home.*insurance"
                    ]
                },
                "settings_language": {
                    "keywords": ["language", "speak", "日本語", "english", "change language"],
                    "patterns": [
                        r"speak.*japanese",
                        r"speak.*english",
                        r"change.*to.*japanese",
                        r"change.*to.*english",
                        r"日本語",
                        r"英語"
                    ]
                },
                "help": {
                    "keywords": ["help", "commands", "what can you do"],
                    "patterns": [
                        r"what.*can.*you.*do",
                        r"help.*me",
                        r"commands"
                    ]
                }
            }
        else:
            # Japanese intent patterns
            intents = {
                "faq": {
                    "keywords": ["何", "どのように", "なぜ", "いつ", "ヘルプ", "質問", "説明", "教えて", "faq", "どうやって"],
                    "patterns": [
                        r"何が保障",
                        r"どうすれば",
                        r"できますか",
                        r"教えてください",
                        r"説明.*保険",
                        r"？.*保障"
                    ]
                },
                "claim_status": {
                    "keywords": ["請求", "状態", "状況", "確認", "どこ", "進捗"],
                    "patterns": [
                        r"請求.*確認",
                        r"請求.*状況",
                        r"請求.*状態",
                        r"どこ.*請求",
                        r"請求.*進捗"
                    ]
                },
                "claim_file": {
                    "keywords": ["申請", "提出", "報告", "事故", "故障", "盗難", "損害"],
                    "patterns": [
                        r"請求.*申請",
                        r"請求.*提出",
                        r"事故.*報告",
                        r"請求したい",
                        r"新しい請求"
                    ]
                },
                "plans_list": {
                    "keywords": ["プラン", "保険", "保障", "オプション", "一覧", "どんなプラン"],
                    "patterns": [
                        r"どんな.*プラン",
                        r"プラン.*見て",
                        r"プラン.*一覧",
                        r"利用可能.*保険",
                        r"どんな.*保障"
                    ]
                },
                "plans_search": {
                    "keywords": ["健康", "自動車", "車", "生命", "住宅", "家", "医療", "歯科"],
                    "patterns": [
                        r"健康.*保険",
                        r"自動車.*保険",
                        r"車.*保険",
                        r"生命.*保険",
                        r"住宅.*保険"
                    ]
                },
                "settings_language": {
                    "keywords": ["言語", "英語", "日本語", "変更"],
                    "patterns": [
                        r"英語.*話",
                        r"日本語.*話",
                        r"英語.*変",
                        r"日本語.*変",
                        r"英語で",
                        r"日本語で"
                    ]
                },
                "help": {
                    "keywords": ["ヘルプ", "コマンド", "できること"],
                    "patterns": [
                        r"何.*でき",
                        r"ヘルプ",
                        r"コマンド"
                    ]
                }
            }

        # Score each intent
        best_intent = "unknown"
        best_score = 0
        entities = {}

        for intent_name, intent_data in intents.items():
            score = 0

            # Keyword matching
            for keyword in intent_data["keywords"]:
                if keyword.lower() in message_lower:
                    score += 1

            # Pattern matching
            for pattern in intent_data["patterns"]:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    score += 2

            # Extract entities based on intent
            if intent_name == "claim_status" and score > 0:
                # Extract claim number
                claim_match = re.search(r'CLM[\w-]+', message, re.IGNORECASE)
                if claim_match:
                    entities["claim_number"] = claim_match.group()

            if intent_name == "plans_search" and score > 0:
                # Extract category
                categories = {
                    "health": ["health", "健康", "医療"],
                    "auto": ["auto", "car", "vehicle", "自動車", "車"],
                    "life": ["life", "生命"],
                    "home": ["home", "house", "住宅", "家"]
                }
                for category, keywords in categories.items():
                    if any(kw in message_lower for kw in keywords):
                        entities["category"] = category
                        break

            if intent_name == "settings_language" and score > 0:
                # Detect requested language
                if any(kw in message_lower for kw in ["日本語", "japanese", "ja"]):
                    entities["language"] = "ja"
                elif any(kw in message_lower for kw in ["英語", "english", "en"]):
                    entities["language"] = "en"

            if score > best_score:
                best_score = score
                best_intent = intent_name
                entities = entities if entities else {}

        return best_intent, entities

    async def _handle_intent(self, intent: str, entities: Dict, message: str,
                            language: str, user_id: str) -> Optional[str]:
        """Handle identified intent and return response"""

        if intent == "unknown":
            return self._get_response("unknown", language)

        if intent == "faq":
            return await self._handle_faq(message, language)

        if intent == "claim_status":
            return await self._handle_claim_status(entities, user_id, language)

        if intent == "claim_file":
            return self._get_response("claim_file_info", language)

        if intent == "plans_list":
            return await self._handle_plans_list(entities, language)

        if intent == "plans_search":
            return await self._handle_plans_search(entities, language)

        if intent == "settings_language":
            return await self._handle_settings_language(entities, user_id, language)

        if intent == "help":
            return self._get_help(language)

        return self._get_response("unknown", language)

    async def _handle_faq(self, message: str, language: str) -> str:
        """Search FAQs and return relevant answer"""
        faqs = self.db.search_faq(message, language)

        if faqs:
            faq = faqs[0]
            if language == "ja":
                return f"**{faq['question_ja']}**\n\n{faq['answer_ja']}"
            else:
                return f"**{faq['question_en']}**\n\n{faq['answer_en']}"

        # No FAQ found
        return self._get_response("no_faq_found", language)

    async def _handle_claim_status(self, entities: Dict, user_id: str, language: str) -> str:
        """Check claim status"""
        if "claim_number" in entities:
            claim = self.db.get_claim_by_number(entities["claim_number"])
            if claim:
                return self._format_claim(claim, language)
            else:
                return self._get_response("claim_not_found", language)
        else:
            # Show all claims for user
            claims = self.db.get_claims_by_user(user_id)
            if claims:
                if language == "ja":
                    response = f"📋 **請求履歴** ({len(claims)}件):\n\n"
                else:
                    response = f"📋 **Claim History** ({len(claims)} claims):\n\n"

                for claim in claims:
                    response += self._format_claim_summary(claim, language) + "\n"
                return response
            else:
                return self._get_response("no_claims", language)

    def _format_claim(self, claim: Dict, language: str) -> str:
        """Format claim details"""
        status_emoji = {
            "submitted": "📤",
            "reviewing": "🔍",
            "approved": "✅",
            "rejected": "❌",
            "paid": "💰"
        }.get(claim["status"], "📋")

        if language == "ja":
            return (
                f"{status_emoji} **請求番号:** {claim['claim_number']}\n"
                f"📊 **ステータス:** {claim['status']}\n"
                f"💵 **金額:** ¥{claim['amount']:,.0f}\n"
                f"📅 **発生日:** {claim['incident_date']}\n"
                f"📝 **説明:** {claim['description_ja']}"
            )
        else:
            return (
                f"{status_emoji} **Claim Number:** {claim['claim_number']}\n"
                f"📊 **Status:** {claim['status']}\n"
                f"💵 **Amount:** ¥{claim['amount']:,.0f}\n"
                f"📅 **Incident Date:** {claim['incident_date']}\n"
                f"📝 **Description:** {claim['description_en']}"
            )

    def _format_claim_summary(self, claim: Dict, language: str) -> str:
        """Format claim summary for list view"""
        status_emoji = {
            "submitted": "📤",
            "reviewing": "🔍",
            "approved": "✅",
            "rejected": "❌",
            "paid": "💰"
        }.get(claim["status"], "📋")

        if language == "ja":
            return f"{status_emoji} {claim['claim_number']}: ¥{claim['amount']:,.0f} ({claim['status']})"
        else:
            return f"{status_emoji} {claim['claim_number']}: ¥{claim['amount']:,.0f} ({claim['status']})"

    async def _handle_plans_list(self, entities: Dict, language: str) -> str:
        """List insurance plans"""
        category = entities.get("category")
        plans = self.db.get_all_plans(category, language)

        if not plans:
            return self._get_response("no_plans", language)

        if language == "ja":
            response = f"📋 **保険プラン一覧** ({len(plans)}件):\n\n"
        else:
            response = f"📋 **Insurance Plans** ({len(plans)} plans):\n\n"

        for plan in plans:
            response += self._format_plan_summary(plan, language) + "\n"

        return response

    async def _handle_plans_search(self, entities: Dict, language: str) -> str:
        """Search insurance plans by category"""
        category = entities.get("category")
        if category:
            return await self._handle_plans_list(entities, language)
        else:
            return await self._handle_plans_list({}, language)

    def _format_plan_summary(self, plan: Dict, language: str) -> str:
        """Format plan summary"""
        name = plan["plan_name_ja"] if language == "ja" else plan["plan_name_en"]
        description = plan["description_ja"] if language == "ja" else plan["description_en"]

        if language == "ja":
            return (
                f"🏥 **{name}**\n"
                f"📝 {description}\n"
                f"💰 月額: ¥{plan['premium_min']:,} - ¥{plan['premium_max']:,}\n"
                f"📦 保障: {', '.join(plan['coverage']) if isinstance(plan['coverage'], list) else plan['coverage']}"
            )
        else:
            return (
                f"🏥 **{name}**\n"
                f"📝 {description}\n"
                f"💰 Monthly: ¥{plan['premium_min']:,} - ¥{plan['premium_max']:,}\n"
                f"📦 Coverage: {', '.join(plan['coverage']) if isinstance(plan['coverage'], list) else plan['coverage']}"
            )

    async def _handle_settings_language(self, entities: Dict, user_id: str, language: str) -> str:
        """Change language settings"""
        new_lang = entities.get("language")
        if new_lang:
            self.db.set_user_language(user_id, new_lang)
            language = new_lang
            if language == "ja":
                return "✅ 言語を日本語に変更しました。これ以降の会話は日本語で行われます。"
            else:
                return "✅ Language changed to English. I'll now respond in English."
        else:
            return self._get_response("language_not_specified", language)

    def _get_response(self, response_key: str, language: str) -> str:
        """Get predefined response based on language"""
        responses = {
            "unknown": {
                "en": "I'm not sure what you're asking. Try asking about insurance plans, claims, or say 'help' for more info.",
                "ja": "質問が理解できませんでした。保険プランや請求について質問するか、「help」と入力して詳細を確認してください。"
            },
            "no_faq_found": {
                "en": "I couldn't find an answer to your question. Try rephrasing or ask a customer service representative for help.",
                "ja": "回答が見つかりませんでした。言い換えて質問するか、カスタマーサービスにお問い合わせください。"
            },
            "claim_not_found": {
                "en": "I couldn't find that claim. Please check the claim number and try again.",
                "ja": "請求が見つかりませんでした。請求番号を確認してもう一度お試しください。"
            },
            "no_claims": {
                "en": "You don't have any claims on file. To file a new claim, say 'file a claim'.",
                "ja": "請求履歴が見つかりません。新しい請求を申請するには「請求を申請する」と言ってください。"
            },
            "no_plans": {
                "en": "No insurance plans found.",
                "ja": "保険プランが見つかりませんでした。"
            },
            "claim_file_info": {
                "en": "To file a new claim, you'll need: 1) Your policy number, 2) Incident date, 3) Description of what happened, 4) Any supporting documents. Contact customer service to start the process.",
                "ja": "新しい請求を申請するには以下が必要です：1) 保険証券番号、2) 発生日、3) 事故の詳細、4) 支援書類。カスタマーサービスにお問い合わせください。"
            },
            "language_not_specified": {
                "en": "Please specify which language you'd like to use (English or Japanese).",
                "ja": "使用したい言語を指定してください（英語または日本語）。"
            }
        }

        return responses.get(response_key, {}).get(language, responses[response_key]["en"])

    def _get_help(self, language: str) -> str:
        """Get help message"""
        if language == "ja":
            return (
                "🤖 **Insurance Bot ヘルプ**\n\n"
                "💬 **会話の例:**\n"
                "• 「健康保険について教えて」 - 保険プランを表示\n"
                "• 「請求状況を確認」 - あなたの請求を表示\n"
                "• 「請求番号 CLM-2024-001」 - 特定の請求を確認\n"
                "• 「自動車保険」 - カテゴリ別プランを検索\n"
                "• 「請求を申請する」 - 新しい請求方法について\n"
                "• 「日本語で話して」 - 言語を日本語に変更\n"
                "• 「英語で話して」 - 言語を英語に変更\n\n"
                "📋 **コマンド:**\n"
                "• `!help` - このヘルプを表示\n"
                "• `!plans` - 全プランを一覧表示\n"
                "• `!claims` - あなたの請求を表示\n"
                "• `!language ja|en` - 言語を変更"
            )
        else:
            return (
                "🤖 **Insurance Bot Help**\n\n"
                "💬 **Conversational Examples:**\n"
                "• \"Tell me about health insurance\" - Show insurance plans\n"
                "• \"Check my claim status\" - Show your claims\n"
                "• \"Claim CLM-2024-001\" - Check a specific claim\n"
                "• \"Auto insurance\" - Search plans by category\n"
                "• \"File a claim\" - Learn about filing claims\n"
                "• \"Speak Japanese\" - Change language to Japanese\n"
                "• \"Speak English\" - Change language to English\n\n"
                "📋 **Commands:**\n"
                "• `!help` - Show this help\n"
                "• `!plans` - List all plans\n"
                "• `!claims` - Show your claims\n"
                "• `!language ja|en` - Change language"
            )

    # Discord Commands
    @commands.command(name="help")
    async def cmd_help(self, ctx):
        """Show help message"""
        user_id = str(ctx.author.id)
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings["language"] if user_settings else "en"
        await ctx.send(self._get_help(language))

    @commands.command(name="plans")
    async def cmd_plans(self, ctx, category: Optional[str] = None):
        """List insurance plans"""
        user_id = str(ctx.author.id)
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings["language"] if user_settings else "en"

        entities = {"category": category} if category else {}
        response = await self._handle_plans_list(entities, language)
        await ctx.send(response)

    @commands.command(name="claims")
    async def cmd_claims(self, ctx):
        """Show user's claims"""
        user_id = str(ctx.author.id)
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings["language"] if user_settings else "en"

        response = await self._handle_claim_status({}, user_id, language)
        await ctx.send(response)

    @commands.command(name="language")
    async def cmd_language(self, ctx, lang: str):
        """Change language (ja|en)"""
        user_id = str(ctx.author.id)
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings["language"] if user_settings else "en"

        lang = lang.lower()
        if lang in ["ja", "jp", "japanese"]:
            entities = {"language": "ja"}
        elif lang in ["en", "english"]:
            entities = {"language": "en"}
        else:
            await ctx.send("Please use 'ja' or 'en' for language.")
            return

        response = await self._handle_settings_language(entities, user_id, language)
        await ctx.send(response)


def run_bot(token: str, db_path: str = "insurance.db"):
    """Run the Discord bot"""
    bot = InsuranceBot(db_path=db_path)
    bot.run(token)


if __name__ == "__main__":
    # For testing purposes
    print("Insurance Discord Bot Module")
    print("Run with: python discord.py <BOT_TOKEN>")
