# 🚀 Telegram Messages Exporter - Complete Guide

Export your Telegram saved messages with modern desktop interfaces!

## ⚡ QUICK START (30 seconds)

### Windows Users:

1. **Double-click:** `Create Desktop Icon.bat`
2. **Double-click:** "Telegram Exporter" icon on desktop
3. **Done!** Application started ✅

---

## 📦 What's Included

This project provides **multiple ways** to use the application:

### 🖥️ Desktop Applications

1. **Tkinter GUI** (Classic) - `gui_visual.py`
   - Native Windows application
   - Full-featured interface
   - Works with Python

2. **Web Interface** (Modern) - `web_ui/`
   - Material UI design
   - Real-time WebSocket updates
   - Accessible from browser

3. **Electron App** (Desktop Web) - `electron_app/`
   - Standalone desktop application
   - Web interface in native window
   - Doesn't require Python after build

---

## 🎯 Choose Your Launch Method

### Method 1: Desktop Shortcut ⭐ RECOMMENDED

**Simplest way:**
```
Double-click: Create Desktop Icon.bat
```

Creates shortcut on desktop. Double-click to launch!

**Features:**
- Instant setup
- One-click launch
- Auto-detects Python command (`py` or `python`)

---

### Method 2: BAT Launcher

**Direct launch:**
```
Double-click: START_HERE.bat
```

Launches with console window (useful for debugging).

---

### Method 3: Silent Launch (No Console)

**Clean launch without console window:**
```
Double-click: Launch_Silent.vbs
```

Or create silent shortcut:
```
Double-click: Create Desktop Icon (Silent).bat
```

---

### Method 4: Web Interface

**Modern browser-based interface:**

```bash
# Start all components
launch_all.bat

# Or manually:
python web_server.py    # Backend (port 8000)
cd web_ui && npm start  # Frontend (port 3000)
```

Access at: http://localhost:3000

---

### Method 5: Standalone EXE

**No Python required:**

```bash
python build_windows_exe.py
```

Creates `dist/TelegramExporter.exe` - works without Python!

---

### Method 6: Electron Desktop App

**Professional desktop application:**

```bash
cd electron_app
npm install
npm run build-win
```

Creates installer: `dist/Telegram Exporter Setup.exe`

---

## 🆚 Interface Comparison

| Feature | Tkinter GUI | Web UI | Electron App |
|---------|-------------|--------|--------------|
| **Launch Time** | Instant | 5 sec | Instant (after build) |
| **Requires Python** | ✅ Yes | ✅ Yes | ❌ No |
| **Interface** | Native | Material UI | Material UI |
| **Real-time Updates** | Threading | WebSocket | WebSocket |
| **Browser Access** | ❌ | ✅ | ❌ |
| **Portable** | ❌ | ❌ | ✅ |
| **Size** | Small | Medium | Large (~200MB) |

---

## ✨ Key Features

- **📥 Export Messages** - Save all Telegram messages
- **📁 Organized Folders** - Each message in separate folder
- **🖼️ Media Download** - Images, videos, files
- **☁️ Google Drive Backup** - Automatic cloud backup
- **🔍 Search** - Find messages by text or filename
- **📊 Statistics** - Track export progress
- **🔄 Resume** - Continue interrupted exports
- **🧹 Auto Cleanup** - Delete local files after backup

---

## 📚 Documentation

- **`START_HERE_README.md`** - Quick start guide
- **`DESKTOP_QUICK_START.md`** - Desktop setup guide
- **`WINDOWS_DESKTOP_GUIDE.md`** - Complete Windows guide
- **`WEB_UI_README.md`** - Web interface documentation
- **`README.md`** - Full project documentation

---

## 🔧 System Requirements

### Minimum:
- **OS:** Windows 10/11
- **Python:** 3.8+ (for BAT/GUI methods)
- **RAM:** 4 GB
- **Storage:** 1 GB + space for exported messages

