#!/usr/bin/env python3
"""
Telegram Saved Messages Exporter - Legacy Entry Point

NOTE: This project has been refactored into multiple modules.
This file serves as a legacy entry point that redirects to the new main.py.

For the new modular structure, please use:
    python main.py

The application is now organized into:
- main.py - Main entry point and CLI handling
- database.py - Database operations
- exporter.py - Export logic
- formatters.py - HTML/Markdown formatting
- media_handler.py - Media download
- utils.py - Utility functions
"""

import sys
import subprocess

def main():
    """Legacy entry point - redirects to new main.py"""
    print("🔄 This is the legacy entry point.")
    print("📁 The project has been refactored into multiple modules for better organization.")
    print("▶️  Redirecting to the new main.py...")
    print()
    
    # Pass all arguments to the new main.py
    args = sys.argv[1:]  # Get all arguments except the script name
    
    try:
        # Run the new main.py with the same arguments
        subprocess.run([sys.executable, 'main.py'] + args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running main.py: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ main.py not found. Please ensure all modular files are present.")
        print("📖 Check README_MODULAR.md for the new project structure.")
        sys.exit(1)

if __name__ == '__main__':
    main()