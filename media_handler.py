"""
Media download functionality for Telegram messages
"""

import os
import time
from pathlib import Path


def format_file_size(size_bytes):
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


class DownloadProgress:
    """Progress tracker for media downloads."""
    
    def __init__(self, total_size):
        self.total_size = total_size
        self.downloaded = 0
        self.start_time = time.time()
        self.last_update = 0
        self.completed = False
        
    def __call__(self, current, total):
        """Progress callback function."""
        self.downloaded = current
        self.total_size = total
        
        # Update progress every 512KB or every 1 second for more responsive updates
        now = time.time()
        if (current - self.last_update > 512 * 1024) or (now - self.start_time > 1 and now - self.last_update > 1):
            self.last_update = current
            
            if total > 0:
                percentage = (current / total) * 100
                downloaded_str = format_file_size(current)
                total_str = format_file_size(total)
                
                # Calculate speed
                elapsed = now - self.start_time
                if elapsed > 0:
                    speed = current / elapsed
                    speed_str = format_file_size(speed) + "/s"
                    
                    # Estimate remaining time
                    if speed > 0:
                        remaining_bytes = total - current
                        eta_seconds = remaining_bytes / speed
                        eta_str = f"{int(eta_seconds)}s"
                    else:
                        eta_str = "∞"
                else:
                    speed_str = "0 B/s"
                    eta_str = "∞"
                
                # Create progress bar
                progress_width = 20
                filled_width = int(progress_width * percentage / 100)
                bar = "█" * filled_width + "░" * (progress_width - filled_width)
                
                # Use carriage return to overwrite the same line
                progress_line = f"\r      📥 {percentage:5.1f}% [{bar}] {downloaded_str}/{total_str} at {speed_str} - ETA: {eta_str}"
                print(progress_line, end="", flush=True)
                
                # Mark as completed if we've reached 100%
                if percentage >= 100 and not self.completed:
                    self.completed = True
    
    def finish(self):
        """Show final completion status."""
        if not self.completed and self.total_size > 0:
            # Show 100% completion
            downloaded_str = format_file_size(self.total_size)
            total_str = format_file_size(self.total_size)
            
            # Calculate final speed
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                speed = self.total_size / elapsed
                speed_str = format_file_size(speed) + "/s"
            else:
                speed_str = "∞ B/s"
            
            progress_width = 20
            bar = "█" * progress_width
            
            progress_line = f"\r      📥 100.0% [{bar}] {downloaded_str}/{total_str} at {speed_str} - DONE!"
            print(progress_line, flush=True)
            self.completed = True


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
        # Get media information first
        media_info = ""
        try:
            if hasattr(message.media, 'document') and message.media.document:
                file_size = message.media.document.size
                media_info = f" ({format_file_size(file_size)})"
            elif hasattr(message.media, 'photo') and message.media.photo:
                # For photos, we can get an approximation from the largest size
                if hasattr(message.media.photo, 'sizes') and message.media.photo.sizes:
                    largest = max(message.media.photo.sizes, key=lambda x: getattr(x, 'size', 0) if hasattr(x, 'size') else 0)
                    if hasattr(largest, 'size'):
                        media_info = f" (~{format_file_size(largest.size)})"
        except:
            pass
        
        print(f"    - Starting media download{media_info}...")
        
        # Clean up any existing media files first to avoid duplicates
        cleanup_existing_media(message_folder, filename_base)
        
        # Create progress tracker
        progress_callback = None
        try:
            if hasattr(message.media, 'document') and message.media.document and message.media.document.size:
                progress_callback = DownloadProgress(message.media.document.size)
        except:
            pass
        
        # Download the media to the message folder with progress tracking
        if progress_callback:
            file_path = await client.download_media(
                message.media, 
                file=message_folder, 
                progress_callback=progress_callback
            )
        else:
            file_path = await client.download_media(message.media, file=message_folder)
        
        if file_path:
            # Show final completion status
            if progress_callback:
                progress_callback.finish()
                print()  # New line after progress bar
            
            # Get final file size
            final_size = os.path.getsize(file_path)
            print(f"    - Media downloaded successfully: {format_file_size(final_size)}")
            
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