# Windows Desktop Client - Guide

## 🎯 Launch Options

You have **3 ways** to use the application on Windows:

### 1️⃣ Desktop Shortcut (Simplest)

Create a shortcut to launch **tkinter GUI** (classic interface):

```bash
python create_desktop_shortcut.py
```

**What happens:**
- ✅ Creates "Telegram Exporter" shortcut on desktop
- ✅ Adds shortcut to Start Menu
- ✅ Creates .bat file for launch (backup option)

**After that:**
- Double-click desktop icon
- Or find "Telegram Exporter" in Start Menu
- Or run `Launch Telegram Exporter.bat`

---

### 2️⃣ Standalone EXE File (No Python Required)

Create a standalone `.exe` file that works **without Python installed**:

```bash
python build_windows_exe.py
```

**What happens:**
- ✅ Installs PyInstaller (if needed)
- ✅ Creates `dist/TelegramExporter.exe` (~50-100 MB)
- ✅ Packages all dependencies inside
- ✅ Creates portable folder with everything needed

**Usage:**
```
dist/
  TelegramExporter.exe          <- Run this file
  TelegramExporter_Portable/    <- Portable version
```

**Advantages:**
- No Python installation required
- Can be copied to other computers
- Single .exe file
- Can create desktop shortcut manually

---

### 3️⃣ Electron Desktop App (Modern Web Interface)

Create a modern desktop application with **web interface**:

#### Install dependencies:
```bash
cd electron_app
npm install
```

#### Run in development mode:
```bash
# Terminal 1: Start FastAPI backend
cd ..
python web_server.py

# Terminal 2: Start React frontend
cd web_ui
npm start

# Terminal 3: Start Electron
cd electron_app
npm start
```

#### Build installer:
```bash
cd electron_app
npm run build-win
```

**What happens:**
- ✅ Creates `dist/Telegram Exporter Setup.exe` - installer
- ✅ Creates `dist/Telegram Exporter Portable.exe` - portable version
- ✅ Automatically creates desktop shortcut on install
- ✅ Adds to Start Menu

**Advantages:**
- Modern Material UI interface
- Real-time updates via WebSocket
- Automatic installation and updates
- System tray minimization

---

## 📊 Options Comparison

| Feature | Shortcut (tkinter) | Standalone EXE | Electron App |
|---------|-------------------|----------------|--------------|
| Requires Python | ✅ Yes | ❌ No | ❌ No |
| Size | ~10 KB (shortcut) | ~50-100 MB | ~150-200 MB |
| Interface | Tkinter GUI | Tkinter GUI | Web (Material UI) |
| Setup Time | Instant | 1-2 minutes | 5-10 minutes |
| Portable | No | ✅ Yes | ✅ Yes |
| Auto-update | ❌ | ❌ | ✅ Possible |
| Real-time updates | ✅ | ✅ | ✅ WebSocket |

---

## 🚀 Recommendations

### For personal use (Python installed):
```bash
python create_desktop_shortcut.py
```
**Pros:** Fast, easy to update code

### For sharing with other users:
```bash
python build_windows_exe.py
```
**Pros:** No Python required, just copy

### For professional use:
```bash
cd electron_app
npm install
npm run build-win
```
**Pros:** Modern interface, auto-install

---

## 🔧 Quick Start (Recommended Path)

### Step 1: Create shortcut
```bash
python create_desktop_shortcut.py
```

### Step 2: Check desktop
Find "Telegram Exporter" icon and double-click

### Step 3: (Optional) Create EXE for backup
```bash
python build_windows_exe.py
```

---

## 📁 File Structure After Build

```
telegram_export/
├── Launch Telegram Exporter.bat    <- Batch file for launch
├── dist/
│   ├── TelegramExporter.exe        <- Standalone executable
│   └── TelegramExporter_Portable/  <- Portable version
├── electron_app/
│   └── dist/
│       ├── Telegram Exporter Setup.exe    <- Installer
│       └── Telegram Exporter Portable.exe <- Portable Electron
└── Desktop Shortcuts/
    └── Telegram Exporter.lnk       <- Desktop shortcut
```

---

## ❓ FAQ

### Q: Which option is fastest?
**A:** Shortcut (option 1) - created in seconds.

### Q: Which option doesn't require Python?
**A:** Standalone EXE (option 2) or Electron App (option 3).

### Q: Can I use all 3 options simultaneously?
**A:** Yes! They work independently and use the same database.

### Q: How to update icon?
**A:** Put `icon.ico` file in `assets/` folder before building.

### Q: Does Electron App require installed Node.js?
**A:** Only for building. Final .exe works without Node.js.

### Q: Where is data stored?
**A:** In `telegram_saved_messages_exports/` folder and `export_history.db` database in project root.

---

## 🎨 Creating Custom Icon

### Option 1: Download ready icon
Put `icon.ico` in `assets/` folder

### Option 2: Create from image
```bash
pip install pillow
python -c "
from PIL import Image
img = Image.open('your_image.png')
img.save('assets/icon.ico', format='ICO', sizes=[(256,256)])
"
```

---

## 🔄 Auto-start on Windows Startup

### After creating shortcut:

1. Press `Win + R`
2. Type: `shell:startup`
3. Copy shortcut to opened folder

Now the application starts on Windows login!

---

## 📞 Support

If something doesn't work:

1. Check that Python is installed: `python --version`
2. Check dependencies: `pip install -r requirements.txt`
3. Check administrator rights when creating shortcuts
4. Check antivirus (may block PyInstaller)

---

## ✅ Done!

Choose a convenient option and enjoy the application! 🚀
