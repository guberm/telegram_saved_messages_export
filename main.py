#!/usr/bin/env python3
"""
Telegram Saved Messages Exporter - Main Entry Point
Exports saved messages from Telegram to separate HTML and Markdown files.
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient

# Import configuration
try:
    from config import (API_ID, API_HASH, PHONE, OUTPUT_DIR, SESSION_NAME,
                       GOOGLE_DRIVE_BACKUP_ENABLED, GOOGLE_DRIVE_CREDENTIALS_FILE,
                       GOOGLE_DRIVE_TOKEN_FILE, GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE)
except ImportError as e:
    # Check if it's just missing Google Drive settings (old config.py)
    try:
        from config import API_ID, API_HASH, PHONE, OUTPUT_DIR, SESSION_NAME
        # Set defaults for Google Drive settings
        GOOGLE_DRIVE_BACKUP_ENABLED = False
        GOOGLE_DRIVE_CREDENTIALS_FILE = 'credentials.json'
        GOOGLE_DRIVE_TOKEN_FILE = 'token.json'
        GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = False
        print("⚠️  Note: Using default Google Drive settings. Update config.py to customize.")
    except ImportError:
        print("⚠️  ERROR: config.py file not found!")
        print("Please create a config.py file with your API credentials.")
        print("You can copy config.py.example and fill in your values.")
        exit(1)

from database import init_database, get_export_stats
from exporter import export_saved_messages
from google_drive_backup import GoogleDriveBackup


async def main():
    """Main function to run the exporter."""
    global OUTPUT_DIR
    
    parser = argparse.ArgumentParser(
        description='Export Telegram saved messages to HTML and Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all saved messages (incremental - skips already exported)
  python main.py
  
  # Export messages from a specific date onwards
  python main.py --from-date 2024-01-01
  
  # Force re-export of already exported messages
  python main.py --force
  
  # Show export statistics
  python main.py --stats
  
  # Export with custom output directory
  python main.py --output my_exports
  
  # Export and backup to Google Drive
  python main.py --backup
  
  # Backup existing exports to Google Drive (no export)
  python main.py --backup-only
  
  # Export, backup, and keep local archive
  python main.py --backup --keep-archive
```
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
    
    parser.add_argument('--backup', action='store_true',
                       help='Backup exports to Google Drive after exporting')
    parser.add_argument('--backup-only', action='store_true',
                       help='Only backup existing exports to Google Drive (skip export)')
    parser.add_argument('--keep-archive', action='store_true',
                       help='Keep local zip archive after uploading to Google Drive')
    
    args = parser.parse_args()
    
    # Update output directory if specified
    current_output_dir = OUTPUT_DIR
    if args.output:
        current_output_dir = args.output
        # We need to update the config module's OUTPUT_DIR
        import config
        config.OUTPUT_DIR = args.output
    
    # Initialize database with the correct output directory
    db_path = init_database(current_output_dir)
    
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
    
    # Handle backup-only mode
    if args.backup_only:
        print("\n" + "="*60)
        print("GOOGLE DRIVE BACKUP MODE (PER-FOLDER)")
        print("="*60)
        
        backup_handler = GoogleDriveBackup(
            credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
            token_file=GOOGLE_DRIVE_TOKEN_FILE
        )
        
        # Authenticate
        if not backup_handler.authenticate():
            print("\n❌ Google Drive authentication failed!")
            return
        
        if not backup_handler.get_or_create_backup_folder():
            print("\n❌ Could not access Google Drive backup folder!")
            return
        
        # Use per-folder backup
        cleanup = not (args.keep_archive or GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE)
        stats = backup_handler.backup_individual_folders(
            current_output_dir,
            db_path,
            cleanup_after_upload=cleanup
        )
        
        print("\n" + "="*60)
        print(f"BACKUP SUMMARY")
        print("="*60)
        print(f"✓ Successfully uploaded: {stats['success']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"⏭️  Skipped (already backed up): {stats['skipped']}")
        
        # Show database backup status
        if 'database_backed_up' in stats:
            if stats['database_backed_up']:
                print(f"📊 Database backup: ✓ Success")
            else:
                print(f"📊 Database backup: ❌ Failed")
        
        if stats['success'] > 0:
            if cleanup:
                print(f"\n✓ Cleaned up {stats['success']} folders and archives")
            print("\n✅ Backup completed successfully!")
        elif stats['failed'] > 0:
            print("\n⚠️  Some backups failed!")
        else:
            print("\n✓ Nothing to backup (all up to date)")
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
    
    # Pre-authenticate with Google Drive if backup is requested
    # This ensures authentication happens before the export starts
    should_backup = args.backup or (GOOGLE_DRIVE_BACKUP_ENABLED and not args.backup_only)
    backup_handler = None
    
    if should_backup:
        print("\n" + "="*60)
        print("GOOGLE DRIVE PRE-AUTHENTICATION")
        print("="*60)
        print("Authenticating with Google Drive before starting export...")
        print("(This ensures backup will work after export completes)\n")
        
        backup_handler = GoogleDriveBackup(
            credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
            token_file=GOOGLE_DRIVE_TOKEN_FILE
        )
        
        # Authenticate early
        if not backup_handler.authenticate():
            print("\n⚠️  WARNING: Google Drive authentication failed!")
            print("Export will continue, but backup will be skipped.\n")
            response = input("Continue with export? (y/n): ").strip().lower()
            if response != 'y':
                print("Export cancelled.")
                return
            backup_handler = None  # Disable backup
        else:
            # Also verify we can access/create the backup folder
            if not backup_handler.get_or_create_backup_folder():
                print("\n⚠️  WARNING: Could not access Google Drive backup folder!")
                print("Export will continue, but backup will be skipped.\n")
                response = input("Continue with export? (y/n): ").strip().lower()
                if response != 'y':
                    print("Export cancelled.")
                    return
                backup_handler = None  # Disable backup
            else:
                print("\n✓ Google Drive authentication successful!")
                print("="*60 + "\n")
    
    # Create Telegram client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✓ Connected to Telegram")
        
        # Export messages
        await export_saved_messages(client, db_path, from_date=from_date, force_reexport=args.force, output_dir=current_output_dir)
        
        # Backup to Google Drive if pre-authenticated handler exists
        if backup_handler is not None:
            print("\n" + "="*60)
            print("BACKING UP TO GOOGLE DRIVE (PER-FOLDER)")
            print("="*60)
            print("Note: Each message folder will be archived and uploaded separately.")
            print("Source folders and archives will be deleted after successful upload.\n")
            
            # Use per-folder backup with cleanup
            cleanup = not (args.keep_archive or GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE)
            stats = backup_handler.backup_individual_folders(
                current_output_dir,
                db_path,
                cleanup_after_upload=cleanup
            )
            
            print("\n" + "="*60)
            print(f"BACKUP SUMMARY")
            print("="*60)
            print(f"✓ Successfully uploaded: {stats['success']}")
            print(f"❌ Failed: {stats['failed']}")
            print(f"⏭️  Skipped (already backed up): {stats['skipped']}")
            
            # Show database backup status
            if 'database_backed_up' in stats:
                if stats['database_backed_up']:
                    print(f"📊 Database backup: ✓ Success")
                else:
                    print(f"📊 Database backup: ❌ Failed")
            
            if stats['success'] > 0:
                if cleanup:
                    print(f"\n✓ Cleaned up {stats['success']} folders and archives")
                else:
                    print(f"\n⚠️  Local folders and archives kept (--keep-archive)")
                print("\n✅ Backup completed successfully!")
            elif stats['failed'] > 0:
                print("\n⚠️  Some backups failed, check messages above")
            else:
                print("\n✓ Nothing to backup (all up to date)")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Export interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    finally:
        print("\n" + "="*60)
        input("Press Enter to exit...")