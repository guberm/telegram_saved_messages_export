# Telegram Saved Messages Exporter

Export your Telegram saved messages to organized HTML and Markdown files with media downloads.

**Windows users:** See [WINDOWS_QUICK_START.md](WINDOWS_QUICK_START.md) for Windows-specific instructions.

## ✨ Features

- **📁 Individual Message Folders** - Each message gets its own folder
- **🎨 Telegram-like HTML Styling** - HTML files look like actual Telegram messages  
- **🖼️ Media Downloads** - Automatically downloads and saves images, videos, etc.
- **📊 SQLite Database Tracking** - Tracks exported messages to avoid duplicates
- **🔄 Incremental Exports** - Only exports new messages by default
- **📈 Export Statistics** - View export stats and progress
- **🔗 Message Links** - Links to original messages in Telegram
- **☁️ Google Drive Backup** - Automatic backup to Google Drive (optional)

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

## Usage

**Windows users:** Replace `python` with `py` in all commands below if Python is not in your PATH.

### Export All Saved Messages

```bash
python main.py
# or on Windows:
py main.py
```

### Export Messages from a Specific Date

```bash
python main.py --from-date 2024-01-01
# or on Windows:
py main.py --from-date 2024-01-01
```

This will export all messages from January 1, 2024 onwards.

### Force Re-export

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

The tool can automatically backup your exports to Google Drive:

- Creates timestamped zip archives
- Uploads to a dedicated backup folder
- Optional: Keep or delete local archives
- Full setup guide: [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)

### Quick Start

1. Set up Google Drive API credentials (see GOOGLE_DRIVE_SETUP.md)
2. Place `credentials.json` in the project directory
3. Enable in `config.py`:
   ```python
   GOOGLE_DRIVE_BACKUP_ENABLED = True
   ```
4. Run normally: `python main.py`

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
