"""
Database operations for tracking exported messages
"""

import sqlite3
from pathlib import Path
def get_db_connection(db_path, timeout=30):
    """Create a database connection with proper settings for concurrent access."""
    conn = sqlite3.connect(
        db_path,
        timeout=timeout,
        check_same_thread=False,
        isolation_level='DEFERRED'
    )
    # Enable WAL mode for better concurrent access
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    return conn


def init_database(output_dir=None):
    """Initialize SQLite database to track exported messages."""
    if output_dir is None:
        # Import configuration
        try:
            from config import OUTPUT_DIR
            output_dir = OUTPUT_DIR
        except ImportError:
            print("⚠️  ERROR: config.py file not found!")
            exit(1)
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    db_path = output_path / 'export_history.db'
    conn = get_db_connection(str(db_path))
    
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
    
    # Create backup tracking table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS backup_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_folder TEXT NOT NULL,
            folder_path TEXT NOT NULL,
            archive_filename TEXT NOT NULL,
            archive_size_bytes INTEGER,
            upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
            google_drive_file_id TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            UNIQUE(message_folder)
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path


def is_message_exported(db_path, message_id):
    """Check if a message has already been exported."""
    conn = get_db_connection(db_path)
    cursor = conn.execute('SELECT 1 FROM exported_messages WHERE message_id = ?', (message_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def mark_message_exported(db_path, message, media_filename=None, file_path=None):
    """Mark a message as exported in the database."""
    conn = get_db_connection(db_path)
    
    # Create a simple hash for change detection
    content_hash = str(hash(str(message.text or '') + str(message.date)))
    
    conn.execute('''
        INSERT OR REPLACE INTO exported_messages 
        (message_id, message_date, message_text, has_media, media_filename, file_path, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.id,
        message.date.isoformat(),  # Convert datetime to string
        (message.text or ''),  # Store full text for search
        bool(message.media),
        media_filename,
        file_path,
        content_hash
    ))
    
    conn.commit()
    conn.close()


def search_messages(db_path, text_query=None, filename_query=None, date_from=None, date_to=None):
    """Search exported messages by text or filename with flexible matching.
    
    Normalizes search by removing extra spaces, underscores, and special characters
    to allow finding files even with approximate matches.
    
    Args:
        db_path: Path to database
        text_query: Search in message text (case-insensitive, normalized)
        filename_query: Search in media filenames (case-insensitive, normalized)
        date_from: Filter messages from this date (YYYY-MM-DD)
        date_to: Filter messages to this date (YYYY-MM-DD)
    
    Returns:
        List of tuples: (message_id, message_date, message_text, media_filename, file_path)
    """
    import re
    
    def normalize_for_search(text):
        """Normalize text for flexible search - remove extra spaces, underscores, special chars
        
        Examples:
            "ха__кер" -> "хакер"
            "test___file___name" -> "testfilename"
            "some-text_with__symbols" -> "some text with symbols"
        """
        if not text:
            return ''
        # Convert to lowercase
        text = text.lower()
        # First, remove ALL underscores completely (don't replace with spaces)
        # This allows "ха__кер" to become "хакер"
        text = text.replace('_', '')
        # Replace hyphens with spaces for word separation
        text = text.replace('-', ' ')
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters except spaces and alphanumeric
        text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        return text.strip()
    
    conn = get_db_connection(db_path)
    
    # Build query
    query = 'SELECT message_id, message_date, message_text, media_filename, file_path FROM exported_messages WHERE 1=1'
    params = []
    
    # Text search with normalization
    if text_query:
        normalized_query = normalize_for_search(text_query)
        # Split into words for flexible matching
        words = normalized_query.split()
        if words:
            # Search for all words (can be in any order)
            # Remove ALL underscores from text for matching
            for word in words:
                query += ' AND LOWER(REPLACE(REPLACE(message_text, "_", ""), "-", " ")) LIKE ?'
                params.append(f'%{word}%')
    
    # Filename search with normalization
    if filename_query:
        normalized_query = normalize_for_search(filename_query)
        # Split into words for flexible matching
        words = normalized_query.split()
        if words:
            # Search for all words in filename
            # Remove ALL underscores from filename for matching
            for word in words:
                query += ' AND LOWER(REPLACE(REPLACE(REPLACE(media_filename, "_", ""), "-", " "), "  ", " ")) LIKE ?'
                params.append(f'%{word}%')
    
    # Date filters
    if date_from:
        query += ' AND message_date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND message_date <= ?'
        params.append(date_to)
    
    query += ' ORDER BY message_date DESC LIMIT 500'
    
    cursor = conn.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return results


def get_export_stats(db_path):
    """Get statistics about exported messages."""
    conn = get_db_connection(db_path)
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
    
    # Return as dictionary
    if stats:
        return {
            'total_messages': stats[0],
            'with_media': stats[1],
            'oldest': stats[2],
            'newest': stats[3],
            'total_folders': stats[0]  # Same as total messages for now
        }
    else:
        return {
            'total_messages': 0,
            'with_media': 0,
            'oldest': None,
            'newest': None,
            'total_folders': 0
        }


def is_folder_backed_up(db_path, folder_name):
    """Check if a folder has already been backed up to Google Drive."""
    conn = get_db_connection(db_path)
    cursor = conn.execute(
        'SELECT status FROM backup_history WHERE message_folder = ? AND status = ?', 
        (folder_name, 'completed')
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def mark_backup_started(db_path, folder_name, folder_path, archive_filename, archive_size):
    """Mark a folder backup as started."""
    conn = get_db_connection(db_path)
    conn.execute('''
        INSERT OR REPLACE INTO backup_history 
        (message_folder, folder_path, archive_filename, archive_size_bytes, status)
        VALUES (?, ?, ?, ?, 'uploading')
    ''', (folder_name, folder_path, archive_filename, archive_size))
    conn.commit()
    conn.close()


def mark_backup_completed(db_path, folder_name, google_drive_file_id):
    """Mark a folder backup as completed with Google Drive file ID."""
    conn = get_db_connection(db_path)
    conn.execute('''
        UPDATE backup_history 
        SET status = 'completed', 
            google_drive_file_id = ?,
            upload_date = CURRENT_TIMESTAMP
        WHERE message_folder = ?
    ''', (google_drive_file_id, folder_name))
    conn.commit()
    conn.close()


def mark_backup_failed(db_path, folder_name, error_message):
    """Mark a folder backup as failed with error message."""
    conn = get_db_connection(db_path)
    conn.execute('''
        UPDATE backup_history 
        SET status = 'failed',
            error_message = ?
        WHERE message_folder = ?
    ''', (error_message, folder_name))
    conn.commit()
    conn.close()


def get_backup_stats(db_path):
    """Get statistics about backups."""
    conn = get_db_connection(db_path)
    cursor = conn.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
            SUM(CASE WHEN status = 'completed' THEN archive_size_bytes ELSE 0 END) as total_uploaded_bytes
        FROM backup_history
    ''')
    stats = cursor.fetchone()
    conn.close()
    
    # Return as dictionary
    if stats:
        return {
            'total_backups': stats[0],
            'completed_backups': stats[1],
            'failed_backups': stats[2],
            'total_bytes_uploaded': stats[3] if stats[3] else 0
        }
    else:
        return {
            'total_backups': 0,
            'completed_backups': 0,
            'failed_backups': 0,
            'total_bytes_uploaded': 0
        }


def get_folders_to_backup(db_path, export_dir):
    """Get list of folders that haven't been backed up yet."""
    from pathlib import Path
    
    export_path = Path(export_dir)
    all_folders = [f for f in export_path.iterdir() if f.is_dir()]
    
    conn = get_db_connection(db_path)
    cursor = conn.execute(
        'SELECT message_folder FROM backup_history WHERE status = ?',
        ('completed',)
    )
    backed_up = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Return folders that haven't been backed up
    folders_to_backup = [f for f in all_folders if f.name not in backed_up]
    return folders_to_backup