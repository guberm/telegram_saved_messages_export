# Quick Reference: Google Drive Backup Commands

## Installation

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Setup

1. Follow the [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) guide to set up Google Drive API
2. Place `credentials.json` in the project directory
3. Configure `config.py`:
   ```python
   GOOGLE_DRIVE_BACKUP_ENABLED = True  # For automatic backup
   ```

## Commands

### Export with Automatic Backup

If `GOOGLE_DRIVE_BACKUP_ENABLED = True` in config:
```bash
python main.py
```

### Export with Manual Backup

```bash
python main.py --backup
```

### Backup Only (No Export)

```bash
python main.py --backup-only
```

### Keep Local Archive

By default, local zip files are deleted after upload. To keep them:
```bash
python main.py --backup --keep-archive
```

Or set in config.py:
```python
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = True
```

### Combined Commands

```bash
# Export from specific date and backup
python main.py --from-date 2024-01-01 --backup

# Force re-export and backup
python main.py --force --backup

# Custom output directory with backup
python main.py --output my_exports --backup

# Backup with custom output and keep archive
python main.py --output my_exports --backup-only --keep-archive
```

## Testing

Test the backup functionality directly:
```bash
python google_drive_backup.py telegram_saved_messages_exports
```

## Configuration Options

In `config.py`:

```python
# Enable/disable automatic backup after export
GOOGLE_DRIVE_BACKUP_ENABLED = True  # or False

# Path to OAuth credentials (download from Google Cloud Console)
GOOGLE_DRIVE_CREDENTIALS_FILE = 'credentials.json'

# Path to store access token (auto-generated)
GOOGLE_DRIVE_TOKEN_FILE = 'token.json'

# Keep local zip archive after upload
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = False  # or True
```

## What Happens During Backup?

1. **Create Archive**: Creates a timestamped zip file of all exports
   - Example: `telegram_exports_20241102_143022.zip`

2. **Upload to Google Drive**: Uploads to "Telegram_Exports_Backup" folder
   - Creates folder if it doesn't exist
   - Updates file if same name exists

3. **Cleanup**: Optionally deletes local archive (unless `--keep-archive`)

## File Size Information

The backup process shows:
- Number of files being archived
- Archive size in MB
- Upload progress

## Authentication

First-time usage:
- Browser opens for Google authentication
- Select your Google account
- Grant permissions
- `token.json` is created for future use

Subsequent uses:
- Automatic authentication using `token.json`
- Token refreshed if expired

## Troubleshooting

### No browser window opens
Copy the URL from console and paste in browser manually.

### Token expired
Delete `token.json` and re-authenticate.

### Upload failed
- Check internet connection
- Verify Google Drive storage space
- Check console for error messages

### Archive too large
Google Drive has upload limits. Consider:
- Backing up more frequently (smaller archives)
- Cleaning old exports before backing up

## Security Reminders

- Keep `credentials.json` private (OAuth client secrets)
- Keep `token.json` private (your access token)
- Both are in `.gitignore` by default
- Never commit these files to version control

## Revoke Access

To remove the app's access to Google Drive:
1. Visit: https://myaccount.google.com/security
2. Go to "Third-party apps with account access"
3. Remove "Telegram Export Backup"
4. Delete `token.json` from project directory
