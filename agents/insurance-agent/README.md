# Insurance Agent (71)

Discord-based insurance agent with SQLite database and natural language processing. Supports both Japanese and English languages.

## Features

- **Multi-language Support**: Japanese and English
- **Natural Language Processing**: Intent recognition and entity extraction
- **Insurance Plans**: Browse and search available insurance plans
- **Claims Management**: Check claim status and history
- **FAQ System**: Search and retrieve frequently asked questions
- **User Preferences**: Per-user language and settings

## File Structure

```
insurance-agent/
├── db.py          # SQLite database module
├── discord.py     # Discord bot with NLP processing
├── requirements.txt
└── README.md
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Discord bot:
   - Go to Discord Developer Portal
   - Create a new application
   - Enable bot and get the token
   - Enable Message Content Intent

3. Run the bot:
```bash
python discord.py YOUR_BOT_TOKEN
```

## Database

The bot automatically creates and initializes an SQLite database (`insurance.db`) with:
- **insurance_plans**: Available insurance plans
- **faq**: Frequently asked questions
- **claims**: User claims
- **user_settings**: User preferences (language, plan)
- **conversation_history**: Message history

## Usage

### Natural Language Conversations

You can interact with the bot using natural language:

**English:**
```
Tell me about health insurance
Check my claim status
What plans do you have?
How do I file a claim?
Speak Japanese
```

**Japanese:**
```
健康保険について教えて
請求状況を確認
どんなプランがありますか？
請求を申請するにはどうすれば？
日本語で話して
```

### Commands

| Command | Description |
|---------|-------------|
| `!help` | Show help message |
| `!plans [category]` | List insurance plans (optional: health, auto, life, home) |
| `!claims` | Show your claims |
| `!language ja|en` | Change language (Japanese/English) |

### Intent Recognition

The bot uses pattern matching and keyword analysis to identify intents:

1. **FAQ**: Questions about coverage, policies, processes
2. **Claim Status**: Check claim status or track claims
3. **Claim File**: Information about filing new claims
4. **Plans List**: Browse available insurance plans
5. **Plans Search**: Search plans by category (health, auto, life, home)
6. **Settings Language**: Change language preference
7. **Help**: Get help and usage information

### Sample Data

The database includes sample data:
- 6 insurance plans (health, auto, life, home)
- 8 FAQs covering common questions
- 2 sample claims

## Database API

### InsuranceDatabase Class

```python
from db import get_db

db = get_db()

# Plans
plans = db.get_all_plans(category="health", language="en")
plan = db.get_plan_by_id(1)
plans = db.search_plans("health", language="ja")

# FAQ
faqs = db.search_faq("claim", language="en")

# Claims
db.create_claim({
    "claim_number": "CLM-2024-003",
    "user_id": "user1",
    "plan_id": 1,
    "incident_date": "2024-02-01",
    "claim_type": "medical",
    "amount": 10000,
    "description_en": "Doctor visit",
    "description_ja": "医師の診察"
})
claims = db.get_claims_by_user("user1")
claim = db.get_claim_by_number("CLM-2024-001")
db.update_claim_status("CLM-2024-001", "approved")

# User Settings
db.set_user_language("user1", "ja")
db.set_user_plan("user1", 2, "2024-02-01")

# Conversation History
db.add_conversation("user1", "message", "response", "faq")
history = db.get_recent_conversations("user1", limit=5)
```

## Language Detection

The bot automatically detects language from:
1. User settings (stored in database)
2. Message content (Japanese characters detection)
3. Explicit language change commands

## Example Interactions

### English
```
User: What plans do you have?
Bot: 📋 Insurance Plans (6 plans):
...
```

```
User: Check my claim status
Bot: 📋 Claim History (2 claims):
...
```

```
User: Speak Japanese
Bot: ✅ Language changed to Japanese. I'll now respond in English.
```

### Japanese
```
User: 健康保険について教えて
Bot: 📋 保険プラン一覧 (6件):
...
```

```
User: 請求状況を確認
Bot: 📋 請求履歴 (2件):
...
```

## Development

### Adding New FAQ

```python
# Use db.py to add FAQ directly
db = get_db()
cursor = db.conn.cursor()
cursor.execute("""
    INSERT INTO faq (question_en, question_ja, answer_en, answer_ja, category, keywords)
    VALUES (?, ?, ?, ?, ?, ?)
""", (q_en, q_ja, a_en, a_ja, category, keywords))
db.conn.commit()
```

### Adding New Insurance Plan

```python
import json
db = get_db()
cursor = db.conn.cursor()
cursor.execute("""
    INSERT INTO insurance_plans (plan_name_en, plan_name_ja, description_en, description_ja,
                                coverage, premium_min, premium_max, category)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (name_en, name_ja, desc_en, desc_ja, json.dumps(coverage), min_premium, max_premium, category))
db.conn.commit()
```

## License

MIT License
