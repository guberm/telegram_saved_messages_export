# Quick Reference Card - Per-Folder Backup

## 🚀 Quick Start

```powershell
# Export and backup (with cleanup)
py main.py --backup

# Backup only existing exports
py main.py --backup-only

# Keep local files after backup
py main.py --backup --keep-archive
```

## 📊 What Happens

```
Each folder → ZIP → Upload → Track in DB → Delete folder & archive
Finally → Upload database file to Google Drive
```

## ✅ Benefits

- ✓ Resume if interrupted
- ✓ Skip already uploaded
- ✓ Save disk space (auto cleanup)
- ✓ See per-folder progress
- ✓ Isolated failures
- ✓ Database backup included

## 📁 File Structure

### Before Backup
```
telegram_saved_messages_exports/
├── 20241101_120000_msg123_Hello/
├── 20241101_130000_msg124_World/
└── 20241101_140000_msg125_Test/
```

### During Backup
```
telegram_saved_messages_exports/
├── 20241101_120000_msg123_Hello.zip  ← Created
├── 20241101_130000_msg124_World/
└── 20241101_140000_msg125_Test/
```

### After Backup (default)
```
telegram_saved_messages_exports/
├── 20241101_130000_msg124_World/  ← Only unuploaded remain
└── 20241101_140000_msg125_Test/
```

### Google Drive
```
Telegram_Exports_Backup/
├── 20241101_120000_msg123_Hello.zip
├── 20241101_130000_msg124_World.zip
├── 20241101_140000_msg125_Test.zip
└── export_history_20240115_143022.db  ← Database backup
```

## 🗄️ Database Tracking

Each folder's status tracked in SQLite:
- `pending` - Not started
- `uploading` - In progress
- `completed` - Successfully uploaded
- `failed` - Error occurred

## 🔄 Resume Example

```powershell
# First run - uploads 50 folders, then interrupted
py main.py --backup
# Uploads: 20 folders
# ❌ Network error!

# Second run - resumes automatically
py main.py --backup-only
# ✓ Skips 20 already uploaded
# ✓ Continues from folder 21
```

## 📈 Progress Output

```
[1/15] Processing: 20241101_120000_msg123_Hello
  - Creating archive...
  - Archive created: 20241101_120000_msg123_Hello.zip (2.34 MB)
  - Uploading to Google Drive...
  ✓ Uploaded successfully
  ✓ Deleted archive
  ✓ Deleted folder

...

==================================================
📊 Backing up database file...
  ✓ Database backed up to Google Drive (156.23 KB)

==================================================
BACKUP SUMMARY
==================================================
✓ Successfully uploaded: 15
❌ Failed: 0
📊 Database backup: ✓ Success
⏭️  Skipped (already backed up): 0
```

## ⚙️ Configuration

In `config.py`:

```python
# Auto-backup after export
GOOGLE_DRIVE_BACKUP_ENABLED = True

# Keep files after upload (not recommended)
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = False
```

## 🔍 Check Status

### View Statistics
```python
from database import get_backup_stats, init_database
stats = get_backup_stats(init_database())
print(f"Completed: {stats[1]}, Failed: {stats[2]}")
```

### List Failed Uploads
```sql
-- Run in SQLite
SELECT message_folder, error_message 
FROM backup_history 
WHERE status='failed';
```

## 🛠️ Troubleshooting

### Resume Interrupted Backup
```powershell
py main.py --backup-only
```

### Re-backup Everything
```sql
DELETE FROM backup_history;
```

### Check Database
```powershell
# Path to database
telegram_saved_messages_exports/export_history.db

# View with any SQLite client
```

## 💾 Disk Space

### Old System (single archive)
```
Before: 1 GB exports
During: 1 GB exports + 1 GB archive = 2 GB needed
After:  1 GB exports (or 0 with cleanup)
```

### New System (per-folder)
```
Before: 1 GB exports
During: 1 GB exports + ~5 MB per folder = 1.005 GB
After:  0 GB (with cleanup) or 1 GB (with --keep-archive)
```

## 🎯 Use Cases

### Daily Backup (Recommended)
```powershell
py main.py --backup
# Exports new messages
# Uploads to Google Drive
# Cleans up automatically
```

### Full Re-export and Backup
```powershell
py main.py --force --backup
# Re-exports everything
# Uploads to Google Drive
```

### Backup Existing Without Export
```powershell
py main.py --backup-only
# Only uploads folders
# Skips export step
```

### Test Before Cleanup
```powershell
py main.py --backup --keep-archive
# Uploads but keeps local files
# Verify in Google Drive first
```

## ⚡ Performance

| Export Size | Old System | New System |
|-------------|-----------|------------|
| 100 folders | 1 large upload | 100 small uploads |
| Network fail | Restart all | Resume from last |
| Disk space | 2x size | 1x size + 1 folder |
| Progress | % complete | Folder X of Y |

## 🔐 Security

- OAuth2 authentication
- `credentials.json` - Keep private
- `token.json` - Auto-generated, keep private
- Database tracks file IDs only (no content)

## 📚 Documentation

- Full Guide: `PER_FOLDER_BACKUP_GUIDE.md`
- Setup: `GOOGLE_DRIVE_SETUP.md`
- Windows: `WINDOWS_QUICK_START.md`
- Summary: `PER_FOLDER_IMPLEMENTATION_SUMMARY.md`

## ✨ Key Differences from Old System

| Feature | Old | New |
|---------|-----|-----|
| Archive | 1 huge file | Per folder |
| Resume | ❌ No | ✅ Yes |
| Tracking | ❌ No | ✅ Database |
| Cleanup | ❌ Manual | ✅ Auto |
| Progress | Basic | Detailed |
| Failures | All fail | Isolated |

## 🎉 Ready to Use!

```powershell
# First time setup
1. Setup Google Drive (see GOOGLE_DRIVE_SETUP.md)
2. Rename client_secret_*.json → credentials.json
3. Add test user in OAuth consent screen

# First backup
py main.py --backup

# That's it! 🚀
```

## 💡 Tips

1. **Enable cleanup** to save disk space
2. **Run regularly** for incremental backups
3. **Check Google Drive** to verify uploads
4. **Use --keep-archive** only for testing
5. **Monitor database** for failed uploads

## 🆘 Common Issues

### "All folders already backed up"
✓ Normal - all done!
To re-backup: Delete backup_history records

### Some folders keep failing
Check error_message in database
Fix issue and rerun (retries failed)

### Want to cancel cleanup
Use `--keep-archive` flag

### Verify uploads
Check Google Drive: Telegram_Exports_Backup folder

---

**Status: Production Ready** ✅

For detailed information, see `PER_FOLDER_BACKUP_GUIDE.md`
