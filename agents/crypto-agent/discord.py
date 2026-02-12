#!/usr/bin/env python3
"""
Crypto Agent - Discord Interface
Natural language processing for crypto asset management
日本語と英語対応 / Supports Japanese and English
"""

import re
from typing import Optional, Dict, List

from db import init_db, add_holding, list_holdings, update_price, get_latest_price, add_alert, list_alerts, get_portfolio_value


class CryptoDiscord:
    """Discord interface for crypto agent with NLP"""

    def __init__(self):
        init_db()

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "add_holding":
            return self._handle_add_holding(entities)
        elif intent == "list_holdings":
            return self._handle_list_holdings(entities)
        elif intent == "update_price":
            return self._handle_update_price(entities)
        elif intent == "get_price":
            return self._handle_get_price(entities)
        elif intent == "add_alert":
            return self._handle_add_alert(entities)
        elif intent == "list_alerts":
            return self._handle_list_alerts(entities)
        elif intent == "portfolio_value":
            return self._handle_portfolio_value(entities)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_unknown(message)

    def _parse_intent(self, message: str) -> tuple:
        """Parse intent and entities from message"""
        entities = {}
        lower_msg = message.lower()

        # Add holding
        if re.search(r'(保有|追加|買った|bought|bought|add.*holding|add.*crypto|buy|purchase)', lower_msg):
            entities['symbol'] = self._extract_crypto_symbol(message)
            entities['amount'] = self._extract_amount(message)
            entities['purchase_price'] = self._extract_price(message)
            return "add_holding", entities

        # List holdings
        if re.search(r'(保有|ホールド|持ち株|holdings|my.*crypto|wallet|show.*holding)', lower_msg):
            return "list_holdings", entities

        # Update price
        if re.search(r'(価格更新|価格を更新|update.*price|set.*price|price.*is)', lower_msg):
            entities['symbol'] = self._extract_crypto_symbol(message)
            entities['price'] = self._extract_price(message)
            return "update_price", entities

        # Get price
        if re.search(r'(価格|現在価格|プライス|price|get.*price|show.*price|what.*price)', lower_msg):
            entities['symbol'] = self._extract_crypto_symbol(message)
            return "get_price", entities

        # Add alert
        if re.search(r'(アラート|通知|価格通知|alert|set.*alert|notify|notify.*when)', lower_msg):
            entities['symbol'] = self._extract_crypto_symbol(message)
            entities['target_price'] = self._extract_price(message)
            entities['alert_type'] = self._extract_alert_type(message)
            return "add_alert", entities

        # List alerts
        if re.search(r'(アラート一覧|通知一覧|show.*alert|list.*alert|my.*alert)', lower_msg):
            entities['status'] = self._extract_status(message)
            return "list_alerts", entities

        # Portfolio value
        if re.search(r'(ポートフォリオ|総額|評価額|portfolio|total|value|net worth)', lower_msg):
            return "portfolio_value", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_crypto_symbol(self, message: str) -> Optional[str]:
        """Extract crypto symbol from message"""
        patterns = [
            r'([A-Z]{2,10})',  # Match 2-10 uppercase letters
            r'([a-z]{2,10})',  # Match 2-10 lowercase letters
        ]

        # Common crypto patterns
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol',
                          'cardano', 'ada', 'dogecoin', 'doge', 'ripple', 'xrp']

        lower_msg = message.lower()

        for keyword in crypto_keywords:
            if keyword in lower_msg:
                if keyword in ['bitcoin', 'btc']:
                    return 'BTC'
                elif keyword in ['ethereum', 'eth']:
                    return 'ETH'
                elif keyword in ['solana', 'sol']:
                    return 'SOL'
                elif keyword in ['cardano', 'ada']:
                    return 'ADA'
                elif keyword in ['dogecoin', 'doge']:
                    return 'DOGE'
                elif keyword in ['ripple', 'xrp']:
                    return 'XRP'

        # Try generic patterns
        for pattern in patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                # Filter out common words
                if match.lower() not in ['is', 'are', 'and', 'or', 'the', 'to', 'of', 'in', 'at']:
                    return match.upper()

        return None

    def _extract_amount(self, message: str) -> Optional[float]:
        """Extract amount from message"""
        patterns = [
            r'(\d+\.?\d*)\s*(?:個|枚|coins?|tokens?)',
            r'(\d+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return float(match.group(1))
        return None

    def _extract_price(self, message: str) -> Optional[float]:
        """Extract price from message"""
        patterns = [
            r'価格[:\s]+(\d+\.?\d*)',
            r'price[:\s]+(\d+\.?\d*)',
            r'\$\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:ドル|$|usd)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_alert_type(self, message: str) -> str:
        """Extract alert type (above/below)"""
        lower_msg = message.lower()
        if re.search(r'(以上|上回る|above|higher)', lower_msg):
            return 'above'
        elif re.search(r'(以下|下回る|below|lower)', lower_msg):
            return 'below'
        return 'above'  # Default

    def _extract_status(self, message: str) -> Optional[str]:
        """Extract alert status filter"""
        lower_msg = message.lower()
        if re.search(r'(有効|active|open)', lower_msg):
            return 'active'
        elif re.search(r'(トリガー済み|triggered|fired)', lower_msg):
            return 'triggered'
        return None

    def _handle_add_holding(self, entities: Dict) -> str:
        """Handle adding crypto holding"""
        symbol = entities.get('symbol')
        amount = entities.get('amount')

        if not symbol or not amount:
            return "シンボルと数量を指定してください。例: BTC 0.5を買った / Bought 0.5 BTC"

        purchase_price = entities.get('purchase_price')

        holding_id = add_holding(symbol, amount, purchase_price)

        price_text = f"、購入価格: ${purchase_price}" if purchase_price else ""
        return f"✅ {symbol} {amount}個を追加しました{price_text}"

    def _handle_list_holdings(self, entities: Dict) -> str:
        """Handle listing holdings"""
        holdings = list_holdings()

        if not holdings:
            return "保有資産はありません / No holdings found"

        response = f"💰 **保有資産** / **Holdings** ({len(holdings)}件):\n\n"
        for h in holdings:
            id, symbol, amount, purchase_price, purchase_date = h
            price_text = f" (購入価格: ${purchase_price})" if purchase_price else ""
            response += f"{symbol}: {amount}個{price_text}\n"

        return response

    def _handle_update_price(self, entities: Dict) -> str:
        """Handle updating crypto price"""
        symbol = entities.get('symbol')
        price = entities.get('price')

        if not symbol or not price:
            return "シンボルと価格を指定してください。例: BTCの価格を$50000に更新"

        update_price(symbol, price)
        return f"✅ {symbol} の価格を ${price} に更新しました"

    def _handle_get_price(self, entities: Dict) -> str:
        """Handle getting crypto price"""
        symbol = entities.get('symbol')

        if not symbol:
            return "シンボルを指定してください。例: BTCの価格は？"

        latest = get_latest_price(symbol)

        if not latest:
            return f"{symbol} の価格データが見つかりません"

        price, timestamp = latest
        return f"💹 **{symbol}** 価格: ${price}\n更新時刻: {timestamp}"

    def _handle_add_alert(self, entities: Dict) -> str:
        """Handle adding price alert"""
        symbol = entities.get('symbol')
        target_price = entities.get('target_price')

        if not symbol or not target_price:
            return "シンボルと目標価格を指定してください。例: BTCが$55000以上になったら通知"

        alert_type = entities.get('alert_type', 'above')

        alert_id = add_alert(symbol, target_price, alert_type)

        type_text = "以上" if alert_type == 'above' else "以下"
        return f"🔔 {symbol} が ${target_price}{type_text}になったら通知します (ID: {alert_id})"

    def _handle_list_alerts(self, entities: Dict) -> str:
        """Handle listing alerts"""
        status = entities.get('status', 'active')
        alerts = list_alerts(status)

        if not alerts:
            return "アラートはありません / No alerts found"

        response = f"🔔 **アラート一覧** / **Alerts** ({len(alerts)}件):\n\n"
        for a in alerts:
            id, symbol, target_price, alert_type, a_status, created_at = a
            type_text = "↑ 以上" if alert_type == 'above' else "↓ 以下"
            response += f"#{id} {symbol} ${target_price}{type_text}\n"

        return response

    def _handle_portfolio_value(self, entities: Dict) -> str:
        """Handle portfolio value calculation"""
        portfolio = get_portfolio_value()

        if not portfolio['details']:
            return "ポートフォリオが空です"

        response = f"💼 **ポートフォリオ評価額** / **Portfolio Value**\n\n"
        response += f"総額: ${portfolio['total']:.2f}\n\n"
        response += "内訳:\n"

        for d in portfolio['details']:
            response += f"  • {d['symbol']}: {d['amount']}個 × ${d['current_price']:.2f} = ${d['value']:.2f}\n"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
💰 **Crypto Agent ヘルプ**

**保有資産管理 / Holdings:**
• BTC 0.5を買った - Add BTC holding
• 保有資産を表示 - Show holdings

**価格管理 / Prices:**
• BTCの価格を$50000に更新 - Update BTC price
• BTCの価格は？ - Get BTC price
• ETHの現在価格 - Get ETH price

**アラート / Alerts:**
• BTCが$55000以上になったら通知 - Set alert above $55000
• ETHが$3000以下になったら通知 - Set alert below $3000
• アラート一覧を表示 - Show alerts

**ポートフォリオ / Portfolio:**
• ポートフォリオ評価額 - Show total portfolio value

**English support:**
• Bought 0.5 BTC at $50000
• Show my holdings
• Update ETH price to $3000
• What's the price of BTC?
• Set alert when SOL goes above $150
• Show portfolio value
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return "すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します / Sorry, I didn't understand that command. Type 'help' for usage."


# Test examples
if __name__ == '__main__':
    agent = CryptoDiscord()

    # Test adding holdings
    print(agent.process_message("BTC 0.5を買った 価格$45000"))
    print(agent.process_message("ETH 3個を買った"))

    # Test listing holdings
    print("\n--- Holdings ---")
    print(agent.process_message("保有資産を表示"))

    # Test price updates
    print("\n--- Price Updates ---")
    print(agent.process_message("BTCの価格を$50000に更新"))
    print(agent.process_message("ETHの価格を$3000に更新"))

    # Test getting prices
    print("\n--- Get Prices ---")
    print(agent.process_message("BTCの価格は？"))

    # Test alerts
    print("\n--- Alerts ---")
    print(agent.process_message("BTCが$55000以上になったら通知"))
    print(agent.process_message("アラート一覧を表示"))

    # Test portfolio
    print("\n--- Portfolio ---")
    print(agent.process_message("ポートフォリオ評価額"))

    # Test help
    print("\n--- Help ---")
    print(agent.process_message("ヘルプ"))
