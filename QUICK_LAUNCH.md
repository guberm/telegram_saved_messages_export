# 🚀 Quick Launch Guide

## Telegram Saved Messages Exporter

### 🎨 GUI Mode (Recommended)

**Windows - Easiest:**
```
Double-click: run_gui.bat
```

**Any OS:**
```bash
py gui.py
```

**Features:**
- ✅ Visual interface
- ✅ Real-time progress
- ✅ Statistics display
- ✅ One-click operations
- ✅ Color-coded logs
- ✅ CLI access built-in

---

### 🖥️ CLI Mode (Advanced)

**Export all messages:**
```bash
py main.py
```

**Export with backup:**
```bash
py main.py --backup
```

**Backup existing exports:**
```bash
py main.py --backup-only
```

**View statistics:**
```bash
py main.py --stats
```

**Help:**
```bash
py main.py --help
```

---

### 📁 Files Overview

| File | Purpose | How to Use |
|------|---------|------------|
| `run_gui.bat` | Start GUI | Double-click |
| `gui.py` | GUI application | `py gui.py` |
| `main.py` | CLI application | `py main.py` |
| `config.py` | Settings | Edit as needed |

---

### 🔧 First Time Setup

1. **Install dependencies:**
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Configure:**
   - Copy `config.py.example` → `config.py`
   - Add your Telegram API credentials
   - (Optional) Configure Google Drive

3. **Run:**
   - GUI: Double-click `run_gui.bat`
   - CLI: `py main.py`

---

### 📚 Documentation

| File | Description |
|------|-------------|
| `GUI_USER_GUIDE.md` | Complete GUI guide |
| `README.md` | Full documentation |
| `GOOGLE_DRIVE_SETUP.md` | Google Drive setup |
| `WINDOWS_QUICK_START.md` | Windows-specific guide |

---

### 💡 Quick Tips

**For daily use:**
- Use GUI (`run_gui.bat`)
- Keep "Force re-export" unchecked
- Enable backup for safety

**For advanced use:**
- Use CLI from GUI ("Open CLI" button)
- Or run `py main.py` with options
- See `py main.py --help` for all options

**Troubleshooting:**
- GUI won't start → Check Python: `py --version`
- Import errors → Reinstall: `py -m pip install -r requirements.txt`
- Auth issues → Delete `telegram_session.session` and retry

---

### 🎯 Common Commands

```bash
# GUI (easiest)
py gui.py

# Export recent messages only
py main.py --from-date 2024-01-01

# Export + backup to Google Drive
py main.py --backup

# Just backup (no new export)
py main.py --backup-only

# View what's been exported
py main.py --stats

# Force re-export everything
py main.py --force

# Keep local files after backup
py main.py --backup --keep-archive

# Custom output folder
py main.py --output my_exports
```

---

### 🌟 Recommended Workflow

**First time:**
1. Open GUI: `run_gui.bat`
2. Click "📥 Export Messages"
3. Wait for completion

**Regular updates:**
1. Open GUI: `run_gui.bat`
2. Click "📥☁️ Export + Backup"
3. Only new messages exported (fast!)

**Backup only:**
1. Open GUI: `run_gui.bat`
2. Click "☁️ Backup Only"

---

**Choose your style:**
- 🎨 **GUI** for easy point-and-click
- 🖥️ **CLI** for automation and scripting
- 🔄 **Both** - GUI for daily use, CLI for advanced tasks

**Start here:** Double-click `run_gui.bat` 🚀
