"""
Database operations for tracking exported messages
"""

import sqlite3
from pathlib import Path

# Import configuration
try:
    from config import OUTPUT_DIR
except ImportError:
    print("⚠️  ERROR: config.py file not found!")
    exit(1)


def init_database():
    """Initialize SQLite database to track exported messages."""
    # Ensure output directory exists
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    db_path = output_path / 'export_history.db'
    conn = sqlite3.connect(db_path)
    
    # Create table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS exported_messages (
            message_id INTEGER PRIMARY KEY,
            date_exported TEXT DEFAULT CURRENT_TIMESTAMP,
            message_date TEXT,
            message_text TEXT,
            has_media BOOLEAN DEFAULT 0,
            media_filename TEXT,
            file_path TEXT,
            hash TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path


def is_message_exported(db_path, message_id):
    """Check if a message has already been exported."""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('SELECT 1 FROM exported_messages WHERE message_id = ?', (message_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def mark_message_exported(db_path, message, media_filename=None, file_path=None):
    """Mark a message as exported in the database."""
    conn = sqlite3.connect(db_path)
    
    # Create a simple hash for change detection
    content_hash = str(hash(str(message.text or '') + str(message.date)))
    
    conn.execute('''
        INSERT OR REPLACE INTO exported_messages 
        (message_id, message_date, message_text, has_media, media_filename, file_path, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.id,
        message.date.isoformat(),  # Convert datetime to string
        (message.text or '')[:500],  # Limit text length for database
        bool(message.media),
        media_filename,
        file_path,
        content_hash
    ))
    
    conn.commit()
    conn.close()


def get_export_stats(db_path):
    """Get statistics about exported messages."""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN has_media = 1 THEN 1 END) as with_media,
            MIN(message_date) as oldest,
            MAX(message_date) as newest
        FROM exported_messages
    ''')
    stats = cursor.fetchone()
    conn.close()
    return stats