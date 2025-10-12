"""
Media download functionality for Telegram messages
"""

from pathlib import Path


async def download_media(client, message, message_folder, filename_base):
    """Download media from a message and save it in the message folder."""
    if not message.media:
        return None
    
    try:
        print(f"    - Starting media download...")
        # Download the media to the message folder
        file_path = await client.download_media(message.media, file=message_folder)
        if file_path:
            print(f"    - Media downloaded successfully")
            # Rename to a consistent name
            file_ext = Path(file_path).suffix
            new_name = f"{filename_base}{file_ext}"
            new_path = message_folder / new_name
            Path(file_path).rename(new_path)
            print(f"    - Media renamed to: {new_name}")
            return new_name
        else:
            print(f"    - Media download returned None")
    except Exception as e:
        print(f"    - Failed to download media: {e}")
    
    return None