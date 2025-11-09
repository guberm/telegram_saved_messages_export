"""
Create desktop shortcut for Telegram Exporter (Tkinter GUI)
"""
import os
import sys
from pathlib import Path

def create_shortcut_windows():
    """Create Windows desktop shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("Installing required packages...")
        os.system("pip install winshell pywin32")
        import winshell
        from win32com.client import Dispatch
    
    # Get paths
    desktop = Path(winshell.desktop())
    script_dir = Path(__file__).parent.absolute()
    
    # Python executable
    python_exe = sys.executable
    
    # Target script
    target_script = script_dir / "gui_visual.py"
    
    # Icon (use Python icon or custom if available)
    icon_path = script_dir / "assets" / "icon.ico"
    if not icon_path.exists():
        # Try to find Python icon
        python_dir = Path(sys.executable).parent
        icon_candidates = [
            python_dir / "python.ico",
            python_dir / "DLLs" / "py.ico",
            python_dir / "pythonw.exe"
        ]
        for candidate in icon_candidates:
            if candidate.exists():
                icon_path = candidate
                break
        else:
            icon_path = python_exe  # Use Python executable as icon
    
    # Shortcut path
    shortcut_path = desktop / "Telegram Exporter.lnk"
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = f'"{python_exe}"'
    shortcut.Arguments = f'"{target_script}"'
    shortcut.WorkingDirectory = str(script_dir)
    shortcut.IconLocation = str(icon_path)
    shortcut.Description = "Telegram Messages Exporter - Desktop Application"
    shortcut.save()
    
    print(f"✓ Desktop shortcut created: {shortcut_path}")
    print(f"  Target: {target_script}")
    print(f"  Icon: {icon_path}")
    
    return True

def create_start_menu_shortcut():
    """Create Start Menu shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        return
    
    # Get paths
    start_menu = Path(winshell.start_menu())
    programs = start_menu / "Programs"
    
    script_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    target_script = script_dir / "gui_visual.py"
    
    # Icon
    icon_path = script_dir / "assets" / "icon.ico"
    if not icon_path.exists():
        icon_path = python_exe
    
    # Create folder if needed
    app_folder = programs / "Telegram Exporter"
    app_folder.mkdir(exist_ok=True)
    
    # Shortcut path
    shortcut_path = app_folder / "Telegram Exporter.lnk"
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = f'"{python_exe}"'
    shortcut.Arguments = f'"{target_script}"'
    shortcut.WorkingDirectory = str(script_dir)
    shortcut.IconLocation = str(icon_path)
    shortcut.Description = "Telegram Messages Exporter"
    shortcut.save()
    
    print(f"✓ Start Menu shortcut created: {shortcut_path}")
    
    return True

def create_batch_launcher():
    """Create .bat launcher as fallback"""
    script_dir = Path(__file__).parent.absolute()
    batch_path = script_dir / "Launch Telegram Exporter.bat"
    
    batch_content = f'''@echo off
title Telegram Exporter
cd /d "{script_dir}"
python gui_visual.py
pause
'''
    
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✓ Batch launcher created: {batch_path}")
    print("  You can double-click this file to launch the application")
    
    return batch_path

if __name__ == "__main__":
    print("=" * 60)
    print("Telegram Exporter - Desktop Shortcut Creator")
    print("=" * 60)
    print()
    
    if sys.platform != "win32":
        print("❌ This script is for Windows only")
        sys.exit(1)
    
    success = False
    
    # Try to create Windows shortcuts
    try:
        create_shortcut_windows()
        create_start_menu_shortcut()
        success = True
    except Exception as e:
        print(f"⚠️ Could not create Windows shortcuts: {e}")
        print("Creating batch launcher instead...")
    
    # Always create batch launcher as backup
    batch_path = create_batch_launcher()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Desktop shortcut created successfully!")
        print("   Look for 'Telegram Exporter' icon on your desktop")
    else:
        print("✅ Batch launcher created!")
        print(f"   Double-click: {batch_path}")
    print("=" * 60)
    
    input("\nPress Enter to exit...")
