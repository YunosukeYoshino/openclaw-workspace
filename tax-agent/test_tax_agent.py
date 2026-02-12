#!/usr/bin/env python3
"""
Unit tests for tax-agent
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db import TaxDatabase
from discord import MessageParser, TaxAgent


def test_database():
    """Test database operations"""
    print("Testing database operations...")

    # Use test database
    test_db_path = "/tmp/test_tax.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = TaxDatabase(test_db_path)

    # Test user settings
    user_id = "test_user"
    settings = db.get_user_settings(user_id)
    assert settings['language'] == 'ja'
    print("✓ Default user settings OK")

    db.set_user_language(user_id, 'en')
    settings = db.get_user_settings(user_id)
    assert settings['language'] == 'en'
    print("✓ Set user language OK")

    # Test add record
    record_id = db.add_record(
        user_id=user_id,
        year=2024,
        category='income',
        amount=50000,
        description='Freelance work'
    )
    assert record_id > 0
    print(f"✓ Add record OK (id={record_id})")

    # Test get record
    record = db.get_record(record_id)
    assert record['amount'] == 50000
    assert record['category'] == 'income'
    print("✓ Get record OK")

    # Test get user records
    records = db.get_user_records(user_id, 2024)
    assert len(records) == 1
    print("✓ Get user records OK")

    # Test add more records
    db.add_record(user_id, 2024, 'expense', 5000, 'Office supplies')
    db.add_record(user_id, 2024, 'expense', 12000, 'Software')
    db.add_record(user_id, 2023, 'income', 40000, 'Salary')

    # Test summary
    summary = db.get_summary(user_id, 2024)
    assert summary['income']['total'] == 50000
    assert summary['expense']['total'] == 17000
    print("✓ Summary OK")

    # Test search
    results = db.search_records(user_id, 'office')
    assert len(results) > 0
    print("✓ Search OK")

    # Test update
    db.update_record(record_id, amount=55000)
    record = db.get_record(record_id)
    assert record['amount'] == 55000
    print("✓ Update record OK")

    # Test delete
    db.delete_record(record_id, user_id)
    record = db.get_record(record_id)
    assert record is None
    print("✓ Delete record OK")

    # Test categories
    categories = db.get_categories('ja')
    assert 'income' in categories
    assert categories['income'] == '所得'
    print("✓ Categories OK")

    db.close()
    os.remove(test_db_path)

    print("✅ Database tests passed!\n")


def test_message_parser():
    """Test message parsing"""
    print("Testing message parser...")

    parser = MessageParser()

    # Test language detection
    assert parser.detect_language("こんにちは") == 'ja'
    assert parser.detect_language("Hello") == 'en'
    print("✓ Language detection OK")

    # Test amount parsing
    assert parser.parse_amount("¥5000") == 5000
    assert parser.parse_amount("$1,234.56") == 1234.56
    assert parser.parse_amount("amount 10000") == 10000
    print("✓ Amount parsing OK")

    # Test year parsing
    assert parser.parse_year("record for 2024") == 2024
    assert parser.parse_year("no year here") is None
    print("✓ Year parsing OK")

    # Test category detection
    assert parser.detect_category("income from salary", 'en') == 'income'
    assert parser.detect_category("経費として記録", 'ja') == 'expense'
    assert parser.detect_category("just some text", 'en') is None
    print("✓ Category detection OK")

    # Test action detection
    assert parser.detect_action("add a record", 'en') == 'add'
    assert parser.detect_action("一覧を表示", 'ja') == 'list'
    assert parser.detect_action("delete this", 'en') == 'delete'
    print("✓ Action detection OK")

    # Test add command parsing (English)
    cmd = parser.parse_add_command("add 5000 expense office supplies 2024", 'en')
    assert cmd['action'] == 'add'
    assert cmd['amount'] == 5000
    assert cmd['category'] == 'expense'
    assert cmd['year'] == 2024
    print("✓ Add command parsing (EN) OK")

    # Test add command parsing (Japanese)
    cmd = parser.parse_add_command("記録 ¥10000 所得 フリーランス 2024", 'ja')
    assert cmd['amount'] == 10000
    assert cmd['category'] == 'income'
    assert cmd['year'] == 2024
    print("✓ Add command parsing (JA) OK")

    # Test list command parsing
    cmd = parser.parse_list_command("list 2024 expense", 'en')
    assert cmd['action'] == 'list'
    assert cmd['year'] == 2024
    assert cmd['category'] == 'expense'
    print("✓ List command parsing OK")

    # Test summary command parsing
    cmd = parser.parse_summary_command("summary 2024", 'en')
    assert cmd['action'] == 'summary'
    assert cmd['year'] == 2024
    print("✓ Summary command parsing OK")

    # Test search command parsing
    cmd = parser.parse_search_command("search office 2024", 'en')
    assert cmd['action'] == 'search'
    assert cmd['keyword'] == 'office 2024'
    print("✓ Search command parsing OK")

    # Test delete command parsing
    cmd = parser.parse_delete_command("delete 123", 'en')
    assert cmd['action'] == 'delete'
    assert cmd['record_id'] == 123
    print("✓ Delete command parsing OK")

    # Test set command parsing
    cmd = parser.parse_set_command("set language english", 'en')
    assert cmd['action'] == 'set'
    assert cmd['value'] == 'en'
    cmd = parser.parse_set_command("言語設定 日本語", 'ja')
    assert cmd['value'] == 'ja'
    print("✓ Set command parsing OK")

    print("✅ Message parser tests passed!\n")


def test_tax_agent():
    """Test full agent functionality"""
    print("Testing tax agent...")

    # Use test database
    test_db_path = "/tmp/test_tax_agent.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    agent = TaxAgent(test_db_path)
    test_user_id = "test_user_agent"

    # Test help command
    response = agent.process_message(test_user_id, "help")
    assert "Commands" in response or "コマンド" in response
    print("✓ Help command OK")

    # Test add record (English)
    response = agent.process_message(test_user_id, "add 5000 expense office supplies 2024")
    assert "Added" in response or "追加" in response
    assert "5000" in response
    print("✓ Add record (EN) OK")

    # Test add record (Japanese)
    response = agent.process_message(test_user_id, "記録 ¥10000 所得 フリーランス 2024")
    assert "10000" in response
    print("✓ Add record (JA) OK")

    # Test list records
    response = agent.process_message(test_user_id, "list 2024")
    assert "2024" in response
    print("✓ List records OK")

    # Test summary
    response = agent.process_message(test_user_id, "summary 2024")
    assert "Summary" in response or "集計" in response
    assert "income" in response.lower() or "所得" in response
    print("✓ Summary OK")

    # Test search
    response = agent.process_message(test_user_id, "search office")
    assert "office" in response.lower() or "オフィス" in response
    print("✓ Search OK")

    # Test language change
    response = agent.process_message(test_user_id, "set language english")
    assert "English" in response or "english" in response.lower()
    print("✓ Set language OK")

    # Verify language preference persisted
    lang = agent.get_user_language(test_user_id)
    assert lang == 'en'
    print("✓ Language preference persisted OK")

    # Test with new language
    response = agent.process_message(test_user_id, "add 3000 expense travel")
    assert "Added" in response
    print("✓ Add with new language OK")

    # Test delete
    records = agent.db.get_user_records(test_user_id, 2024)
    if records:
        record_id = records[0]['id']
        response = agent.process_message(test_user_id, f"delete {record_id}")
        assert "Deleted" in response or "deleted" in response.lower()
        print("✓ Delete record OK")

    agent.db.close()
    os.remove(test_db_path)

    print("✅ Tax agent tests passed!\n")


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Tax Agent Test Suite")
    print("=" * 50)
    print()

    try:
        test_database()
        test_message_parser()
        test_tax_agent()

        print("=" * 50)
        print("🎉 All tests passed!")
        print("=" * 50)
        return True

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
