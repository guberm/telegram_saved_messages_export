# Windows Cleanup Troubleshooting

## Issue: "Access is denied" Error During Folder Cleanup

If you see warnings like this during backup:
```
⚠️  Folder cleanup warning: [WinError 5] Access is denied: 'telegram_saved_messages_exports\...'
```

**This is a Windows file permission issue.** The folders **were successfully uploaded** to Google Drive, but couldn't be deleted locally.

## Why This Happens

Windows can prevent folder deletion for several reasons:

### 1. **Files Are Open/Locked**
- Windows Explorer preview is reading the files
- Another program has the files open
- System indexing service is accessing the files
- Antivirus is scanning the files

### 2. **Read-Only or System Attributes**
- Files have read-only flag set
- Folders have special attributes
- Windows protected the files

### 3. **Long File Paths**
- Folder names with Cyrillic or special characters
- Windows path length limitations (260 characters)
- Unicode handling issues

### 4. **File System Issues**
- Disk errors or corruption
- NTFS permissions problems
- User account doesn't have full control

## What Was Already Uploaded?

**Good news:** The error occurs **AFTER** successful upload. Your data is safe in Google Drive!

✅ ZIP archive created successfully
✅ Uploaded to Google Drive successfully  
✅ Tracked in database successfully
✅ ZIP archive deleted successfully
❌ Source folder deletion failed (locked by Windows)

## Automatic Retry Logic

The system now automatically:
1. **Tries normal deletion** with `shutil.rmtree()`
2. **Removes readonly flags** and retries
3. **Waits 1 second** if folder is locked
4. **Retries with force** after clearing file attributes
5. **Shows clear warning** if still fails

## Solutions

### Solution 1: Close Windows Explorer
1. **Close all File Explorer windows** viewing the export folder
2. Run backup again: `py main.py --backup-only`
3. Folders should delete successfully this time

### Solution 2: Close Preview Pane
1. Open File Explorer
2. Click **View** → Uncheck **Preview pane**
3. Navigate away from the export folder
4. Run backup again: `py main.py --backup-only`

### Solution 3: Disable Windows Search Indexing (Temporary)
1. Press **Win + R**, type `services.msc`
2. Find **Windows Search** service
3. Right-click → **Stop**
4. Run backup again
5. Re-enable Windows Search when done

### Solution 4: Exclude from Antivirus
1. Open your antivirus software
2. Add `C:\telegram_export\telegram_saved_messages_exports` to exclusions
3. Run backup again
4. Remove exclusion when done (optional)

### Solution 5: Manual Cleanup
After successful upload, manually delete the folders:

```cmd
cd C:\telegram_export\telegram_saved_messages_exports
```

Then delete folders one by one:
```cmd
rmdir /s /q "20161220_055428_msg126379_Вредные_советы_для_Вашего_стар"
```

Or use Windows Explorer with **Shift+Delete** (permanent delete).

### Solution 6: Use --keep-archive Flag
Keep local folders and skip cleanup entirely:

```cmd
py main.py --backup --keep-archive
```

This uploads everything but doesn't delete local files. You can manually clean up later when convenient.

### Solution 7: Reboot and Retry
Sometimes Windows locks persist:

1. Restart your computer
2. Run `py main.py --backup-only` immediately after reboot
3. Don't open File Explorer before backup completes

## Verify Backup Success

Even with cleanup warnings, verify your files are in Google Drive:

### Method 1: Check Database
```cmd
py main.py --stats
```

Look for backup statistics showing completed uploads.

