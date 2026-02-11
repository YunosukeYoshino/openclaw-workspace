#!/usr/bin/env python3
"""
パスワード管理エージェント
- パスワードの保存・管理
- 安全なパスワード生成
- パスワードの自動入力
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import secrets
import string
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64

DB_PATH = Path(__file__).parent / "passwords.db"
KEY_ITERATIONS = 100000

class PasswordManager:
    """パスワードマネージャー"""

    def __init__(self, master_password=None):
        self.master_password = master_password
        self.key = None
        self.salt = None

    def derive_key(self, salt=None):
        """マスターパスワードから暗号化キーを導出"""
        if salt is None:
            self.salt = secrets.token_bytes(16)
        else:
            self.salt = salt

        self.key = PBKDF2(
            self.master_password.encode('utf-8'),
            self.salt,
            dkLen=32,
            count=KEY_ITERATIONS
        )
        return self.key

    def encrypt(self, data):
        """データを暗号化"""
        iv = secrets.token_bytes(16)
        cipher = AES.new(self.key, AES.MODE_GCM, iv)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return base64.b64encode(iv + tag + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data):
        """データを復号化"""
        try:
            data = base64.b64decode(encrypted_data)
            iv = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]

            cipher = AES.new(self.key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError("Decryption failed")

_manager = None

def init_db(master_password):
    """データベース初期化"""
    global _manager

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # パスワードエントリテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT NOT NULL,
        site_url TEXT,
        username TEXT,
        encrypted_password TEXT NOT NULL,
        salt TEXT NOT NULL,
        category_id INTEGER,
        notes TEXT,
        last_used TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )
    ''')

    # カテゴリテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        color TEXT DEFAULT '#888888',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # タグテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # パスワード・タグ紐付け
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS password_tags (
        password_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (password_id, tag_id),
        FOREIGN KEY (password_id) REFERENCES passwords(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_passwords_timestamp
    AFTER UPDATE ON passwords
    BEGIN
        UPDATE passwords SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_passwords_site ON passwords(site_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_passwords_category ON passwords(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_passwords_created ON passwords(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_password_tags_tag ON password_tags(tag_id)')

    # デフォルトカテゴリ
    default_categories = [
        ('Social', '#3498db'),
        ('Work', '#2ecc71'),
        ('Finance', '#e74c3c'),
        ('Shopping', '#f39c12'),
        ('Entertainment', '#9b59b6'),
    ]
    for name, color in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)', (name, color))

    conn.commit()
    conn.close()

    # マネージャー初期化
    _manager = PasswordManager(master_password)

    print("✅ パスワードデータベース初期化完了")

def generate_password(length=16, use_uppercase=True, use_lowercase=True,
                     use_digits=True, use_symbols=True, exclude_ambiguous=True):
    """安全なパスワードを生成"""
    chars = ""

    if use_uppercase:
        chars += string.ascii_uppercase
    if use_lowercase:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # 曖昧な文字を除外
    if exclude_ambiguous:
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('l', '').replace('I', '')

    if not chars:
        chars = string.ascii_letters + string.digits

    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password

def add_password(site_name, username, password, site_url=None, category=None, notes=None, tags=None):
    """パスワードを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # カテゴリID取得/作成
    category_id = None
    if category:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]

    # パスワードを暗号化
    salt = secrets.token_bytes(16)
    _manager.salt = salt
    _manager.derive_key(salt)
    encrypted_password = _manager.encrypt(password)

    # パスワード追加
    cursor.execute('''
    INSERT INTO passwords (site_name, site_url, username, encrypted_password, salt, category_id, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (site_name, site_url, username, encrypted_password,
          base64.b64encode(salt).decode('utf-8'), category_id, notes))

    password_id = cursor.lastrowid

    # タグ紐付け
    if tags:
        for tag in tags:
            cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO password_tags (password_id, tag_id) VALUES (?, ?)',
                          (password_id, tag_id))

    conn.commit()
    conn.close()
    return password_id

def get_password(password_id):
    """パスワードを取得（復号化）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM passwords WHERE id = ?', (password_id,))
    result = cursor.fetchone()

    if result:
        # パスワードを復号化
        salt = base64.b64decode(result[5])
        _manager.salt = salt
        _manager.derive_key(salt)
        decrypted_password = _manager.decrypt(result[4])

        # 最終使用時刻を更新
        cursor.execute('UPDATE passwords SET last_used = CURRENT_TIMESTAMP WHERE id = ?', (password_id,))
        conn.commit()

        conn.close()
        return result[0], result[1], result[2], result[3], decrypted_password, result[8]
    else:
        conn.close()
        return None

def list_passwords(limit=50, category=None):
    """パスワード一覧（パスワードは非表示）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if category:
        cursor.execute('''
        SELECT p.id, p.site_name, p.site_url, p.username, c.name, p.created_at, p.updated_at
        FROM passwords p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE c.name = ?
        ORDER BY p.created_at DESC
        LIMIT ?
        ''', (category, limit))
    else:
        cursor.execute('''
        SELECT p.id, p.site_name, p.site_url, p.username, c.name, p.created_at, p.updated_at
        FROM passwords p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.created_at DESC
        LIMIT ?
        ''', (limit,))

    passwords = cursor.fetchall()
    conn.close()
    return passwords

def search_passwords(keyword):
    """パスワードを検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT p.id, p.site_name, p.site_url, p.username, c.name, p.created_at, p.updated_at
    FROM passwords p
    LEFT JOIN categories c ON p.category_id = c.id
    WHERE p.site_name LIKE ? OR p.site_url LIKE ? OR p.username LIKE ? OR p.notes LIKE ?
    ORDER BY p.created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    passwords = cursor.fetchall()
    conn.close()
    return passwords

def update_password(password_id, site_name=None, username=None, password=None,
                    site_url=None, category=None, notes=None):
    """パスワードを更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if site_name is not None:
        updates.append('site_name = ?')
        params.append(site_name)
    if username is not None:
        updates.append('username = ?')
        params.append(username)
    if password is not None:
        salt = secrets.token_bytes(16)
        _manager.salt = salt
        _manager.derive_key(salt)
        encrypted_password = _manager.encrypt(password)
        updates.append('encrypted_password = ?')
        params.append(encrypted_password)
        updates.append('salt = ?')
        params.append(base64.b64encode(salt).decode('utf-8'))
    if site_url is not None:
        updates.append('site_url = ?')
        params.append(site_url)
    if notes is not None:
        updates.append('notes = ?')
        params.append(notes)
    if category is not None:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]
        updates.append('category_id = ?')
        params.append(category_id)

    if updates:
        params.append(password_id)
        cursor.execute(f'UPDATE passwords SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()

    conn.close()

def delete_password(password_id):
    """パスワードを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
    conn.commit()
    conn.close()

def get_categories():
    """カテゴリ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_tags():
    """タグ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tags ORDER BY name')
    tags = cursor.fetchall()
    conn.close()
    return tags

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全パスワード数
    cursor.execute('SELECT COUNT(*) FROM passwords')
    stats['total_passwords'] = cursor.fetchone()[0]

    # カテゴリ別
    cursor.execute('''
    SELECT c.name, COUNT(p.id) as count
    FROM categories c
    LEFT JOIN passwords p ON c.id = p.category_id
    GROUP BY c.id
    ORDER BY count DESC
    ''')
    stats['by_category'] = dict(cursor.fetchall())

    # タグ別
    cursor.execute('''
    SELECT t.name, COUNT(pt.password_id) as count
    FROM tags t
    LEFT JOIN password_tags pt ON t.id = pt.tag_id
    GROUP BY t.id
    ORDER BY count DESC
    ''')
    stats['by_tag'] = dict(cursor.fetchall())

    # 最近追加
    cursor.execute('SELECT COUNT(*) FROM passwords WHERE created_at > datetime("now", "-7 days")')
    stats['recent_additions'] = cursor.fetchone()[0]

    conn.close()
    return stats

def check_password_strength(password):
    """パスワード強度をチェック"""
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("8文字以上にしてください")

    if len(password) >= 12:
        score += 1

    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("大文字を含めてください")

    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("小文字を含めてください")

    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("数字を含めてください")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        feedback.append("記号を含めてください")

    if len(password) >= 16:
        score += 1

    # 強度レベル
    if score >= 6:
        level = "強 / Strong"
    elif score >= 4:
        level = "中 / Medium"
    elif score >= 2:
        level = "弱 / Weak"
    else:
        level = "非常に弱 / Very Weak"

    return {
        'score': score,
        'level': level,
        'feedback': feedback
    }

if __name__ == '__main__':
    # テスト用のマスターパスワード
    import sys
    if len(sys.argv) > 1:
        init_db(sys.argv[1])
        print("\n生成されたパスワード:")
        print(generate_password(16))
        print("\nパスワード強度チェック:")
        print(check_password_strength(generate_password(16)))
