# Telegram Saved Messages Exporter

A modular Python application for exporting Telegram saved messages to HTML and Markdown files.

## Project Structure

The application is now organized into multiple modules for better maintainability:

- `main.py` - Main entry point and CLI handling
- `config.py` - Configuration file with API credentials
- `database.py` - SQLite database operations for tracking exported messages  
- `exporter.py` - Core export logic
- `formatters.py` - HTML and Markdown formatting functions
- `media_handler.py` - Media download functionality
- `utils.py` - Utility functions (filename sanitization, etc.)
- `telegram_export.py` - Legacy entry point (redirects to main.py)

## Usage

### Basic Export
```bash
# Export all new messages (incremental)
python main.py

# Or use the legacy entry point
python telegram_export.py
```

### Advanced Options
```bash
# Export from a specific date
python main.py --from-date 2024-01-01

# Force re-export of already exported messages  
python main.py --force

# Show export statistics
python main.py --stats

# Custom output directory
python main.py --output my_exports
```

## Features

- **Incremental exports** - Only exports new messages by default
- **Rich formatting** - Preserves Telegram formatting (bold, code, links)
- **Media support** - Downloads and embeds images, videos, and other files
- **Progress tracking** - Detailed progress logging with time estimates
- **Multiple formats** - Exports to both HTML and Markdown
- **Database tracking** - SQLite database to track exported messages

## Setup

1. Copy `config.py.example` to `config.py`
2. Fill in your Telegram API credentials from https://my.telegram.org/auth
3. Install requirements: `pip install -r requirements.txt`
4. Run: `python main.py`

## Output Structure

Each message is exported to its own folder with the naming pattern:
```
YYYYMMDD_HHMMSS_msgID_preview/
├── message.html  # Rich HTML format
└── message.md    # Markdown format
└── media.*       # Media files (if present)
```

## Progress Logging

The application now provides detailed progress information:
- Current message being processed
- Time per message and average processing time
- Estimated time remaining
- Progress updates every 10 messages

This helps you track the export progress, especially for large numbers of messages.