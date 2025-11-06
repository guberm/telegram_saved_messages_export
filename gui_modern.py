"""
Modern GUI for Telegram Saved Messages Exporter
Beautiful interface with ttkbootstrap
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledText
import threading
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

# Import existing modules
from config import *
from database import init_database, get_export_stats, get_backup_stats
from exporter import export_saved_messages
from google_drive_backup import GoogleDriveBackup
from telethon import TelegramClient


class ModernExporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Saved Messages Exporter")
        self.root.geometry("1000x750")
        
        # Variables
        self.is_running = False
        self.current_thread = None
        
        # Setup UI
        self.setup_ui()
        
        # Load initial stats
        self.load_stats()
        
        # Show welcome toast
        self.show_toast("Welcome!", "Telegram Exporter Ready", icon="✨")
    
    def setup_ui(self):
        """Create modern user interface"""
        
        # Main container with padding
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill=BOTH, expand=YES)
        
        # ===== HEADER =====
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=X, pady=(0, 15))
        
        # Title with icon
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=LEFT)
        
        ttk.Label(
            title_frame,
            text="📱 Telegram Saved Messages Exporter",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        # Version badge
        ttk.Label(
            title_frame,
            text="v2.0",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(10, 0))
        
        # Status indicator
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side=RIGHT)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="● Ready",
            font=("Segoe UI", 10),
            bootstyle="success"
        )
        self.status_label.pack()
        
        # ===== STATS CARDS =====
        stats_container = ttk.Frame(main_container)
        stats_container.pack(fill=X, pady=(0, 15))
        
        # Create 4 stat cards
        self.create_stat_card(stats_container, "📨 Messages", "0", "messages_label", 0)
        self.create_stat_card(stats_container, "📁 Folders", "0", "folders_label", 1)
        self.create_stat_card(stats_container, "☁️ Backed Up", "0%", "backup_label", 2)
        self.create_stat_card(stats_container, "💾 Size", "0 GB", "size_label", 3)
        
        # ===== OPTIONS PANEL =====
        options_frame = ttk.Labelframe(
            main_container,
            text="⚙️  Export Options",
            padding=15,
            bootstyle="info"
        )
        options_frame.pack(fill=X, pady=(0, 15))
        
        # Date filter row
        date_row = ttk.Frame(options_frame)
        date_row.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            date_row,
            text="📅 From Date:",
            font=("Segoe UI", 10)
        ).pack(side=LEFT, padx=(0, 10))
        
        self.date_entry = ttk.Entry(
            date_row,
            width=15,
            font=("Segoe UI", 10)
        )
        self.date_entry.pack(side=LEFT, padx=(0, 10))
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.bind("<FocusIn>", lambda e: self.date_entry.delete(0, "end") if self.date_entry.get() == "YYYY-MM-DD" else None)
        
        ttk.Label(
            date_row,
            text="(leave empty for all messages)",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side=LEFT)
        
        # Checkboxes with icons
        self.force_var = ttk.BooleanVar(value=False)
        self.backup_var = ttk.BooleanVar(value=GOOGLE_DRIVE_BACKUP_ENABLED)
        self.keep_archive_var = ttk.BooleanVar(value=GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE)
        
        check_frame = ttk.Frame(options_frame)
        check_frame.pack(fill=X)
        
        ttk.Checkbutton(
            check_frame,
            text="🔄 Force re-export (slower, re-exports everything)",
            variable=self.force_var,
            bootstyle="warning-round-toggle"
        ).pack(anchor=W, pady=3)
        
        ttk.Checkbutton(
            check_frame,
            text="☁️ Backup to Google Drive after export",
            variable=self.backup_var,
            bootstyle="info-round-toggle"
        ).pack(anchor=W, pady=3)
        
        ttk.Checkbutton(
            check_frame,
            text="💾 Keep local files after backup (uses more disk space)",
            variable=self.keep_archive_var,
            bootstyle="secondary-round-toggle"
        ).pack(anchor=W, pady=3)
        
        # ===== ACTION BUTTONS =====
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=X, pady=(0, 15))
        
        # Main action buttons (larger)
        action_row1 = ttk.Frame(button_frame)
        action_row1.pack(fill=X, pady=(0, 10))
        
        self.export_btn = ttk.Button(
            action_row1,
            text="📥 Export Messages",
            command=self.start_export,
            bootstyle="success",
            width=25
        )
        self.export_btn.pack(side=LEFT, padx=(0, 10), ipady=10)
        
        self.export_backup_btn = ttk.Button(
            action_row1,
            text="📥☁️ Export + Backup",
            command=self.start_export_with_backup,
            bootstyle="primary",
            width=25
        )
        self.export_backup_btn.pack(side=LEFT, padx=(0, 10), ipady=10)
        
        self.backup_btn = ttk.Button(
            action_row1,
            text="☁️ Backup Only",
            command=self.start_backup_only,
            bootstyle="info",
            width=25
        )
        self.backup_btn.pack(side=LEFT, ipady=10)
        
        # Secondary buttons (smaller)
        action_row2 = ttk.Frame(button_frame)
        action_row2.pack(fill=X)
        
        self.stop_btn = ttk.Button(
            action_row2,
            text="⏹️ Stop",
            command=self.stop_operation,
            bootstyle="danger",
            state=DISABLED,
            width=15
        )
        self.stop_btn.pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            action_row2,
            text="🔄 Refresh",
            command=self.load_stats,
            bootstyle="secondary-outline",
            width=15
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            action_row2,
            text="📂 Open Folder",
            command=self.open_export_folder,
            bootstyle="secondary-outline",
            width=15
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            action_row2,
            text="🖥️ CLI",
            command=self.open_cli,
            bootstyle="secondary-outline",
            width=15
        ).pack(side=LEFT)
        
        # ===== PROGRESS SECTION =====
        progress_frame = ttk.Labelframe(
            main_container,
            text="📊  Progress & Logs",
            padding=15,
            bootstyle="primary"
        )
        progress_frame.pack(fill=BOTH, expand=YES)
        
        # Progress bar
        progress_container = ttk.Frame(progress_frame)
        progress_container.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            progress_container,
            text="Status:",
            font=("Segoe UI", 10)
        ).pack(side=LEFT, padx=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_container,
            mode='indeterminate',
            bootstyle="success-striped"
        )
        self.progress_bar.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        self.progress_label = ttk.Label(
            progress_container,
            text="Idle",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        self.progress_label.pack(side=LEFT)
        
        # Log area with custom styling
        self.log_text = ScrolledText(
            progress_frame,
            autohide=True,
            height=15,
            font=("Consolas", 10),
            wrap=WORD
        )
        self.log_text.pack(fill=BOTH, expand=YES)
        
        # Configure log text tags for colors
        self.log_text.text.tag_config("timestamp", foreground="#6c757d")
        self.log_text.text.tag_config("info", foreground="#0d6efd")
        self.log_text.text.tag_config("success", foreground="#198754")
        self.log_text.text.tag_config("warning", foreground="#ffc107")
        self.log_text.text.tag_config("error", foreground="#dc3545")
        self.log_text.text.tag_config("header", foreground="#6610f2", font=("Consolas", 10, "bold"))
        
        # Initial welcome message
        self.log("="*80, "header")
        self.log("Welcome to Telegram Saved Messages Exporter!", "header")
        self.log("="*80, "header")
        self.log("Ready to export your messages. Choose an option above to get started.", "info")
    
    def create_stat_card(self, parent, title, value, label_name, col):
        """Create a statistics card"""
        card = ttk.Frame(parent, bootstyle="light")
        card.grid(row=0, column=col, padx=5, sticky="ew")
        parent.columnconfigure(col, weight=1)
        
        # Card content with padding
        content = ttk.Frame(card, padding=15)
        content.pack(fill=BOTH, expand=YES)
        
        # Title
        ttk.Label(
            content,
            text=title,
            font=("Segoe UI", 11),
            bootstyle="secondary"
        ).pack(anchor=W)
        
        # Value (will be updated)
        value_label = ttk.Label(
            content,
            text=value,
            font=("Segoe UI", 24, "bold"),
            bootstyle="primary"
        )
        value_label.pack(anchor=W, pady=(5, 0))
        
        # Store reference
        setattr(self, label_name, value_label)
    
    def show_toast(self, title, message, icon="ℹ️", duration=3000):
        """Show a toast notification"""
        toast = ToastNotification(
            title=f"{icon} {title}",
            message=message,
            duration=duration,
            bootstyle="info"
        )
        toast.show_toast()
    
    def log(self, message, level="info"):
        """Add message to log area with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Detect emoji/icon for visual separation
        if level == "header":
            self.log_text.text.insert("end", f"\n{message}\n", level)
        else:
            self.log_text.text.insert("end", f"[{timestamp}] ", "timestamp")
            self.log_text.text.insert("end", f"{message}\n", level)
        
        # Auto-scroll to bottom
        self.log_text.text.see("end")
        self.root.update()
    
    def update_status(self, text, style="success"):
        """Update status indicator"""
        symbols = {
            "success": "●",
            "info": "●",
            "warning": "●",
            "error": "●",
            "working": "◉"
        }
        symbol = symbols.get(style, "●")
        self.status_label.config(text=f"{symbol} {text}", bootstyle=style)
    
    def load_stats(self):
        """Load and display statistics in cards"""
        try:
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            
            if not db_path.exists():
                self.messages_label.config(text="0")
                self.folders_label.config(text="0")
                self.backup_label.config(text="N/A")
                self.size_label.config(text="0 GB")
                return
            
            # Get export stats
            export_stats = get_export_stats(str(db_path))
            total_messages = export_stats['total_messages']
            total_folders = export_stats['total_folders']
            
            self.messages_label.config(text=f"{total_messages:,}")
            self.folders_label.config(text=f"{total_folders:,}")
            
            # Get backup stats
            try:
                backup_stats = get_backup_stats(str(db_path))
                total_backups = backup_stats['total_backups']
                completed_backups = backup_stats['completed_backups']
                total_bytes = backup_stats['total_bytes_uploaded']
                total_gb = total_bytes / (1024**3)
                
                if total_backups > 0:
                    percent = int((completed_backups / total_backups) * 100)
                    self.backup_label.config(text=f"{percent}%")
                else:
                    self.backup_label.config(text="0%")
                
                self.size_label.config(text=f"{total_gb:.2f} GB")
            except:
                self.backup_label.config(text="N/A")
                self.size_label.config(text="N/A")
            
            self.show_toast("Stats Updated", f"Found {total_messages:,} messages", "📊")
            
        except Exception as e:
            self.log(f"Error loading stats: {e}", "error")
            self.backup_label.config(text="Error")
    
    def set_buttons_state(self, running=False):
        """Enable/disable buttons based on operation state"""
        state = DISABLED if running else NORMAL
        stop_state = NORMAL if running else DISABLED
        
        self.export_btn.config(state=state)
        self.export_backup_btn.config(state=state)
        self.backup_btn.config(state=state)
        self.stop_btn.config(state=stop_state)
        
        if running:
            self.progress_bar.start(10)
            self.update_status("Working...", "working")
            self.progress_label.config(text="Processing...")
        else:
            self.progress_bar.stop()
            self.update_status("Ready", "success")
            self.progress_label.config(text="Idle")
    
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
            self.show_toast("Already Running", "Please wait for current operation to finish", "⚠️")
            return
        
        self.is_running = True
        self.set_buttons_state(running=True)
        
        # Clear log
        self.log_text.text.delete(1.0, "end")
        
        # Run in thread
        self.current_thread = threading.Thread(target=operation_func, daemon=True)
        self.current_thread.start()
    
    def stop_operation(self):
        """Stop current operation"""
        if messagebox.askyesno("Stop Operation", "Are you sure you want to stop?"):
            self.log("⚠️ Stop requested. Finishing current task...", "warning")
            self.update_status("Stopping...", "warning")
            self.is_running = False
    
    def export_operation(self):
        """Run export operation"""
        try:
            from_date_str = self.date_entry.get().strip()
            if from_date_str == "YYYY-MM-DD":
                from_date_str = ""
            from_date = from_date_str if from_date_str else None
            force = self.force_var.get()
            backup = self.backup_var.get()
            keep_archive = self.keep_archive_var.get()
            
            self.log("="*80, "header")
            self.log("🚀 STARTING EXPORT OPERATION", "header")
            self.log("="*80, "header")
            
            if from_date:
                self.log(f"📅 Export from: {from_date}", "info")
            if force:
                self.log("🔄 Force re-export enabled", "warning")
            if backup:
                self.log("☁️ Google Drive backup enabled", "info")
            
            # Initialize database
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            init_database(OUTPUT_DIR)
            
            # Pre-authenticate Google Drive
            backup_handler = None
            if backup:
                self.log("\n" + "="*80, "header")
                self.log("🔐 GOOGLE DRIVE AUTHENTICATION", "header")
                self.log("="*80, "header")
                self.progress_label.config(text="Authenticating...")
                
                try:
                    backup_handler = GoogleDriveBackup(
                        credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
                        token_file=GOOGLE_DRIVE_TOKEN_FILE
                    )
                    
                    if not backup_handler.authenticate():
                        self.log("❌ Authentication failed!", "error")
                        response = messagebox.askyesno(
                            "Authentication Failed",
                            "Continue without backup?"
                        )
                        if not response:
                            return
                        backup_handler = None
                    else:
                        if backup_handler.get_or_create_backup_folder():
                            self.log("✓ Google Drive ready!", "success")
                        else:
                            backup_handler = None
                except Exception as e:
                    self.log(f"❌ Google Drive error: {e}", "error")
                    backup_handler = None
            
            # Export messages
            self.progress_label.config(text="Exporting messages...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def do_export():
                client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
                try:
                    await client.start(phone=PHONE)
                    self.log("✓ Connected to Telegram", "success")
                    
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
            
            # Redirect print to log
            original_print = print
            def gui_print(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                if message.strip():
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
                self.log("\n" + "="*80, "header")
                self.log("☁️ STARTING BACKUP", "header")
                self.log("="*80, "header")
                self.progress_label.config(text="Backing up to Google Drive...")
                
                cleanup = not keep_archive
                stats = backup_handler.backup_individual_folders(
                    OUTPUT_DIR,
                    str(db_path),
                    cleanup_after_upload=cleanup
                )
                
                self.log("\n" + "="*80, "header")
                self.log("📊 BACKUP SUMMARY", "header")
                self.log("="*80, "header")
                self.log(f"✓ Uploaded: {stats['success']}", "success")
                self.log(f"❌ Failed: {stats['failed']}", "error" if stats['failed'] > 0 else "info")
                self.log(f"⏭️ Skipped: {stats['skipped']}", "info")
                
                if stats.get('database_backed_up'):
                    self.log("📊 Database: ✓ Backed up", "success")
            
            self.log("\n✅ ALL OPERATIONS COMPLETED!", "success")
            self.show_toast("Success!", "Export completed successfully", "✅", 5000)
            
        except Exception as e:
            self.log(f"\n❌ Error: {e}", "error")
            self.show_toast("Error", str(e), "❌", 5000)
        
        finally:
            self.is_running = False
            self.set_buttons_state(running=False)
            self.load_stats()
    
    def backup_only_operation(self):
        """Backup only operation"""
        try:
            keep_archive = self.keep_archive_var.get()
            
            self.log("="*80, "header")
            self.log("☁️ BACKUP ONLY MODE", "header")
            self.log("="*80, "header")
            self.progress_label.config(text="Backing up...")
            
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            if not db_path.exists():
                self.log("❌ No database found!", "error")
                self.show_toast("Error", "Run export first!", "❌")
                return
            
            # Redirect print
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
                    self.log("❌ Authentication failed!", "error")
                    return
                
                if not backup_handler.get_or_create_backup_folder():
                    self.log("❌ Cannot access backup folder!", "error")
                    return
                
                cleanup = not keep_archive
                stats = backup_handler.backup_individual_folders(
                    OUTPUT_DIR,
                    str(db_path),
                    cleanup_after_upload=cleanup
                )
                
                self.log("\n" + "="*80, "header")
                self.log("📊 BACKUP SUMMARY", "header")
                self.log("="*80, "header")
                self.log(f"✓ Uploaded: {stats['success']}", "success")
                self.log(f"❌ Failed: {stats['failed']}", "error" if stats['failed'] > 0 else "info")
                
                if stats.get('database_backed_up'):
                    self.log("📊 Database: ✓ Backed up", "success")
                
                self.show_toast("Backup Complete!", f"Uploaded {stats['success']} folders", "✅", 5000)
                
            finally:
                builtins.print = original_print
        
        except Exception as e:
            self.log(f"\n❌ Error: {e}", "error")
            self.show_toast("Error", str(e), "❌", 5000)
        
        finally:
            self.is_running = False
            self.set_buttons_state(running=False)
            self.load_stats()
    
    def open_export_folder(self):
        """Open export folder"""
        import os
        export_path = Path(OUTPUT_DIR)
        if export_path.exists():
            os.startfile(export_path)
            self.show_toast("Opening Folder", "Export folder opened in File Explorer", "📂")
        else:
            self.show_toast("Not Found", "Export folder doesn't exist yet", "⚠️")
    
    def open_cli(self):
        """Open CLI"""
        import subprocess
        response = messagebox.askyesno(
            "Open Command Line",
            "Open command prompt for advanced CLI commands?\n\n"
            "Available commands:\n"
            "• py main.py --help\n"
            "• py main.py --stats\n"
            "• py main.py --backup-only"
        )
        if response:
            subprocess.Popen(['cmd.exe', '/K', 'cd', '/d', str(Path.cwd())])
            self.show_toast("CLI Opened", "Command prompt ready", "🖥️")


def main():
    """Main entry point"""
    # Use modern theme
    app = ttk.Window(
        title="Telegram Saved Messages Exporter",
        themename="darkly",  # Options: cosmo, flatly, litera, minty, lumen, sandstone, yeti, pulse, united, morph, journal, darkly, superhero, solar, cyborg, vapor, simplex, cerculean
        size=(1000, 750),
        resizable=(True, True)
    )
    
    gui = ModernExporterGUI(app)
    app.mainloop()


if __name__ == "__main__":
    main()
