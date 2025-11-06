# GUI Troubleshooting - Common Errors

## Error: "Cannot create a file when that file already exists"

### Full Error Message
```
❌ Error: [WinError 183] Cannot create a file when that file already exists: 
'telegram_saved_messages_exports\\export_history.db'
```

### Cause
The database initialization function was being called with the wrong parameter (file path instead of directory path).

### ✅ Fixed
The issue has been resolved in the latest version of `gui.py`. The `init_database()` function now receives the correct directory path.

### If You Still See This Error

1. **Update the code:**
   ```bash
   git pull
   ```

2. **Or manually fix in gui.py line ~329:**
   
   **Wrong:**
   ```python
   db_path = Path(OUTPUT_DIR) / "export_history.db"
   db_path.parent.mkdir(parents=True, exist_ok=True)
   init_database(str(db_path))  # ❌ Passing file path
   ```
   
   **Correct:**
   ```python
   db_path = Path(OUTPUT_DIR) / "export_history.db"
   init_database(OUTPUT_DIR)  # ✅ Passing directory path
   ```

3. **Restart GUI:**
   ```bash
   py gui.py
   ```

---

## Error: "tuple indices must be integers or slices, not str"

### Full Error Message
```
Error loading stats: tuple indices must be integers or slices, not str
```

### Cause
This appears when the database query returns data in an unexpected format.

### Solution
1. **Check database file exists:**
   ```bash
   dir telegram_saved_messages_exports\export_history.db
   ```

2. **If corrupted, backup and recreate:**
   ```bash
   copy telegram_saved_messages_exports\export_history.db export_history.db.backup
   del telegram_saved_messages_exports\export_history.db
   py main.py
   ```

3. **Or use CLI to check:**
   ```bash
   py main.py --stats
   ```

---

## Error: GUI Won't Start

### Symptoms
- Double-clicking `run_gui.bat` opens and closes immediately
- No error message visible

### Solutions

1. **Check Python is installed:**
   ```bash
   py --version
   ```
   Should show: `Python 3.x.x`

2. **Run GUI directly to see errors:**
   ```bash
   py gui.py
   ```
   This will show the actual error message.

3. **Check tkinter is available:**
   ```bash
   py -c "import tkinter; print('tkinter OK')"
   ```

4. **Reinstall dependencies:**
   ```bash
   py -m pip install --upgrade -r requirements.txt
   ```

---

## Error: Import Errors

### Error Message Examples
```
ImportError: cannot import name 'export_saved_messages'
ModuleNotFoundError: No module named 'telethon'
```

### Solution

1. **Install all dependencies:**
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Check config.py exists:**
   ```bash
   dir config.py
   ```
   If not, copy from example:
   ```bash
   copy config.py.example config.py
   ```

3. **Edit config.py with your credentials**

---

## Error: Authentication Failed

### Telegram Authentication

**Error:** "Could not connect to Telegram"

**Solution:**
1. Check internet connection
2. Verify credentials in `config.py`:
   - `API_ID` (numbers only)
   - `API_HASH` (string)
   - `PHONE` (with country code, e.g., `+1234567890`)
3. Delete session and retry:
   ```bash
   del telegram_session.session
   py gui.py
   ```

### Google Drive Authentication

**Error:** "Google Drive authentication failed"

**Solution:**
1. Check `credentials.json` exists
2. Delete old token and re-authenticate:
   ```bash
   del token.json
   py gui.py
   ```
3. Follow OAuth flow in browser
4. See [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) for setup

---

## Error: Progress Stuck

### Symptoms
- Progress bar animating but no log updates
- Last message: "Processing: folder_name"
- No error messages

### Possible Causes & Solutions

1. **Large file downloading:**
   - Just wait, it can take time for big files
   - Watch Windows Task Manager for network activity

2. **Network timeout:**
   - Check internet connection
   - Click **Stop** and restart

