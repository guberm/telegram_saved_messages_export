"""
Google Drive Backup Module
Handles uploading exported Telegram messages to Google Drive
"""

import os
import io
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import zipfile
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveBackup:
    """Handle Google Drive backup operations."""
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """Initialize Google Drive backup handler.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.backup_folder_id = None
        
    def authenticate(self):
        """Authenticate with Google Drive API."""
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                print(f"⚠️  Error loading token: {e}")
                creds = None
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Refreshing Google Drive access token...")
                    creds.refresh(Request())
                except Exception as e:
                    print(f"⚠️  Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"\n❌ Error: Google Drive credentials file '{self.credentials_file}' not found!")
                    print("\nTo set up Google Drive backup:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a new project or select existing one")
                    print("3. Enable Google Drive API")
                    print("4. Create OAuth 2.0 credentials (Desktop app)")
                    print("5. Download credentials and save as 'credentials.json'")
                    print("6. Place the file in the same directory as this script\n")
                    return False
                
                try:
                    print("\n🔐 Opening browser for Google Drive authentication...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"❌ Authentication failed: {e}")
                    return False
            
            # Save the credentials for the next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                print("✓ Google Drive authentication successful")
            except Exception as e:
                print(f"⚠️  Warning: Could not save token: {e}")
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            print("✓ Connected to Google Drive")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Google Drive: {e}")
            return False
    
    def get_or_create_backup_folder(self, folder_name='Telegram_Exports_Backup'):
        """Get or create the backup folder in Google Drive.
        
        Args:
            folder_name: Name of the backup folder
            
        Returns:
            Folder ID or None on error
        """
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            items = results.get('files', [])
            
            if items:
                # Folder exists
                self.backup_folder_id = items[0]['id']
                print(f"✓ Found existing backup folder: {folder_name}")
                return self.backup_folder_id
            else:
                # Create new folder
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                self.backup_folder_id = folder.get('id')
                print(f"✓ Created backup folder: {folder_name}")
                return self.backup_folder_id
                
        except Exception as e:
            print(f"❌ Error managing backup folder: {e}")
            return None
    
    def create_zip_archive(self, source_dir, output_filename=None):
        """Create a zip archive of the export directory.
        
        Args:
            source_dir: Path to the directory to archive
            output_filename: Optional custom filename for the archive
            
        Returns:
            Path to the created zip file or None on error
        """
        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f"❌ Source directory not found: {source_dir}")
            return None
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"telegram_exports_{timestamp}.zip"
        
        # Create zip in a temporary location or same directory as source
        zip_path = source_path.parent / output_filename
        
        try:
            print(f"Creating zip archive: {output_filename}")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through directory
                file_count = 0
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = Path(root) / file
                        # Calculate relative path for archive
                        arcname = file_path.relative_to(source_path.parent)
                        zipf.write(file_path, arcname)
                        file_count += 1
                        
                        if file_count % 100 == 0:
                            print(f"  Archived {file_count} files...")
            
            file_size_mb = zip_path.stat().st_size / (1024 * 1024)
            print(f"✓ Created archive: {output_filename} ({file_size_mb:.2f} MB, {file_count} files)")
            return zip_path
            
        except Exception as e:
            print(f"❌ Error creating zip archive: {e}")
            if zip_path.exists():
                try:
                    zip_path.unlink()
                except:
                    pass
            return None
    
    def upload_file(self, file_path, parent_folder_id=None, delete_after_upload=False):
        """Upload a file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            parent_folder_id: ID of parent folder (uses backup folder if None)
            delete_after_upload: Whether to delete local file after successful upload
            
        Returns:
            File ID on success, None on error
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        if parent_folder_id is None:
            parent_folder_id = self.backup_folder_id
        
        if parent_folder_id is None:
            print("❌ No parent folder specified and backup folder not set")
            return None
        
        try:
            file_metadata = {
                'name': file_path.name,
                'parents': [parent_folder_id]
            }
            
            # Check if file already exists
            query = f"name='{file_path.name}' and '{parent_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)'
            ).execute()
            
            existing_files = results.get('files', [])
            
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            if existing_files:
                print(f"⚠️  File '{file_path.name}' already exists in Google Drive")
                print(f"   Updating existing file...")
                
                # Update existing file
                media = MediaFileUpload(str(file_path), resumable=True)
                file = self.service.files().update(
                    fileId=existing_files[0]['id'],
                    media_body=media
                ).execute()
                
                print(f"✓ Updated file in Google Drive: {file_path.name} ({file_size_mb:.2f} MB)")
            else:
                # Upload new file
                print(f"Uploading to Google Drive: {file_path.name} ({file_size_mb:.2f} MB)")
                media = MediaFileUpload(str(file_path), resumable=True)
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print(f"✓ Uploaded to Google Drive: {file_path.name}")
            
            # Delete local file if requested
            if delete_after_upload:
                try:
                    file_path.unlink()
                    print(f"✓ Deleted local file: {file_path.name}")
                except Exception as e:
                    print(f"⚠️  Could not delete local file: {e}")
            
            return file.get('id')
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return None
    
    def backup_exports(self, export_dir, create_archive=True, keep_local_archive=False):
        """Backup entire export directory to Google Drive.
        
        Args:
            export_dir: Path to the export directory
            create_archive: Whether to create a zip archive before uploading
            keep_local_archive: Whether to keep the local archive after upload
            
        Returns:
            True on success, False on error
        """
        if not self.authenticate():
            return False
        
        if not self.get_or_create_backup_folder():
            return False
        
        export_path = Path(export_dir)
        if not export_path.exists():
            print(f"❌ Export directory not found: {export_dir}")
            return False
        
        try:
            if create_archive:
                # Create zip archive
                zip_path = self.create_zip_archive(export_dir)
                if not zip_path:
                    return False
                
                # Upload zip file
                file_id = self.upload_file(
                    zip_path, 
                    delete_after_upload=not keep_local_archive
                )
                
                return file_id is not None
            else:
                # Upload individual files (create folder structure)
                print("⚠️  Note: Uploading individual files is not yet implemented.")
                print("    Using archive mode instead.")
                return self.backup_exports(export_dir, create_archive=True, keep_local_archive=keep_local_archive)
                
        except Exception as e:
            print(f"❌ Error during backup: {e}")
            return False


def backup_to_google_drive(export_dir, keep_local_archive=False):
    """Convenience function to backup exports to Google Drive.
    
    Args:
        export_dir: Path to the export directory
        keep_local_archive: Whether to keep the local zip archive
        
    Returns:
        True on success, False on error
    """
    backup = GoogleDriveBackup()
    return backup.backup_exports(export_dir, create_archive=True, keep_local_archive=keep_local_archive)


if __name__ == '__main__':
    # Test the backup functionality
    import sys
    
    if len(sys.argv) > 1:
        export_dir = sys.argv[1]
    else:
        export_dir = 'telegram_saved_messages_exports'
    
    print(f"Testing Google Drive backup for: {export_dir}\n")
    success = backup_to_google_drive(export_dir, keep_local_archive=True)
    
    if success:
        print("\n✅ Backup completed successfully!")
    else:
        print("\n❌ Backup failed!")
