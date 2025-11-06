# GUI User Guide

## 🎨 Telegram Saved Messages Exporter - Graphical Interface

Simple and user-friendly interface for exporting and backing up your Telegram saved messages.

## 🚀 Quick Start

### Windows
Double-click `run_gui.bat`

### Any OS
```bash
py gui.py
```

## 📋 Interface Overview

```
┌─────────────────────────────────────────────────┐
│  📱 Telegram Saved Messages Exporter            │
├─────────────────────────────────────────────────┤
│  📊 Statistics                                   │
│  • Exported Messages: 7,169                     │
│  • Total Folders: 7,178                         │
│  • Backed Up: 15 / 7,178                        │
│  • Total Uploaded: 1.23 GB                      │
├─────────────────────────────────────────────────┤
│  ⚙️ Options                                      │
│  Export from date: [2024-01-01]                 │
│  ☑ Force re-export                              │
│  ☑ Backup to Google Drive                       │
│  ☐ Keep local archives                          │
├─────────────────────────────────────────────────┤
│  [📥 Export]  [📥☁️ Export+Backup]  [☁️ Backup]   │
├─────────────────────────────────────────────────┤
│  📋 Progress                                     │
│  [████████░░░░░░░░] 45%                         │
│  [12:30:45] ✓ Uploaded successfully             │
│  [12:30:45] ✓ Deleted folder                    │
│  [12:30:46] Processing next...                  │
├─────────────────────────────────────────────────┤
│  [🔄 Refresh] [📂 Open Folder] [🖥️ CLI] [❌ Exit] │
└─────────────────────────────────────────────────┘
```

## 🎯 Main Features

### 1. Statistics Panel
Shows real-time statistics:
- **Exported Messages** - Total messages exported
- **Total Folders** - Number of message folders
- **Backed Up** - Completed / Total backups
- **Total Uploaded** - Total data uploaded to Google Drive

Click **🔄 Refresh Stats** to update.

### 2. Options Panel

#### Export from date
- Enter date in `YYYY-MM-DD` format
- Leave empty to export all messages
- Only messages from this date onwards will be exported

#### Force re-export
- ☑ Re-export already exported messages
- ☐ Skip already exported (incremental - faster)

#### Backup to Google Drive
- ☑ Upload to Google Drive after export
- ☐ Export only (no backup)
- Requires Google Drive setup (see [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md))

#### Keep local archives
- ☑ Keep ZIP files and folders after upload
- ☐ Delete after successful upload (save disk space)

### 3. Action Buttons

#### 📥 Export Messages
- Export messages to local disk
- No Google Drive backup
- Fast and simple

#### 📥☁️ Export + Backup
- Export messages
- Backup each folder to Google Drive
- Delete local files after upload (optional)
- Most complete option

#### ☁️ Backup Only
- No new export
- Backup existing folders to Google Drive
- Use when export is done, just need backup

#### ⏹️ Stop
- Stop current operation
- Safely interrupts export/backup
- Can resume later

### 4. Progress Panel

Real-time log with color coding:
- **Green** - Success messages (✓)
- **Red** - Error messages (❌)
- **Yellow** - Warning messages (⚠️)
- **Blue** - Section headers (===)
- **White** - Info messages

**Progress bar:**
- Animated during operations
- Shows activity

### 5. Bottom Buttons

#### 🔄 Refresh Stats
- Update statistics from database
- Click after operations complete

#### 📂 Open Export Folder
- Opens `telegram_saved_messages_exports` in File Explorer
- View your exported messages

#### 🖥️ Open CLI
- Opens command prompt in current directory
- Use for advanced CLI commands
- Access to full CLI functionality

