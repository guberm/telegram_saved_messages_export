# Telegram Saved Messages Exporter

Export your Telegram saved messages to organized HTML and Markdown files with media downloads.

**🎨 NEW! Modern GUI Available!** Double-click `run_gui.bat` for a beautiful interface!

**Windows users:** See [WINDOWS_QUICK_START.md](WINDOWS_QUICK_START.md) for Windows-specific instructions.

## ✨ Features

- **🎨 Modern GUI** - Beautiful interface with dark theme, stat cards, and toast notifications
- **🖥️ Simple GUI** - Lightweight alternative interface
- **📁 Individual Message Folders** - Each message gets its own folder
- **🎨 Telegram-like HTML Styling** - HTML files look like actual Telegram messages  
- **🖼️ Media Downloads** - Automatically downloads and saves images, videos, etc.
- **📊 SQLite Database Tracking** - Tracks exported messages and backups
- **🔄 Incremental Exports** - Only exports new messages by default
- **📈 Export Statistics** - View export stats and progress
- **🔗 Message Links** - Links to original messages in Telegram
- **☁️ Google Drive Backup** - Per-folder backup with automatic cleanup
- **🔁 Resume Capability** - Interrupted backups resume where they left off
- **🧹 Auto Cleanup** - Deletes folders after successful upload (optional)

## 🚀 Quick Start

### Using Modern GUI (Recommended)

**Windows:**
1. Double-click `run_gui.bat`
2. Configure options in the beautiful interface
3. Click "📥 Export Messages" or "📥☁️ Export + Backup"

**Features:**
- 🎨 Dark theme with visual stat cards
- 🔔 Toast notifications
- 📊 Real-time progress
- 🎯 Status indicator
- 🌈 Color-coded logs

**Or run directly:**
```bash
py gui_modern.py
```

### Using Simple GUI

For a lightweight alternative:
```bash
py gui.py
```

### Using CLI