### Method 2: Check Google Drive
1. Go to [Google Drive](https://drive.google.com)
2. Open **Telegram_Exports_Backup** folder
3. Verify your ZIP files are there
4. Check the database file: `export_history_YYYYMMDD_HHMMSS.db`

### Method 3: Query Database Directly
```cmd
sqlite3 telegram_saved_messages_exports\export_history.db "SELECT COUNT(*) FROM backup_history WHERE status='completed';"
```

## Improved Cleanup Logic

The backup script now includes:

```python
def _delete_folder_windows(self, folder_path, folder_name):
    """Delete folder with Windows-specific error handling."""
    
    # Try 1: Normal deletion
    shutil.rmtree(folder_path, onerror=remove_readonly)
    
    # Try 2: Wait and force permissions
    time.sleep(1)
    for file in folder:
        file.chmod(stat.S_IWRITE)  # Remove readonly
    shutil.rmtree(folder_path, onerror=remove_readonly)
```

## Best Practices

### Before Backup
1. ✅ Close all File Explorer windows
2. ✅ Close any programs viewing the export folder
3. ✅ Temporarily disable preview pane
4. ✅ Let Windows finish indexing (wait a few minutes after export)

### During Backup
1. ✅ Don't open the export folder
2. ✅ Don't browse the files while backup is running
3. ✅ Let the script run uninterrupted
4. ✅ Don't use file search or preview while running

### After Backup
1. ✅ Verify uploads in Google Drive
2. ✅ Check database shows "completed" status
3. ✅ Manually delete leftover folders if cleanup failed
4. ✅ Run `--backup-only` again to retry cleanup

## Understanding the Output

### Success (Full):
```
✓ Uploaded successfully
✓ Deleted archive: folder.zip
✓ Deleted folder: folder_name
```
Everything worked perfectly!

### Success (Upload Only):
```
✓ Uploaded successfully
✓ Deleted archive: folder.zip
⚠️  Folder cleanup warning: [WinError 5] Access is denied
   You may need to manually delete: folder_name
```
**Upload succeeded**, but folder still on disk. Safe to delete manually.

### Success (After Retry):
```
✓ Uploaded successfully
✓ Deleted archive: folder.zip
⏳ Folder locked, waiting...
✓ Deleted folder: folder_name (after retry)
```
Retry logic worked! Folder deleted after brief wait.

### Failure:
```
❌ Upload failed
```
Upload itself failed. Folder kept for retry. Check network/auth.

## FAQ

### Q: Are my files safe if cleanup fails?
**A: Yes!** Files are already in Google Drive. The error only affects local cleanup.

### Q: Will failed cleanup break future backups?
**A: No!** The database tracks what's uploaded. Already-uploaded folders are automatically skipped.

### Q: Should I manually delete folders?
**A: Optional.** They're safe to delete anytime after successful upload. Or keep them as local backup.

### Q: Can I disable cleanup entirely?
**A: Yes!** Use `--keep-archive` flag or set `GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = True` in `config.py`.

### Q: Will retry help?
**A: Usually yes!** Run `py main.py --backup-only` after closing File Explorer.

### Q: What about Cyrillic folder names?
**A: Should work fine.** The error is permissions, not Unicode. But if issues persist, consider shorter folder names.

## Prevention: Configure in config.py

Keep all local files by default:

```python
# config.py
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = True
```

Then you can manually clean up when convenient without permission issues.

## Command Reference

```cmd
# Retry backup (skips already uploaded)
py main.py --backup-only

# Keep local files (no cleanup)
py main.py --backup --keep-archive

# Check what's backed up
py main.py --stats

# Manual cleanup (PowerShell)
Get-ChildItem -Directory | Where-Object {$_.Name -match "^2016"} | Remove-Item -Recurse -Force

# Manual cleanup (CMD)
for /d %i in (2016*) do rmdir /s /q "%i"
```

## Summary

| Issue | Status | Solution |
|-------|--------|----------|
| Files locked by Windows | Common | Close File Explorer, retry |
| Upload failed | Check output | Network/auth issue |
| Cleanup failed | Upload OK | Manually delete or retry |
| Preview pane locking files | Common | Disable preview pane |
| Antivirus locking files | Possible | Exclude folder temporarily |
| Read-only files | Handled | Script removes flags automatically |

**Remember:** If you see "✓ Uploaded successfully", your data is safely backed up to Google Drive regardless of cleanup warnings! 🎉
