# Google Drive Backup Feature - Summary of Changes

## Overview

Added comprehensive Google Drive backup functionality to the Telegram Saved Messages Exporter. Users can now automatically or manually backup their exports to Google Drive as compressed archives.

## New Files Created

### 1. `google_drive_backup.py`
Main backup module containing:
- `GoogleDriveBackup` class for handling all Google Drive operations
- OAuth2 authentication with Google Drive API
- Automatic folder creation in Google Drive
- Zip archive creation from export directory
- File upload with duplicate detection
- Progress reporting and error handling
- Standalone testing capability

### 2. `GOOGLE_DRIVE_SETUP.md`
Comprehensive setup guide covering:
- Step-by-step Google Cloud Console setup
- Google Drive API enablement
- OAuth2 credential creation
- First-time authentication process
- Configuration instructions
- Usage examples
- Troubleshooting common issues
- Security best practices

### 3. `BACKUP_QUICK_REFERENCE.md`
Quick reference guide with:
- Command examples
- Configuration options
- Workflow explanation
- Troubleshooting tips
- Security reminders

## Modified Files

### 1. `requirements.txt`
Added Google Drive API dependencies:
- `google-auth>=2.23.0`
- `google-auth-oauthlib>=1.1.0`
- `google-auth-httplib2>=0.1.1`
- `google-api-python-client>=2.100.0`

### 2. `config.py`
Added Google Drive settings:
- `GOOGLE_DRIVE_BACKUP_ENABLED` - Enable/disable automatic backup
- `GOOGLE_DRIVE_CREDENTIALS_FILE` - Path to OAuth credentials
- `GOOGLE_DRIVE_TOKEN_FILE` - Path to access token
- `GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE` - Keep/delete local archive after upload

### 3. `config.py.example`
Updated template to include Google Drive configuration options.

### 4. `main.py`
Integrated backup functionality:
- Import Google Drive backup module
- Handle missing Google Drive config gracefully (backward compatibility)
- Added command-line arguments:
  - `--backup` - Backup after export
  - `--backup-only` - Backup without exporting
  - `--keep-archive` - Keep local zip file
- Automatic backup after export (if enabled)
- Backup-only mode for existing exports

### 5. `README.md`
Updated documentation:
- Added Google Drive backup to features list
- Installation instructions updated
- New usage examples for backup commands
- Google Drive quick start guide
- Updated security notes
- Expanded troubleshooting section

### 6. `.gitignore`
Added entries for Google Drive files:
- `credentials.json` - OAuth credentials
- `token.json` - Access token
- `*.zip` - Backup archives

## Key Features

### 1. Automatic Backup
- Set `GOOGLE_DRIVE_BACKUP_ENABLED = True` in config
- Backs up automatically after each export
- No manual intervention needed

### 2. Manual Backup
- Use `--backup` flag to backup after export
- Use `--backup-only` to backup existing exports
- Flexible control over when backups occur

### 3. Archive Management
- Creates timestamped zip archives
- Format: `telegram_exports_YYYYMMDD_HHMMSS.zip`
- Optionally keeps or deletes local archives
- Shows file count and size information

### 4. Google Drive Integration
- OAuth2 authentication (secure)
- Auto-creates backup folder
- Detects and updates duplicate files
- Resumable uploads for large files
- Persistent authentication via token

### 5. User-Friendly
- Clear progress messages
- Detailed error reporting
- Browser-based authentication
- Comprehensive documentation

### 6. Security
- OAuth2 flow (no password storage)
- Local credential storage
- Token refresh handling
- Files excluded from git by default

## Usage Examples

### Basic Usage
```bash
# Export with backup
python main.py --backup

# Backup only
python main.py --backup-only

# Keep local archive
python main.py --backup --keep-archive
```

### Combined with Existing Features
```bash
# Export from date and backup
python main.py --from-date 2024-01-01 --backup

# Force re-export and backup
python main.py --force --backup

# Custom output directory with backup
python main.py --output my_exports --backup
```

## Setup Process

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Create Google Cloud project** and enable Drive API
3. **Create OAuth2 credentials** (Desktop app)
4. **Download credentials** as `credentials.json`
5. **Update config.py** with Google Drive settings
6. **Run first backup** - browser opens for authentication
7. **Authenticate** - token saved for future use

## Technical Details

### Dependencies
- `google-auth` - Authentication library
- `google-auth-oauthlib` - OAuth2 flow
- `google-auth-httplib2` - HTTP transport
- `google-api-python-client` - Drive API client

### Authentication Flow
1. Check for existing `token.json`
2. If valid, use existing token
3. If expired, refresh token
4. If missing, initiate OAuth flow
5. Save token for future use

### Backup Process
1. Create zip archive of export directory
2. Calculate file count and size
3. Authenticate with Google Drive
4. Get or create backup folder
5. Check for existing file
6. Upload or update file
7. Optionally delete local archive

### Error Handling
- Graceful handling of missing credentials
- Token refresh on expiration
- Detailed error messages
- Non-critical failures don't stop exports

## Backward Compatibility

- Works with existing config.py files (uses defaults)
- Optional feature - doesn't affect normal operation
- Graceful degradation if credentials missing
- All existing functionality preserved

## Documentation

Three comprehensive guides:
1. **GOOGLE_DRIVE_SETUP.md** - Full setup instructions
2. **BACKUP_QUICK_REFERENCE.md** - Command reference
3. **README.md** - Updated with backup info

## Testing

Standalone test capability:
```bash
python google_drive_backup.py telegram_saved_messages_exports
```

## Security Considerations

- OAuth2 credentials never exposed
- Token stored locally
- Files excluded from version control
- Revocation instructions provided
- Best practices documented

## Future Enhancements (Possible)

- Selective folder backup
- Incremental backups
- Multiple cloud providers
- Encryption at rest
- Scheduled backups
- Backup rotation/cleanup
- Progress bars for large uploads
- Parallel file uploads

## Notes

- First backup requires browser authentication
- Subsequent backups are automatic
- Archives are timestamped (no overwrites)
- Large exports may take time to upload
- Google Drive storage limits apply
- Free Google accounts: 15GB storage
