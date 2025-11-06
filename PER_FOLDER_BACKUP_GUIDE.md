# Per-Folder Backup Feature - Implementation Guide

## Overview

The backup system has been enhanced to archive and upload each message folder **individually** instead of creating one large archive. This provides better reliability, progress tracking, and automatic cleanup.

## Key Features

✅ **Individual Archives** - Each message folder becomes a separate ZIP file
✅ **Database Tracking** - SQLite tracks upload status for each folder
✅ **Database Backup** - SQLite database automatically backed up to Google Drive
✅ **Resume Capability** - Interrupted backups can resume where they left off
✅ **Automatic Cleanup** - Deletes source folders and archives after successful upload
✅ **Progress Reporting** - Shows detailed progress for each folder
✅ **Failure Resilience** - Failed uploads don't affect successful ones

## How It Works

### Workflow

```
For each message folder:
┌─────────────────────────────────────┐
│ 1. Check if already backed up (DB)  │
│    └─ If yes: Skip                  │
└──────────────┬──────────────────────┘
               │ Not backed up
               ▼
┌─────────────────────────────────────┐
│ 2. Create ZIP archive                │
│    folder_name.zip                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Mark as 'uploading' in DB        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Upload to Google Drive            │
└──────────────┬──────────────────────┘
               │
          ┌────┴────┐
      Success    Failure
          │           │
          ▼           ▼
    ┌─────────┐  ┌──────────┐
    │ Mark as │  │ Mark as  │
    │completed│  │ failed   │
    └────┬────┘  └──────────┘
         │
         ▼
    ┌─────────────────────┐
    │ 5. Delete folder    │
    │ 6. Delete archive   │
    └─────────────────────┘
```

### Database Schema

New table: `backup_history`

```sql
CREATE TABLE backup_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_folder TEXT NOT NULL,          -- Folder name
    folder_path TEXT NOT NULL,             -- Full path
    archive_filename TEXT NOT NULL,        -- ZIP filename
    archive_size_bytes INTEGER,            -- Archive size
    upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
    google_drive_file_id TEXT,             -- Google Drive file ID
    status TEXT DEFAULT 'pending',         -- pending/uploading/completed/failed
    error_message TEXT,                    -- Error details if failed
    UNIQUE(message_folder)
);
```

## Usage

### Basic Export with Backup

```powershell
py main.py --backup
```

Output example:
```
============================================================
BACKING UP TO GOOGLE DRIVE (PER-FOLDER)
============================================================
Note: Each message folder will be archived and uploaded separately.
Source folders and archives will be deleted after successful upload.

📦 Found 15 folders to backup

[1/15] Processing: 20241101_120000_msg123_Hello
  - Creating archive...
  - Archive created: 20241101_120000_msg123_Hello.zip (2.34 MB)
  - Uploading to Google Drive...
  ✓ Uploaded successfully
  ✓ Deleted archive: 20241101_120000_msg123_Hello.zip
  ✓ Deleted folder: 20241101_120000_msg123_Hello

[2/15] Processing: 20241101_130000_msg124_World
  - Creating archive...
  - Archive created: 20241101_130000_msg124_World.zip (1.12 MB)
  - Uploading to Google Drive...
  ✓ Uploaded successfully
  ✓ Deleted archive: 20241101_130000_msg124_World.zip
  ✓ Deleted folder: 20241101_130000_msg124_World

...

==============================================================
📊 Backing up database file...
  ✓ Database backed up to Google Drive (156.23 KB)

==============================================================
BACKUP SUMMARY
==============================================================
✓ Successfully uploaded: 15
❌ Failed: 0
⏭️  Skipped (already backed up): 0
📊 Database backup: ✓ Success

✓ Cleaned up 15 folders and archives

✅ Backup completed successfully!
```

### Backup Only (No Export)

```powershell
py main.py --backup-only
```

This only backs up existing folders without exporting new messages.

### Keep Local Files

```powershell
py main.py --backup --keep-archive
```

Uploads to Google Drive but **keeps** the source folders and archives locally.

### Resume Interrupted Backup

Simply run the same command again:
```powershell
py main.py --backup-only
```

The system automatically:
- Checks the database for completed uploads
- Skips folders already backed up
- Only processes pending/failed folders

## Database Functions

### Check if Folder is Backed Up

```python
from database import is_folder_backed_up

if is_folder_backed_up(db_path, "20241101_120000_msg123_Hello"):
    print("Already backed up")
```

### Get Folders Needing Backup

```python
from database import get_folders_to_backup

folders = get_folders_to_backup(db_path, "telegram_saved_messages_exports")
print(f"Need to backup: {len(folders)} folders")
```

### Get Backup Statistics

```python
from database import get_backup_stats

stats = get_backup_stats(db_path)
print(f"Total: {stats[0]}")
print(f"Completed: {stats[1]}")
print(f"Failed: {stats[2]}")
print(f"Total uploaded bytes: {stats[3]}")
```

### Track Backup Progress

```python
from database import mark_backup_started, mark_backup_completed, mark_backup_failed

# When starting upload
mark_backup_started(db_path, folder_name, folder_path, archive_name, archive_size)

# On success
mark_backup_completed(db_path, folder_name, google_drive_file_id)

# On failure
mark_backup_failed(db_path, folder_name, error_message)
```

