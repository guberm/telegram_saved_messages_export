# Windows Quick Start Guide

## Python Command Issues on Windows

If you see an error like:
```
python : The term 'python' is not recognized...
```

**Solution:** Use `py` instead of `python` for all commands.

## Installation

```powershell
# Install dependencies
py -m pip install -r requirements.txt
```

## Common Commands (Windows)

### Export Messages
```powershell
# Export all saved messages
py main.py

# Export from specific date
py main.py --from-date 2024-01-01

# Force re-export
py main.py --force

# View statistics
py main.py --stats
```

### Backup Commands
```powershell
# Export and backup to Google Drive
py main.py --backup

# Backup only (no export)
py main.py --backup-only

# Keep local archive after backup
py main.py --backup --keep-archive

# Export from date and backup
py main.py --from-date 2024-01-01 --backup
```

### Other Options
```powershell
# Custom output directory
py main.py --output my_exports

# Combined commands
py main.py --force --backup --keep-archive
```

## Setup Steps (Windows)

### 1. Install Python
If Python is not installed:
1. Download from https://www.python.org/downloads/
2. Run installer
3. **Important:** Check "Add Python to PATH" during installation
4. Restart your terminal/PowerShell

### 2. Install Dependencies
```powershell
cd C:\telegram_export
py -m pip install -r requirements.txt
```

### 3. Configure Telegram API
1. Copy the config template:
   ```powershell
   copy config.py.example config.py
   ```

2. Edit `config.py` in Notepad or your favorite editor:
   ```powershell
   notepad config.py
   ```

3. Replace these values:
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `PHONE` - Your phone number with country code

### 4. (Optional) Setup Google Drive Backup

See [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) for detailed instructions.

Quick version:
1. Get OAuth credentials from Google Cloud Console
2. Save as `credentials.json` in project folder
3. Edit `config.py` and set:
   ```python
   GOOGLE_DRIVE_BACKUP_ENABLED = True
   ```

### 5. Run First Export
```powershell
py main.py
```

You'll be asked to enter a verification code sent to your Telegram.

## Troubleshooting Windows Issues

### "py is not recognized"
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation
- Restart PowerShell/Command Prompt after installation

### "pip is not recognized"
Use the full command:
```powershell
py -m pip install -r requirements.txt
```

### Permission Errors
- Run PowerShell as Administrator
- Or change to a folder where you have write permissions

### Long Path Issues
Windows has a 260 character path limit. If you get path errors:
1. Enable long paths in Windows 10/11:
   - Run as Administrator:
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```
2. Or use a shorter output path:
   ```powershell
   py main.py --output C:\exports
   ```

### Execution Policy Errors
If you see script execution errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## PowerShell vs Command Prompt

Both work! Choose whichever you prefer:

### PowerShell (Recommended)
```powershell
PS C:\telegram_export> py main.py --backup
```

### Command Prompt
```cmd
C:\telegram_export> py main.py --backup
```

## Checking Your Setup

### Verify Python Installation
```powershell
py --version
# Should show: Python 3.x.x
```

### Verify Dependencies
```powershell
py -c "import telethon; print('Telethon OK')"
py -c "from google_drive_backup import GoogleDriveBackup; print('Google Drive OK')"
```

### Verify Configuration
```powershell
py -c "from config import API_ID, API_HASH; print('Config OK')"
```

## Running in Background (Windows)

To run without keeping the window open:
```powershell
Start-Process py -ArgumentList "main.py --backup" -WindowStyle Hidden
```

Or create a scheduled task:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
   - Program: `py`
   - Arguments: `C:\telegram_export\main.py --backup`
   - Start in: `C:\telegram_export`

## File Explorer Integration

Create a batch file (`run_export.bat`) for easy double-click execution:
```batch
@echo off
cd /d "%~dp0"
py main.py --backup
pause
```

Save in the project folder, then double-click to run!

## Creating Desktop Shortcut

1. Right-click on `run_export.bat`
2. Send to > Desktop (create shortcut)
3. Rename shortcut to "Telegram Export"
4. Optional: Right-click > Properties > Change Icon

## Visual Studio Code (VS Code)

If using VS Code on Windows:
1. Open terminal: `Ctrl + ~`
2. Run commands normally:
   ```powershell
   py main.py
   ```

## Common Windows Paths

- Python: `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx\`
- Project: `C:\telegram_export\`
- Exports: `C:\telegram_export\telegram_saved_messages_exports\`
- Config: `C:\telegram_export\config.py`

## Getting Help

View all available options:
```powershell
py main.py --help
```

## Quick Command Reference

| Task | Command |
|------|---------|
| Install dependencies | `py -m pip install -r requirements.txt` |
| Export messages | `py main.py` |
| Export from date | `py main.py --from-date 2024-01-01` |
| Backup to Drive | `py main.py --backup` |
| Backup only | `py main.py --backup-only` |
| View stats | `py main.py --stats` |
| Force re-export | `py main.py --force` |
| Get help | `py main.py --help` |

## Example Session

```powershell
# Navigate to project
cd C:\telegram_export

# Install dependencies (first time only)
py -m pip install -r requirements.txt

# Configure (first time only)
copy config.py.example config.py
notepad config.py
# Edit and save

# Run export
py main.py

# Export and backup
py main.py --backup

# View statistics
py main.py --stats
```

## Need More Help?

- Main README: [README.md](README.md)
- Google Drive Setup: [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)
- Command Reference: [BACKUP_QUICK_REFERENCE.md](BACKUP_QUICK_REFERENCE.md)
- Visual Guide: [VISUAL_WORKFLOW_GUIDE.md](VISUAL_WORKFLOW_GUIDE.md)
