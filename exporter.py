"""
Main export logic for Telegram saved messages
"""

import time
from pathlib import Path
from telethon.tl.types import Message

# Import configuration
try:
    from config import OUTPUT_DIR
except ImportError:
    print("⚠️  ERROR: config.py file not found!")
    exit(1)

from utils import sanitize_filename
from database import is_message_exported, mark_message_exported
from formatters import message_to_html_with_media, message_to_markdown
from media_handler import download_media


async def export_saved_messages(client, db_path, from_date=None, force_reexport=False, output_dir=None):
    """Export saved messages from Telegram."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
        
    print("Fetching saved messages...")
    
    # Get saved messages (chat with yourself)
    me = await client.get_me()
    saved_messages = await client.get_entity('me')
    
    # Create output directory
    output_path = Path(output_dir)
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
    print(f"\nStarting export process...")
    start_time = time.time()
    
    for idx, message in enumerate(messages, 1):
        try:
            msg_start_time = time.time()
            print(f"\n[{idx}/{len(messages)}] Processing message {message.id}... (Started at {time.strftime('%H:%M:%S')})")
            
            # Create filename based on date and message preview
            date_str = message.date.strftime('%Y%m%d_%H%M%S')
            print(f"  - Creating filename from date: {date_str}")
            
            # Get a preview of the message for filename
            if message.text:
                preview = sanitize_filename(message.text[:30])
                print(f"  - Using text preview: {preview}")
            else:
                preview = "message"
                print(f"  - No text, using default name: {preview}")
            
            filename_base = f"{date_str}_msg{message.id}_{preview}"
            print(f"  - Final filename base: {filename_base}")
            
            # Create individual message folder
            message_folder = output_path / filename_base
            message_folder.mkdir(exist_ok=True)
            print(f"  - Created folder: {message_folder}")
            
            # Download media if present (save in message folder)
            media_filename = None
            if message.media:
                print(f"  - Downloading media...")
                media_filename = await download_media(client, message, message_folder, "media")
                print(f"  - Media downloaded: {media_filename}")
            else:
                print(f"  - No media to download")
            
            # Generate HTML with media support
            print(f"  - Generating HTML content...")
            html_content = await message_to_html_with_media(message, media_filename)
            html_path = message_folder / "message.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  - HTML file saved")
            
            # Generate Markdown
            print(f"  - Generating Markdown content...")
            md_content = message_to_markdown(message)
            md_path = message_folder / "message.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  - Markdown file saved")
            
            # Mark message as exported in database
            print(f"  - Updating database...")
            mark_message_exported(db_path, message, media_filename, str(html_path))
            
            exported_count += 1
            msg_end_time = time.time()
            msg_duration = msg_end_time - msg_start_time
            elapsed_total = msg_end_time - start_time
            avg_time_per_message = elapsed_total / exported_count
            estimated_remaining = (len(messages) - exported_count) * avg_time_per_message
            
            print(f"✓ Exported {exported_count}/{len(messages)}: {filename_base}")
            print(f"  - Message took: {msg_duration:.2f}s | Avg: {avg_time_per_message:.2f}s | Est. remaining: {estimated_remaining/60:.1f}min")
            
            # Show progress every 10 messages
            if exported_count % 10 == 0:
                print(f"\n*** PROGRESS UPDATE: {exported_count}/{len(messages)} messages exported ({exported_count/len(messages)*100:.1f}%) ***")
                print(f"*** Time elapsed: {elapsed_total/60:.1f}min | Estimated remaining: {estimated_remaining/60:.1f}min ***\n")
            
        except Exception as e:
            print(f"Error exporting message {message.id}: {e}")
            continue
    
    print(f"\n✓ Successfully exported {exported_count} messages to '{OUTPUT_DIR}' directory")