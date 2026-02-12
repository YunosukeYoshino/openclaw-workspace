#!/usr/bin/env python3
"""
NLP Integration Module
NLP統合 - 自然言語処理・意図認識
"""

from typing import Dict, Any, List, Optional
import re


class NLPProcessor:
    """NLPプロセッサー"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.intent_patterns = {}
        self.entities = {}

    def register_intent(self, intent_name: str, patterns: List[str]):
        """意図を登録"""
        self.intent_patterns[intent_name] = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in patterns
        ]

    def extract_intent(self, text: str) -> Optional[str]:
        """意図を抽出"""
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return intent_name
        return None

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """エンティティを抽出"""
        entities = {}

        # 日付抽出
        date_patterns = r'\b(今日|明日|来週|今週|来月|今月)\b'
        dates = re.findall(date_patterns, text)
        if dates:
            entities['dates'] = dates

        # 数値抽出
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]

        return entities

    def tokenize(self, text: str) -> List[str]:
        """トークン化"""
        return text.split()

    def normalize_text(self, text: str) -> str:
        """テキストを正規化"""
        # 小文字化
        text = text.lower()
        # 余分なスペース削除
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class SentimentAnalyzer:
    """感情分析クラス"""

    def __init__(self):
        self.positive_words = ['嬉しい', '楽しい', 'いい', '好き', 'ありがとう', 'great', 'good', 'thanks']
        self.negative_words = ['悲しい', '嫌い', '悪い', '駄目', 'bad', 'hate', 'sorry']

    def analyze(self, text: str) -> Dict[str, Any]:
        """感情を分析"""
        text = text.lower()
        positive_score = sum(1 for word in self.positive_words if word in text)
        negative_score = sum(1 for word in self.negative_words if word in text)

        if positive_score > negative_score:
            sentiment = 'positive'
        elif negative_score > positive_score:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'positive_score': positive_score,
            'negative_score': negative_score
        }


if __name__ == '__main__':
    processor = NLPProcessor()
    print("NLP Integration Module initialized")
