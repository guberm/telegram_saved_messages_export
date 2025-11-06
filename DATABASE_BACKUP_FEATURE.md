# Database Backup Feature

## Overview
The SQLite database file (`export_history.db`) is automatically backed up to Google Drive after all message folders are uploaded successfully. This ensures you have a complete backup including the tracking data.

## Why Backup the Database?
- **Preservation of Tracking Data**: If local files are deleted during cleanup, the database preserves which folders were backed up and when
- **Restore Capability**: You can download the database from Google Drive to see what was backed up
- **Audit Trail**: Complete history of all exports and backups with timestamps and file IDs
- **Disaster Recovery**: Even if local drive fails, you have the database in the cloud

## How It Works

### 1. Automatic Backup
After all message folders are uploaded, the system automatically:
1. Creates a timestamped copy of the database: `export_history_YYYYMMDD_HHMMSS.db`
2. Uploads it to the "Telegram_Exports_Backup" folder in Google Drive
3. Deletes the temporary local copy (original database remains on local disk)
4. Shows success/failure in the backup summary

### 2. Timestamped Filenames
Each database backup has a unique timestamp to prevent overwriting previous backups:
- `export_history_20240115_143022.db` - Backup from Jan 15, 2024 at 14:30:22
- `export_history_20240116_091545.db` - Backup from Jan 16, 2024 at 09:15:45

This allows you to track changes over time and restore to a specific point.

### 3. Backup Summary Display
```
==============================================================
BACKUP SUMMARY
==============================================================
✓ Successfully uploaded: 5
❌ Failed: 0
⏭️  Skipped (already backed up): 0
📊 Database backup: ✓ Success

✓ Cleaned up 5 folders and archives

✅ Backup completed successfully!
```

## Database Schema
The database contains two tables:

### `exported_messages`
Tracks individual exported messages:
- `message_id` - Telegram message ID
- `message_folder` - Folder name where message was saved
- `export_date` - When message was exported
- `media_type` - Type of media (if any)
- `file_path` - Path to saved message

### `backup_history`
Tracks backup operations:
- `message_folder` - Folder name (unique)
- `folder_path` - Full path to folder
- `archive_filename` - ZIP filename
- `archive_size_bytes` - Size of archive
- `upload_date` - When uploaded to Google Drive
- `google_drive_file_id` - Google Drive file ID
- `status` - pending/uploading/completed/failed
- `error_message` - Error details if failed

## Usage Examples

### Normal Export with Backup
```cmd
py main.py --backup
```
- Exports messages
- Backs up each folder
- **Backs up the database**
- Deletes local folders and archives

### Backup-Only Mode
```cmd
py main.py --backup-only
```
- Skips export
- Backs up existing folders
- **Backs up the database**
- Deletes local folders and archives

### Keep Local Files
```cmd
py main.py --backup --keep-archive
```
- Exports and backs up
- **Backs up the database**
- Keeps local folders and archives

## What Happens During Cleanup?
- ✅ **Original database kept locally** (`export_history.db`)
- ✅ **Timestamped copy uploaded to Google Drive**
- ✅ **Temporary local copy deleted**
- ✅ **Message folders deleted** (after successful upload)
- ✅ **ZIP archives deleted** (after successful upload)

## Restoring from Google Drive

### Download Database
1. Go to Google Drive → Telegram_Exports_Backup folder
2. Find the latest `export_history_YYYYMMDD_HHMMSS.db` file
3. Download it
4. Rename to `export_history.db`
5. Place in `telegram_saved_messages_exports/` folder

### Query Backup History
```cmd
sqlite3 export_history.db "SELECT message_folder, upload_date, archive_size_bytes/1024/1024 as size_mb FROM backup_history WHERE status='completed' ORDER BY upload_date DESC;"
```

### View Failed Backups
```cmd
sqlite3 export_history.db "SELECT message_folder, error_message FROM backup_history WHERE status='failed';"
```

## Troubleshooting

### Database Backup Failed
If you see:
```
📊 Database backup: ❌ Failed
⚠️  Warning: Database backup failed, but folder backups completed
```

**Possible causes:**
- Database file locked (close any SQLite browsers)
- Insufficient permissions to create temporary file
- Google Drive quota exceeded
- Network interruption during upload

**Solutions:**
1. Close any programs accessing `export_history.db`
2. Run `py main.py --backup-only` to retry just the backup
3. Check Google Drive storage quota
4. Manually upload the database:
   ```cmd
   py -c "from google_drive_backup import GoogleDriveBackup; b = GoogleDriveBackup(); b.authenticate(); b.upload_database_file('telegram_saved_messages_exports/export_history.db')"
   ```

### Database Not Found
If you see:
```
⚠️  Database file not found: telegram_saved_messages_exports\export_history.db
```

The database hasn't been created yet. Run an export first:
```cmd
py main.py
```

## Technical Details

### Upload Method
```python
def upload_database_file(self, db_path):
    """Upload the SQLite database file to Google Drive."""
    - Creates timestamped copy
    - Uploads to Google Drive
    - Deletes temporary copy
    - Returns file_id on success
```

### When It Runs
The database upload triggers **only if** at least one folder was successfully uploaded:
```python
if stats['success'] > 0:
    db_file_id = self.upload_database_file(db_path)
```

### File Location
- **Local**: `telegram_saved_messages_exports/export_history.db`
- **Google Drive**: `Telegram_Exports_Backup/export_history_YYYYMMDD_HHMMSS.db`

## Best Practices

### Regular Backups
Run `--backup-only` periodically to ensure database is backed up:
```cmd
py main.py --backup-only
```

### Download Database Backups
Periodically download your database backups from Google Drive to a safe location (external drive, second cloud storage, etc.)

### Check Backup Status
Before cleanup, verify the database backup succeeded in the summary output.

### Monitor Storage
Each database backup is small (usually < 1 MB), but they accumulate over time. Periodically clean old backups from Google Drive if needed.

## Summary
✅ **Automatic** - No manual action required  
✅ **Timestamped** - Each backup preserved with unique name  
✅ **Safe** - Original local database always kept  
✅ **Verified** - Success/failure shown in backup summary  
✅ **Complete** - Full tracking data backed up to cloud
