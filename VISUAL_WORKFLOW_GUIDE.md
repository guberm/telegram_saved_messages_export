# Google Drive Backup - Visual Workflow Guide

## 🎯 Overview

This visual guide shows how the Google Drive backup feature works with your Telegram export tool.

## 📊 Backup Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM EXPORT TOOL                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Export Telegram Messages                           │
│  • Fetches saved messages                                   │
│  • Downloads media files                                    │
│  • Creates HTML/Markdown files                              │
│  • Saves in: telegram_saved_messages_exports/               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Create ZIP Archive (if backup enabled)             │
│  • Compresses entire export directory                       │
│  • Format: telegram_exports_YYYYMMDD_HHMMSS.zip            │
│  • Shows size and file count                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Authenticate with Google Drive                     │
│  • First time: Browser opens for login                      │
│  • Subsequent: Uses saved token                             │
│  • Token refreshed if expired                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Upload to Google Drive                             │
│  • Creates folder: Telegram_Exports_Backup                  │
│  • Uploads ZIP archive                                      │
│  • Updates if file exists                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Cleanup (optional)                                 │
│  • Deletes local ZIP (unless --keep-archive)                │
│  • Shows completion message                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication Flow (First Time)

```
┌──────────────┐
│ Run Backup   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ credentials.json?    │
└──────┬───────────────┘
       │ Yes
       ▼
┌──────────────────────┐
│ token.json exists?   │
└──────┬───────────────┘
       │ No (First time)
       ▼
┌──────────────────────┐
│ Open Browser         │
│ for Authentication   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User Grants          │
│ Permissions          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Save token.json      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Proceed with Upload  │
└──────────────────────┘
```

## 🔄 Authentication Flow (Subsequent Times)

```
┌──────────────┐
│ Run Backup   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Load token.json      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Token valid?         │
└──────┬───────────────┘
       │ Yes
       ▼
┌──────────────────────┐
│ Use Token            │
│ (No browser needed)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Proceed with Upload  │
└──────────────────────┘
```

## 📁 File Structure Before Backup

```
telegram_export/
├── main.py
├── google_drive_backup.py
├── config.py
├── credentials.json          ← From Google Cloud Console
└── telegram_saved_messages_exports/
    ├── 20241101_120000_msg123_Hello/
    │   ├── message.html
    │   ├── message.md
    │   └── photo.jpg
    ├── 20241101_130000_msg124_World/
    │   ├── message.html
    │   └── message.md
    └── ...
```

## 📦 After Archive Creation

```
telegram_export/
├── main.py
├── google_drive_backup.py
├── config.py
├── credentials.json
├── token.json                ← Created after first auth
├── telegram_exports_20241102_143022.zip  ← New archive
└── telegram_saved_messages_exports/
    └── (all export folders...)
```

## ☁️ Google Drive Structure

```
Google Drive
└── My Drive
    └── Telegram_Exports_Backup/        ← Created automatically
        ├── telegram_exports_20241101_090000.zip
        ├── telegram_exports_20241102_143022.zip
        ├── telegram_exports_20241103_180000.zip
        └── ...
```

## 🎮 Command Examples with Flow

### Example 1: Export and Backup (Automatic)

```
config.py: GOOGLE_DRIVE_BACKUP_ENABLED = True

Command:
$ python main.py

Flow:
1. Export messages → 2. Create ZIP → 3. Upload → 4. Done ✓
```

### Example 2: Export and Backup (Manual)

```
config.py: GOOGLE_DRIVE_BACKUP_ENABLED = False

Command:
$ python main.py --backup

Flow:
1. Export messages → 2. Create ZIP → 3. Upload → 4. Done ✓
```

### Example 3: Backup Only

```
Command:
$ python main.py --backup-only

Flow:
1. Skip export → 2. Create ZIP → 3. Upload → 4. Done ✓
```

### Example 4: Keep Local Archive

