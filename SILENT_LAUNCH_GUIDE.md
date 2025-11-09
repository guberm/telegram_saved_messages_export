# 🔇 Silent Launch Options (No Console Windows)

## Available Silent Launchers:

### 1. **Launch_Silent.vbs** - Tkinter GUI Only
**What it does:**
- Launches the visual Tkinter GUI
- No console window appears
- Clean, professional look

**How to use:**
- Double-click `Launch_Silent.vbs`
- GUI opens silently
- No terminal windows!

---

### 2. **Launch_Web_Silent.vbs** - Web Interface Only (NEW!)
**What it does:**
- Starts FastAPI server in background
- Starts React UI in background
- Opens browser automatically
- No console windows visible

**How to use:**
- Double-click `Launch_Web_Silent.vbs`
- Wait ~8 seconds
- Browser opens to http://localhost:3000
- Everything runs silently!

**To stop web services:**
- Open Task Manager (Ctrl+Shift+Esc)
- Find "node.exe" and "python.exe" processes
- End these processes

---

### 3. **Create Desktop Shortcuts**

#### For GUI (Silent):
1. Run `Create Desktop Icon (Silent).bat`
2. Desktop shortcut created
3. Double-click shortcut = Silent GUI launch!

#### For Web Interface (Manual):
1. Right-click on Desktop → New → Shortcut
2. Location: `C:\telegram_export\Launch_Web_Silent.vbs`
3. Name: "Telegram Exporter - Web"
4. Click Finish
5. (Optional) Right-click shortcut → Properties → Change Icon

---

## Quick Reference:

| File | What It Opens | Console Windows? |
|------|---------------|------------------|
| `START_HERE.bat` | Tkinter GUI | ✅ Shows console |
| `Launch_Silent.vbs` | Tkinter GUI | ❌ No console |
| `launch_all.bat` | Menu (GUI/Web/All) | ✅ Shows console |
| `launch_web_only.bat` | Web UI (API + React) | ✅ Shows 2 consoles |
| `Launch_Web_Silent.vbs` | Web UI (API + React) | ❌ No console |

---

## Recommended for Clean Look:

### Desktop Users:
```
Use: Launch_Silent.vbs
- Clean Tkinter interface
- No console clutter
- All features available
```

### Web Interface Users:
```
Use: Launch_Web_Silent.vbs
- Modern web interface
- Runs in background
- Access from any browser tab
```

---

## Tips:

**To check if web services are running:**
1. Open browser to http://localhost:3000
2. If it loads, services are running!

**To stop silent web services:**
1. Task Manager (Ctrl+Shift+Esc)
2. End "node.exe" and "python.exe" processes
3. Or restart your computer

**To make startup easier:**
1. Create desktop shortcut to `.vbs` file
2. Pin to taskbar for one-click launch
3. Add to Windows startup folder for auto-start

---

## Creating Desktop Shortcuts:

### Quick Method:
1. Right-click `Launch_Silent.vbs` or `Launch_Web_Silent.vbs`
2. Select "Create shortcut"
3. Drag shortcut to Desktop

### Custom Icon Method:
1. Right-click shortcut → Properties
2. Click "Change Icon"
3. Browse to an icon file or use Windows icons
4. Click OK

---

**Enjoy your clean, console-free experience! 🎉**