3. **Folder permission issue:**
   - Close Windows Explorer
   - Make sure folder isn't open in other programs
   - See [WINDOWS_CLEANUP_TROUBLESHOOTING.md](WINDOWS_CLEANUP_TROUBLESHOOTING.md)

---

## Error: Statistics Not Updating

### Symptoms
- Numbers in statistics panel don't change
- After export, still shows old counts

### Solution

1. **Click "🔄 Refresh Stats" button**

2. **If still wrong, restart GUI:**
   - Click **❌ Exit**
   - Reopen: `py gui.py`

3. **Check from CLI:**
   ```bash
   py main.py --stats
   ```

4. **Verify database file:**
   ```bash
   dir telegram_saved_messages_exports\export_history.db
   ```

---

## Error: Cannot Stop Operation

### Symptoms
- Clicked **Stop** button
- Operation continues running

### Explanation
Some operations need to finish their current task before stopping:
- Uploading a file must complete
- Database transaction must commit

### Solution
**Wait a few seconds** for current operation to finish, then it will stop.

---

## Error: "Open Export Folder" Does Nothing

### Cause
Folder doesn't exist yet (no exports done).

### Solution
Run an export first:
1. Click **📥 Export Messages**
2. Wait for completion
3. Then **📂 Open Export Folder** will work

---

## Error: CLI Commands Don't Work from GUI

### When Using "🖥️ Open CLI" Button

The CLI opens in the correct directory, but you need to run commands properly:

**Wrong:**
```bash
main.py --help
```

**Correct:**
```bash
py main.py --help
```

---

## Getting More Help

### Enable Debug Mode

Run GUI with Python directly to see all errors:
```bash
py gui.py
```

### Check Logs

Look at the Progress panel in GUI - it shows detailed error messages with colors:
- 🔴 Red = Errors
- 🟡 Yellow = Warnings

### Use CLI for Detailed Errors

```bash
py main.py --stats
py main.py --backup-only
```

CLI often provides more detailed error messages.

### Documentation

- [GUI_USER_GUIDE.md](GUI_USER_GUIDE.md) - Complete GUI guide
- [README.md](README.md) - Full documentation
- [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) - Google Drive setup
- [WINDOWS_CLEANUP_TROUBLESHOOTING.md](WINDOWS_CLEANUP_TROUBLESHOOTING.md) - Cleanup issues

---

## Quick Diagnostic Commands

```bash
# Check Python
py --version

# Check dependencies
py -c "import telethon, google; print('Dependencies OK')"

# Check GUI
py -c "import gui; print('GUI OK')"

# Check config
py -c "import config; print(f'API_ID: {config.API_ID}')"

# Check database
dir telegram_saved_messages_exports\export_history.db

# Test import
py main.py --stats
```

---

## Prevention Tips

1. **Keep GUI updated:**
   ```bash
   git pull
   ```

2. **Use latest dependencies:**
   ```bash
   py -m pip install --upgrade -r requirements.txt
   ```

3. **Close File Explorer before operations**
   - Prevents permission errors
   - Allows cleanup to work

4. **Don't interrupt database operations**
   - Let current folder finish
   - Then click Stop

5. **Check disk space**
   - Exports need space for folders
   - Backup needs space for ZIPs

---

## Still Having Issues?

1. **Try CLI instead:**
   ```bash
   py main.py --help
   ```

2. **Check all config files exist:**
   - `config.py` ✅
   - `credentials.json` (for Google Drive) ⚠️ optional
   - `telegram_session.session` (created on first run)

3. **Restart computer**
   - Sometimes Windows locks files
   - Fresh start helps

4. **Run as Administrator** (if permission errors persist)
   - Right-click `run_gui.bat`
   - "Run as administrator"

---

**Most issues are solved by:**
1. Updating the code (`git pull`)
2. Reinstalling dependencies (`py -m pip install -r requirements.txt`)
3. Checking `config.py` settings
4. Reading error messages in the Progress panel

**GUI makes things easier, but CLI is always there as backup!** 🖥️✨
