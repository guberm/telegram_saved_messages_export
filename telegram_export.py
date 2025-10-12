#!/usr/bin/env python3
"""
Telegram Saved Messages Exporter
Exports saved messages from Telegram to separate HTML and Markdown files.
"""

import asyncio
import os
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import Message
import html

# Import configuration
try:
    from config import API_ID, API_HASH, PHONE, OUTPUT_DIR, SESSION_NAME
except ImportError:
    print("⚠️  ERROR: config.py file not found!")
    print("Please create a config.py file with your API credentials.")
    print("You can copy config.py.example and fill in your values.")
    exit(1)


def sanitize_filename(text, max_length=50):
    """Create a safe filename from text."""
    if not text:
        return 'unnamed'
    
    # Remove or replace invalid characters including newlines and tabs
    invalid_chars = '<>:"/\\|?*\n\r\t'
    for char in invalid_chars:
        text = text.replace(char, '_')
    
    # Replace emojis and special characters that might cause issues
    import re
    # Remove emojis and special unicode characters
    text = re.sub(r'[^\w\s\-_.]', '_', text)
    
    # Limit length and strip whitespace
    text = text[:max_length].strip()
    
    # Replace multiple spaces/underscores with single underscore
    while '  ' in text:
        text = text.replace('  ', ' ')
    while '__' in text:
        text = text.replace('__', '_')
    
    # Replace spaces with underscores for filename safety
    text = text.replace(' ', '_')
    
    return text if text else 'unnamed'


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


