#!/usr/bin/env python3
"""Quick test to check database and stats"""

from database import init_database, get_export_stats
from config import OUTPUT_DIR
from pathlib import Path

print("Testing database initialization and stats...")
print(f"Output directory: {OUTPUT_DIR}")

# Initialize database
db_path = init_database(OUTPUT_DIR)
print(f"Database path: {db_path}")
print(f"Database exists: {Path(db_path).exists()}")

# Get stats
stats = get_export_stats(str(db_path))
print(f"\nStats:")
print(f"  Total messages: {stats['total_messages']}")
print(f"  With media: {stats.get('with_media', 0)}")
print(f"  Total folders: {stats.get('total_folders', 0)}")
print(f"  Oldest: {stats.get('oldest', 'N/A')}")
print(f"  Newest: {stats.get('newest', 'N/A')}")
print("\n✅ Database is working correctly!")
