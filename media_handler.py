"""
Media download functionality for Telegram messages
"""

from pathlib import Path


def cleanup_existing_media(message_folder, filename_base):
    """Clean up any existing media files to avoid duplicates."""
    try:
        media_files = []
        
        # First, collect all media files (non-HTML/MD files)
        for file_path in message_folder.iterdir():
            if file_path.is_file():
                # Skip HTML and Markdown files
                if file_path.suffix.lower() not in ['.html', '.md']:
                    media_files.append(file_path)
        
        if media_files:
            print(f"    - Found {len(media_files)} existing media file(s) to clean up")
            for file_path in media_files:
                print(f"    - Removing existing media file: {file_path.name}")
                file_path.unlink()
        else:
            print(f"    - No existing media files to clean up")
                    
    except Exception as e:
        print(f"    - Warning: Could not clean up existing media files: {e}")


async def download_media(client, message, message_folder, filename_base):
    """Download media from a message and save it in the message folder."""
    if not message.media:
        return None
    
    try:
        print(f"    - Starting media download...")
        
        # Clean up any existing media files first to avoid duplicates
        cleanup_existing_media(message_folder, filename_base)
        
        # Download the media to the message folder
        file_path = await client.download_media(message.media, file=message_folder)
        if file_path:
            print(f"    - Media downloaded successfully")
            # Rename to a consistent name
            file_ext = Path(file_path).suffix
            new_name = f"{filename_base}{file_ext}"
            new_path = message_folder / new_name
            
            # If the target file already exists, remove it first
            if new_path.exists():
                print(f"    - Removing existing file: {new_name}")
                new_path.unlink()
            
            Path(file_path).rename(new_path)
            print(f"    - Media renamed to: {new_name}")
            return new_name
        else:
            print(f"    - Media download returned None")
    except Exception as e:
        print(f"    - Failed to download media: {e}")
    
    return None