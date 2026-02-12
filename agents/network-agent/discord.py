"""
network-agent/discord.py
Discord bot for network agent with NLP-based message processing
ネットワーク管理エージェント - 自然言語処理付きDiscordボット
Supports Japanese and English languages
"""

import discord
from discord.ext import commands
import re
from typing import Optional, Dict
from db import NetworkDatabase


class NetworkBot(commands.Bot):
    """Network Management Discord bot with NLP-based intent recognition"""

    def __init__(self, db_path: str = "network.db", command_prefix: str = "!net "):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = NetworkDatabase(db_path)

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"{self.user} is ready!")
        activity = discord.Activity(type=discord.ActivityType.watching, name="your network")
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        """Process incoming messages"""
        if message.author == self.user:
            return

        # Process commands first
        await self.process_commands(message)

        # Process natural language messages
        if message.content and not message.content.startswith("!net "):
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

    def _analyze_intent(self, message: str, language: str):
        """
        Analyze message to determine intent and extract entities
        Returns (intent, entities) tuple
        """
        message_lower = message.lower()

        # Define intent patterns for English
        if language == "en":
            intents = {
                "summary": {
                    "keywords": ["summary", "overview", "status", "network status"],
                    "patterns": [
                        r"network.*summary",
                        r"how.*is.*my.*network",
                        r"network.*overview"
                    ]
                },
                "wifi_add": {
                    "keywords": ["add wifi", "new wifi", "register wifi", "add network"],
                    "patterns": [
                        r"add.*wifi",
                        r"new.*wifi.*network",
                        r"register.*wifi"
                    ]
                },
                "wifi_list": {
                    "keywords": ["wifi", "networks", "show wifi", "my wifi"],
                    "patterns": [
                        r"show.*wifi",
                        r"list.*networks",
                        r"my.*wifi.*networks"
                    ]
                },
                "device_add": {
                    "keywords": ["add device", "new device", "register device"],
                    "patterns": [
                        r"add.*device",
                        r"new.*network.*device",
                        r"register.*device"
                    ]
                },
                "device_list": {
                    "keywords": ["devices", "list devices", "my devices", "network devices"],
                    "patterns": [
                        r"show.*devices",
                        r"list.*devices",
                        r"my.*network.*devices"
                    ]
                },
                "port_add": {
                    "keywords": ["add port", "port forward", "forward port", "open port"],
                    "patterns": [
                        r"add.*port.*forward",
                        r"forward.*port",
                        r"open.*port"
                    ]
                },
                "port_list": {
                    "keywords": ["port forwards", "forwarded ports", "port forwarding"],
                    "patterns": [
                        r"show.*port.*forwards",
                        r"list.*port.*forwarding",
                        r"forwarded.*ports"
                    ]
                },
                "vpn_add": {
                    "keywords": ["add vpn", "new vpn", "setup vpn", "configure vpn"],
                    "patterns": [
                        r"add.*vpn",
                        r"new.*vpn.*config",
                        r"setup.*vpn"
                    ]
                },
                "vpn_list": {
                    "keywords": ["vpn", "vpns", "my vpn", "vpn configs"],
                    "patterns": [
                        r"show.*vpn",
                        r"list.*vpns",
                        r"my.*vpn.*configs"
                    ]
                },
                "dns_add": {
                    "keywords": ["add dns", "new dns", "set dns"],
                    "patterns": [
                        r"add.*dns",
                        r"new.*dns.*setting",
                        r"set.*dns"
                    ]
                },
                "dns_list": {
                    "keywords": ["dns", "dns settings", "my dns"],
                    "patterns": [
                        r"show.*dns",
                        r"list.*dns",
                        r"my.*dns.*settings"
                    ]
                },
                "password_add": {
                    "keywords": ["add password", "new password", "save password", "store password"],
                    "patterns": [
                        r"add.*password",
                        r"save.*password",
                        r"store.*password"
                    ]
                },
                "password_list": {
                    "keywords": ["passwords", "list passwords", "my passwords", "password vault"],
                    "patterns": [
                        r"show.*passwords",
                        r"list.*passwords",
                        r"my.*passwords"
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
                    "keywords": ["サマリー", "概要", "状況", "ステータス", "ネットワーク状況"],
                    "patterns": [
                        r"ネットワーク.*状況",
                        r"サマリー見て",
                        r"どうなってる",
                        r"ネットワーク.*概要"
                    ]
                },
                "wifi_add": {
                    "keywords": ["wifi追加", "wifi追加", "wifi登録", "新規wifi"],
                    "patterns": [
                        r"wifi.*追加",
                        r"wifi.*登録",
                        r"新しい.*wifi"
                    ]
                },
                "wifi_list": {
                    "keywords": ["wifi一覧", "wifiリスト", "wifi見て", "ネットワーク一覧"],
                    "patterns": [
                        r"wifi.*一覧",
                        r"wifi.*見て",
                        r"ネットワーク.*一覧"
                    ]
                },
                "device_add": {
                    "keywords": ["デバイス追加", "機器追加", "機器登録", "新しいデバイス"],
                    "patterns": [
                        r"デバイス.*追加",
                        r"機器.*登録",
                        r"新しい.*デバイス"
                    ]
                },
                "device_list": {
                    "keywords": ["デバイス一覧", "機器一覧", "デバイス見て", "接続機器"],
                    "patterns": [
                        r"デバイス.*一覧",
                        r"機器.*一覧",
                        r"接続.*機器"
                    ]
                },
                "port_add": {
                    "keywords": ["ポート追加", "ポート開放", "ポート転送", "フォワード"],
                    "patterns": [
                        r"ポート.*追加",
                        r"ポート.*開放",
                        r"ポート.*転送"
                    ]
                },
                "port_list": {
                    "keywords": ["ポート一覧", "ポート転送", "フォワード一覧"],
                    "patterns": [
                        r"ポート.*一覧",
                        r"ポート.*転送.*見て"
                    ]
                },
                "vpn_add": {
                    "keywords": ["vpn追加", "vpn設定", "vpnセットアップ", "新しいvpn"],
                    "patterns": [
                        r"vpn.*追加",
                        r"vpn.*設定",
                        r"vpn.*セットアップ"
                    ]
                },
                "vpn_list": {
                    "keywords": ["vpn一覧", "vpnリスト", "vpn見て"],
                    "patterns": [
                        r"vpn.*一覧",
                        r"vpn.*見て",
                        r"設定.*vpn"
                    ]
                },
                "dns_add": {
                    "keywords": ["dns追加", "dns設定", "dns変更"],
                    "patterns": [
                        r"dns.*追加",
                        r"dns.*設定",
                        r"dns.*変更"
                    ]
                },
                "dns_list": {
                    "keywords": ["dns一覧", "dnsリスト", "dns見て"],
                    "patterns": [
                        r"dns.*一覧",
                        r"dns.*見て",
                        r"dns.*設定.*見て"
                    ]
                },
                "password_add": {
                    "keywords": ["パスワード追加", "パスワード保存", "新しいパスワード"],
                    "patterns": [
                        r"パスワード.*追加",
                        r"パスワード.*保存",
                        r"新しい.*パスワード"
                    ]
                },
                "password_list": {
                    "keywords": ["パスワード一覧", "パスワードリスト", "パスワード見て", "パスワード保管"],
                    "patterns": [
                        r"パスワード.*一覧",
                        r"パスワード.*見て",
                        r"保管.*パスワード"
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

            # Extract entities
            if score > 0:
                entities = self._extract_entities(message, intent_name)

            if score > best_score:
                best_score = score
                best_intent = intent_name

        return best_intent, entities

    def _extract_entities(self, message: str, intent: str) -> Dict:
        """Extract entities from message based on intent"""
        entities = {}

        # Extract SSID for WiFi
        if intent == "wifi_add":
            ssid_match = re.search(r'ssid[:=]\s*"?([^"\s]+)"?', message, re.IGNORECASE)
            if ssid_match:
                entities["ssid"] = ssid_match.group(1)

        # Extract IP addresses
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', message)
        if ip_match:
            entities["ip"] = ip_match.group(1)

        # Extract ports
        port_match = re.search(r'port[:=]?\s*(\d+)', message, re.IGNORECASE)
        if port_match:
            entities["port"] = int(port_match.group(1))

        # Extract protocol
        if re.search(r'\btcp\b', message, re.IGNORECASE):
            entities["protocol"] = "TCP"
        elif re.search(r'\budp\b', message, re.IGNORECASE):
            entities["protocol"] = "UDP"

        return entities

    async def _handle_intent(self, intent: str, entities: Dict, message: str,
                            language: str, user_id: str) -> Optional[str]:
        """Handle identified intent and return response"""

        if intent == "unknown":
            return self._get_response("unknown", language)

        if intent == "summary":
            return await self._handle_summary(language, user_id)

        if intent == "wifi_add":
            return self._get_response("wifi_add_guide", language)

        if intent == "wifi_list":
            return await self._handle_wifi_list(language, user_id)

        if intent == "device_add":
            return self._get_response("device_add_guide", language)

        if intent == "device_list":
            return await self._handle_device_list(language, user_id)

        if intent == "port_add":
            return self._get_response("port_add_guide", language)

        if intent == "port_list":
            return await self._handle_port_list(language, user_id)

        if intent == "vpn_add":
            return self._get_response("vpn_add_guide", language)

        if intent == "vpn_list":
            return await self._handle_vpn_list(language, user_id)

        if intent == "dns_add":
            return self._get_response("dns_add_guide", language)

        if intent == "dns_list":
            return await self._handle_dns_list(language, user_id)

        if intent == "password_add":
            return self._get_response("password_add_guide", language)

        if intent == "password_list":
            return await self._handle_password_list(language, user_id)

        if intent == "help":
            return self._get_help(language)

        return self._get_response("unknown", language)

    async def _handle_summary(self, language: str, user_id: str) -> str:
        """Get network management summary"""
        summary = self.db.get_summary(user_id)

        if language == "ja":
            return (
                f"🌐 **ネットワーク管理サマリー / Network Summary**\n\n"
                f"📶 WiFiネットワーク / Networks: {summary['wifi_count']}\n"
                f"📱 デバイス / Devices: {summary['device_count']}\n"
                f"🔀 ポート転送 / Port Forwards: {summary['enabled_port_forward_count']}/{summary['port_forward_count']}\n"
                f"🔒 VPN / VPNs: {summary['active_vpn_count']}/{summary['vpn_count']}\n"
                f"🔑 パスワード / Passwords: {summary['password_count']}"
            )
        else:
            return (
                f"🌐 **Network Summary**\n\n"
                f"📶 WiFi Networks: {summary['wifi_count']}\n"
                f"📱 Devices: {summary['device_count']}\n"
                f"🔀 Port Forwards: {summary['enabled_port_forward_count']}/{summary['port_forward_count']}\n"
                f"🔒 VPNs: {summary['active_vpn_count']}/{summary['vpn_count']}\n"
                f"🔑 Passwords: {summary['password_count']}"
            )

    async def _handle_wifi_list(self, language: str, user_id: str) -> str:
        """List WiFi networks"""
        networks = self.db.get_all_wifi(user_id)

        if not networks:
            return self._get_response("no_wifi", language)

        if language == "ja":
            response = f"📶 **WiFiネットワーク / WiFi Networks ({len(networks)})**:\n\n"
        else:
            response = f"📶 **WiFi Networks ({len(networks)})**:\n\n"

        for net in networks:
            primary = "⭐ " if net['is_primary'] else ""
            freq = "5GHz" if net['frequency_5ghz'] else "2.4GHz"
            location = f" | 場所: {net['location']}" if net['location'] else ""
            response += f"{primary}📶 **{net['ssid']}**\n   暗号化: {net['security_type']} | 周波数: {freq}{location}\n\n"

        return response

    async def _handle_device_list(self, language: str, user_id: str) -> str:
        """List network devices"""
        devices = self.db.get_all_devices(user_id)

        if not devices:
            return self._get_response("no_devices", language)

        if language == "ja":
            response = f"📱 **ネットワークデバイス / Devices ({len(devices)})**:\n\n"
        else:
            response = f"📱 **Devices ({len(devices)})**:\n\n"

        for dev in devices:
            ip = f" | IP: {dev['ip_address']}" if dev['ip_address'] else ""
            mac = f" | MAC: {dev['mac_address']}" if dev['mac_address'] else ""
            dev_type = f" ({dev['device_type']})" if dev['device_type'] else ""
            response += f"📱 **{dev['name']}**{dev_type}\n   メーカー: {dev['manufacturer'] or 'N/A'}{ip}{mac}\n\n"

        return response

    async def _handle_port_list(self, language: str, user_id: str) -> str:
        """List port forwards"""
        ports = self.db.get_all_port_forwards(user_id)

        if not ports:
            return self._get_response("no_ports", language)

        if language == "ja":
            response = f"🔀 **ポート転送 / Port Forwards ({len(ports)})**:\n\n"
        else:
            response = f"🔀 **Port Forwards ({len(ports)})**:\n\n"

        for port in ports:
            status = "✅ " if port['enabled'] else "❌ "
            response += f"{status}🔀 **{port['service_name']}**\n   外部ポート: {port['external_port']} → 内部: {port['internal_ip']}:{port['internal_port']} ({port['protocol']})\n\n"

        return response

    async def _handle_vpn_list(self, language: str, user_id: str) -> str:
        """List VPN configurations"""
        vpns = self.db.get_all_vpns(user_id)

        if not vpns:
            return self._get_response("no_vpns", language)

        if language == "ja":
            response = f"🔒 **VPN設定 / VPN Configs ({len(vpns)})**:\n\n"
        else:
            response = f"🔒 **VPN Configs ({len(vpns)})**:\n\n"

        for vpn in vpns:
            status = "✅ " if vpn['is_active'] else ""
            provider = f" | プロバイダ: {vpn['provider']}" if vpn['provider'] else ""
            response += f"{status}🔒 **{vpn['name']}**\n   サーバー: {vpn['server_address'] or 'N/A'} | プロトコル: {vpn['protocol']}{provider}\n\n"

        return response

    async def _handle_dns_list(self, language: str, user_id: str) -> str:
        """List DNS configurations"""
        dns_list = self.db.get_all_dns(user_id)

        if not dns_list:
            return self._get_response("no_dns", language)

        if language == "ja":
            response = f"🔍 **DNS設定 / DNS Settings ({len(dns_list)})**:\n\n"
        else:
            response = f"🔍 **DNS Settings ({len(dns_list)})**:\n\n"

        for dns in dns_list:
            default = "⭐ " if dns['is_default'] else ""
            secondary = f" | セカンダリ: {dns['secondary_dns']}" if dns['secondary_dns'] else ""
            response += f"{default}🔍 **{dns['name']}**\n   プライマリ: {dns['primary_dns']}{secondary}\n\n"

        return response

    async def _handle_password_list(self, language: str, user_id: str) -> str:
        """List passwords (without actual passwords for security)"""
        passwords = self.db.get_all_passwords(user_id)

        if not passwords:
            return self._get_response("no_passwords", language)

        if language == "ja":
            response = f"🔑 **パスワード保管 / Password Vault ({len(passwords)})**:\n\n"
        else:
            response = f"🔑 **Password Vault ({len(passwords)})**:\n\n"

        for pwd in passwords:
            url = f"\n   URL: {pwd['url']}" if pwd['url'] else ""
            username = f" | ユーザー: {pwd['username']}" if pwd['username'] else ""
            response += f"🔑 **{pwd['service_name']}**\n   カテゴリ: {pwd['category']}{username}{url}\n\n"

        return response

    def _get_response(self, response_key: str, language: str) -> str:
        """Get predefined response based on language"""
        responses = {
            "unknown": {
                "en": "I'm not sure what you're asking. Try asking about WiFi, devices, port forwarding, VPNs, or say 'help' for more info.",
                "ja": "質問が理解できませんでした。WiFi、デバイス、ポート転送、VPNについて質問するか、「help」と入力して詳細を確認してください。"
            },
            "wifi_add_guide": {
                "en": "To add a WiFi network, use: `!net wifi add <ssid> <password>`\nExample: `!net wifi add MyHomeWifi mypassword123`",
                "ja": "WiFiを追加するには: `!net wifi add <SSID> <パスワード>`\n例: `!net wifi add MyHomeWifi mypassword123`"
            },
            "device_add_guide": {
                "en": "To add a device, use: `!net device add <name> [mac_address] [ip_address] [type]`\nExample: `!net device add \"My Laptop\" AA:BB:CC:DD:EE:FF 192.168.1.100 laptop`",
                "ja": "デバイスを追加するには: `!net device add <名前> [MACアドレス] [IPアドレス] [タイプ]`\n例: `!net device add \"マイPC\" AA:BB:CC:DD:EE:FF 192.168.1.100 laptop`"
            },
            "port_add_guide": {
                "en": "To add a port forward, use: `!net port add <name> <external_port> <internal_port> <internal_ip> [protocol]`\nExample: `!net port add \"Web Server\" 80 80 192.168.1.50 TCP`",
                "ja": "ポート転送を追加するには: `!net port add <名前> <外部ポート> <内部ポート> <内部IP> [プロトコル]`\n例: `!net port add \"Webサーバー\" 80 80 192.168.1.50 TCP`"
            },
            "vpn_add_guide": {
                "en": "To add a VPN, use: `!net vpn add <name> <server_address> [username] [password] [provider]`\nExample: `!net vpn add \"Office VPN\" vpn.company.com user pass123`",
                "ja": "VPNを追加するには: `!net vpn add <名前> <サーバーアドレス> [ユーザー名] [パスワード] [プロバイダ]`\n例: `!net vpn add \"オフィスVPN\" vpn.company.com user pass123`"
            },
            "dns_add_guide": {
                "en": "To add a DNS setting, use: `!net dns add <name> <primary_dns> [secondary_dns] [type]`\nExample: `!net dns add \"Google DNS\" 8.8.8.8 8.8.4.4 home`",
                "ja": "DNS設定を追加するには: `!net dns add <名前> <プライマリDNS> [セカンダリDNS] [タイプ]`\n例: `!net dns add \"Google DNS\" 8.8.8.8 8.8.4.4 home`"
            },
            "password_add_guide": {
                "en": "To add a password, use: `!net password add <service_name> <password> [username] [url] [category]`\nExample: `!net password add \"Router Admin\" mypass123 admin 192.168.1.1 network`",
                "ja": "パスワードを追加するには: `!net password add <サービス名> <パスワード> [ユーザー名] [URL] [カテゴリ]`\n例: `!net password add \"ルーター管理\" mypass123 admin 192.168.1.1 network`"
            },
            "no_wifi": {
                "en": "📭 No WiFi networks registered. Add one with `!net wifi add <ssid> <password>`.",
                "ja": "📭 WiFiネットワークが登録されていません。`!net wifi add <SSID> <パスワード>` で追加してください。"
            },
            "no_devices": {
                "en": "📭 No devices registered. Add one with `!net device add <name>`.",
                "ja": "📭 デバイスが登録されていません。`!net device add <名前>` で追加してください。"
            },
            "no_ports": {
                "en": "📭 No port forwards configured.",
                "ja": "📭 ポート転送が設定されていません。"
            },
            "no_vpns": {
                "en": "📭 No VPN configurations found.",
                "ja": "📭 VPN設定が見つかりません。"
            },
            "no_dns": {
                "en": "📭 No DNS settings configured.",
                "ja": "📭 DNS設定がありません。"
            },
            "no_passwords": {
                "en": "📭 No passwords stored in vault.",
                "ja": "📭 パスワード保管庫に保存されたパスワードがありません。"
            }
        }

        return responses.get(response_key, {}).get(language, responses[response_key]["en"])

    def _get_help(self, language: str) -> str:
        """Get help message"""
        if language == "ja":
            return (
                "🌐 **Network Agent ヘルプ**\n\n"
                "💬 **会話の例:**\n"
                "• 「ネットワークの状況」 - サマリーを表示\n"
                "• 「WiFi一覧を見て」 - WiFiネットワークを表示\n"
                "• 「デバイス一覧」 - デバイスを表示\n"
                "• 「ポート転送一覧」 - ポート転送設定を表示\n"
                "• 「VPN一覧」 - VPN設定を表示\n"
                "• 「DNS設定」 - DNSを表示\n"
                "• 「パスワード一覧」 - 保管されたパスワードを表示\n\n"
                "📋 **コマンド:**\n"
                "• `!net summary` - 全体状況を表示\n"
                "• `!net wifi add <ssid> <password>` - WiFi追加\n"
                "• `!net wifi list` - WiFi一覧\n"
                "• `!net device add <name> [mac] [ip] [type]` - デバイス追加\n"
                "• `!net device list` - デバイス一覧\n"
                "• `!net port add <name> <ext> <int> <ip> [proto]` - ポート転送追加\n"
                "• `!net port list` - ポート転送一覧\n"
                "• `!net vpn add <name> <server> [user] [pass]` - VPN追加\n"
                "• `!net vpn list` - VPN一覧\n"
                "• `!net dns add <name> <primary> [secondary]` - DNS追加\n"
                "• `!net dns list` - DNS一覧\n"
                "• `!net password add <service> <password>` - パスワード追加\n"
                "• `!net password list` - パスワード一覧"
            )
        else:
            return (
                "🌐 **Network Agent Help**\n\n"
                "💬 **Conversational Examples:**\n"
                "• \"How is my network?\" - Show summary\n"
                "• \"Show my WiFi\" - List WiFi networks\n"
                "• \"Device list\" - List devices\n"
                "• \"Port forwards\" - Show port forwarding\n"
                "• \"VPN configs\" - Show VPN settings\n"
                "• \"DNS settings\" - Show DNS\n"
                "• \"My passwords\" - Show stored passwords\n\n"
                "📋 **Commands:**\n"
                "• `!net summary` - Show overall status\n"
                "• `!net wifi add <ssid> <password>` - Add WiFi\n"
                "• `!net wifi list` - List WiFi\n"
                "• `!net device add <name> [mac] [ip] [type]` - Add device\n"
                "• `!net device list` - List devices\n"
                "• `!net port add <name> <ext> <int> <ip> [proto]` - Add port forward\n"
                "• `!net port list` - List port forwards\n"
                "• `!net vpn add <name> <server> [user] [pass]` - Add VPN\n"
                "• `!net vpn list` - List VPNs\n"
                "• `!net dns add <name> <primary> [secondary]` - Add DNS\n"
                "• `!net dns list` - List DNS\n"
                "• `!net password add <service> <password>` - Add password\n"
                "• `!net password list` - List passwords"
            )

    # Discord Commands
    @commands.command(name="help", aliases=["ヘルプ", "使い方"])
    async def cmd_help(self, ctx):
        """Show help message"""
        language = self._detect_language(ctx.content)
        await ctx.send(self._get_help(language))

    @commands.group(name="wifi")
    async def cmd_wifi(self, ctx):
        """WiFi commands"""
        if ctx.invoked_subcommand is None:
            language = self._detect_language(ctx.content)
            response = await self._handle_wifi_list(language, str(ctx.author.id))
            await ctx.send(response)

    @cmd_wifi.command(name="add")
    async def cmd_wifi_add(self, ctx, ssid: str, password: str):
        """Add a WiFi network"""
        wifi_id = self.db.add_wifi(str(ctx.author.id), ssid, password)
        await ctx.send(f"📶 WiFiを追加しました (ID: {wifi_id}): {ssid}")

    @cmd_wifi.command(name="list")
    async def cmd_wifi_list(self, ctx):
        """List WiFi networks"""
        language = self._detect_language(ctx.content)
        response = await self._handle_wifi_list(language, str(ctx.author.id))
        await ctx.send(response)

    @commands.group(name="device")
    async def cmd_device(self, ctx):
        """Device commands"""
        if ctx.invoked_subcommand is None:
            language = self._detect_language(ctx.content)
            response = await self._handle_device_list(language, str(ctx.author.id))
            await ctx.send(response)

    @cmd_device.command(name="add")
    async def cmd_device_add(self, ctx, name: str, mac: str = None, ip: str = None, dev_type: str = None):
        """Add a device"""
        device_id = self.db.add_device(str(ctx.author.id), name, mac, ip, dev_type)
        await ctx.send(f"📱 デバイスを追加しました (ID: {device_id}): {name}")

    @cmd_device.command(name="list")
    async def cmd_device_list(self, ctx):
        """List devices"""
        language = self._detect_language(ctx.content)
        response = await self._handle_device_list(language, str(ctx.author.id))
        await ctx.send(response)

    @commands.group(name="port")
    async def cmd_port(self, ctx):
        """Port forward commands"""
        if ctx.invoked_subcommand is None:
            language = self._detect_language(ctx.content)
            response = await self._handle_port_list(language, str(ctx.author.id))
            await ctx.send(response)

    @cmd_port.command(name="add")
    async def cmd_port_add(self, ctx, name: str, ext_port: int, int_port: int, int_ip: str, protocol: str = "TCP"):
        """Add a port forward"""
        pf_id = self.db.add_port_forward(str(ctx.author.id), name, ext_port, int_port, int_ip, protocol)
        await ctx.send(f"🔀 ポート転送を追加しました (ID: {pf_id}): {name} ({ext_port} → {int_ip}:{int_port})")

    @cmd_port.command(name="list")
    async def cmd_port_list(self, ctx):
        """List port forwards"""
        language = self._detect_language(ctx.content)
        response = await self._handle_port_list(language, str(ctx.author.id))
        await ctx.send(response)

    @commands.group(name="vpn")
    async def cmd_vpn(self, ctx):
        """VPN commands"""
        if ctx.invoked_subcommand is None:
            language = self._detect_language(ctx.content)
            response = await self._handle_vpn_list(language, str(ctx.author.id))
            await ctx.send(response)

    @cmd_vpn.command(name="add")
    async def cmd_vpn_add(self, ctx, name: str, server: str, user: str = None, password: str = None, provider: str = None):
        """Add a VPN configuration"""
        vpn_id = self.db.add_vpn(str(ctx.author.id), name, provider, server, user, password)
        await ctx.send(f"🔒 VPNを追加しました (ID: {vpn_id}): {name}")

    @cmd_vpn.command(name="list")
    async def cmd_vpn_list(self, ctx):
        """List VPN configurations"""
        language = self._detect_language(ctx.content)
        response = await self._handle_vpn_list(language, str(ctx.author.id))
        await ctx.send(response)

    @commands.group(name="dns")
    async def cmd_dns(self, ctx):
        """DNS commands"""
        if ctx.invoked_subcommand is None:
            language = self._detect_language(ctx.content)
            response = await self._handle_dns_list(language, str(ctx.author.id))
            await ctx.send(response)

    @cmd_dns.command(name="add")
    async def cmd_dns_add(self, ctx, name: str, primary: str, secondary: str = None, net_type: str = "home"):
        """Add a DNS configuration"""
        dns_id = self.db.add_dns(str(ctx.author.id), name, primary, secondary, net_type)
        await ctx.send(f"🔍 DNSを追加しました (ID: {dns_id}): {name}")

    @cmd_dns.command(name="list")
    async def cmd_dns_list(self, ctx):
        """List DNS configurations"""
        language = self._detect_language(ctx.content)
        response = await self._handle_dns_list(language, str(ctx.author.id))
        await ctx.send(response)

    @commands.group(name="password")
    async def cmd_password(self, ctx):
        """Password vault commands"""
        if ctx.invoked_subcommand is None:
            language = self._detect_language(ctx.content)
            response = await self._handle_password_list(language, str(ctx.author.id))
            await ctx.send(response)

    @cmd_password.command(name="add")
    async def cmd_password_add(self, ctx, service: str, password: str, user: str = None, url: str = None, category: str = "network"):
        """Add a password"""
        pwd_id = self.db.add_password(str(ctx.author.id), service, password, user, url, category)
        await ctx.send(f"🔑 パスワードを保存しました (ID: {pwd_id}): {service}")

    @cmd_password.command(name="list")
    async def cmd_password_list(self, ctx):
        """List passwords"""
        language = self._detect_language(ctx.content)
        response = await self._handle_password_list(language, str(ctx.author.id))
        await ctx.send(response)


def run_bot(token: str, db_path: str = "network.db"):
    """Run the Discord bot"""
    bot = NetworkBot(db_path=db_path)
    bot.run(token)


if __name__ == "__main__":
    # For testing purposes
    print("Network Discord Bot Module")
    print("Run with: python discord.py <BOT_TOKEN>")
