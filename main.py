#!/usr/bin/env python3
"""
Telegram Saved Messages Exporter - Main Entry Point
Exports saved messages from Telegram to separate HTML and Markdown files.
"""

import asyncio
import argparse
from datetime import datetime
from telethon import TelegramClient

# Import configuration
try:
    from config import API_ID, API_HASH, PHONE, OUTPUT_DIR, SESSION_NAME
except ImportError:
    print("⚠️  ERROR: config.py file not found!")
    print("Please create a config.py file with your API credentials.")
    print("You can copy config.py.example and fill in your values.")
    exit(1)

from database import init_database, get_export_stats
from exporter import export_saved_messages


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
        await export_saved_messages(client, db_path, from_date=from_date, force_reexport=args.force, output_dir=current_output_dir)
        
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