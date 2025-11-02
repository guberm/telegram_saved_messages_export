# Google Drive Backup Setup Guide

This guide will help you set up automatic backup of your Telegram exports to Google Drive.

## Prerequisites

- A Google account
- Python packages installed (run `pip install -r requirements.txt`)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Telegram Export Backup")
5. Click "Create"

## Step 2: Enable Google Drive API

1. In the Google Cloud Console, select your project
2. Go to "APIs & Services" > "Library"
3. Search for "Google Drive API"
4. Click on "Google Drive API"
5. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" at the top
3. Select "OAuth client ID"
4. If prompted to configure the OAuth consent screen:
   - Click "Configure Consent Screen"
   - Select "External" user type
   - Click "Create"
   - Fill in the required fields:
     - App name: "Telegram Export Backup"
     - User support email: Your email
     - Developer contact email: Your email
   - Click "Save and Continue"
   - Click "Save and Continue" on Scopes page (no changes needed)
   - Click "Save and Continue" on Test users page
   - Click "Back to Dashboard"
5. Return to "Credentials" and click "Create Credentials" > "OAuth client ID"
6. Select "Desktop app" as the application type
7. Enter a name (e.g., "Telegram Export Desktop")
8. Click "Create"

## Step 4: Download Credentials

1. After creating the OAuth client ID, a dialog will appear
2. Click "Download JSON"
3. Save the file as `credentials.json` in your project directory (same folder as `main.py`)

**Important:** Keep this file secure and never share it publicly!

## Step 5: Configure the Application

Edit your `config.py` file and set the following variables:

```python
# Google Drive Backup settings
GOOGLE_DRIVE_BACKUP_ENABLED = True  # Enable automatic backup after each export
GOOGLE_DRIVE_CREDENTIALS_FILE = 'credentials.json'  # Path to credentials file
GOOGLE_DRIVE_TOKEN_FILE = 'token.json'  # Path to store access token (auto-generated)
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = False  # Set to True to keep local zip file after upload
```

## Step 6: First-Time Authentication

The first time you run a backup, your web browser will open asking you to:

1. Select your Google account
2. Click "Continue" when warned that the app isn't verified
3. Review permissions (the app needs to access Google Drive)
4. Click "Allow"

After authentication, a `token.json` file will be created. This stores your access token for future use.

## Usage

### Automatic Backup

If you set `GOOGLE_DRIVE_BACKUP_ENABLED = True` in config.py, backups will happen automatically after each export:

```bash
python main.py
```

### Manual Backup (after export)

```bash
python main.py --backup
```

### Backup Only (without exporting)

```bash
python main.py --backup-only
```

### Keep Local Archive

By default, the local zip archive is deleted after successful upload. To keep it:

```bash
python main.py --backup --keep-archive
```

Or set in config.py:
```python
GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE = True
```

### Test Backup Standalone

You can also test the backup functionality directly:

```bash
python google_drive_backup.py telegram_saved_messages_exports
```

## What Gets Backed Up?

The backup process:

1. Creates a timestamped zip archive of your entire export directory
2. Uploads it to a folder called "Telegram_Exports_Backup" in your Google Drive
3. If a file with the same name already exists, it updates that file
4. Optionally deletes the local zip file after successful upload

## File Structure in Google Drive

```
Google Drive
└── Telegram_Exports_Backup/
    ├── telegram_exports_20241102_143022.zip
    ├── telegram_exports_20241103_091545.zip
    └── ...
```

## Troubleshooting

### Error: credentials.json not found

Make sure you downloaded the OAuth credentials and saved them as `credentials.json` in the project directory.

### Error: Access denied or invalid token

Delete the `token.json` file and run the backup again. You'll need to re-authenticate.

### Browser doesn't open for authentication

The authentication URL will be printed in the console. Copy and paste it into your browser manually.

### Upload is slow

Large archives may take time to upload depending on your internet connection. The progress will be shown in the console.

### Error: Quota exceeded

Google Drive has storage limits. Check your Google Drive storage and free up space if needed.

## Security Notes

- **credentials.json**: Contains OAuth client secrets. Keep it private!
- **token.json**: Contains your access token. Keep it private!
- Consider adding both files to your `.gitignore` if using version control

## Revoking Access

If you want to revoke the app's access to your Google Drive:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Scroll to "Third-party apps with account access"
3. Find "Telegram Export Backup" and click "Remove Access"
4. Delete the `token.json` file from your project directory

## Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