See [Usage](#-usage) section below for command-line options.

## 📋 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users:** If `pip` or `python` commands are not recognized, use one of these alternatives:
```powershell
# Option 1: Use py launcher (recommended for Windows)
py -m pip install -r requirements.txt

# Option 2: Use python3
python3 -m pip install -r requirements.txt

# Option 3: Use full path (adjust version as needed)
C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt
```

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 3. Configure the Script

1. Copy the example config file:
   ```bash
   copy config.py.example config.py
   ```

2. Edit `config.py` and replace the placeholder values:
   ```python
   API_ID = '12345678'  # Your API ID
   API_HASH = 'your_api_hash_here'  # Your API Hash
   PHONE = '+1234567890'  # Your phone number
   ```

### 4. (Optional) Setup Google Drive Backup

To enable automatic backup to Google Drive, see [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) for detailed instructions.

Quick setup:
1. Enable Google Drive API in Google Cloud Console
2. Download OAuth credentials as `credentials.json`
3. Set `GOOGLE_DRIVE_BACKUP_ENABLED = True` in `config.py`

### 5. First Run Authentication

On the first run, you'll be asked to enter the verification code sent to your Telegram account.

## 🎯 Usage

### Using GUI (Recommended)

**Start GUI:**
```bash
py gui.py
```

Or on Windows, double-click: `run_gui.bat`

**GUI Features:**
- 📊 Real-time statistics display
- 📅 Date filter for selective exports
- ☑️ Checkboxes for all options
- 📥 One-click export operations
- 📋 Live progress log with color coding
- 🖥️ Open CLI button for advanced commands

**GUI Buttons:**
- **📥 Export Messages** - Export without backup
- **📥☁️ Export + Backup** - Export and backup to Google Drive
- **☁️ Backup Only** - Backup existing exports (no new export)
- **🔄 Refresh Stats** - Update statistics display
- **📂 Open Export Folder** - Open in File Explorer
- **🖥️ Open CLI** - Launch command prompt for CLI commands

### Using CLI (Advanced)

**Windows users:** Replace `python` with `py` in all commands below if Python is not in your PATH.

#### Export All Saved Messages

```bash
python main.py
# or on Windows:
py main.py
```

#### Export Messages from a Specific Date

```bash
python main.py --from-date 2024-01-01
# or on Windows:
py main.py --from-date 2024-01-01
```

This will export all messages from January 1, 2024 onwards.

#### Force Re-export

```bash
python main.py --force
```

Re-exports messages that were already exported.

### View Statistics

```bash
python main.py --stats
```

### Backup to Google Drive

```bash
# Export and backup
python main.py --backup

# Backup only (without exporting)
python main.py --backup-only

# Keep local archive after backup
python main.py --backup --keep-archive
```

### Custom Output Directory

```bash
python main.py --output my_exports
```

Default output directory is `telegram_saved_messages_exports/`.

## Output Format

Each message is saved in its own folder with the following structure:

### Folder Format
```
telegram_saved_messages_exports/
└── YYYYMMDD_HHMMSS_msgID_preview/
    ├── message.html
    ├── message.md
    └── media (if present)
```

Example:
```
telegram_saved_messages_exports/
└── 20241011_143052_msg12345_Hello_world/
    ├── message.html
    ├── message.md
    └── photo.jpg
```

### HTML Files
- Beautiful, responsive design
- Styled with CSS
- Includes metadata, forward info, and media details
- Opens directly in any browser

### Markdown Files
- Clean, readable format
- Compatible with any Markdown editor
- Includes all message metadata
- Easy to import into other systems

## Examples

```bash
# Export everything (incremental - only new messages)
python main.py

# Export messages from June 2024 onwards
python main.py --from-date 2024-06-01

# Force re-export all messages
python main.py --force

# View export statistics
python main.py --stats

# Export and backup to Google Drive
python main.py --backup

# Only backup existing exports to Google Drive
python main.py --backup-only

# Export with custom output directory
python main.py --output backup_2024

# Export and backup, keeping local archive
python main.py --backup --keep-archive
```

## What Gets Exported

✅ Message text
✅ Date and time
✅ Message ID
✅ Forward information (who forwarded, when)
✅ Media type (photos, videos, documents, etc.)
✅ Media files (downloaded and saved)
✅ Media captions
✅ Web page previews
✅ Links

## Google Drive Backup

The tool can automatically backup your exports to Google Drive with advanced features:

- **Per-Folder Archives** - Each message folder backed up separately
- **Database Tracking** - SQLite tracks upload status for each folder
- **Resume Capability** - Interrupted backups automatically resume
- **Automatic Cleanup** - Deletes folders/archives after successful upload (saves disk space)
- **Progress Reporting** - See detailed progress for each folder
- **Failure Isolation** - One failed folder doesn't affect others

### Quick Start

1. Set up Google Drive API credentials (see [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md))
2. Rename downloaded file to `credentials.json` in project directory
3. Add your email as test user in OAuth consent screen
4. Enable in `config.py`:
   ```python
   GOOGLE_DRIVE_BACKUP_ENABLED = True
   ```
5. Run: `py main.py --backup` (or `python main.py --backup`)

### How It Works

```
For each message folder:
1. Create ZIP archive
2. Upload to Google Drive
3. Track in database
4. Delete folder & archive (unless --keep-archive)
5. Resume automatically if interrupted
```

### Guides

- **Complete Guide**: [PER_FOLDER_BACKUP_GUIDE.md](PER_FOLDER_BACKUP_GUIDE.md)
- **Setup Instructions**: [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)
- **Implementation Details**: [PER_FOLDER_IMPLEMENTATION_SUMMARY.md](PER_FOLDER_IMPLEMENTATION_SUMMARY.md)

## Notes

- **First run**: You'll need to enter a verification code sent by Telegram
- **Session file**: A `telegram_session.session` file will be created to store your authentication
- **Rate limits**: The script respects Telegram's rate limits
- **Privacy**: All data is processed locally on your computer
- **Media files**: Downloaded and saved in message folders
- **Database**: `exports.db` tracks exported messages to avoid duplicates

## Troubleshooting

### "Please configure your API credentials first!"
- Make sure you've replaced `YOUR_API_ID`, `YOUR_API_HASH`, and `YOUR_PHONE_NUMBER` in `config.py`

### "Invalid date format"
- Use the format `YYYY-MM-DD` for dates (e.g., `2024-01-15`)

### "Could not connect to Telegram"
- Check your internet connection
- Verify your API credentials are correct
- Make sure your phone number includes the country code (e.g., `+1234567890`)

### Google Drive Authentication Issues
- Make sure `credentials.json` is in the project directory
- Delete `token.json` and re-authenticate if you see token errors
- See [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) for detailed troubleshooting

### Permission Errors
- Make sure you have write permissions in the output directory
- Try running with a different output folder using `--output`

## Security

- Keep your `api_id` and `api_hash` private
- Don't share your `telegram_session.session` file
- The session file contains your authentication token
- Keep `credentials.json` and `token.json` private (Google Drive access)
- Consider adding these files to `.gitignore` if using version control

## License

Free to use and modify for personal use.