## Google Drive Structure

Before (old system):
```
Google Drive/Telegram_Exports_Backup/
└── telegram_exports_20241106_143022.zip  (huge single file)
```

After (new system):
```
Google Drive/Telegram_Exports_Backup/
├── 20241101_120000_msg123_Hello.zip
├── 20241101_130000_msg124_World.zip
├── 20241101_140000_msg125_Test.zip
├── 20241101_150000_msg126_Example.zip
└── ...
```

## Benefits

### 1. **Reliability**
- If one folder fails, others still succeed
- No need to re-upload everything on failure
- Better handling of network interruptions

### 2. **Resume Capability**
- Database tracks what's uploaded
- Can stop and resume anytime
- No duplicate uploads

### 3. **Space Management**
- Deletes folders after upload (saves disk space)
- Can keep originals if needed (--keep-archive)
- No huge temporary archives

### 4. **Progress Visibility**
- See exactly which folder is being processed
- Know how many remain
- Clear success/failure status

### 5. **Failure Isolation**
- One bad folder doesn't stop everything
- Clear error messages per folder
- Failed folders can be retried separately

## Configuration

In `config.py`:

```python
# Set to True for automatic backup after export
GOOGLE_DRIVE_BACKUP_ENABLED = True

# Set to True to keep folders and archives after upload
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = False  # Recommended: False for auto-cleanup
```

## Cleanup Behavior

### Default (cleanup enabled):
```
After upload:
- ✓ Delete source folder
- ✓ Delete ZIP archive
- ✓ Free up disk space
```

### With --keep-archive:
```
After upload:
- ⏭️ Keep source folder
- ⏭️ Keep ZIP archive
- ⚠️ Uses more disk space
```

## Error Handling

### Network Failure During Upload
- Status marked as 'failed' in database
- Folder and archive kept locally
- Next run will retry failed folders

### Archive Creation Failure
- Error logged to database
- Source folder kept
- Next run will retry

### Google Drive Quota Exceeded
- Upload fails with quota error
- All data kept locally
- Retry after clearing space

## Comparison: Old vs New

| Aspect | Old System | New System |
|--------|-----------|------------|
| Archive Size | One huge file | Many small files |
| Upload Progress | All or nothing | Granular per folder |
| Failure Impact | Must restart all | Retry only failed |
| Resume Support | No | Yes (via database) |
| Disk Space | Needs 2x space | Cleanup as you go |
| Progress Tracking | Limited | Detailed per folder |
| Database | No tracking | Full tracking |
| Recovery | Manual | Automatic resume |

## Monitoring

### View Backup Status

```powershell
# Check database directly (from Python)
py -c "from database import get_backup_stats, init_database; db=init_database(); print(get_backup_stats(db))"
```

### Query Failed Backups

```python
import sqlite3
from pathlib import Path

db_path = Path("telegram_saved_messages_exports/export_history.db")
conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT message_folder, error_message FROM backup_history WHERE status='failed'")
for row in cursor:
    print(f"Failed: {row[0]} - {row[1]}")
conn.close()
```

## Troubleshooting

### "All folders already backed up"
- Database shows all folders have status='completed'
- This is normal if re-running after successful backup
- To re-backup: Delete rows from backup_history table

### Some Folders Keep Failing
- Check error_message in database
- Common issues: Network timeout, quota exceeded, invalid characters in filename
- Fix issue and rerun (will retry failed ones)

### Want to Re-backup Everything
```sql
-- Run in SQLite
DELETE FROM backup_history;
```
Then run: `py main.py --backup-only`

### Check What's Uploaded

```sql
-- Run in SQLite
SELECT message_folder, archive_size_bytes/1024/1024 as size_mb, upload_date 
FROM backup_history 
WHERE status='completed' 
ORDER BY upload_date DESC;
```

## Performance

### Large Exports (1000+ messages)
- Old system: Creates 1GB+ archive → slow, risky
- New system: Uploads concurrently → faster, safer

### Disk Space During Backup
- Old system: Needs 2x total export size
- New system: Only needs space for 1 folder at a time

### Network Interruption
- Old system: Must restart from beginning
- New system: Resumes from last successful folder

## Best Practices

1. **Enable cleanup** (default) to save disk space
2. **Run regularly** to keep backups up to date
3. **Check stats** periodically: `py main.py --stats`
4. **Use --keep-archive** only for testing or verification
5. **Monitor database** for failed uploads

## Testing

Test with a small export:

```powershell
# Export just a few messages
py main.py --from-date 2024-11-01 --backup

# Verify upload
# Check Google Drive for individual ZIP files

# Check database
py -c "from database import get_backup_stats, init_database; print(get_backup_stats(init_database()))"
```

## Migration from Old System

If you have old full-archive backups:
1. New system works with any existing exports
2. First run will upload all folders individually
3. Old ZIP archives in Google Drive can be deleted manually
4. Database will track new per-folder backups

## Summary

The new per-folder backup system provides:
- ✅ Better reliability
- ✅ Resume capability
- ✅ Automatic cleanup
- ✅ Clear progress tracking
- ✅ Isolated failure handling
- ✅ Efficient disk usage

**Recommended for all users, especially those with large exports (100+ messages).**