#### ❌ Exit
- Close the application
- Safe to use (won't interrupt operations)

## 📖 Common Workflows

### First Time Export

1. **Start GUI**: Double-click `run_gui.bat`
2. **Check options**: 
   - Date filter: Leave empty (export all)
   - Force re-export: Unchecked
   - Backup to Google Drive: Check if desired
3. **Click**: "📥 Export Messages" or "📥☁️ Export + Backup"
4. **Wait**: Watch progress log
5. **Done**: Message count shown in statistics

### Regular Updates (Incremental)

1. **Start GUI**
2. **Options**:
   - Date filter: Empty (or recent date)
   - Force re-export: **Unchecked** ✅
   - Backup: Checked
3. **Click**: "📥☁️ Export + Backup"
4. **Result**: Only new messages exported (fast!)

### Backup Existing Exports

1. **Start GUI**
2. **Click**: "☁️ Backup Only"
3. **Wait**: All folders uploaded
4. **Check**: Google Drive folder

### Export Specific Date Range

1. **Start GUI**
2. **Enter date**: `2024-01-01` in date field
3. **Click**: "📥 Export Messages"
4. **Result**: Only messages from 2024 onwards

### Re-export Everything (Force)

1. **Start GUI**
2. **Check**: ☑ Force re-export
3. **Click**: "📥 Export Messages"
4. **Warning**: Can take a long time!

## 🎨 Progress Log Colors

| Color | Meaning | Example |
|-------|---------|---------|
| 🟢 Green | Success | `✓ Uploaded successfully` |
| 🔴 Red | Error | `❌ Upload failed` |
| 🟡 Yellow | Warning | `⚠️ Cleanup warning` |
| 🔵 Blue | Header | `================` |
| ⚪ White | Info | `Processing: folder_name` |
| 🕐 Gray | Timestamp | `[12:30:45]` |

## ⚡ Tips & Tricks

### Faster Exports
- Use date filter for recent messages only
- Leave "Force re-export" unchecked (incremental mode)
- Close other programs to free up resources

### Save Disk Space
- Enable "Backup to Google Drive"
- Uncheck "Keep local archives"
- Folders auto-deleted after upload

### Troubleshooting
- Click **🔄 Refresh Stats** if numbers don't update
- Use **🖥️ Open CLI** for detailed error messages
- Check progress log for error details
- See [WINDOWS_CLEANUP_TROUBLESHOOTING.md](WINDOWS_CLEANUP_TROUBLESHOOTING.md) for cleanup issues

### Monitoring Progress
- Watch progress bar animation (shows it's working)
- Read progress log for details
- Check statistics after completion

### Google Drive Authentication
- First backup: Browser opens for OAuth
- Credentials saved in `token.json`
- Future backups: Automatic (no browser)

## 🔄 Resume Interrupted Operations

### If Export Interrupted
1. Restart GUI
2. Run same export command
3. Already exported messages automatically skipped ✅

### If Backup Interrupted
1. Restart GUI
2. Click "☁️ Backup Only"
3. Already uploaded folders automatically skipped ✅

## 🖥️ CLI Access from GUI

Click **🖥️ Open CLI** to access advanced commands:

```cmd
# View detailed help
py main.py --help

# View statistics with more details
py main.py --stats

# Custom output directory
py main.py --output my_custom_folder

# Advanced options not in GUI
py main.py --from-date 2024-01-01 --force --backup
```

## ⚙️ Preferences

GUI reads settings from `config.py`:
- `GOOGLE_DRIVE_BACKUP_ENABLED` - Default backup state
- `GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE` - Default keep archive state
- `OUTPUT_DIR` - Export directory
- `API_ID`, `API_HASH`, `PHONE` - Telegram credentials

Edit `config.py` to change defaults.

## 🐛 Troubleshooting

### GUI Won't Start
```bash
# Check Python is installed
py --version

# Run directly to see errors
py gui.py
```

### Authentication Fails
- Check `config.py` has correct credentials
- Delete `telegram_session.session` and try again
- For Google Drive: Delete `token.json` and re-authenticate

### Progress Stuck
- Check progress log for errors
- Click **⏹️ Stop** and retry
- Use **🖥️ Open CLI** for manual commands

### Statistics Don't Update
- Click **🔄 Refresh Stats**
- Close and restart GUI
- Check database exists: `telegram_saved_messages_exports/export_history.db`

## 📚 Related Documentation

- [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) - Google Drive setup guide
- [WINDOWS_QUICK_START.md](WINDOWS_QUICK_START.md) - Windows-specific instructions
- [PER_FOLDER_BACKUP_GUIDE.md](PER_FOLDER_BACKUP_GUIDE.md) - Backup system details
- [WINDOWS_CLEANUP_TROUBLESHOOTING.md](WINDOWS_CLEANUP_TROUBLESHOOTING.md) - Cleanup issues
- [README.md](README.md) - Complete documentation

## 🎉 Summary

**GUI Benefits:**
- ✅ Easy to use (no command typing)
- ✅ Visual feedback (progress bar, colors)
- ✅ One-click operations
- ✅ Statistics display
- ✅ CLI access when needed
- ✅ Windows-friendly
- ✅ Error handling with dialogs

**When to Use CLI:**
- Advanced options not in GUI
- Automation/scripting
- Custom output directories
- Preference for command line
- Remote server usage

**Best Practice:**
Start with GUI for daily use, access CLI for advanced features! 🚀
