"""
Ultra Modern GUI for Telegram Saved Messages Exporter
No CLI logs - Pure visual interface
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification
import threading
import asyncio
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
import queue

# Import existing modules
from config import *
from database import init_database, get_export_stats, get_backup_stats
from exporter import export_saved_messages
from google_drive_backup import GoogleDriveBackup
from telethon import TelegramClient


class VisualExporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Saved Messages Exporter")
        self.root.geometry("900x700")
        
        # Variables
        self.is_running = False
        self.current_thread = None
        self.message_queue = queue.Queue()
        # Cancellation event for cooperative stopping
        self.cancel_event = threading.Event()
        
        # Stats tracking
        self.current_progress = 0
        self.total_items = 0
        self.current_item_name = ""
        
        # Setup UI
        self.setup_ui()
        
        # Load initial stats
        self.load_stats()
        # Init tooltips
        self._init_tooltips()
        # Start activity window auto-refresh loop
        self.last_activity_render_count = 0
        self.schedule_activity_refresh()
        
        # Start message processor
        self.process_messages()
        
        # Show welcome
        self.show_toast("Welcome! 👋", "Ready to export your Telegram messages")
    
    def setup_ui(self):
        """Create pure visual interface"""
        
        # Main container
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=BOTH, expand=YES)
        
        # ===== HEADER =====
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=LEFT)
        
        ttk.Label(
            title_frame,
            text="📱 Telegram Messages Exporter",
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)
        
        ttk.Label(
            title_frame,
            text="v3.0",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(10, 0))
        
        # Status indicator
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side=RIGHT)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="● Idle",
            font=("Segoe UI", 11, "bold"),
            bootstyle="success"
        )
        self.status_label.pack()
        
        # ===== STATS CARDS =====
        stats_container = ttk.Frame(main_container)
        stats_container.pack(fill=X, pady=(0, 20))
        
        self.create_stat_card(stats_container, "📨", "Messages", "0", "messages_label", 0)
        self.create_stat_card(stats_container, "📁", "Folders", "0", "folders_label", 1)
        self.create_stat_card(stats_container, "☁️", "Backed Up", "0%", "backup_label", 2)
        self.create_stat_card(stats_container, "💾", "Total Size", "0 GB", "size_label", 3)
        
        # ===== OPTIONS =====
        options_frame = ttk.Labelframe(
            main_container,
            text="⚙️  Export Settings",
            padding=20,
            bootstyle="info"
        )
        options_frame.pack(fill=X, pady=(0, 20))
        
        # Date filter
        date_row = ttk.Frame(options_frame)
        date_row.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            date_row,
            text="📅",
            font=("Segoe UI", 16)
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(
            date_row,
            text="From Date:",
            font=("Segoe UI", 11)
        ).pack(side=LEFT, padx=(0, 10))
        
        self.date_entry = ttk.Entry(date_row, width=15, font=("Segoe UI", 11))
        self.date_entry.pack(side=LEFT, padx=(0, 10))
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.bind("<FocusIn>", lambda e: self.date_entry.delete(0, "end") if self.date_entry.get() == "YYYY-MM-DD" else None)
        
        ttk.Label(
            date_row,
            text="(empty = all messages)",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        ).pack(side=LEFT)
        
        # Options with icons
        self.force_var = ttk.BooleanVar(value=False)
        self.backup_var = ttk.BooleanVar(value=GOOGLE_DRIVE_BACKUP_ENABLED)
        self.keep_archive_var = ttk.BooleanVar(value=GOOGLE_DRIVE_KEEP_LOCAL_ARCHIVE)
        
        opt_frame = ttk.Frame(options_frame)
        opt_frame.pack(fill=X)
        
        ttk.Checkbutton(
            opt_frame,
            text="🔄 Force re-export (slower)",
            variable=self.force_var,
            bootstyle="warning-round-toggle"
        ).pack(anchor=W, pady=5)
        
        ttk.Checkbutton(
            opt_frame,
            text="☁️ Backup to Google Drive",
            variable=self.backup_var,
            bootstyle="info-round-toggle"
        ).pack(anchor=W, pady=5)
        
        ttk.Checkbutton(
            opt_frame,
            text="💾 Keep local files (uses more space)",
            variable=self.keep_archive_var,
            bootstyle="secondary-round-toggle"
        ).pack(anchor=W, pady=5)
        
        # ===== ACTION BUTTONS =====
        button_container = ttk.Frame(main_container)
        button_container.pack(fill=X, pady=(0, 20))
        
        # Main buttons
        btn_row1 = ttk.Frame(button_container)
        btn_row1.pack(fill=X, pady=(0, 10))
        
        self.export_btn = ttk.Button(
            btn_row1,
            text="📥 Export Messages",
            command=self.start_export,
            bootstyle="success",
            width=28
        )
        self.export_btn.pack(side=LEFT, padx=(0, 10), ipady=12)
        
        self.export_backup_btn = ttk.Button(
            btn_row1,
            text="📥☁️ Export + Backup",
            command=self.start_export_with_backup,
            bootstyle="primary",
            width=28
        )
        self.export_backup_btn.pack(side=LEFT, padx=(0, 10), ipady=12)
        
        self.backup_btn = ttk.Button(
            btn_row1,
            text="☁️ Backup Only",
            command=self.start_backup_only,
            bootstyle="info",
            width=28
        )
        self.backup_btn.pack(side=LEFT, ipady=12)
        
        # Utility buttons
        btn_row2 = ttk.Frame(button_container)
        btn_row2.pack(fill=X)
        
        self.stop_btn = ttk.Button(
            btn_row2,
            text="⏹️ Stop",
            command=self.stop_operation,
            bootstyle="danger",
            state=DISABLED,
            width=18
        )
        self.stop_btn.pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_row2,
            text="🔄 Refresh Stats",
            command=self.load_stats,
            bootstyle="secondary-outline",
            width=18
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_row2,
            text="📂 Open Folder",
            command=self.open_export_folder,
            bootstyle="secondary-outline",
            width=18
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_row2,
            text="📋 View Logs",
            command=self.open_log_window,
            bootstyle="info-outline",
            width=18
        ).pack(side=LEFT)

        ttk.Button(
            btn_row2,
            text="🕒 Recent Activity",
            command=self.open_activity_window,
            bootstyle="warning-outline",
            width=18
        ).pack(side=LEFT, padx=(5,0))
        
        # ===== VISUAL PROGRESS AREA (scrollable) =====
        progress_frame = ttk.Labelframe(
            main_container,
            text="📊  Current Activity",
            padding=5,
            bootstyle="primary"
        )
        progress_frame.pack(fill=BOTH, expand=YES)

        scroll_container = ttk.Frame(progress_frame)
        scroll_container.pack(fill=BOTH, expand=YES)
        self.activity_canvas_main = tk.Canvas(scroll_container, highlightthickness=0)
        self.activity_canvas_main.pack(side=LEFT, fill=BOTH, expand=YES)
        main_scrollbar = ttk.Scrollbar(scroll_container, orient=VERTICAL, command=self.activity_canvas_main.yview)
        main_scrollbar.pack(side=RIGHT, fill=Y)
        self.activity_canvas_main.configure(yscrollcommand=main_scrollbar.set)
        self.current_activity_content = ttk.Frame(self.activity_canvas_main)
        self.canvas_window = self.activity_canvas_main.create_window((0,0), window=self.current_activity_content, anchor=NW, width=self.activity_canvas_main.winfo_width())
        
        def _update_canvas_width(event):
            # Update canvas width and window width to match
            canvas_width = event.width
            self.activity_canvas_main.itemconfig(self.canvas_window, width=canvas_width)
            self.activity_canvas_main.configure(scrollregion=self.activity_canvas_main.bbox("all"))
        
        self.activity_canvas_main.bind("<Configure>", _update_canvas_width)
        
        self.current_activity_content.bind(
            "<Configure>",
            lambda e: self.activity_canvas_main.configure(scrollregion=self.activity_canvas_main.bbox("all"))
        )
        def _on_main_mousewheel(event):
            self.activity_canvas_main.yview_scroll(int(-1*(event.delta/120)), "units")
        self.activity_canvas_main.bind_all('<MouseWheel>', _on_main_mousewheel)

        # Current operation label
        self.operation_label = ttk.Label(
            self.current_activity_content,
            text="Waiting to start...",
            font=("Segoe UI", 13),
            foreground="#e9ecef"  # Light text for visibility
        )
        self.operation_label.pack(pady=(0, 15))

        # Main progress bar
        progress_container = ttk.Frame(self.current_activity_content)
        progress_container.pack(fill=X, pady=(0, 10), padx=10)
        
        ttk.Label(
            progress_container,
            text="Overall Progress:",
            font=("Segoe UI", 10, "bold"),
            foreground="#f8f9fa"
        ).pack(anchor=W, pady=(0, 5))
        
        # Calmer progress bar style (no stripes, no animation)
        self.main_progress = ttk.Progressbar(
            progress_container,
            mode='determinate',
            bootstyle="success"
        )
        self.main_progress.pack(fill=X, expand=YES, pady=(0, 5))
        
        self.progress_text = ttk.Label(
            progress_container,
            text="0 / 0 (0%)",
            font=("Segoe UI", 11),
            foreground="#ced4da"  # Light gray for visibility
        )
        self.progress_text.pack()
        
        # Secondary progress bar (for archive/upload operations)
        secondary_container = ttk.Frame(self.current_activity_content)
        secondary_container.pack(fill=X, pady=(0, 20), padx=10)
        
        ttk.Label(
            secondary_container,
            text="Current Operation:",
            font=("Segoe UI", 10, "bold"),
            foreground="#f8f9fa"
        ).pack(anchor=W, pady=(0, 5))
        
        self.secondary_progress = ttk.Progressbar(
            secondary_container,
            mode='determinate',
            bootstyle="info"
        )
        self.secondary_progress.pack(fill=X, expand=YES, pady=(0, 5))
        
        self.secondary_progress_text = ttk.Label(
            secondary_container,
            text="Ready",
            font=("Segoe UI", 10),
            foreground="#ced4da"
        )
        self.secondary_progress_text.pack()

        # ===== LIVE METRICS PANEL (always visible) =====
        stats_panel = ttk.Labelframe(
            self.current_activity_content,
            text="Live Stats",
            padding=10,
            bootstyle="secondary"
        )
        stats_panel.pack(fill=X, pady=(0, 15))
        metrics_frame = ttk.Frame(stats_panel)
        metrics_frame.pack(fill=X)

        # Metrics dictionary to hold dynamic values
        self.metrics = {
            'total_messages': 0,
            'skipped_messages': 0,
            'exported_messages': 0,
            'current_message_id': '',
            'avg_time_per_msg': 0.0,
            'elapsed_time': 0.0,
            'eta_minutes': 0.0,
            'current_retries': 0,
            'connection_status': 'Idle',
            'last_error': '',
            'media_file': '',
            'media_percent': 0.0,
            'media_speed': '',
            'media_eta': '',
            'archive_file': '',
            'archive_percent': 0.0,
            'archive_speed': '',
            'archive_eta': ''
        }

        # Layout: two columns of labels
        def make_metric_row(row, label_text, attr):
            label = ttk.Label(metrics_frame, text=label_text, font=("Segoe UI", 9, "bold"))
            label.grid(row=row, column=0, sticky=W, padx=(2,4), pady=2)
            lbl = ttk.Label(metrics_frame, text="-", font=("Segoe UI", 9))
            lbl.grid(row=row, column=1, sticky=W, padx=(2,4), pady=2)
            setattr(self, f"metric_{attr}", lbl)

        make_metric_row(0, "Messages (exported/total/skipped):", "messages")
        make_metric_row(1, "Current Message ID:", "current_id")
        make_metric_row(2, "Avg Time / Msg:", "avg_time")
        make_metric_row(3, "Elapsed (min):", "elapsed")
        make_metric_row(4, "ETA (min):", "eta")
        make_metric_row(5, "Retries (current):", "retries")
        make_metric_row(6, "Connection Status:", "conn")
        make_metric_row(7, "Last Error:", "error")
        make_metric_row(8, "Media Download:", "media")
        make_metric_row(9, "Archive Progress:", "archive")

        for c in range(2):
            metrics_frame.columnconfigure(c, weight=1)

        def update_metrics_labels():
            # Compose combined strings
            self.metric_messages.config(text=f"{self.metrics['exported_messages']}/{self.metrics['total_messages']} (skipped {self.metrics['skipped_messages']})")
            self.metric_current_id.config(text=self.metrics['current_message_id'] or '-')
            self.metric_avg_time.config(text=f"{self.metrics['avg_time_per_msg']:.2f}s" if self.metrics['avg_time_per_msg'] else '-')
            self.metric_elapsed.config(text=f"{self.metrics['elapsed_time']/60:.1f}" if self.metrics['elapsed_time'] else '-')
            self.metric_eta.config(text=f"{self.metrics['eta_minutes']:.1f}" if self.metrics['eta_minutes'] else '-')
            self.metric_retries.config(text=str(self.metrics['current_retries']))
            self.metric_conn.config(text=self.metrics['connection_status'])
            self.metric_error.config(text=self.metrics['last_error'][:50] + ('…' if len(self.metrics['last_error'])>50 else ''))

            media_line = '-'
            if self.metrics['media_file']:
                media_line = f"{self.metrics['media_file'][:30]} {self.metrics['media_percent']:.1f}%"\
                    + (f" {self.metrics['media_speed']}" if self.metrics['media_speed'] else '')\
                    + (f" ETA {self.metrics['media_eta']}" if self.metrics['media_eta'] else '')
            self.metric_media.config(text=media_line)

            archive_line = '-'
            if self.metrics['archive_file']:
                archive_line = f"{self.metrics['archive_file'][:30]} {self.metrics['archive_percent']:.1f}%"\
                    + (f" {self.metrics['archive_speed']}" if self.metrics['archive_speed'] else '')\
                    + (f" ETA {self.metrics['archive_eta']}" if self.metrics['archive_eta'] else '')
            self.metric_archive.config(text=archive_line)

        self._update_metrics_labels = update_metrics_labels

        # No collapsing/animation; panel always shown

        
        # Current item
        item_frame = ttk.Frame(progress_frame)
        item_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            item_frame,
            text="Current:",
            font=("Segoe UI", 10, "bold"),
            foreground="#f8f9fa"  # Bright white text
        ).pack(side=LEFT, padx=(0, 10))
        
        self.current_item_label = ttk.Label(
            item_frame,
            text="None",
            font=("Segoe UI", 10),
            foreground="#4dabf7"  # Bright blue
        )
        self.current_item_label.pack(side=LEFT)
        
        # Activities now moved to separate window on demand
        self.activities_data = []  # store tuples (icon,title,description,status,timestamp)
        self.activity_window = None
        # Record initial activity (will show when window first opened)
        self.add_activity("✨", "Ready", "Application started successfully", "success")

        # Lock horizontal resizing only; allow vertical resizing freely
        self.root.update_idletasks()
        self.root.resizable(False, True)
        # Preserve current width; set comfortable height range
        fixed_w = self.root.winfo_width()
        self.root.minsize(fixed_w, 500)
        self.root.maxsize(fixed_w, 1600)
    
    def create_stat_card(self, parent, icon, title, value, label_name, col):
        """Create visual stat card"""
        card = ttk.Frame(parent, bootstyle="light")
        card.grid(row=0, column=col, padx=8, sticky="ew")
        parent.columnconfigure(col, weight=1)
        
        content = ttk.Frame(card, padding=20)
        content.pack(fill=BOTH, expand=YES)
        
        # Icon
        ttk.Label(
            content,
            text=icon,
            font=("Segoe UI", 32)
        ).pack(anchor=W)
        
        # Title
        ttk.Label(
            content,
            text=title,
            font=("Segoe UI", 10),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(5, 0))
        
        # Value
        value_label = ttk.Label(
            content,
            text=value,
            font=("Segoe UI", 22, "bold"),
            bootstyle="primary"
        )
        value_label.pack(anchor=W, pady=(5, 0))
        
        setattr(self, label_name, value_label)
    
    def add_activity(self, icon, title, description, status="info"):
        """Record an activity and update activity window if open"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activities_data.append((icon, title, description, status, timestamp))
        # Keep last 50
        if len(self.activities_data) > 50:
            self.activities_data = self.activities_data[-50:]

        # If window open, append new widget
        if self.activity_window and self.activity_window.winfo_exists():
            self._create_activity_widget(self.activity_items_frame, icon, title, description, status, timestamp)
            # Auto-scroll
            self.activity_canvas.update_idletasks()
            self.activity_canvas.yview_moveto(1.0)

    def _create_activity_widget(self, parent, icon, title, description, status, timestamp):
        colors = {
            "success": "#28a745",
            "error": "#ff4d4d",
            "warning": "#ffd700",
            "info": "#4dabf7"
        }
        color = colors.get(status, colors["info"])
        item = ttk.Frame(parent, bootstyle="dark")
        item.pack(fill=X, pady=5, padx=10)
        content = ttk.Frame(item, padding=10)
        content.pack(fill=X)
        ttk.Label(content, text=icon, font=("Segoe UI", 20)).pack(side=LEFT, padx=(0, 15))
        text_frame = ttk.Frame(content)
        text_frame.pack(side=LEFT, fill=X, expand=YES)
        ttk.Label(text_frame, text=title, font=("Segoe UI", 11, "bold"), foreground=color).pack(anchor=W)
        ttk.Label(text_frame, text=description, font=("Segoe UI", 9), foreground="#adb5bd").pack(anchor=W)
        ttk.Label(content, text=timestamp, font=("Segoe UI", 9), foreground="#6c757d").pack(side=RIGHT)

    def open_activity_window(self):
        if self.activity_window and self.activity_window.winfo_exists():
            self.activity_window.focus()
            return
        self.activity_window = tk.Toplevel(self.root)
        self.activity_window.title("Recent Activities")
        self.activity_window.geometry("600x500")
        container = ttk.Frame(self.activity_window, padding=10)
        container.pack(fill=BOTH, expand=YES)
        # Canvas + scrollbar
        self.activity_canvas = tk.Canvas(container, bg="#2b3e50", highlightthickness=0)
        self.activity_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=self.activity_canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.activity_canvas.configure(yscrollcommand=scrollbar.set)
        inner = ttk.Frame(self.activity_canvas)
        self.activity_canvas.create_window((0, 0), window=inner, anchor=NW)
        inner.bind("<Configure>", lambda e: self.activity_canvas.configure(scrollregion=self.activity_canvas.bbox("all")))
        self.activity_items_frame = inner
        # Populate
        for icon, title, desc, status, ts in self.activities_data:
            self._create_activity_widget(inner, icon, title, desc, status, ts)
        self.activity_canvas.update_idletasks()
        self.activity_canvas.yview_moveto(1.0)
        self.last_activity_render_count = len(self.activities_data)

    def schedule_activity_refresh(self):
        # Periodically ensure any new activities show in the open window
        if self.activity_window and self.activity_window.winfo_exists():
            current_count = len(self.activities_data)
            if current_count > self.last_activity_render_count:
                # Add missing ones
                for icon, title, desc, status, ts in self.activities_data[self.last_activity_render_count:]:
                    self._create_activity_widget(self.activity_items_frame, icon, title, desc, status, ts)
                self.activity_canvas.update_idletasks()
                self.activity_canvas.yview_moveto(1.0)
                self.last_activity_render_count = current_count
        # Reschedule
        self.root.after(2000, self.schedule_activity_refresh)

    
    def update_progress(self, current, total, item_name=""):
        """Update visual progress"""
        self.current_progress = current
        self.total_items = total
        self.current_item_name = item_name
        
        if total > 0:
            percent = int((current / total) * 100)
            self.main_progress['value'] = percent
            self.progress_text.config(text=f"{current} / {total} ({percent}%)")
        else:
            self.main_progress['value'] = 0
            self.progress_text.config(text="Starting...")
        
        if item_name:
            # Truncate long names
            display_name = item_name if len(item_name) <= 60 else item_name[:57] + "..."
            self.current_item_label.config(text=display_name)
        
        self.root.update()
    
    def update_secondary_progress(self, data):
        """Update secondary progress bar (for archives, downloads, etc) with optional speed/ETA"""
        if 'percent' in data:
            percent = data['percent']
            self.secondary_progress['value'] = percent
        elif 'current' in data and 'total' in data:
            current = data['current']
            total = data['total']
            percent = int((current / total) * 100) if total > 0 else 0
            self.secondary_progress['value'] = percent

        # Compose text
        if 'text' in data:
            text = data['text']
            speed = data.get('speed')
            eta = data.get('eta')
            if speed or eta:
                extra = []
                if speed:
                    extra.append(speed)
                if eta:
                    extra.append(f"ETA {eta}")
                text = f"{text} ({', '.join(extra)})"
            self.secondary_progress_text.config(text=text)

        self.root.update_idletasks()

        # Update tooltip text if available
        if hasattr(self, 'secondary_tooltip') and self.secondary_tooltip:
            self.secondary_tooltip.update_text(self.secondary_progress_text.cget('text'))

    class _Tooltip:
        def __init__(self, widget, text=""):
            self.widget = widget
            self.text = text
            self.tipwindow = None
            widget.bind("<Enter>", self.show)
            widget.bind("<Leave>", self.hide)
        def show(self, event=None):
            if self.tipwindow or not self.text:
                return
            import tkinter as tk
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=self.text, justify='left',
                             background="#343a40", foreground="#f8f9fa",
                             relief='solid', borderwidth=1,
                             font=("Segoe UI", 9))
            label.pack(ipadx=6, ipady=4)
        def hide(self, event=None):
            if self.tipwindow:
                self.tipwindow.destroy()
                self.tipwindow = None
        def update_text(self, text):
            self.text = text
            # If visible, refresh
            if self.tipwindow:
                self.hide()
                self.show()

    def _init_tooltips(self):
        # Attach tooltip to secondary progress text label
        self.secondary_tooltip = self._Tooltip(self.secondary_progress_text, self.secondary_progress_text.cget('text'))

    
    def show_toast(self, title, message, duration=3000):
        """Show toast notification"""
        toast = ToastNotification(
            title=title,
            message=message,
            duration=duration,
            bootstyle="info"
        )
        toast.show_toast()
    
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
        """Load statistics"""
        try:
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            
            if not db_path.exists():
                self.messages_label.config(text="0")
                self.folders_label.config(text="0")
                self.backup_label.config(text="0%")
                self.size_label.config(text="0 GB")
                return
            
            export_stats = get_export_stats(str(db_path))
            total_messages = export_stats['total_messages']
            total_folders = export_stats['total_folders']
            
            self.messages_label.config(text=f"{total_messages:,}")
            self.folders_label.config(text=f"{total_folders:,}")
            
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
            
            self.add_activity("📊", "Stats Updated", f"Found {total_messages:,} messages in {total_folders:,} folders", "success")
            
        except Exception as e:
            self.add_activity("❌", "Error", f"Failed to load stats: {e}", "error")
    
    def set_buttons_state(self, running=False):
        """Toggle buttons"""
        state = DISABLED if running else NORMAL
        stop_state = NORMAL if running else DISABLED
        
        self.export_btn.config(state=state)
        self.export_backup_btn.config(state=state)
        self.backup_btn.config(state=state)
        self.stop_btn.config(state=stop_state)
        
        if running:
            # Keep determinate mode; show 0% initially for calmer UI
            self.main_progress.config(mode='determinate')
            self.main_progress['value'] = 0
            self.update_status("Working...", "working")
        else:
            self.main_progress.stop()
            self.main_progress.config(mode='determinate')
            self.main_progress['value'] = 0
            self.secondary_progress['value'] = 0
            self.secondary_progress_text.config(text="Ready")
            self.update_status("Idle", "success")
            self.operation_label.config(text="Waiting to start...")
            self.current_item_label.config(text="None")
            self.progress_text.config(text="0 / 0 (0%)")
    
    def process_messages(self):
        """Process queued messages"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "activity":
                    self.add_activity(data['icon'], data['title'], data['desc'], data['status'])
                elif msg_type == "progress":
                    self.update_progress(data['current'], data['total'], data.get('item', ''))
                elif msg_type == "secondary_progress":
                    self.update_secondary_progress(data)
                elif msg_type == "operation":
                    self.operation_label.config(text=data['text'])
                elif msg_type == "toast":
                    self.show_toast(data['title'], data['message'], data.get('duration', 3000))
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_messages)
    
    def start_export(self):
        """Start export"""
        self.backup_var.set(False)
        self._run_operation(self.export_operation)
    
    def start_export_with_backup(self):
        """Start export with backup"""
        self.backup_var.set(True)
        self._run_operation(self.export_operation)
    
    def start_backup_only(self):
        """Start backup only"""
        self._run_operation(self.backup_only_operation)
    
    def _run_operation(self, operation_func):
        """Run operation in thread"""
        if self.is_running:
            self.show_toast("⚠️ Already Running", "Please wait for current operation to finish")
            return
        
        self.is_running = True
        # Reset cancellation state
        self.cancel_event.clear()
        self.set_buttons_state(running=True)
        self.update_progress(0, 0)
        
        self.current_thread = threading.Thread(target=operation_func, daemon=True)
        self.current_thread.start()
    
    def stop_operation(self):
        """Stop operation"""
        if messagebox.askyesno("Stop Operation", "Stop the current operation?"):
            self.message_queue.put(("activity", {
                'icon': '⚠️',
                'title': 'Stopping',
                'desc': 'Finishing current task...',
                'status': 'warning'
            }))
            self.is_running = False
            # Signal cooperative cancellation
            self.cancel_event.set()
    
    def export_operation(self):
        """Export operation"""
        try:
            from_date_str = self.date_entry.get().strip()
            if from_date_str == "YYYY-MM-DD":
                from_date_str = ""
            from_date = from_date_str if from_date_str else None
            force = self.force_var.get()
            backup = self.backup_var.get()
            keep_archive = self.keep_archive_var.get()
            
            self.message_queue.put(("operation", {'text': '🚀 Starting export...'}))
            self.message_queue.put(("activity", {
                'icon': '🚀',
                'title': 'Export Started',
                'desc': 'Initializing export process',
                'status': 'info'
            }))
            
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            init_database(OUTPUT_DIR)
            
            backup_handler = None
            if backup:
                self.message_queue.put(("operation", {'text': '🔐 Authenticating Google Drive...'}))
                self.message_queue.put(("activity", {
                    'icon': '☁️',
                    'title': 'Google Drive',
                    'desc': 'Authenticating...',
                    'status': 'info'
                }))
                
                try:
                    backup_handler = GoogleDriveBackup(
                        credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
                        token_file=GOOGLE_DRIVE_TOKEN_FILE
                    )
                    
                    if backup_handler.authenticate() and backup_handler.get_or_create_backup_folder():
                        self.message_queue.put(("activity", {
                            'icon': '✓',
                            'title': 'Google Drive Ready',
                            'desc': 'Authentication successful',
                            'status': 'success'
                        }))
                    else:
                        backup_handler = None
                        self.message_queue.put(("activity", {
                            'icon': '⚠️',
                            'title': 'Google Drive Failed',
                            'desc': 'Continuing without backup',
                            'status': 'warning'
                        }))
                except Exception as e:
                    backup_handler = None
            
            # Export
            self.message_queue.put(("operation", {'text': '📥 Exporting messages...'}))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def do_export():
                client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
                try:
                    await client.start(phone=PHONE)
                    self.message_queue.put(("activity", {
                        'icon': '✓',
                        'title': 'Telegram Connected',
                        'desc': 'Successfully connected to Telegram',
                        'status': 'success'
                    }))
                    
                    # Check stop flag before export
                    if not self.is_running:
                        return
                    
                    await export_saved_messages(
                        client,
                        str(db_path),
                        from_date=from_date,
                        force_reexport=force,
                        output_dir=OUTPUT_DIR,
                        cancel_event=self.cancel_event
                    )
                    
                    # Check stop flag after export
                    if not self.is_running:
                        self.message_queue.put(("activity", {
                            'icon': '⚠️',
                            'title': 'Export Stopped',
                            'desc': 'Operation was cancelled by user',
                            'status': 'warning'
                        }))
                        return
                    
                    self.message_queue.put(("activity", {
                        'icon': '✅',
                        'title': 'Export Complete',
                        'desc': 'All messages exported successfully',
                        'status': 'success'
                    }))
                finally:
                    await client.disconnect()
            
            # Redirect print output to log windows and parse for GUI updates
            import builtins
            import re
            original_print = print
            
            # Track last line for carriage return handling
            last_line_start = {}
            
            def custom_print(*args, **kwargs):
                message = ' '.join(map(str, args))
                end = kwargs.get('end', '\n')
                now_ts = datetime.now().timestamp()
                
                # Print to log windows if they exist
                if hasattr(self, 'log_windows') and self.log_windows:
                    for log_window, log_text in self.log_windows:
                        if log_window.winfo_exists():
                            # Handle carriage return (\r) - update same line
                            if message.startswith('\r'):
                                # Remove \r prefix
                                clean_message = message[1:]
                                
                                # Get window id for tracking
                                window_id = id(log_window)
                                
                                # If we have a previous line start position, delete only that line content
                                if window_id in last_line_start:
                                    log_text.delete(f"{last_line_start[window_id]}", f"{last_line_start[window_id]} lineend")
                                else:
                                    # Store current end position as start of this line
                                    last_line_start[window_id] = log_text.index(tk.END + "-1c linestart")
                                
                                # Insert new content
                                log_text.insert(tk.END, clean_message)
                                
                                # If end is newline, move to next line and clear tracker
                                if end == '\n':
                                    log_text.insert(tk.END, '\n')
                                    if window_id in last_line_start:
                                        del last_line_start[window_id]
                                else:
                                    # Update tracker for next overwrite
                                    last_line_start[window_id] = log_text.index(tk.END + "-1c linestart")
                            else:
                                # Normal print - just append
                                log_text.insert(tk.END, message + end)
                                window_id = id(log_window)
                                if window_id in last_line_start:
                                    del last_line_start[window_id]
                            
                            log_text.see(tk.END)
                            log_text.update()
                
                # Skip progress bar messages from GUI updates
                    if message.startswith('\r'):
                        # Normalize message (remove leading CR)
                        cr_msg = message.lstrip('\r')
                        # Pattern: 📦 Archiving: 45.5% (10/22) - filename.jpg
                        archive_match = re.search(r'📦 Archiving: ([\d.]+)% \((\d+)/(\d+)\) - (.+?)(?: at ([^\s]+/s) - ETA: (\S+))?$', cr_msg)
                        if archive_match:
                            percent = float(archive_match.group(1))
                            current = int(archive_match.group(2))
                            total = int(archive_match.group(3))
                            filename = archive_match.group(4).strip()
                            speed = archive_match.group(5)
                            eta = archive_match.group(6)
                            payload = {
                                'current': current,
                                'total': total,
                                'percent': percent,
                                'text': f'Archiving: {filename[:30]}'
                            }
                            if speed:
                                payload['speed'] = speed
                            if eta:
                                payload['eta'] = eta
                            self.message_queue.put(("secondary_progress", payload))
                            self.root.update_idletasks()
                            return

                        # Download progress with optional filename, speed and ETA
                        # Example: 📥 filename.ext  12.3% [████░░░] 1.2MB/10MB at 500KB/s - ETA: 3s
                        # Primary pattern with icon
                        dl_match = re.search(r'📥\s+(?:(?P<name>.+?)\s+)?(?P<percent>\d+(?:\.\d+)?)%.*?at\s+(?P<speed>[^\s]+/s)\s+-\s+ETA:\s+(?P<eta>\S+)', cr_msg)
                        # Fallback pattern (maybe missing icon at start)
                        if not dl_match:
                            dl_match = re.search(r'^(?:(?P<name>.+?)\s+)?(?P<percent>\d+(?:\.\d+)?)%\s+\[[█░]+\].*?at\s+(?P<speed>[^\s]+/s)\s+-\s+ETA:\s+(?P<eta>\S+)', cr_msg)
                        if dl_match:
                            percent = float(dl_match.group('percent'))
                            fname = dl_match.group('name')
                            speed = dl_match.group('speed')
                            eta = dl_match.group('eta')
                            base_label = f'Downloading: {fname[:30]}' if fname else 'Downloading media'
                            self.message_queue.put(("secondary_progress", {
                                'percent': percent,
                                'text': base_label,
                                'speed': speed,
                                'eta': eta
                            }))
                            self.root.update_idletasks()
                            return
                        return
                
                    # Skip other progress bar messages
                    if '📥' in message and '%' in message:
                        # Non-CR download progress lines already handled above
                        return
                
                # Parse message for GUI updates
                # Pattern: [1/123] Processing message 12345...
                # Normalize leading spaces/newlines so regex matches lines like "\n[1/7055] ..."
                norm_msg = message.lstrip()
                progress_match = re.match(r'\[(\d+)/(\d+)\] Processing message (\d+)', norm_msg)
                if progress_match:
                    current = int(progress_match.group(1))
                    total = int(progress_match.group(2))
                    msg_id = progress_match.group(3)
                    # Update metrics baseline
                    self.metrics['exported_messages'] = current - 1
                    self.metrics['total_messages'] = total
                    self.metrics['current_message_id'] = msg_id
                    if not hasattr(self, '_export_start_time'):
                        self._export_start_time = now_ts
                    elapsed = now_ts - getattr(self, '_export_start_time', now_ts)
                    if current > 1:
                        avg = elapsed / (current - 1)
                        remaining = (total - (current - 1)) * avg
                        self.metrics['avg_time_per_msg'] = avg
                        self.metrics['elapsed_time'] = elapsed
                        self.metrics['eta_minutes'] = remaining / 60.0
                    self._update_metrics_labels()
                    self.message_queue.put(("progress", {
                        'current': current,
                        'total': total,
                        'item': f'Message {msg_id}'
                    }))
                    self.message_queue.put(("operation", {
                        'text': f'📥 Processing message {current}/{total}'
                    }))
                    self.root.update_idletasks()
                
                # Pattern: Found X new messages to export
                elif 'Found' in message and 'messages to export' in message:
                    match = re.search(r'Found (\d+) new messages', norm_msg)
                    if match:
                        total = int(match.group(1))
                        self.metrics['total_messages'] = total
                        self.metrics['exported_messages'] = 0
                        self.metrics['skipped_messages'] = 0
                        self._export_start_time = now_ts
                        self._update_metrics_labels()
                        self.message_queue.put(("progress", {
                            'current': 0,
                            'total': total,
                            'item': 'Initializing...'
                        }))
                        self.root.update_idletasks()
                
                # Pattern: Starting media download
                elif 'Starting media download' in norm_msg or 'Downloading media' in norm_msg:
                    self.message_queue.put(("operation", {
                        'text': '📥 Downloading media files...'
                    }))
                    self.metrics['media_file'] = ''
                    self.metrics['media_percent'] = 0.0
                    self.metrics['media_speed'] = ''
                    self.metrics['media_eta'] = ''
                    self._update_metrics_labels()
                    self.root.update_idletasks()
                elif 'Skipped' in norm_msg and 'already exported messages' in norm_msg:
                    skipped_match = re.search(r'Skipped (\d+) already exported messages', norm_msg)
                    if skipped_match:
                        self.metrics['skipped_messages'] = int(skipped_match.group(1))
                        self._update_metrics_labels()
                elif 'Retrying message' in norm_msg:
                    retry_match = re.search(r'Retrying message \(attempt (\d+)/(\d+)\)', norm_msg)
                    if retry_match:
                        self.metrics['current_retries'] = int(retry_match.group(1))
                        self._update_metrics_labels()
                elif 'Failed to export message' in norm_msg or 'Error exporting message' in norm_msg:
                    self.metrics['last_error'] = norm_msg
                    self._update_metrics_labels()
                elif 'Telegram Connected' in norm_msg or 'Reconnected successfully' in norm_msg:
                    self.metrics['connection_status'] = 'Connected'
                    self._update_metrics_labels()
                elif 'Attempting to reconnect' in norm_msg:
                    self.metrics['connection_status'] = 'Reconnecting'
                    self._update_metrics_labels()
                elif 'Failed to reconnect' in norm_msg:
                    self.metrics['connection_status'] = 'Failed'
                    self._update_metrics_labels()
                elif norm_msg.startswith('✓ Successfully exported'):
                    # Final summary line
                    final_exported_match = re.search(r'✓ Successfully exported (\d+) messages', norm_msg)
                    if final_exported_match:
                        self.metrics['exported_messages'] = int(final_exported_match.group(1))
                        self._update_metrics_labels()
            
            builtins.print = custom_print
            
            try:
                loop.run_until_complete(do_export())
            finally:
                builtins.print = original_print
            
            # Backup
            if backup_handler:
                # Check stop flag before backup
                if not self.is_running:
                    self.message_queue.put(("activity", {
                        'icon': '⚠️',
                        'title': 'Backup Cancelled',
                        'desc': 'Operation was stopped by user',
                        'status': 'warning'
                    }))
                    return
                
                self.message_queue.put(("operation", {'text': '☁️ Backing up to Google Drive...'}))
                self.message_queue.put(("activity", {
                    'icon': '☁️',
                    'title': 'Backup Started',
                    'desc': 'Uploading folders to Google Drive',
                    'status': 'info'
                }))
                
                cleanup = not keep_archive
                stats = backup_handler.backup_individual_folders(
                    OUTPUT_DIR,
                    str(db_path),
                    cleanup_after_upload=cleanup,
                    cancel_event=self.cancel_event
                )
                
                # Check stop flag after backup
                if not self.is_running:
                    self.message_queue.put(("activity", {
                        'icon': '⚠️',
                        'title': 'Backup Incomplete',
                        'desc': 'Operation was stopped by user',
                        'status': 'warning'
                    }))
                    return
                
                self.message_queue.put(("activity", {
                    'icon': '✅',
                    'title': 'Backup Complete',
                    'desc': f"Uploaded {stats['success']} folders, {stats['failed']} failed",
                    'status': 'success' if stats['failed'] == 0 else 'warning'
                }))
            
            self.message_queue.put(("operation", {'text': '✅ All operations completed!'}))
            self.message_queue.put(("toast", {
                'title': '✅ Success!',
                'message': 'Export completed successfully',
                'duration': 5000
            }))
            
        except Exception as e:
            self.message_queue.put(("activity", {
                'icon': '❌',
                'title': 'Error',
                'desc': str(e),
                'status': 'error'
            }))
            self.message_queue.put(("toast", {
                'title': '❌ Error',
                'message': str(e),
                'duration': 5000
            }))
        
        finally:
            self.is_running = False
            self.set_buttons_state(running=False)
            self.load_stats()
    
    def backup_only_operation(self):
        """Backup only"""
        try:
            self.message_queue.put(("operation", {'text': '☁️ Starting backup...'}))
            
            db_path = Path(OUTPUT_DIR) / "export_history.db"
            if not db_path.exists():
                self.message_queue.put(("activity", {
                    'icon': '❌',
                    'title': 'Error',
                    'desc': 'No database found. Run export first!',
                    'status': 'error'
                }))
                return
            
            # Redirect print output to log windows and parse for GUI updates
            import builtins
            import re
            original_print = print
            
            # Track last line for carriage return handling
            last_line_start_backup = {}
            
            def custom_print(*args, **kwargs):
                message = ' '.join(map(str, args))
                end = kwargs.get('end', '\n')
                
                # Print to log windows if they exist
                if hasattr(self, 'log_windows') and self.log_windows:
                    for log_window, log_text in self.log_windows:
                        if log_window.winfo_exists():
                            # Handle carriage return (\r) - update same line
                            if message.startswith('\r'):
                                # Remove \r prefix
                                clean_message = message[1:]
                                
                                # Get window id for tracking
                                window_id = id(log_window)
                                
                                # If we have a previous line start position, delete from there
                                if window_id in last_line_start_backup:
                                    log_text.delete(f"{last_line_start_backup[window_id]}", f"{last_line_start_backup[window_id]} lineend")
                                else:
                                    # Store current end position as start of this line
                                    last_line_start_backup[window_id] = log_text.index(tk.END + "-1c linestart")
                                
                                # Insert new content
                                log_text.insert(tk.END, clean_message)
                                
                                # If end is newline, move to next line and clear tracker
                                if end == '\n':
                                    log_text.insert(tk.END, '\n')
                                    if window_id in last_line_start_backup:
                                        del last_line_start_backup[window_id]
                                else:
                                    # Update tracker for next overwrite
                                    last_line_start_backup[window_id] = log_text.index(tk.END + "-1c linestart")
                            else:
                                # Normal print - just append
                                log_text.insert(tk.END, message + end)
                                window_id = id(log_window)
                                if window_id in last_line_start_backup:
                                    del last_line_start_backup[window_id]
                            
                            log_text.see(tk.END)
                            log_text.update()
                
                # Skip progress bar messages from GUI updates
                    if message.startswith('\r'):
                        cr_msg = message.lstrip('\r')
                        archive_match = re.search(r'📦 Archiving: ([\d.]+)% \((\d+)/(\d+)\) - (.+?)(?: at ([^\s]+/s) - ETA: (\S+))?$', cr_msg)
                        if archive_match:
                            percent = float(archive_match.group(1))
                            current = int(archive_match.group(2))
                            total = int(archive_match.group(3))
                            filename = archive_match.group(4).strip()
                            speed = archive_match.group(5)
                            eta = archive_match.group(6)
                            payload = {
                                'current': current,
                                'total': total,
                                'percent': percent,
                                'text': f'Archiving: {filename[:30]}'
                            }
                            if speed:
                                payload['speed'] = speed
                            if eta:
                                payload['eta'] = eta
                            self.message_queue.put(("secondary_progress", payload))
                            self.root.update_idletasks()
                            return
                        return

                    if '📥' in message and '%' in message:
                        return
                
                # Parse message for GUI updates
                # Pattern: Backing up folder X/Y
                    # Pattern: [1/10] Processing: folder_name
                    folder_match = re.match(r'\[(\d+)/(\d+)\] Processing: (.+)', message)
                    if folder_match:
                        current = int(folder_match.group(1))
                        total = int(folder_match.group(2))
                        folder_name = folder_match.group(3).strip()
                    
                        self.message_queue.put(("progress", {
                            'current': current,
                            'total': total,
                            'item': folder_name[:50]
                        }))
                        self.message_queue.put(("operation", {
                            'text': f'☁️ Backing up folder {current}/{total}: {folder_name[:30]}'
                        }))
                        self.root.update_idletasks()
                
                    # Pattern: Backing up folder X/Y (fallback)
                    backup_match = re.search(r'Backing up folder (\d+)/(\d+)', message)
                if backup_match:
                    current = int(backup_match.group(1))
                    total = int(backup_match.group(2))
                    self.message_queue.put(("progress", {
                        'current': current,
                        'total': total,
                        'item': f'Folder {current}/{total}'
                    }))
                    self.message_queue.put(("operation", {
                        'text': f'☁️ Backing up folder {current}/{total}'
                    }))
                    # Force GUI update
                    self.root.update_idletasks()
                
                # Pattern: Uploading/Archiving
                elif 'Uploading' in message or 'Archiving' in message or 'Creating archive' in message:
                    self.message_queue.put(("operation", {
                        'text': '📦 ' + message[:50]
                    }))
                    self.root.update_idletasks()
            
            builtins.print = custom_print
            
            try:
                backup_handler = GoogleDriveBackup(
                    credentials_file=GOOGLE_DRIVE_CREDENTIALS_FILE,
                    token_file=GOOGLE_DRIVE_TOKEN_FILE
                )
                
                if not backup_handler.authenticate():
                    self.message_queue.put(("activity", {
                        'icon': '❌',
                        'title': 'Authentication Failed',
                        'desc': 'Could not authenticate with Google Drive',
                        'status': 'error'
                    }))
                    return
                
                # Check stop flag before backup
                if not self.is_running:
                    self.message_queue.put(("activity", {
                        'icon': '⚠️',
                        'title': 'Backup Cancelled',
                        'desc': 'Operation was stopped by user',
                        'status': 'warning'
                    }))
                    return
                
                cleanup = not self.keep_archive_var.get()
                stats = backup_handler.backup_individual_folders(
                    OUTPUT_DIR,
                    str(db_path),
                    cleanup_after_upload=cleanup,
                    cancel_event=self.cancel_event
                )
                
                # Check stop flag after backup
                if not self.is_running:
                    self.message_queue.put(("activity", {
                        'icon': '⚠️',
                        'title': 'Backup Incomplete',
                        'desc': 'Operation was stopped by user',
                        'status': 'warning'
                    }))
                    return
                
                self.message_queue.put(("activity", {
                    'icon': '✅',
                    'title': 'Backup Complete',
                    'desc': f"Uploaded {stats['success']} folders",
                    'status': 'success'
                }))
                
            finally:
                builtins.print = original_print
        
        except Exception as e:
            self.message_queue.put(("activity", {
                'icon': '❌',
                'title': 'Error',
                'desc': str(e),
                'status': 'error'
            }))
        
        finally:
            self.is_running = False
            self.set_buttons_state(running=False)
            self.load_stats()
    
    def open_export_folder(self):
        """Open folder"""
        import os
        export_path = Path(OUTPUT_DIR)
        if export_path.exists():
            os.startfile(export_path)
            self.show_toast("📂 Folder Opened", "Export folder opened in File Explorer")
        else:
            self.show_toast("⚠️ Not Found", "Export folder doesn't exist yet")
    
    def open_log_window(self):
        """Open a separate window with CLI-style logs"""
        # Create new window
        log_window = tk.Toplevel(self.root)
        log_window.title("Detailed Logs - Telegram Exporter")
        log_window.geometry("800x600")
        log_window.configure(bg="#2b3e50")
        
        # Create scrolled text widget
        from tkinter.scrolledtext import ScrolledText
        
        log_text = ScrolledText(
            log_window,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1a1a1a",
            fg="#00ff00",
            insertbackground="white",
            state=NORMAL
        )
        log_text.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Redirect print to this window
        class LogRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget
                self.original_print = print
            
            def write(self, message):
                if message.strip():  # Ignore empty messages
                    self.text_widget.insert(tk.END, message)
                    self.text_widget.see(tk.END)
                    self.text_widget.update()
            
            def flush(self):
                pass
        
        # Store reference to log window
        if not hasattr(self, 'log_windows'):
            self.log_windows = []
        
        self.log_windows.append((log_window, log_text))
        
        # Add initial message
        log_text.insert(tk.END, "=== Telegram Exporter - Detailed Logs ===\n")
        log_text.insert(tk.END, f"Opened at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_text.insert(tk.END, "All print statements will appear here during operations.\n")
        log_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Button to clear logs
        btn_frame = ttk.Frame(log_window)
        btn_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        def clear_logs():
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, "=== Logs Cleared ===\n\n")
        
        ttk.Button(
            btn_frame,
            text="🗑️ Clear Logs",
            command=clear_logs,
            bootstyle="danger-outline"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ Close",
            command=log_window.destroy,
            bootstyle="secondary-outline"
        ).pack(side=LEFT)
        
        self.show_toast("📋 Logs Window", "Opened detailed logs window")


def main():
    """Main entry"""
    import tkinter as tk
    
    app = ttk.Window(
        title="Telegram Saved Messages Exporter",
        themename="darkly",
        size=(900, 700),
        resizable=(False, True)
    )
    
    # Make tk available in global scope
    import sys
    sys.modules['tkinter'] = tk
    globals()['tk'] = tk
    
    gui = VisualExporterGUI(app)
    app.mainloop()


if __name__ == "__main__":
    main()
