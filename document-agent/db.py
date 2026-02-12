#!/usr/bin/env python3
"""
Document Agent - Database Management
Document storage and management with natural language support
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "document.db"
EXPORT_DIR = Path(__file__).parent / "exports"

# Language detection patterns
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]')

def detect_language(text: str) -> str:
    """Detect if text is primarily Japanese or English"""
    if not text:
        return 'en'

    japanese_chars = len(JAPANESE_PATTERN.findall(text))
    english_chars = len(ENGLISH_PATTERN.findall(text))

    if japanese_chars > english_chars:
        return 'ja'
    return 'en'

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        tags TEXT,
        language TEXT DEFAULT 'ja',
        author TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active','archived','deleted')),
        priority INTEGER DEFAULT 0,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP
    )
    ''')

    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        color TEXT,
        parent_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES categories(id)
    )
    ''')

    # Tags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        color TEXT,
        count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Document tags junction table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS document_tags (
        document_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (document_id, tag_id),
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    ''')

    # Search history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        language TEXT,
        results_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Document versions table (for versioning)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS document_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        version INTEGER DEFAULT 1,
        title TEXT,
        content TEXT,
        change_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_language ON documents(language)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_updated ON documents(updated_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_tags_doc ON document_tags(document_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_tags_tag ON document_tags(tag_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_history_created ON search_history(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_versions_doc ON document_versions(document_id)')

    # Create default categories
    default_categories = [
        ('General', '一般', None),
        ('Work', '仕事', None),
        ('Personal', '個人', None),
        ('Ideas', 'アイデア', None),
        ('Reference', '参考資料', None),
        ('Meeting', '会議', None),
        ('Project', 'プロジェクト', None),
    ]

    for name_en, name_ja, parent in default_categories:
        cursor.execute('''
        INSERT OR IGNORE INTO categories (name, description, parent_id)
        VALUES (?, ?, ?)
        ''', (name_ja, name_en, parent))

    conn.commit()
    conn.close()

    # Create exports directory
    EXPORT_DIR.mkdir(exist_ok=True)
    print("✅ Database initialized")

def add_document(title: str, content: str, category: Optional[str] = None,
                 tags: Optional[List[str]] = None, author: Optional[str] = None,
                 priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> int:
    """Add a new document"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Detect language
    language = detect_language(content + ' ' + title)

    tags_json = json.dumps(tags) if tags else None
    metadata_json = json.dumps(metadata) if metadata else None

    cursor.execute('''
    INSERT INTO documents (title, content, category, tags, language, author, priority, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, content, category, tags_json, language, author, priority, metadata_json))

    doc_id = cursor.lastrowid

    # Process tags
    if tags:
        for tag in tags:
            # Add or get tag
            cursor.execute('''
            INSERT OR IGNORE INTO tags (name) VALUES (?)
            ''', (tag,))
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]

            # Update tag count
            cursor.execute('UPDATE tags SET count = count + 1 WHERE id = ?', (tag_id,))

            # Link document and tag
            cursor.execute('''
            INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)
            ''', (doc_id, tag_id))

    conn.commit()
    conn.close()
    return doc_id

def get_document(doc_id: int) -> Optional[Dict[str, Any]]:
    """Get a document by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
    row = cursor.fetchone()

    if row:
        doc = dict(row)
        # Update last accessed
        cursor.execute('UPDATE documents SET last_accessed = CURRENT_TIMESTAMP WHERE id = ?', (doc_id,))
        conn.commit()
        conn.close()
        return doc

    conn.close()
    return None

def get_documents(category: Optional[str] = None, language: Optional[str] = None,
                   status: str = 'active', tag: Optional[str] = None,
                   author: Optional[str] = None, limit: int = 50,
                   offset: int = 0) -> List[Dict[str, Any]]:
    """Get documents with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM documents WHERE status = ?'
    params = [status]

    if category:
        query += ' AND category = ?'
        params.append(category)
    if language:
        query += ' AND language = ?'
        params.append(language)
    if author:
        query += ' AND author = ?'
        params.append(author)

    if tag:
        query += ' AND id IN (SELECT document_id FROM document_tags WHERE tag_id IN (SELECT id FROM tags WHERE name = ?))'
        params.append(tag)

    query += ' ORDER BY updated_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    cursor.execute(query, params)
    docs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return docs

def update_document(doc_id: int, title: Optional[str] = None,
                    content: Optional[str] = None, category: Optional[str] = None,
                    tags: Optional[List[str]] = None, status: Optional[str] = None,
                    priority: Optional[int] = None) -> bool:
    """Update a document"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if document exists
    cursor.execute('SELECT id FROM documents WHERE id = ?', (doc_id,))
    if not cursor.fetchone():
        conn.close()
        return False

    # Build update query
    updates = []
    params = []

    if title:
        updates.append('title = ?')
        params.append(title)
    if content:
        updates.append('content = ?')
        params.append(content)
        # Update language
        language = detect_language(content)
        updates.append('language = ?')
        params.append(language)
    if category:
        updates.append('category = ?')
        params.append(category)
    if status:
        updates.append('status = ?')
        params.append(status)
    if priority is not None:
        updates.append('priority = ?')
        params.append(priority)
    if tags:
        tags_json = json.dumps(tags)
        updates.append('tags = ?')
        params.append(tags_json)

    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        query = f"UPDATE documents SET {', '.join(updates)} WHERE id = ?"
        params.append(doc_id)
        cursor.execute(query, params)

        # Update tags if provided
        if tags:
            # Remove old tag associations
            cursor.execute('DELETE FROM document_tags WHERE document_id = ?', (doc_id,))

            # Add new tag associations
            for tag in tags:
                cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
                tag_id = cursor.fetchone()[0]
                cursor.execute('INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)', (doc_id, tag_id))

        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

def delete_document(doc_id: int) -> bool:
    """Delete a document (soft delete by status)"""
    return update_document(doc_id, status='deleted')

def search_documents(query: str, category: Optional[str] = None,
                     language: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Search documents by title or content"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search_query = f'%{query}%'
    sql = 'SELECT * FROM documents WHERE status = "active" AND (title LIKE ? OR content LIKE ?)'
    params = [search_query, search_query]

    if category:
        sql += ' AND category = ?'
        params.append(category)
    if language:
        sql += ' AND language = ?'
        params.append(language)

    sql += ' ORDER BY updated_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(sql, params)
    docs = [dict(row) for row in cursor.fetchall()]

    # Record search history
    detected_lang = detect_language(query)
    cursor.execute('''
    INSERT INTO search_history (query, language, results_count)
    VALUES (?, ?, ?)
    ''', (query, detected_lang, len(docs)))

    conn.commit()
    conn.close()
    return docs

def get_categories() -> List[Dict[str, Any]]:
    """Get all categories"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return categories

def add_category(name: str, description: Optional[str] = None,
                 parent_id: Optional[int] = None) -> int:
    """Add a new category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO categories (name, description, parent_id)
    VALUES (?, ?, ?)
    ''', (name, description, parent_id))

    cat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cat_id