def message_to_markdown(message):
    """Convert a Telegram message to Markdown format."""
    md_content = []
    
    # Header with metadata
    md_content.append(f"# Message {message.id}\n")
    md_content.append(f"**Date:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if message.forward:
        if message.forward.from_name:
            md_content.append(f"**Forwarded from:** {message.forward.from_name}\n")
        md_content.append(f"**Originally sent:** {message.forward.date.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    md_content.append("\n---\n\n")
    
    # Message text
    if message.text:
        md_content.append(message.text)
        md_content.append("\n")
    
    # Media information
    if message.media:
        md_content.append(f"\n**Media Type:** {type(message.media).__name__}\n")
        
        if hasattr(message.media, 'caption') and message.media.caption:
            md_content.append(f"\n**Caption:** {message.media.caption}\n")
    
    # Web page preview
    if message.web_preview:
        md_content.append(f"\n**Link:** [{message.web_preview.title}]({message.web_preview.url})\n")
    
    return ''.join(md_content)


def process_telegram_formatting(text):
    """Process Telegram formatting like **bold**, `code`, etc."""
    if not text:
        return ""
    
    # Escape HTML first
    text = html.escape(text)
    
    # Process bold text **text**
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<span class="bold">\1</span>', text)
    
    # Process code `text`
    text = re.sub(r'`([^`]+)`', r'<span class="code">\1</span>', text)
    
    # Process code blocks ```text```
    text = re.sub(r'```(.*?)```', r'<div class="code-block">\1</div>', text, flags=re.DOTALL)
    
    # Process links (simple http/https detection)
    text = re.sub(r'(https?://[^\s]+)', r'<a href="\1" class="message-link" target="_blank">\1</a>', text)
    
    return text


def message_to_html(message):
    """Convert a Telegram message to HTML format that matches Telegram's appearance."""
    html_parts = []
    
    # Start HTML document
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Message {}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .chat-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #1e2832;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .chat-header {{
            background: #2b5278;
            padding: 15px 20px;
            color: #ffffff;
            font-weight: 500;
            font-size: 16px;
            border-bottom: 1px solid #3d5980;
        }}
        .message-bubble {{
            background: #2f3c4c;
            margin: 12px 20px;
            padding: 12px 16px;
            border-radius: 12px;
            border-top-left-radius: 4px;
            position: relative;
            max-width: 85%;
        }}
        .message-content {{
            color: #ffffff;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .message-time {{
            color: #8596a8;
            font-size: 12px;
            margin-top: 8px;
            text-align: right;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .message-forward {{
            color: #64b5ef;
            font-size: 13px;
            margin-bottom: 8px;
            padding-left: 12px;
            border-left: 3px solid #64b5ef;
        }}
        .message-media {{
            margin-top: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            font-size: 12px;
            color: #8596a8;
        }}
        .message-link {{
            color: #64b5ef;
            text-decoration: none;
            border-bottom: 1px solid rgba(100, 181, 239, 0.3);
        }}
        .message-link:hover {{
            border-bottom-color: #64b5ef;
        }}
        .bold {{
            font-weight: 600;
        }}
        .code {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .code-block {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 8px 0;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            Saved Messages
        </div>
        <div class="message-bubble">
""".format(message.id))
    
    # Forward information
    if message.forward:
        html_parts.append('            <div class="message-forward">\n')
        if message.forward.from_name:
            html_parts.append(f'                Forwarded from {html.escape(message.forward.from_name)}\n')
        else:
            html_parts.append('                Forwarded message\n')
        html_parts.append('            </div>\n')
    
    # Message content with Telegram formatting
    if message.text:
        # Process Telegram formatting
        formatted_text = process_telegram_formatting(message.text)
        html_parts.append('            <div class="message-content">\n')
        html_parts.append(f'                {formatted_text}\n')
        html_parts.append('            </div>\n')
    
    # Media information
    if message.media:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                📎 {html.escape(type(message.media).__name__)}\n')
        
        if hasattr(message.media, 'caption') and message.media.caption:
            caption_formatted = process_telegram_formatting(message.media.caption)
            html_parts.append(f'<br>                {caption_formatted}\n')
        
        html_parts.append('            </div>\n')
    
    # Web page preview
    if message.web_preview:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                🔗 <a href="{html.escape(message.web_preview.url)}" class="message-link" target="_blank">{html.escape(message.web_preview.title or message.web_preview.url)}</a>\n')
        html_parts.append('            </div>\n')
    
    # Message time and link
    html_parts.append('            <div class="message-time">\n')
    # Add link to original message in Telegram
    telegram_link = f'tg://openmessage?user_id=me&message_id={message.id}'
    html_parts.append(f'                <a href="{telegram_link}" class="message-link" style="font-size: 11px; opacity: 0.7;">🔗</a>\n')
    html_parts.append(f'                <span>{html.escape(message.date.strftime("%H:%M"))}</span>\n')
    html_parts.append('            </div>\n')
    
    # Close HTML
    html_parts.append("""        </div>
    </div>
</body>
</html>""")
    
    return ''.join(html_parts)


async def download_media(client, message, message_folder, filename_base):
    """Download media from a message and save it in the message folder."""
    if not message.media:
        return None
    
    try:
        # Download the media to the message folder
        file_path = await client.download_media(message.media, file=message_folder)
        if file_path:
            # Rename to a consistent name
            file_ext = Path(file_path).suffix
            new_name = f"{filename_base}{file_ext}"
            new_path = message_folder / new_name
            Path(file_path).rename(new_path)
            return new_name
    except Exception as e:
        print(f"Failed to download media: {e}")
    
    return None


async def message_to_html_with_media(message, media_filename):
    """Convert a Telegram message to HTML format with media support."""
    html_parts = []
    
    # Start HTML document (same as before)
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Message {}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .chat-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #1e2832;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .chat-header {{
            background: #2b5278;
            padding: 15px 20px;
            color: #ffffff;
            font-weight: 500;
            font-size: 16px;
            border-bottom: 1px solid #3d5980;
        }}
        .message-bubble {{
            background: #2f3c4c;
            margin: 12px 20px;
            padding: 12px 16px;
            border-radius: 12px;
            border-top-left-radius: 4px;
            position: relative;
            max-width: 85%;
        }}
        .message-content {{
            color: #ffffff;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .message-time {{
            color: #8596a8;
            font-size: 12px;
            margin-top: 8px;
            text-align: right;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .message-forward {{
            color: #64b5ef;
            font-size: 13px;
            margin-bottom: 8px;
            padding-left: 12px;
            border-left: 3px solid #64b5ef;
        }}
        .message-media {{
            margin-top: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            font-size: 12px;
            color: #8596a8;
        }}
        .message-image {{
            margin-top: 8px;
            border-radius: 8px;
            overflow: hidden;
        }}
        .message-image img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .message-link {{
            color: #64b5ef;
            text-decoration: none;
            border-bottom: 1px solid rgba(100, 181, 239, 0.3);
        }}
        .message-link:hover {{
            border-bottom-color: #64b5ef;
        }}
        .bold {{
            font-weight: 600;
        }}
        .code {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .code-block {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 8px 0;
            overflow-x: auto;
        }}
        .post-link {{
            background: rgba(100, 181, 239, 0.1);
            border: 1px solid rgba(100, 181, 239, 0.3);
            border-radius: 8px;
            padding: 8px;
            margin-top: 8px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            Saved Messages
        </div>
        <div class="message-bubble">
""".format(message.id))
    
    # Forward information
    if message.forward:
        html_parts.append('            <div class="message-forward">\n')
        if message.forward.from_name:
            html_parts.append(f'                Forwarded from {html.escape(message.forward.from_name)}\n')
        else:
            html_parts.append('                Forwarded message\n')
        html_parts.append('            </div>\n')
    
    # Message content with Telegram formatting
    if message.text:
        # Process Telegram formatting
        formatted_text = process_telegram_formatting(message.text)
        html_parts.append('            <div class="message-content">\n')
        html_parts.append(f'                {formatted_text}\n')
        html_parts.append('            </div>\n')
    
    # Media (images, videos, etc.)
    if media_filename:
        html_parts.append('            <div class="message-image">\n')
        html_parts.append(f'                <img src="{media_filename}" alt="Message media" loading="lazy">\n')
        html_parts.append('            </div>\n')
    elif message.media:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                📎 {html.escape(type(message.media).__name__)}\n')
        
        if hasattr(message.media, 'caption') and message.media.caption:
            caption_formatted = process_telegram_formatting(message.media.caption)
            html_parts.append(f'<br>                {caption_formatted}\n')
        
        html_parts.append('            </div>\n')
    
    # Web page preview
    if message.web_preview:
        html_parts.append('            <div class="message-media">\n')
        html_parts.append(f'                🔗 <a href="{html.escape(message.web_preview.url)}" class="message-link" target="_blank">{html.escape(message.web_preview.title or message.web_preview.url)}</a>\n')
        html_parts.append('            </div>\n')
    
    # Add original post link if it's forwarded from a public channel
    if message.forward and hasattr(message.forward, 'from_id') and message.forward.from_id:
        try:
            # Try to create a public link for channels/groups
            if hasattr(message.forward.from_id, 'channel_id'):
                channel_id = message.forward.from_id.channel_id
                post_id = getattr(message.forward, 'channel_post', message.id)
                # This is a simplified approach - in reality you'd need to know the channel username
                html_parts.append('            <div class="post-link">\n')
                html_parts.append(f'                🔗 <a href="https://t.me/c/{channel_id}/{post_id}" class="message-link" target="_blank">View original post</a>\n')
                html_parts.append('            </div>\n')
        except:
            pass
    
    # Message time and link
    html_parts.append('            <div class="message-time">\n')
    # Add link to original message in Telegram (works in Telegram apps)
    telegram_link = f'tg://openmessage?user_id=me&message_id={message.id}'
    html_parts.append(f'                <a href="{telegram_link}" class="message-link" style="font-size: 11px; opacity: 0.7;">📱</a>\n')
    html_parts.append(f'                <span>{html.escape(message.date.strftime("%H:%M"))}</span>\n')
    html_parts.append('            </div>\n')
    
    # Close HTML
    html_parts.append("""        </div>
    </div>
</body>
</html>""")
    
    return ''.join(html_parts)


async def export_saved_messages(client, db_path, from_date=None, force_reexport=False):
    """Export saved messages from Telegram."""
    print("Fetching saved messages...")
    
    # Get saved messages (chat with yourself)
    me = await client.get_me()
    saved_messages = await client.get_entity('me')
    
    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    # Fetch messages
    messages = []
    skipped_count = 0
    async for message in client.iter_messages(saved_messages):
        if isinstance(message, Message):
            # Filter by date if specified
            if from_date and message.date.date() < from_date:
                continue
            
            # Check if message was already exported (unless force reexport)
            if not force_reexport and is_message_exported(db_path, message.id):
                skipped_count += 1
                continue
                
            messages.append(message)
    
    print(f"Found {len(messages)} new messages to export")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} already exported messages")
    
    # Export each message
    exported_count = 0
    for idx, message in enumerate(messages, 1):
        try:
            # Create filename based on date and message preview
            date_str = message.date.strftime('%Y%m%d_%H%M%S')
            
            # Get a preview of the message for filename
            if message.text:
                preview = sanitize_filename(message.text[:30])
            else:
                preview = "message"
            
            filename_base = f"{date_str}_msg{message.id}_{preview}"
            
            # Create individual message folder
            message_folder = output_path / filename_base
            message_folder.mkdir(exist_ok=True)
            
            # Download media if present (save in message folder)
            media_filename = None
            if message.media:
                media_filename = await download_media(client, message, message_folder, "media")
            
            # Generate HTML with media support
            html_content = await message_to_html_with_media(message, media_filename)
            html_path = message_folder / "message.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate Markdown
            md_content = message_to_markdown(message)
            md_path = message_folder / "message.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # Mark message as exported in database
            mark_message_exported(db_path, message, media_filename, str(html_path))
            
            exported_count += 1
            print(f"Exported {exported_count}/{len(messages)}: {filename_base}")
            
        except Exception as e:
            print(f"Error exporting message {message.id}: {e}")
            continue
    
    print(f"\n✓ Successfully exported {exported_count} messages to '{OUTPUT_DIR}' directory")


async def main():
    """Main function to run the exporter."""
    global OUTPUT_DIR
    
    parser = argparse.ArgumentParser(
        description='Export Telegram saved messages to HTML and Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all saved messages (incremental - skips already exported)
  python telegram_export.py
  
  # Export messages from a specific date onwards
  python telegram_export.py --from-date 2024-01-01
  
  # Force re-export of already exported messages
  python telegram_export.py --force
  
  # Show export statistics
  python telegram_export.py --stats
  
  # Export with custom output directory
  python telegram_export.py --output my_exports
        """
    )
    
    parser.add_argument('--from-date', type=str,
                      help='Export messages from this date onwards (format: YYYY-MM-DD). If not specified, exports all messages.')
    parser.add_argument('--force', action='store_true',
                      help='Force re-export of already exported messages')
    parser.add_argument('--stats', action='store_true',
                      help='Show export statistics and exit')
    
    parser.add_argument('--output', type=str, default=OUTPUT_DIR,
                       help=f'Output directory (default: {OUTPUT_DIR})')
    
    args = parser.parse_args()
    
    # Update output directory if specified
    OUTPUT_DIR = args.output
    
    # Initialize database
    db_path = init_database()
    
    # Show stats if requested
    if args.stats:
        stats = get_export_stats(db_path)
        if stats[0] > 0:
            print(f"\n📊 Export Statistics:")
            print(f"Total messages exported: {stats[0]}")
            print(f"Messages with media: {stats[1]}")
            print(f"Date range: {stats[2]} to {stats[3]}")
        else:
            print("No messages have been exported yet.")
        return
    
    # Parse date if provided
    from_date = None
    if args.from_date:
        try:
            from_date = datetime.strptime(args.from_date, '%Y-%m-%d').date()
            print(f"Exporting messages from {from_date} onwards")
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            return
    else:
        print("Exporting all saved messages (incremental - skipping already exported)")
    
    # Check if credentials are set
    if not API_ID or not API_HASH or API_ID == 'YOUR_API_ID' or API_HASH == 'YOUR_API_HASH':
        print("\n⚠️  ERROR: Please configure your API credentials first!")
        print("\n1. Go to https://my.telegram.org/auth")
        print("2. Log in with your phone number")
        print("3. Go to 'API development tools'")
        print("4. Create a new application (if you haven't)")
        print("5. Copy your api_id and api_hash")
        print("6. Edit config.py and replace the placeholder values")
        print("7. Also replace the phone number with your own\n")
        return
    
    # Create Telegram client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✓ Connected to Telegram")
        
        # Export messages
        await export_saved_messages(client, db_path, from_date=from_date, force_reexport=args.force)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
