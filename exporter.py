"""
Main export logic for Telegram saved messages
"""

import time
import asyncio
from pathlib import Path
from telethon.tl.types import Message
from telethon.errors import (
    ServerError, 
    FloodWaitError,
    TimedOutError
)

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


async def reconnect_client(client, max_retries=3, delay=5):
    """Reconnect to Telegram with retries."""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempting to reconnect... (Attempt {attempt + 1}/{max_retries})")
            
            if client.is_connected():
                await client.disconnect()
            
            await asyncio.sleep(delay)
            await client.connect()
            
            if client.is_connected():
                print("✓ Reconnected successfully!")
                return True
                
        except Exception as e:
            print(f"⚠️ Reconnection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
    
    print("❌ Failed to reconnect after all attempts")
    return False


async def safe_operation(client, operation, *args, max_retries=3, **kwargs):
    """Execute an operation with automatic reconnection on network errors."""
    for attempt in range(max_retries):
        try:
            return await operation(*args, **kwargs)
            
        except (ConnectionError, TimedOutError, OSError) as e:
            print(f"⚠️ Connection error: {e}")
            
            if attempt < max_retries - 1:
                print(f"🔄 Retrying operation (attempt {attempt + 2}/{max_retries})...")
                
                # Try to reconnect
                if not client.is_connected():
                    reconnected = await reconnect_client(client)
                    if not reconnected:
                        raise Exception("Failed to reconnect to Telegram")
                
                await asyncio.sleep(2)
            else:
                print(f"❌ Operation failed after {max_retries} attempts")
                raise
                
        except FloodWaitError as e:
            wait_time = e.seconds
            print(f"⚠️ Flood wait error: need to wait {wait_time} seconds")
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            await asyncio.sleep(wait_time)
            
        except ServerError as e:
            print(f"⚠️ Server error: {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in 5 seconds... (attempt {attempt + 2}/{max_retries})")
                await asyncio.sleep(5)
            else:
                raise
    
    raise Exception(f"Operation failed after {max_retries} attempts")


async def export_saved_messages(client, db_path, from_date=None, force_reexport=False, output_dir=None, cancel_event=None):
    """Export saved messages from Telegram with automatic reconnection."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
        
    print("Fetching saved messages...")
    
    # Get saved messages (chat with yourself) with retry logic
    me = await safe_operation(client, client.get_me)
    saved_messages = await safe_operation(client, client.get_entity, 'me')
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Fetch messages with connection handling
    messages = []
    skipped_count = 0
    
    try:
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
    except (ConnectionError, OSError) as e:
        print(f"⚠️ Connection lost while fetching messages: {e}")
        print("🔄 Attempting to reconnect and continue...")
        
        if await reconnect_client(client):
            # Retry fetching from where we left off
            print("Continuing message fetch...")
            async for message in client.iter_messages(saved_messages):
                if isinstance(message, Message):
                    if from_date and message.date.date() < from_date:
                        continue
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
        # Cooperative cancellation check
        if cancel_event and cancel_event.is_set():
            print("\n⚠️ Cancellation requested. Stopping export after current message.")
            break
        retry_count = 0
        max_message_retries = 3
        
        while retry_count < max_message_retries:
            if cancel_event and cancel_event.is_set():
                print(f"⚠️ Cancelled before processing message {message.id}")
                break
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
                
                # Download media if present with retry logic
                media_filename = None
                if message.media:
                    print(f"  - Downloading media...")
                    try:
                        media_filename = await safe_operation(
                            client,
                            download_media,
                            client, message, message_folder, "media", cancel_event
                        )
                        print(f"  - Media downloaded: {media_filename}")
                    except Exception as e:
                        if cancel_event and cancel_event.is_set():
                            print(f"  ⚠️ Media download cancelled")
                            break
                        print(f"  ⚠️ Failed to download media: {e}")
                        print(f"  - Continuing without media...")
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
                    if cancel_event and cancel_event.is_set():
                        print("⚠️ Cancellation detected during progress update.")
                        break
                    print(f"\n*** PROGRESS UPDATE: {exported_count}/{len(messages)} messages exported ({exported_count/len(messages)*100:.1f}%) ***")
                    print(f"*** Time elapsed: {elapsed_total/60:.1f}min | Estimated remaining: {estimated_remaining/60:.1f}min ***\n")
                
                # Success - break retry loop
                break
                
            except (ConnectionError, OSError, TimedOutError) as e:
                retry_count += 1
                print(f"⚠️ Connection error while processing message {message.id}: {e}")
                
                if retry_count < max_message_retries:
                    print(f"🔄 Retrying message (attempt {retry_count + 1}/{max_message_retries})...")
                    
                    # Try to reconnect
                    if not client.is_connected():
                        reconnected = await reconnect_client(client)
                        if not reconnected:
                            print(f"❌ Failed to reconnect, skipping message {message.id}")
                            break
                    
                    # Check cancellation before retry wait
                    if cancel_event and cancel_event.is_set():
                        print("⚠️ Cancelled during retry.")
                        break
                    
                    await asyncio.sleep(3)
                else:
                    print(f"❌ Failed to export message {message.id} after {max_message_retries} attempts, skipping...")
                    
            except Exception as e:
                print(f"❌ Error exporting message {message.id}: {e}")
                print(f"  - Skipping this message and continuing...")
                break
            print(f"Error exporting message {message.id}: {e}")
            continue
    
    if cancel_event and cancel_event.is_set():
        print(f"\n⚠️ Export cancelled. {exported_count} messages exported (partial).")
    else:
        print(f"\n✓ Successfully exported {exported_count} messages to '{OUTPUT_DIR}' directory")