def get_tags(popular_only: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
    """Get tags"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if popular_only:
        cursor.execute('SELECT * FROM tags WHERE count > 0 ORDER BY count DESC LIMIT ?', (limit,))
    else:
        cursor.execute('SELECT * FROM tags ORDER BY name LIMIT ?', (limit,))

    tags = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tags

def get_statistics() -> Dict[str, Any]:
    """Get document statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total documents
    cursor.execute('SELECT COUNT(*) FROM documents WHERE status = "active"')
    total = cursor.fetchone()[0]

    # By language
    cursor.execute('SELECT language, COUNT(*) FROM documents WHERE status = "active" GROUP BY language')
    by_language = dict(cursor.fetchall())

    # By category
    cursor.execute('SELECT category, COUNT(*) FROM documents WHERE status = "active" GROUP BY category')
    by_category = dict(cursor.fetchall())

    # Recent documents
    cursor.execute('SELECT COUNT(*) FROM documents WHERE status = "active" AND created_at >= datetime("now", "-7 days")')
    recent = cursor.fetchone()[0]

    conn.close()

    return {
        'total': total,
        'by_language': by_language,
        'by_category': by_category,
        'recent_last_7_days': recent
    }

def export_documents(output_format: str = 'json', category: Optional[str] = None) -> str:
    """Export documents to file"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM documents WHERE status = "active"'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)

    query += ' ORDER BY title'

    cursor.execute(query, params)
    docs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if output_format == 'json':
        output_path = EXPORT_DIR / f"documents_export_{timestamp}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
    else:
        # Markdown format
        output_path = EXPORT_DIR / f"documents_export_{timestamp}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in docs:
                f.write(f"# {doc['title']}\n\n")
                f.write(f"**Category:** {doc['category'] or 'N/A'} | ")
                f.write(f"**Language:** {doc['language']} | ")
                f.write(f"**Created:** {doc['created_at']}\n\n")
                if doc['tags']:
                    f.write(f"**Tags:** {doc['tags']}\n\n")
                f.write(f"{doc['content']}\n\n")
                f.write("---\n\n")

    return str(output_path)

def get_recent_documents(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recently updated documents"""
    return get_documents(status='active', limit=limit)

if __name__ == '__main__':
    init_db()
