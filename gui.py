"""
Simple GUI for Telegram Saved Messages Exporter
Provides a user-friendly interface while keeping CLI available
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Import existing modules
from config import *
from database import init_database, get_export_stats, get_backup_stats
from exporter import export_saved_messages
from google_drive_backup import GoogleDriveBackup
from telethon import TelegramClient


class ExporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Saved Messages Exporter")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.is_running = False
        self.current_thread = None
        
        # Setup UI
        self.setup_ui()
        
        # Load initial stats
        self.load_stats()
    
    def setup_ui(self):
        """Create the user interface"""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="📱 Telegram Saved Messages Exporter",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # Stats Frame
        stats_frame = ttk.LabelFrame(self.root, text="📊 Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_text = ttk.Label(stats_frame, text="Loading statistics...", justify=tk.LEFT)
        self.stats_text.pack(anchor=tk.W)
        
        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="⚙️ Options", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date filter
        date_frame = ttk.Frame(options_frame)
        date_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(date_frame, text="Export from date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry = ttk.Entry(date_frame, width=15)
        self.date_entry.pack(side=tk.LEFT)
        ttk.Label(date_frame, text="(leave empty for all messages)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Checkboxes
        self.force_var = tk.BooleanVar(value=False)
        self.backup_var = tk.BooleanVar(value=GOOGLE_DRIVE_BACKUP_ENABLED)
        self.keep_archive_var = tk.BooleanVar(value=GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE)
        
        ttk.Checkbutton(
            options_frame,
            text="🔄 Force re-export (export already exported messages)",
            variable=self.force_var
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="☁️ Backup to Google Drive after export",
            variable=self.backup_var
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="💾 Keep local archives after backup",
            variable=self.keep_archive_var
        ).pack(anchor=tk.W, pady=2)
        
        # Action Buttons Frame
        buttons_frame = ttk.Frame(self.root, padding="10")
        buttons_frame.pack(fill=tk.X, padx=10)
        
        # Export button
        self.export_btn = ttk.Button(
            buttons_frame,
            text="📥 Export Messages",
            command=self.start_export,
            style="Accent.TButton"
        )
        self.export_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Export + Backup button
        self.export_backup_btn = ttk.Button(
            buttons_frame,
            text="📥☁️ Export + Backup",
            command=self.start_export_with_backup
        )
        self.export_backup_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Backup only button
        self.backup_btn = ttk.Button(
            buttons_frame,
            text="☁️ Backup Only",
            command=self.start_backup_only
        )
        self.backup_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Stop button
        self.stop_btn = ttk.Button(
            buttons_frame,
            text="⏹️ Stop",
            command=self.stop_operation,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="📋 Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Progress bar
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Log area
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            height=20,
            font=("Consolas", 9),
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(
            bottom_frame,
            text="🔄 Refresh Stats",
            command=self.load_stats
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="📂 Open Export Folder",
            command=self.open_export_folder
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="🖥️ Open CLI",
            command=self.open_cli
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="❌ Exit",
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=5)
    
    def log(self, message, level="info"):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "info": "#d4d4d4",
            "success": "#4ec9b0",
            "warning": "#dcdcaa",
            "error": "#f48771",
            "header": "#569cd6"
        }
        
        color = colors.get(level, colors["info"])
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", level)
        
        # Configure tags
        self.log_text.tag_config("timestamp", foreground="#858585")
        self.log_text.tag_config(level, foreground=color)
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
        self.root.update()
    
    def load_stats(self):
        """Load and display statistics"""
        try:
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            
            if not db_path.exists():
                stats_msg = "No database found. Run an export first."
                self.stats_text.config(text=stats_msg)
                return
            
            # Get export stats
            export_stats = get_export_stats(str(db_path))
            total_messages = export_stats['total_messages']
            total_folders = export_stats['total_folders']
            
            # Get backup stats
            try:
                backup_stats = get_backup_stats(str(db_path))
                total_backups = backup_stats['total_backups']
                completed_backups = backup_stats['completed_backups']
                failed_backups = backup_stats['failed_backups']
                total_bytes = backup_stats['total_bytes_uploaded']
                total_gb = total_bytes / (1024**3)
                
                stats_msg = (
                    f"📨 Exported Messages: {total_messages:,}\n"
                    f"📁 Total Folders: {total_folders:,}\n"
                    f"☁️ Backed Up: {completed_backups:,} / {total_backups:,}\n"
                    f"❌ Failed: {failed_backups:,}\n"
                    f"💾 Total Uploaded: {total_gb:.2f} GB"
                )
            except:
                stats_msg = (
                    f"📨 Exported Messages: {total_messages:,}\n"
                    f"📁 Total Folders: {total_folders:,}\n"
                    f"☁️ Backup stats not available"
                )
            
            self.stats_text.config(text=stats_msg)
            
        except Exception as e:
            self.stats_text.config(text=f"Error loading stats: {e}")
    
    def set_buttons_state(self, running=False):
        """Enable/disable buttons based on operation state"""
        state = tk.DISABLED if running else tk.NORMAL
        stop_state = tk.NORMAL if running else tk.DISABLED
        
        self.export_btn.config(state=state)
        self.export_backup_btn.config(state=state)
        self.backup_btn.config(state=state)
        self.stop_btn.config(state=stop_state)
        
        if running:
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_var.set(0)
    
    def start_export(self):
        """Start export without backup"""
        self.backup_var.set(False)
        self._run_operation(self.export_operation)
    
    def start_export_with_backup(self):
        """Start export with backup"""
        self.backup_var.set(True)
        self._run_operation(self.export_operation)
    
    def start_backup_only(self):
        """Start backup only (no export)"""
        self._run_operation(self.backup_only_operation)
    
    def _run_operation(self, operation_func):
        """Run operation in a separate thread"""
        if self.is_running:
            messagebox.showwarning("Already Running", "An operation is already in progress!")
            return
        
        self.is_running = True
        self.set_buttons_state(running=True)
        self.log_text.delete(1.0, tk.END)
        
        # Run in thread to avoid blocking GUI
        self.current_thread = threading.Thread(target=operation_func, daemon=True)
        self.current_thread.start()
    
    def stop_operation(self):
        """Stop current operation"""
        if messagebox.askyesno("Stop Operation", "Are you sure you want to stop the current operation?"):
            self.log("⚠️ Stop requested by user. Cleaning up...", "warning")
            # The operation will check self.is_running flag
            self.is_running = False
    
    def export_operation(self):
        """Run export operation"""
        try:
            # Get parameters
            from_date_str = self.date_entry.get().strip()
            from_date = from_date_str if from_date_str else None
            force = self.force_var.get()
            backup = self.backup_var.get()
            keep_archive = self.keep_archive_var.get()
            
            self.log("="*60, "header")
            self.log("🚀 STARTING EXPORT", "header")
            self.log("="*60, "header")
            
            if from_date:
                self.log(f"📅 Export from: {from_date}", "info")
            if force:
                self.log("🔄 Force re-export enabled", "warning")
            if backup:
                self.log("☁️ Google Drive backup enabled", "info")
            
            # Initialize database
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            # Use OUTPUT_DIR for init_database (it expects directory, not file path)
            init_database(OUTPUT_DIR)
            
            # Pre-authenticate Google Drive if backup enabled
            backup_handler = None
            if backup:
                self.log("\n" + "="*60, "header")
                self.log("🔐 GOOGLE DRIVE PRE-AUTHENTICATION", "header")
                self.log("="*60, "header")
                self.log("Authenticating with Google Drive before starting export...", "info")
                
                try:
                    backup_handler = GoogleDriveBackup(
                        credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
                        token_file=GOOGLE_DRIVE_TOKEN_FILE
                    )
                    
                    if not backup_handler.authenticate():
                        self.log("❌ Google Drive authentication failed!", "error")
                        response = messagebox.askyesno(
                            "Authentication Failed",
                            "Google Drive authentication failed!\n\nContinue without backup?"
                        )
                        if not response:
                            self.log("Export cancelled by user", "warning")
                            return
                        backup_handler = None
                    else:
                        if not backup_handler.get_or_create_backup_folder():
                            self.log("⚠️ Could not access Google Drive backup folder!", "warning")
                            response = messagebox.askyesno(
                                "Backup Folder Issue",
                                "Could not access Google Drive backup folder!\n\nContinue without backup?"
                            )
                            if not response:
                                return
                            backup_handler = None
                        else:
                            self.log("✓ Google Drive authentication successful!", "success")
                except Exception as e:
                    self.log(f"❌ Error during Google Drive setup: {e}", "error")
                    backup_handler = None
            
            # Run export in asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def do_export():
                client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
                try:
                    await client.start(phone=PHONE)
                    self.log("✓ Connected to Telegram", "success")
                    
                    # Export messages
                    await export_saved_messages(
                        client,
                        str(db_path),
                        from_date=from_date,
                        force_reexport=force,
                        output_dir=OUTPUT_DIR
                    )
                    
                    self.log("✓ Export completed!", "success")
                    
                finally:
                    await client.disconnect()
            
            # Monkey-patch print to redirect to GUI
            original_print = print
            def gui_print(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                if message.strip():
                    # Detect message type
                    if "✓" in message or "Success" in message:
                        level = "success"
                    elif "❌" in message or "Error" in message or "Failed" in message:
                        level = "error"
                    elif "⚠️" in message or "Warning" in message:
                        level = "warning"
                    elif "=" in message[:10]:
                        level = "header"
                    else:
                        level = "info"
                    self.log(message, level)
            
            import builtins
            builtins.print = gui_print
            
            try:
                loop.run_until_complete(do_export())
            finally:
                builtins.print = original_print
            
            # Backup if enabled
            if backup_handler:
                self.log("\n" + "="*60, "header")
                self.log("☁️ BACKING UP TO GOOGLE DRIVE", "header")
                self.log("="*60, "header")
                
                cleanup = not keep_archive
                stats = backup_handler.backup_individual_folders(
                    OUTPUT_DIR,
                    str(db_path),
                    cleanup_after_upload=cleanup
                )
                
                self.log("\n" + "="*60, "header")
                self.log("📊 BACKUP SUMMARY", "header")
                self.log("="*60, "header")
                self.log(f"✓ Successfully uploaded: {stats['success']}", "success")
                self.log(f"❌ Failed: {stats['failed']}", "error" if stats['failed'] > 0 else "info")
                self.log(f"⏭️ Skipped: {stats['skipped']}", "info")
                
                if 'database_backed_up' in stats:
                    if stats['database_backed_up']:
                        self.log("📊 Database backup: ✓ Success", "success")
                    else:
                        self.log("📊 Database backup: ❌ Failed", "error")
            
            self.log("\n✅ ALL OPERATIONS COMPLETED!", "success")
            messagebox.showinfo("Success", "Export completed successfully!")
            
        except Exception as e:
            self.log(f"\n❌ Error: {e}", "error")
            messagebox.showerror("Error", f"An error occurred:\n\n{e}")
        
        finally:
            self.is_running = False
            self.set_buttons_state(running=False)
            self.load_stats()
    
    def backup_only_operation(self):
        """Run backup only operation"""
        try:
            keep_archive = self.keep_archive_var.get()
            
            self.log("="*60, "header")
            self.log("☁️ BACKUP ONLY MODE", "header")
            self.log("="*60, "header")
            
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            if not db_path.exists():
                self.log("❌ No database found. Run export first!", "error")
                messagebox.showerror("Error", "No export database found!\n\nRun an export first.")
                return
            
            # Monkey-patch print
            original_print = print
            def gui_print(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                if message.strip():
                    if "✓" in message or "Success" in message:
                        level = "success"
                    elif "❌" in message or "Error" in message:
                        level = "error"
                    elif "⚠️" in message or "Warning" in message:
                        level = "warning"
                    elif "=" in message[:10]:
                        level = "header"
                    else:
                        level = "info"
                    self.log(message, level)
            
            import builtins
            builtins.print = gui_print
            
            try:
                backup_handler = GoogleDriveBackup(
                    credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
                    token_file=GOOGLE_DRIVE_TOKEN_FILE
                )
                
                if not backup_handler.authenticate():
                    self.log("❌ Google Drive authentication failed!", "error")
                    messagebox.showerror("Error", "Google Drive authentication failed!")
                    return
                
                if not backup_handler.get_or_create_backup_folder():
                    self.log("❌ Could not access backup folder!", "error")
                    messagebox.showerror("Error", "Could not access Google Drive backup folder!")
                    return
                
                cleanup = not keep_archive
                stats = backup_handler.backup_individual_folders(
                    OUTPUT_DIR,
                    str(db_path),
                    cleanup_after_upload=cleanup
                )
                
                self.log("\n" + "="*60, "header")
                self.log("📊 BACKUP SUMMARY", "header")
                self.log("="*60, "header")
                self.log(f"✓ Successfully uploaded: {stats['success']}", "success")
                self.log(f"❌ Failed: {stats['failed']}", "error" if stats['failed'] > 0 else "info")
                self.log(f"⏭️ Skipped: {stats['skipped']}", "info")
                
                if 'database_backed_up' in stats:
                    if stats['database_backed_up']:
                        self.log("📊 Database backup: ✓ Success", "success")
                    else:
                        self.log("📊 Database backup: ❌ Failed", "error")
                
                self.log("\n✅ BACKUP COMPLETED!", "success")
                messagebox.showinfo("Success", "Backup completed successfully!")
                
            finally:
                builtins.print = original_print
        
        except Exception as e:
            self.log(f"\n❌ Error: {e}", "error")
            messagebox.showerror("Error", f"An error occurred:\n\n{e}")
        
        finally:
            self.is_running = False
            self.set_buttons_state(running=False)
            self.load_stats()
    
    def open_export_folder(self):
        """Open export folder in file explorer"""
        import os
        export_path = Path(OUTPUT_DIR)
        if export_path.exists():
            os.startfile(export_path)
        else:
            messagebox.showwarning("Not Found", "Export folder doesn't exist yet.")
    
    def open_cli(self):
        """Open command prompt in the current directory"""
        import os
        import subprocess
        
        response = messagebox.askyesno(
            "Open CLI",
            "This will open a command prompt where you can use CLI commands.\n\n"
            "Available commands:\n"
            "• py main.py --help\n"
            "• py main.py --stats\n"
            "• py main.py --backup-only\n\n"
            "Continue?"
        )
        
        if response:
            subprocess.Popen(['cmd.exe', '/K', 'cd', '/d', str(Path.cwd())])


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = ExporterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
