"""
insurance-agent/db.py
SQLite database module for insurance agent
Supports insurance plans, FAQ, claims, and user settings
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json


class InsuranceDatabase:
    """Database manager for insurance agent with multi-language support"""

    def __init__(self, db_path: str = "insurance.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_sample_data()

    def _create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()

        # Insurance plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name_en TEXT NOT NULL,
                plan_name_ja TEXT NOT NULL,
                description_en TEXT,
                description_ja TEXT,
                coverage TEXT,  -- JSON array of coverage items
                premium_min REAL,
                premium_max REAL,
                category TEXT,  -- health, auto, life, home, etc.
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # FAQ table with multi-language support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_en TEXT NOT NULL,
                question_ja TEXT NOT NULL,
                answer_en TEXT NOT NULL,
                answer_ja TEXT NOT NULL,
                category TEXT,
                keywords TEXT,  -- Comma-separated for search
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_number TEXT UNIQUE NOT NULL,
                user_id TEXT,
                plan_id INTEGER,
                incident_date TEXT,
                claim_type TEXT,
                amount REAL,
                status TEXT DEFAULT 'submitted',  -- submitted, reviewing, approved, rejected, paid
                description_en TEXT,
                description_ja TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES insurance_plans(id)
            )
        """)

        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                language TEXT DEFAULT 'en',
                plan_id INTEGER,
                coverage_start_date TEXT,
                FOREIGN KEY (plan_id) REFERENCES insurance_plans(id)
            )
        """)

        # Conversation history for context
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT,
                intent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def _seed_sample_data(self):
        """Seed initial data for common insurance plans and FAQs"""
        cursor = self.conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM insurance_plans")
        if cursor.fetchone()[0] > 0:
            return

        # Sample insurance plans
        plans = [
            {
                "plan_name_en": "Basic Health Plan",
                "plan_name_ja": "基本健康保険プラン",
                "description_en": "Essential medical coverage for individuals",
                "description_ja": "個人向け基本医療保障",
                "coverage": json.dumps(["doctor_visits", "prescription_drugs", "hospitalization"]),
                "premium_min": 5000,
                "premium_max": 8000,
                "category": "health"
            },
            {
                "plan_name_en": "Premium Health Plan",
                "plan_name_ja": "プレミアム健康保険プラン",
                "description_en": "Comprehensive medical coverage with dental and vision",
                "description_ja": "歯科・視覚を含む包括的医療保障",
                "coverage": json.dumps(["doctor_visits", "prescription_drugs", "hospitalization", "dental", "vision", "mental_health"]),
                "premium_min": 12000,
                "premium_max": 20000,
                "category": "health"
            },
            {
                "plan_name_en": "Auto Insurance Basic",
                "plan_name_ja": "自動車保険（基本）",
                "description_en": "Basic auto coverage with liability protection",
                "description_ja": "賠償責任を含む基本自動車保険",
                "coverage": json.dumps(["liability", "collision", "comprehensive"]),
                "premium_min": 30000,
                "premium_max": 50000,
                "category": "auto"
            },
            {
                "plan_name_en": "Auto Insurance Premium",
                "plan_name_ja": "自動車保険（プレミアム）",
                "description_en": "Full auto coverage with roadside assistance",
                "description_ja": "ロードサイドアシスタンス付き包括的自動車保険",
                "coverage": json.dumps(["liability", "collision", "comprehensive", "roadside_assistance", "rental"]),
                "premium_min": 60000,
                "premium_max": 100000,
                "category": "auto"
            },
            {
                "plan_name_en": "Life Insurance Term",
                "plan_name_ja": "生命保険（定期）",
                "description_en": "Term life insurance for specified period",
                "description_ja": "期間限定の定期生命保険",
                "coverage": json.dumps(["death_benefit", "accidental_death"]),
                "premium_min": 2000,
                "premium_max": 5000,
                "category": "life"
            },
            {
                "plan_name_en": "Home Insurance Basic",
                "plan_name_ja": "住宅保険（基本）",
                "description_en": "Basic home and contents coverage",
                "description_ja": "住宅・家財基本保障",
                "coverage": json.dumps(["fire", "theft", "natural_disaster"]),
                "premium_min": 15000,
                "premium_max": 25000,
                "category": "home"
            }
        ]

        for plan in plans:
            cursor.execute("""
                INSERT INTO insurance_plans (plan_name_en, plan_name_ja, description_en, description_ja,
                                            coverage, premium_min, premium_max, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (plan["plan_name_en"], plan["plan_name_ja"], plan["description_en"], plan["description_ja"],
                  plan["coverage"], plan["premium_min"], plan["premium_max"], plan["category"]))

        # Sample FAQs
        faqs = [
            {
                "question_en": "How do I file a claim?",
                "question_ja": "保険金請求はどうすればいいですか？",
                "answer_en": "To file a claim, provide your claim number, incident details, and supporting documents. Claims are typically processed within 5-7 business days.",
                "answer_ja": "保険金請求を行うには、請求番号、事故の詳細、および必要書類をご提出ください。通常5〜7営業日で処理されます。",
                "category": "claims",
                "keywords": "claim,file,apply,請求,申請"
            },
            {
                "question_en": "What is covered under the health insurance?",
                "question_ja": "健康保険で何が保障されますか？",
                "answer_en": "Health insurance covers doctor visits, prescription drugs, hospitalization, and depending on your plan, dental, vision, and mental health services.",
                "answer_ja": "健康保険は、医師の診察、処方薬、入院を保障します。プランによっては、歯科、視覚、メンタルヘルスサービスも含まれます。",
                "category": "coverage",
                "keywords": "coverage,benefit,include,保障,給付,含む"
            },
            {
                "question_en": "How can I change my payment method?",
                "question_ja": "支払い方法を変更するにはどうすればいいですか？",
                "answer_en": "You can change your payment method through your online account or by contacting customer service. We accept credit cards, bank transfers, and automatic debits.",
                "answer_ja": "オンラインアカウントまたはカスタマーサービスで支払い方法を変更できます。クレジットカード、銀行振込、自動引き落としを受け付けています。",
                "category": "billing",
                "keywords": "payment,change,method,支払い,変更,方法"
            },
            {
                "question_en": "What is the waiting period for new coverage?",
                "question_ja": "新規保障の待機期間はどのくらいですか？",
                "answer_en": "Most plans have a waiting period of 30 days before coverage takes effect. Some pre-existing conditions may have longer waiting periods.",
                "answer_ja": "ほとんどのプランでは、保障が開始されるまで30日間の待機期間があります。既往症については、より長い待機期間が適用される場合があります。",
                "category": "enrollment",
                "keywords": "waiting,period,new,waiting,待機,期間,新規"
            },
            {
                "question_en": "How do I add a family member to my plan?",
                "question_ja": "家族をプランに追加するにはどうすればいいですか？",
                "answer_en": "Family members can be added during open enrollment or after qualifying life events (marriage, birth, adoption). Submit the required forms and documents to add coverage.",
                "answer_ja": "家族は加入期間または人生の変動（結婚、出産、養子縁組）の後に追加できます。必要なフォームと書類を提出して保障を追加してください。",
                "category": "enrollment",
                "keywords": "family,add,member,dependent,家族,追加,扶養家族"
            },
            {
                "question_en": "What should I do if my claim is denied?",
                "question_ja": "請求が拒否された場合、どうすればいいですか？",
                "answer_en": "If your claim is denied, you'll receive a letter explaining the reason. You can appeal the decision within 30 days by providing additional information or documentation.",
                "answer_ja": "請求が拒否された場合、理由を説明する通知が届きます。追加情報や書類を提出することで、30日以内に決定を異議申し立てすることができます。",
                "category": "claims",
                "keywords": "denied,reject,appeal,拒否,異議申し立て"
            },
            {
                "question_en": "Can I cancel my insurance at any time?",
                "question_ja": "いつでも保険を解約できますか？",
                "answer_en": "Yes, you can cancel your insurance at any time. Refunds are prorated based on remaining coverage period. A cancellation fee may apply.",
                "answer_ja": "はい、いつでも保険を解約できます。返金は残存保障期間に基づいて按分されます。解約手数料がかかる場合があります。",
                "category": "policy",
                "keywords": "cancel,terminate,解約,終了"
            },
            {
                "question_en": "How do I update my personal information?",
                "question_ja": "個人情報を更新するにはどうすればいいですか？",
                "answer_en": "Update your personal information through your online account or contact customer service. Changes to address or beneficiaries may require additional verification.",
                "answer_ja": "オンラインアカウントまたはカスタマーサービスで個人情報を更新してください。住所または受取人の変更には追加の確認が必要な場合があります。",
                "category": "account",
                "keywords": "update,personal,information,profile,更新,個人情報"
            }
        ]

        for faq in faqs:
            cursor.execute("""
                INSERT INTO faq (question_en, question_ja, answer_en, answer_ja, category, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (faq["question_en"], faq["question_ja"], faq["answer_en"], faq["answer_ja"],
                  faq["category"], faq["keywords"]))

        # Sample claims
        claims = [
            {
                "claim_number": "CLM-2024-001",
                "user_id": "user1",
                "plan_id": 1,
                "incident_date": "2024-01-15",
                "claim_type": "medical",
                "amount": 25000,
                "status": "approved",
                "description_en": "Hospitalization for appendicitis",
                "description_ja": "虫垂炎による入院"
            },
            {
                "claim_number": "CLM-2024-002",
                "user_id": "user1",
                "plan_id": 3,
                "incident_date": "2024-01-20",
                "claim_type": "collision",
                "amount": 150000,
                "status": "reviewing",
                "description_en": "Car accident - rear-end collision",
                "description_ja": "自動車事故 - 追突事故"
            }
        ]

        for claim in claims:
            cursor.execute("""
                INSERT INTO claims (claim_number, user_id, plan_id, incident_date, claim_type,
                                    amount, status, description_en, description_ja)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (claim["claim_number"], claim["user_id"], claim["plan_id"], claim["incident_date"],
                  claim["claim_type"], claim["amount"], claim["status"],
                  claim["description_en"], claim["description_ja"]))

        self.conn.commit()

    # Insurance Plan Methods
    def get_all_plans(self, category: Optional[str] = None, language: str = "en") -> List[Dict]:
        """Get all insurance plans, optionally filtered by category"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute(
                "SELECT * FROM insurance_plans WHERE category = ? AND is_active = 1",
                (category,)
            )
        else:
            cursor.execute("SELECT * FROM insurance_plans WHERE is_active = 1")

        plans = []
        for row in cursor.fetchall():
            plan = dict(row)
            plan["coverage"] = json.loads(plan["coverage"]) if plan["coverage"] else []
            plans.append(plan)
        return plans

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """Get a specific insurance plan by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM insurance_plans WHERE id = ?", (plan_id,))
        row = cursor.fetchone()
        if row:
            plan = dict(row)
            plan["coverage"] = json.loads(plan["coverage"]) if plan["coverage"] else []
            return plan
        return None

    def search_plans(self, query: str, language: str = "en") -> List[Dict]:
        """Search insurance plans by name or description"""
        cursor = self.conn.cursor()
        if language == "ja":
            cursor.execute("""
                SELECT * FROM insurance_plans
                WHERE (plan_name_ja LIKE ? OR description_ja LIKE ?) AND is_active = 1
            """, (f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("""
                SELECT * FROM insurance_plans
                WHERE (plan_name_en LIKE ? OR description_en LIKE ?) AND is_active = 1
            """, (f"%{query}%", f"%{query}%"))

        plans = []
        for row in cursor.fetchall():
            plan = dict(row)
            plan["coverage"] = json.loads(plan["coverage"]) if plan["coverage"] else []
            plans.append(plan)
        return plans

    # FAQ Methods
    def search_faq(self, query: str, language: str = "en") -> List[Dict]:
        """Search FAQs by question, answer, or keywords"""
        cursor = self.conn.cursor()
        if language == "ja":
            cursor.execute("""
                SELECT * FROM faq
                WHERE question_ja LIKE ? OR answer_ja LIKE ? OR keywords LIKE ?
                ORDER BY id
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("""
                SELECT * FROM faq
                WHERE question_en LIKE ? OR answer_en LIKE ? OR keywords LIKE ?
                ORDER BY id
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))

        return [dict(row) for row in cursor.fetchall()]

    def get_faq_by_category(self, category: str, language: str = "en") -> List[Dict]:
        """Get all FAQs for a specific category"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM faq WHERE category = ?", (category,))
        return [dict(row) for row in cursor.fetchall()]

    # Claim Methods
    def create_claim(self, claim_data: Dict) -> int:
        """Create a new insurance claim"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO claims (claim_number, user_id, plan_id, incident_date, claim_type,
                               amount, description_en, description_ja)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_data.get("claim_number"),
            claim_data.get("user_id"),
            claim_data.get("plan_id"),
            claim_data.get("incident_date"),
            claim_data.get("claim_type"),
            claim_data.get("amount"),
            claim_data.get("description_en"),
            claim_data.get("description_ja")
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_claims_by_user(self, user_id: str) -> List[Dict]:
        """Get all claims for a specific user"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM claims WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_claim_by_number(self, claim_number: str) -> Optional[Dict]:
        """Get a specific claim by claim number"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM claims WHERE claim_number = ?", (claim_number,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_claim_status(self, claim_number: str, status: str) -> bool:
        """Update the status of a claim"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE claims SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE claim_number = ?
        """, (status, claim_number))
        self.conn.commit()
        return cursor.rowcount > 0

    # User Settings Methods
    def get_user_settings(self, user_id: str) -> Optional[Dict]:
        """Get settings for a specific user"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def set_user_language(self, user_id: str, language: str) -> bool:
        """Set or update user's preferred language"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO user_settings (user_id, language)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = ?
        """, (user_id, language, language))
        self.conn.commit()
        return cursor.rowcount > 0

    def set_user_plan(self, user_id: str, plan_id: int, start_date: str) -> bool:
        """Set or update user's insurance plan"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO user_settings (user_id, plan_id, coverage_start_date)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET plan_id = ?, coverage_start_date = ?
        """, (user_id, plan_id, start_date, plan_id, start_date))
        self.conn.commit()
        return cursor.rowcount > 0

    # Conversation History Methods
    def add_conversation(self, user_id: str, message: str, response: str, intent: str) -> int:
        """Add a conversation entry to history"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_history (user_id, message, response, intent)
            VALUES (?, ?, ?, ?)
        """, (user_id, message, response, intent))
        self.conn.commit()
        return cursor.lastrowid

    def get_recent_conversations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversation history for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM conversation_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for quick access
def get_db(db_path: str = "insurance.db") -> InsuranceDatabase:
    """Get database instance"""
    return InsuranceDatabase(db_path)