### For Web Interface:
- **Node.js:** 16+ (for React frontend)

### For Standalone EXE:
- **No requirements** - works on any Windows PC

---

## 📦 Installation

### Quick Setup (Recommended):

1. **Clone repository:**
   ```bash
   git clone https://github.com/guberm/telegram_saved_messages_export.git
   cd telegram_saved_messages_export
   ```

2. **Install dependencies:**
   ```bash
   py -m pip install -r requirements.txt
   ```

3. **Create desktop shortcut:**
   ```bash
   py create_desktop_shortcut.py
   ```
   Or just double-click: `Create Desktop Icon.bat`

4. **Launch:**
   Double-click desktop icon!

---

## ⚙️ Configuration

### First Launch:

1. **Telegram API Credentials:**
   - Get from: https://my.telegram.org/apps
   - Set `API_ID` and `API_HASH` in `config.py`

2. **Google Drive (Optional):**
   - Create credentials.json
   - See `GOOGLE_DRIVE_SETUP.md`

3. **Launch Application:**
   - Click "📥 Export Messages"
   - Wait for completion
   - Data saved in `telegram_saved_messages_exports/`

---

## 🎨 Features Showcase

### Tkinter GUI:
- ✅ Modern dark theme
- ✅ Real-time progress bars
- ✅ Live statistics
- ✅ Activity log
- ✅ Search functionality
- ✅ Copy/paste support

### Web Interface:
- ✅ Material UI design
- ✅ WebSocket real-time updates
- ✅ Responsive layout
- ✅ Three tabs: Export, Search, Statistics
- ✅ Progress visualization
- ✅ Notification system

---

## 🔄 Auto-Start on Windows

To launch automatically on startup:

1. Create desktop shortcut (if not done)
2. Press `Win + R`
3. Type: `shell:startup`
4. Copy shortcut to opened folder

Done! Application starts with Windows.

---

## 🐛 Troubleshooting

### "Python not found"
**Solution:** Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

### "Module not found"
**Solution:** 
```bash
py -m pip install -r requirements.txt
```

### Desktop shortcut doesn't work
**Solution:** 
1. Try running as Administrator
2. Or use `START_HERE.bat` directly

### Application crashes
**Solution:**
1. Run `START_HERE.bat` to see error messages
2. Check `config.py` for correct API credentials
3. Install missing dependencies

---

## 📊 File Structure

```
telegram_export/
├── START_HERE.bat              # Main launcher
├── Launch_Silent.vbs           # Silent launcher (no console)
├── Create Desktop Icon.bat     # Creates desktop shortcut
├── gui_visual.py              # Tkinter GUI application
├── web_server.py              # FastAPI backend
├── config.py                  # Configuration
├── database.py                # SQLite operations
├── exporter.py                # Export logic
├── web_ui/                    # React frontend
│   ├── src/
│   │   └── App.js            # Main React component
│   └── package.json          # Dependencies
├── electron_app/              # Electron desktop app
│   ├── main.js               # Electron main process
│   └── package.json          # Dependencies
└── telegram_saved_messages_exports/  # Exported data
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📄 License

Open source project. Use freely.

---

## 🎉 Ready to Start!

**Choose your preferred method and launch the application:**

- ⚡ **Fastest:** Double-click `START_HERE.bat`
- 🖥️ **Best:** Create desktop icon and use it
- 🌐 **Modern:** Launch web interface
- 📦 **Portable:** Build standalone .exe

**All methods work with the same database - choose what fits you best!** 🚀

---

## 📞 Support

Having issues? Check:
1. ✅ Python installed: `py --version`
2. ✅ Dependencies installed: `py -m pip install -r requirements.txt`
3. ✅ Config file correct: `config.py`
4. ✅ Antivirus not blocking

For detailed guides, see documentation files listed above.

---

**Made with ❤️ for Telegram users who want to backup their messages!**