```
Command:
$ python main.py --backup --keep-archive

Flow:
1. Export → 2. Create ZIP → 3. Upload → 4. Keep ZIP ✓
```

## ⚙️ Configuration Matrix

| Setting | Automatic | Manual | Keeps Archive |
|---------|-----------|--------|---------------|
| `GOOGLE_DRIVE_BACKUP_ENABLED = True` | ✓ | ✓ | ✗ |
| `GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = True` | ✓ | ✓ | ✓ |
| `--backup` flag | ✗ | ✓ | ✗ |
| `--backup-only` flag | ✗ | ✓ | ✗ |
| `--keep-archive` flag | depends | ✓ | ✓ |

## 🔍 What Gets Backed Up?

```
ZIP Archive Contents:
telegram_saved_messages_exports/
├── All message folders
├── All HTML files
├── All Markdown files
├── All media files (images, videos, etc.)
├── exports.db (database)
└── Complete directory structure
```

## 📊 Size Examples

| Export Size | Archive Size | Upload Time* |
|------------|--------------|--------------|
| 100 MB | ~30 MB | ~30 seconds |
| 500 MB | ~150 MB | ~2 minutes |
| 1 GB | ~300 MB | ~5 minutes |
| 5 GB | ~1.5 GB | ~15 minutes |

*Times vary based on internet speed and compression ratio

## ✅ Success Indicators

### During Export:
```
Fetching saved messages...
Found 50 new messages to export
[1/50] Processing message 12345...
  - Created folder: 20241102_143022_msg12345_Hello_world
  - Downloaded media: photo.jpg
  - Generated HTML content
  - Exported to: message.html
✓ Export completed successfully!
```

### During Backup:
```
============================================================
BACKING UP TO GOOGLE DRIVE
============================================================
Creating zip archive: telegram_exports_20241102_143022.zip
  Archived 100 files...
  Archived 200 files...
✓ Created archive: telegram_exports_20241102_143022.zip (145.23 MB, 234 files)
✓ Connected to Google Drive
✓ Found existing backup folder: Telegram_Exports_Backup
Uploading to Google Drive: telegram_exports_20241102_143022.zip (145.23 MB)
✓ Uploaded to Google Drive: telegram_exports_20241102_143022.zip
✓ Deleted local file: telegram_exports_20241102_143022.zip

✅ Backup completed successfully!
```

## ❌ Error Handling

### Missing Credentials:
```
❌ Error: Google Drive credentials file 'credentials.json' not found!

To set up Google Drive backup:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials and save as 'credentials.json'
```

### Authentication Failed:
```
🔐 Opening browser for Google Drive authentication...
❌ Authentication failed: [error details]

⚠️  Backup failed, but exports are saved locally
```

### Upload Failed:
```
Uploading to Google Drive: telegram_exports_20241102_143022.zip
❌ Error uploading file: [error details]

⚠️  Backup failed, but exports are saved locally
Local archive saved: telegram_exports_20241102_143022.zip
```

## 💡 Tips

1. **First backup takes longer** - Authentication + setup
2. **Subsequent backups are faster** - Token cached
3. **Large exports** - Consider backing up more frequently
4. **Internet issues** - Exports saved locally regardless
5. **Token expiry** - Automatically refreshed
6. **Manual backup** - Use `--backup-only` anytime

## 🚀 Quick Start Summary

```bash
# 1. Setup (one-time)
pip install -r requirements.txt
# Download credentials.json from Google Cloud Console
# Edit config.py: GOOGLE_DRIVE_BACKUP_ENABLED = True

# 2. First run (authenticate)
python main.py --backup

# 3. Subsequent runs (automatic)
python main.py
```

## 📚 More Information

- **Detailed Setup:** GOOGLE_DRIVE_SETUP.md
- **Command Reference:** BACKUP_QUICK_REFERENCE.md
- **Implementation Details:** CHANGES_SUMMARY.md
- **Complete Guide:** README.md
