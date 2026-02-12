"""
car-agent/discord.py
Discord bot for car agent with NLP-based message processing
車管理エージェント - 自然言語処理付きDiscordボット
Supports Japanese and English languages
"""

import discord
from discord.ext import commands
import re
import sys
import os
from typing import Optional, Tuple, Dict, List
from db import CarDB


class CarBot(commands.Bot):
    """Car Management Discord bot with NLP-based intent recognition"""

    def __init__(self, db_path: str = "car.db", command_prefix: str = "!car "):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = CarDB(db_path)

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"{self.user} is ready!")
        activity = discord.Activity(type=discord.ActivityType.watching, name="your vehicles")
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        """Process incoming messages"""
        if message.author == self.user:
            return

        # Process commands first
        await self.process_commands(message)

        # Process natural language messages
        if message.content and not message.content.startswith("!car "):
            response = await self.process_message(message.content, str(message.author.id))
            if response:
                await message.channel.send(response)

    async def process_message(self, message: str, user_id: str) -> Optional[str]:
        """
        Process natural language message and return response
        Uses NLP-style pattern matching and keyword analysis
        """
        # Detect language from message
        language = self._detect_language(message)

        # Identify intent and extract entities
        intent, entities = self._analyze_intent(message, language)

        # Route to appropriate handler
        response = await self._handle_intent(intent, entities, message, language, user_id)

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
                "summary": {
                    "keywords": ["summary", "overview", "status", "what", "situation"],
                    "patterns": [
                        r"how.*are.*my.*cars",
                        r"car.*summary",
                        r"vehicle.*overview",
                        r"status.*of.*my.*cars"
                    ]
                },
                "vehicle_add": {
                    "keywords": ["add", "new", "register", "create", "add a car", "add a vehicle"],
                    "patterns": [
                        r"add.*new.*car",
                        r"register.*vehicle",
                        r"create.*new.*vehicle"
                    ]
                },
                "vehicle_list": {
                    "keywords": ["vehicles", "cars", "list", "show", "my cars", "my vehicles"],
                    "patterns": [
                        r"show.*my.*cars",
                        r"list.*vehicles",
                        r"what.*cars.*do.*i.*have"
                    ]
                },
                "fuel_add": {
                    "keywords": ["fuel", "gas", "refuel", "fill", "fill up", "gas station"],
                    "patterns": [
                        r"add.*fuel",
                        r"record.*gas",
                        r"filled.*up",
                        r"refueled"
                    ]
                },
                "fuel_list": {
                    "keywords": ["fuel history", "gas history", "fill records", "fuel records"],
                    "patterns": [
                        r"show.*fuel.*history",
                        r"gas.*records",
                        r"refueling.*history"
                    ]
                },
                "fuel_stats": {
                    "keywords": ["fuel stats", "gas stats", "average", "mpg", "fuel efficiency", "consumption"],
                    "patterns": [
                        r"fuel.*statistics",
                        r"gas.*stats",
                        r"average.*fuel",
                        r"fuel.*efficiency"
                    ]
                },
                "maintenance_add": {
                    "keywords": ["maintenance", "service", "oil change", "tire", "brake", "inspection"],
                    "patterns": [
                        r"add.*maintenance",
                        r"record.*service",
                        r"did.*maintenance",
                        r"oil.*change"
                    ]
                },
                "maintenance_list": {
                    "keywords": ["maintenance history", "service history", "maintenance records"],
                    "patterns": [
                        r"show.*maintenance",
                        r"service.*history",
                        r"maintenance.*records"
                    ]
                },
                "repair_add": {
                    "keywords": ["repair", "fix", "broken", "issue", "problem", "damaged"],
                    "patterns": [
                        r"add.*repair",
                        r"record.*repair",
                        r"need.*to.*fix",
                        r"something.*wrong"
                    ]
                },
                "repair_list": {
                    "keywords": ["repair history", "repairs", "fix records"],
                    "patterns": [
                        r"show.*repairs",
                        r"repair.*history",
                        r"what.*repairs"
                    ]
                },
                "insurance_add": {
                    "keywords": ["insurance", "policy", "coverage", "add insurance"],
                    "patterns": [
                        r"add.*insurance",
                        r"new.*policy",
                        r"update.*insurance"
                    ]
                },
                "insurance_list": {
                    "keywords": ["insurance policies", "coverage", "insurance history"],
                    "patterns": [
                        r"show.*insurance",
                        r"my.*policies",
                        r"insurance.*information"
                    ]
                },
                "reminder_add": {
                    "keywords": ["reminder", "remind", "schedule", "upcoming", "due"],
                    "patterns": [
                        r"add.*reminder",
                        r"set.*reminder",
                        r"remind.*me.*to"
                    ]
                },
                "reminder_list": {
                    "keywords": ["reminders", "upcoming", "due soon"],
                    "patterns": [
                        r"show.*reminders",
                        r"what.*is.*due",
                        r"upcoming.*maintenance"
                    ]
                },
                "help": {
                    "keywords": ["help", "what can you do", "commands", "how to use"],
                    "patterns": [
                        r"what.*can.*you.*do",
                        r"help.*me",
                        r"how.*do.*i.*use"
                    ]
                }
            }
        else:
            # Japanese intent patterns
            intents = {
                "summary": {
                    "keywords": ["サマリー", "概要", "状況", "ステータス", "どうなってる"],
                    "patterns": [
                        r"車の状況",
                        r"サマリー見て",
                        r"どうなってる",
                        r"状況.*確認"
                    ]
                },
                "vehicle_add": {
                    "keywords": ["追加", "新規", "登録", "作成", "車追加"],
                    "patterns": [
                        r"車.*追加",
                        r"新規.*登録",
                        r"車両.*登録"
                    ]
                },
                "vehicle_list": {
                    "keywords": ["車一覧", "車両一覧", "所有車", "表示"],
                    "patterns": [
                        r"車.*見て",
                        r"車両.*一覧",
                        r"どんな.*車"
                    ]
                },
                "fuel_add": {
                    "keywords": ["給油", "ガソリン", "給油した", "満タン"],
                    "patterns": [
                        r"給油.*記録",
                        r"ガソリン.*追加",
                        r"満タン.*した"
                    ]
                },
                "fuel_list": {
                    "keywords": ["給油記録", "給油履歴", "ガソリン履歴"],
                    "patterns": [
                        r"給油.*履歴",
                        r"給油.*記録.*見て"
                    ]
                },
                "fuel_stats": {
                    "keywords": ["燃料統計", "燃費", "平均", "消費"],
                    "patterns": [
                        r"燃料.*統計",
                        r"燃費.*見て",
                        r"平均.*給油"
                    ]
                },
                "maintenance_add": {
                    "keywords": ["メンテナンス", "点検", "オイル交換", "タイヤ", "ブレーキ"],
                    "patterns": [
                        r"メンテナンス.*記録",
                        r"点検.*した",
                        r"オイル交換"
                    ]
                },
                "maintenance_list": {
                    "keywords": ["メンテ履歴", "点検履歴", "メンテ記録"],
                    "patterns": [
                        r"メンテナンス.*履歴",
                        r"点検.*記録"
                    ]
                },
                "repair_add": {
                    "keywords": ["修理", "故障", "トラブル", "不具合", "直す"],
                    "patterns": [
                        r"修理.*記録",
                        r"故障.*した",
                        r"修理.*必要"
                    ]
                },
                "repair_list": {
                    "keywords": ["修理履歴", "修理記録"],
                    "patterns": [
                        r"修理.*履歴",
                        r"修理.*記録.*見て"
                    ]
                },
                "insurance_add": {
                    "keywords": ["保険", "保険追加", "加入", "更新"],
                    "patterns": [
                        r"保険.*追加",
                        r"新規.*保険",
                        r"保険.*更新"
                    ]
                },
                "insurance_list": {
                    "keywords": ["保険一覧", "加入保険", "契約中"],
                    "patterns": [
                        r"保険.*見て",
                        r"保険.*一覧",
                        r"どんな.*保険"
                    ]
                },
                "reminder_add": {
                    "keywords": ["リマインダー", "予定", "期限", "予定追加"],
                    "patterns": [
                        r"リマインダー.*追加",
                        r"予定.*登録",
                        r"期限.*設定"
                    ]
                },
                "reminder_list": {
                    "keywords": ["リマインダー一覧", "予定一覧", "期限確認"],
                    "patterns": [
                        r"リマインダー.*見て",
                        r"予定.*確認",
                        r"期限.*近い"
                    ]
                },
                "help": {
                    "keywords": ["ヘルプ", "使い方", "できること", "コマンド"],
                    "patterns": [
                        r"何.*でき",
                        r"ヘルプ",
                        r"使い方.*教"
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
            if intent_name in ["vehicle_add", "fuel_add", "maintenance_add", "repair_add", "reminder_add"]:
                # Extract vehicle name/ID
                vehicle_match = re.search(r'(?:vehicle|car|車両|車)\s*[:#]?\s*(\d+|[a-zA-Z]+)', message, re.IGNORECASE)
                if vehicle_match:
                    entities["vehicle_id"] = vehicle_match.group(1)

            if intent_name == "fuel_add":
                # Extract odometer reading
                odometer_match = re.search(r'(\d{3,})\s*(?:km|miles)', message, re.IGNORECASE)
                if odometer_match:
                    entities["odometer"] = int(odometer_match.group(1))

                # Extract fuel amount
                liters_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|liters|litres)', message, re.IGNORECASE)
                if liters_match:
                    entities["liters"] = float(liters_match.group(1))

                # Extract price
                price_match = re.search(r'¥?(\d+)\s*[/／]?\s*(?:L|liter|litre)', message)
                if price_match:
                    entities["price_per_liter"] = float(price_match.group(1))

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

        if intent == "summary":
            return await self._handle_summary(language)

        if intent == "vehicle_add":
            return self._get_response("vehicle_add_guide", language)

        if intent == "vehicle_list":
            return await self._handle_vehicle_list(language)

        if intent == "fuel_add":
            return self._get_response("fuel_add_guide", language)

        if intent == "fuel_list":
            return await self._handle_fuel_list(language)

        if intent == "fuel_stats":
            return self._get_response("fuel_stats_guide", language)

        if intent == "maintenance_add":
            return self._get_response("maintenance_add_guide", language)

        if intent == "maintenance_list":
            return await self._handle_maintenance_list(language)

        if intent == "repair_add":
            return self._get_response("repair_add_guide", language)

        if intent == "repair_list":
            return await self._handle_repair_list(language)

        if intent == "insurance_add":
            return self._get_response("insurance_add_guide", language)

        if intent == "insurance_list":
            return await self._handle_insurance_list(language)

        if intent == "reminder_add":
            return self._get_response("reminder_add_guide", language)

        if intent == "reminder_list":
            return await self._handle_reminder_list(language)

        if intent == "help":
            return self._get_help(language)

        return self._get_response("unknown", language)

    async def _handle_summary(self, language: str) -> str:
        """Get car management summary"""
        summary = self.db.get_summary()

        if language == "ja":
            return (
                f"🚗 **車管理サマリー / Car Summary**\n\n"
                f"🚙 車両数 / Vehicles: {summary['active_vehicles']}\n"
                f"🔧 修理中 / Open Repairs: {summary['open_repairs']}\n"
                f"📅 リマインダー / Upcoming: {summary['upcoming_reminders']}\n"
                f"📄 保険期限切れ / Expiring: {summary['expiring_insurance']}"
            )
        else:
            return (
                f"🚗 **Car Summary**\n\n"
                f"🚙 Vehicles: {summary['active_vehicles']}\n"
                f"🔧 Open Repairs: {summary['open_repairs']}\n"
                f"📅 Upcoming Reminders: {summary['upcoming_reminders']}\n"
                f"📄 Expiring Insurance: {summary['expiring_insurance']}"
            )

    async def _handle_vehicle_list(self, language: str) -> str:
        """List all vehicles"""
        vehicles = self.db.get_vehicles()

        if not vehicles:
            return self._get_response("no_vehicles", language)

        if language == "ja":
            response = f"🚙 **車両一覧 / Vehicles ({len(vehicles)})**:\n\n"
        else:
            response = f"🚙 **Vehicles ({len(vehicles)})**:\n\n"

        for vehicle in vehicles:
            details = f"{vehicle['make'] or ''} {vehicle['model'] or ''} {vehicle['year'] or ''}".strip()
            odometer = f"{vehicle['odometer'] or 0:,} km" if vehicle['odometer'] else "N/A"
            response += f"🚗 {vehicle['name']} (ID: {vehicle['id']}) - {details}\n   走行距離: {odometer} | ナンバー: {vehicle['license_plate'] or 'N/A'}\n\n"

        return response

    async def _handle_fuel_list(self, language: str) -> str:
        """List fuel records"""
        records = self.db.get_fuel_records(limit=10)

        if not records:
            return self._get_response("no_fuel_records", language)

        if language == "ja":
            response = f"⛽ **給油記録 / Fuel Records ({len(records)})**:\n\n"
        else:
            response = f"⛽ **Fuel Records ({len(records)})**:\n\n"

        for record in records:
            total = record['total_price']
            response += f"📅 {record['fill_date']} - {record['odometer']:,} km\n   {record['fuel_liters']}L @ ¥{record['price_per_liter']}/L = ¥{total:.2f}\n\n"

        return response

    async def _handle_maintenance_list(self, language: str) -> str:
        """List maintenance records"""
        records = self.db.get_maintenance()

        if not records:
            return self._get_response("no_maintenance", language)

        if language == "ja":
            response = f"🔧 **メンテナンス一覧 / Maintenance ({len(records)})**:\n\n"
        else:
            response = f"🔧 **Maintenance ({len(records)})**:\n\n"

        for record in records[:10]:
            cost_str = f"¥{record['cost']:,.0f}" if record['cost'] else "N/A"
            response += f"🔧 {record['service_type']} - {record['service_date']}\n   {record['odometer']:,} km | 費用: {cost_str}\n   {record['description'] or ''}\n\n"

        return response

    async def _handle_repair_list(self, language: str) -> str:
        """List repair records"""
        repairs = self.db.get_repairs()

        if not repairs:
            return self._get_response("no_repairs", language)

        if language == "ja":
            response = f"🔨 **修理一覧 / Repairs ({len(repairs)})**:\n\n"
        else:
            response = f"🔨 **Repairs ({len(repairs)})**:\n\n"

        status_emoji = {'open': '📝', 'in_progress': '🔨', 'completed': '✅', 'cancelled': '❌'}
        severity_emoji = {'minor': '🟢', 'moderate': '🟡', 'critical': '🔴'}

        for repair in repairs[:10]:
            s_emoji = status_emoji.get(repair['status'], '❓')
            sev_emoji = severity_emoji.get(repair['severity'], '⚪')
            response += f"{s_emoji} {repair['issue']} ({repair['issue_date']})\n   {sev_emoji} 重要度: {repair['severity']} | {repair['odometer'] or 0:,} km\n\n"

        return response

    async def _handle_insurance_list(self, language: str) -> str:
        """List insurance policies"""
        policies = self.db.get_insurance()

        if not policies:
            return self._get_response("no_insurance", language)

        if language == "ja":
            response = f"📄 **保険一覧 / Insurance Policies ({len(policies)})**:\n\n"
        else:
            response = f"📄 **Insurance Policies ({len(policies)})**:\n\n"

        for policy in policies:
            status_emoji = '✅' if policy['status'] == 'active' else '⚠️'
            premium_str = f"¥{policy['premium']:,.0f}/年" if policy['premium'] else "N/A"
            response += f"{status_emoji} {policy['provider']}\n   ポリシー: {policy['policy_number']}\n   期間: {policy['start_date']} ~ {policy['end_date']}\n   料金: {premium_str}\n\n"

        return response

    async def _handle_reminder_list(self, language: str) -> str:
        """List reminders"""
        reminders = self.db.get_reminders(status='pending')

        if not reminders:
            return self._get_response("no_reminders", language)

        if language == "ja":
            response = f"📅 **リマインダー / Reminders ({len(reminders)})**:\n\n"
        else:
            response = f"📅 **Reminders ({len(reminders)})**:\n\n"

        for reminder in reminders[:10]:
            due_str = f"期限: {reminder['due_date']}" if reminder['due_date'] else "期限なし"
            response += f"⏳ {reminder['reminder_type']}\n   {reminder['description']}\n   {due_str}\n\n"

        return response

    def _get_response(self, response_key: str, language: str) -> str:
        """Get predefined response based on language"""
        responses = {
            "unknown": {
                "en": "I'm not sure what you're asking. Try asking about your cars, fuel, maintenance, or say 'help' for more info.",
                "ja": "質問が理解できませんでした。車、給油、メンテナンスについて質問するか、「help」と入力して詳細を確認してください。"
            },
            "vehicle_add_guide": {
                "en": "To add a vehicle, use: `!car vehicle <name> [make] [model] [year]`\nExample: `!car vehicle MyCar Toyota Camry 2020`",
                "ja": "車両を追加するには: `!car vehicle <名前> [メーカー] [モデル] [年]`\n例: `!car vehicle マイカー トヨタ カムリー 2020`"
            },
            "fuel_add_guide": {
                "en": "To add fuel record: `!car fuel <vehicle_id> <odometer> <liters> <price_per_liter>`\nExample: `!car fuel 1 50000 45.5 175`",
                "ja": "給油を記録するには: `!car fuel <車両ID> <走行距離> <給油量L> <価格/L>`\n例: `!car fuel 1 50000 45.5 175`"
            },
            "fuel_stats_guide": {
                "en": "To show fuel stats: `!car fuelstats <vehicle_id> [days]`\nExample: `!car fuelstats 1 30`",
                "ja": "燃料統計を表示するには: `!car fuelstats <車両ID> [日数]`\n例: `!car fuelstats 1 30`"
            },
            "maintenance_add_guide": {
                "en": "To add maintenance: `!car maintenance <vehicle_id> <type> <odometer> [description]`\nExample: `!car maintenance 1 oil_change 51000 Regular oil change`",
                "ja": "メンテナンスを追加するには: `!car maintenance <車両ID> <タイプ> <走行距離> [説明]`\n例: `!car maintenance 1 oil_change 51000 定期オイル交換`"
            },
            "repair_add_guide": {
                "en": "To add repair: `!car repair <vehicle_id> <issue> <odometer> [severity]`\nExample: `!car repair 1 Brake_noise 52500 moderate`",
                "ja": "修理を追加するには: `!car repair <車両ID> <問題> <走行距離> [重要度]`\n例: `!car repair 1 ブレーキ音 52500 moderate`"
            },
            "insurance_add_guide": {
                "en": "To add insurance: `!car insurance <vehicle_id> <provider> <policy_number> <start_date> <end_date>`\nExample: `!car insurance 1 \"Insurance Co\" POL-12345 2024-01-01 2025-01-01`",
                "ja": "保険を追加するには: `!car insurance <車両ID> <保険会社> <証券番号> <開始日> <終了日>`\n例: `!car insurance 1 \"保険会社\" POL-12345 2024-01-01 2025-01-01`"
            },
            "reminder_add_guide": {
                "en": "To add reminder: `!car reminder <vehicle_id> <type> <description> [due_date]`\nExample: `!car reminder 1 inspection Annual inspection 2024-06-01`",
                "ja": "リマインダーを追加するには: `!car reminder <車両ID> <タイプ> <説明> [期限]`\n例: `!car reminder 1 inspection 車検 2024-06-01`"
            },
            "no_vehicles": {
                "en": "📭 No vehicles registered. Add one with `!car vehicle <name>`.",
                "ja": "📭 車両が登録されていません。`!car vehicle <名前>` で追加してください。"
            },
            "no_fuel_records": {
                "en": "📭 No fuel records found.",
                "ja": "📭 給油記録がありません。"
            },
            "no_maintenance": {
                "en": "📭 No maintenance records found.",
                "ja": "📭 メンテナンス記録がありません。"
            },
            "no_repairs": {
                "en": "📭 No repair records found.",
                "ja": "📭 修理記録がありません。"
            },
            "no_insurance": {
                "en": "📭 No insurance records found.",
                "ja": "📭 保険記録がありません。"
            },
            "no_reminders": {
                "en": "📭 No reminders found.",
                "ja": "📭 リマインダーがありません。"
            }
        }

        return responses.get(response_key, {}).get(language, responses[response_key]["en"])

    def _get_help(self, language: str) -> str:
        """Get help message"""
        if language == "ja":
            return (
                "🚗 **Car Agent ヘルプ**\n\n"
                "💬 **会話の例:**\n"
                "• 「車の状況」 - サマリーを表示\n"
                "• 「車一覧を見て」 - 車両を表示\n"
                "• 「給油記録」 - 給油履歴を表示\n"
                "• 「メンテナンス履歴」 - メンテ履歴を表示\n"
                "• 「修理状況」 - 修理記録を表示\n"
                "• 「保険一覧」 - 保険情報を表示\n"
                "• 「リマインダー」 - 予定を表示\n\n"
                "📋 **コマンド:**\n"
                "• `!car summary` - 全体状況を表示\n"
                "• `!car vehicle <name>` - 車両追加\n"
                "• `!car vehicles` - 車両一覧\n"
                "• `!car fuel <id> <odometer> <liters> <price>` - 給油記録\n"
                "• `!car fuels [id]` - 記録一覧\n"
                "• `!car fuelstats <id> [days]` - 統計\n"
                "• `!car maintenance <id> <type> <odometer>` - メンテ追加\n"
                "• `!car maintenances` - 一覧\n"
                "• `!car repair <id> <issue> <odometer>` - 修理追加\n"
                "• `!car repairs` - 一覧\n"
                "• `!car insurance <id> <provider> <policy> <start> <end>` - 保険追加\n"
                "• `!car insurances` - 一覧\n"
                "• `!car reminder <id> <type> <desc> [date]` - 追加\n"
                "• `!car reminders` - 一覧"
            )
        else:
            return (
                "🚗 **Car Agent Help**\n\n"
                "💬 **Conversational Examples:**\n"
                "• \"How are my cars?\" - Show summary\n"
                "• \"Show my vehicles\" - List vehicles\n"
                "• \"Fuel history\" - Show fuel records\n"
                "• \"Maintenance history\" - Show maintenance records\n"
                "• \"Repair status\" - Show repair records\n"
                "• \"Insurance list\" - Show insurance information\n"
                "• \"Reminders\" - Show upcoming items\n\n"
                "📋 **Commands:**\n"
                "• `!car summary` - Show overall status\n"
                "• `!car vehicle <name>` - Add vehicle\n"
                "• `!car vehicles` - List vehicles\n"
                "• `!car fuel <id> <odometer> <liters> <price>` - Add fuel record\n"
                "• `!car fuels [id]` - List fuel records\n"
                "• `!car fuelstats <id> [days]` - Show fuel statistics\n"
                "• `!car maintenance <id> <type> <odometer>` - Add maintenance\n"
                "• `!car maintenances` - List maintenance\n"
                "• `!car repair <id> <issue> <odometer>` - Add repair\n"
                "• `!car repairs` - List repairs\n"
                "• `!car insurance <id> <provider> <policy> <start> <end>` - Add insurance\n"
                "• `!car insurances` - List insurance\n"
                "• `!car reminder <id> <type> <desc> [date]` - Add reminder\n"
                "• `!car reminders` - List reminders"
            )

    # Discord Commands
    @commands.command(name="help", aliases=["ヘルプ", "使い方"])
    async def cmd_help(self, ctx):
        """Show help message"""
        language = self._detect_language(ctx.content)
        await ctx.send(self._get_help(language))

    @commands.command(name="summary", aliases=["概要", "サマリー"])
    async def cmd_summary(self, ctx):
        """Show car management summary"""
        language = self._detect_language(ctx.content)
        response = await self._handle_summary(language)
        await ctx.send(response)

    @commands.command(name="vehicles", aliases=["車両一覧"])
    async def cmd_vehicles(self, ctx, status: str = None):
        """List all vehicles"""
        language = self._detect_language(ctx.content)
        response = await self._handle_vehicle_list(language)
        await ctx.send(response)

    @commands.command(name="fuels", aliases=["給油記録"])
    async def cmd_fuels(self, ctx, vehicle_id: int = None, limit: int = 10):
        """List fuel records"""
        language = self._detect_language(ctx.content)
        response = await self._handle_fuel_list(language)
        await ctx.send(response)

    @commands.command(name="fuelstats", aliases=["燃料統計"])
    async def cmd_fuelstats(self, ctx, vehicle_id: int, days: int = 30):
        """Show fuel statistics"""
        stats = self.db.get_fuel_stats(vehicle_id, days)
        language = self._detect_language(ctx.content)

        if language == "ja":
            response = f"⛽ **燃料統計 / Fuel Statistics ({days}日)**\n\n"
            response += f"給油回数 / Fills: {stats['fill_count']} 回\n"
            response += f"総給油量 / Total Liters: {stats['total_liters']:.1f} L\n"
            response += f"総費用 / Total Cost: ¥{stats['total_cost']:,.2f}\n"
            response += f"平均価格 / Avg Price: ¥{stats['avg_price_per_liter']:.2f}/L"
            if stats['fill_count'] > 1:
                avg_per_fill = stats['total_cost'] / stats['fill_count']
                response += f"\n1回あたり / Per Fill: ¥{avg_per_fill:,.2f}"
        else:
            response = f"⛽ **Fuel Statistics ({days} days)**\n\n"
            response += f"Fills: {stats['fill_count']}\n"
            response += f"Total Liters: {stats['total_liters']:.1f} L\n"
            response += f"Total Cost: ¥{stats['total_cost']:,.2f}\n"
            response += f"Avg Price: ¥{stats['avg_price_per_liter']:.2f}/L"
            if stats['fill_count'] > 1:
                avg_per_fill = stats['total_cost'] / stats['fill_count']
                response += f"\nPer Fill: ¥{avg_per_fill:,.2f}"

        await ctx.send(response)

    @commands.command(name="maintenances", aliases=["メンテナンス一覧"])
    async def cmd_maintenances(self, ctx, vehicle_id: int = None, service_type: str = None):
        """List maintenance records"""
        language = self._detect_language(ctx.content)
        response = await self._handle_maintenance_list(language)
        await ctx.send(response)

    @commands.command(name="repairs", aliases=["修理一覧"])
    async def cmd_repairs(self, ctx, vehicle_id: int = None, status: str = None):
        """List repair records"""
        language = self._detect_language(ctx.content)
        response = await self._handle_repair_list(language)
        await ctx.send(response)

    @commands.command(name="insurances", aliases=["保険一覧"])
    async def cmd_insurances(self, ctx, vehicle_id: int = None):
        """List insurance policies"""
        language = self._detect_language(ctx.content)
        response = await self._handle_insurance_list(language)
        await ctx.send(response)

    @commands.command(name="reminders", aliases=["リマインダー一覧"])
    async def cmd_reminders(self, ctx, vehicle_id: int = None, status: str = None):
        """List reminders"""
        language = self._detect_language(ctx.content)
        response = await self._handle_reminder_list(language)
        await ctx.send(response)


def run_bot(token: str, db_path: str = "car.db"):
    """Run the Discord bot"""
    bot = CarBot(db_path=db_path)
    bot.run(token)


if __name__ == "__main__":
    # For testing purposes
    print("Car Discord Bot Module")
    print("Run with: python discord.py <BOT_TOKEN>")
