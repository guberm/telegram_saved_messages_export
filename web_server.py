#!/usr/bin/env python3
"""
FastAPI Web Server for Telegram Exporter
Provides REST API endpoints for the React web interface
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import configuration and modules
try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = "telegram_saved_messages_exports"

from database import init_database, get_export_stats
from exporter import export_saved_messages
from telethon import TelegramClient

# Import API credentials
try:
    from config import API_ID, API_HASH, PHONE, SESSION_NAME
except ImportError:
    print("❌ ERROR: config.py not found or incomplete!")
    print("Please create config.py from config.py.example")
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global DB_PATH
    
    # Startup
    print("🚀 Starting Telegram Exporter API Server...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    
    # Initialize database and get path
    DB_PATH = init_database(OUTPUT_DIR)
    print("✅ Database initialized")
    
    yield
    
    # Shutdown (if needed)
    print("👋 Shutting down Telegram Exporter API Server...")


app = FastAPI(title="Telegram Exporter API", version="1.0.0", lifespan=lifespan)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
export_status = {
    "running": False,
    "progress": 0,
    "message": "",
    "error": None
}

# Database path (will be set at startup)
DB_PATH = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telegram Exporter API",
        "version": "1.0.0",
        "endpoints": {
            "stats": "/api/stats",
            "export": "/api/export/start",
            "status": "/api/export/status",
            "folder": "/api/open-folder"
        }
    }


@app.get("/api/stats")
async def get_stats():
    """Get export statistics"""
    try:
        if DB_PATH is None:
            print("❌ Database not initialized")
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        print(f"📊 Fetching stats from: {DB_PATH}")
        
        # Get stats
        stats = get_export_stats(DB_PATH)
        
        print(f"✅ Stats retrieved: {stats}")
        
        return {
            "total_messages": stats.get("total_messages", 0),
            "exported_messages": stats.get("total_messages", 0),
            "export_sessions": stats.get("total_messages", 0),
            "last_export": stats.get("newest")
        }
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/status")
async def get_export_status():
    """Get current export status"""
    print(f"📊 Export status requested: {export_status}")
    return export_status


async def run_export_task(force_reexport=False):
    """Background task to run the export
    
    Args:
        force_reexport: If True, re-export already exported messages
    """
    global export_status
    
    try:
        print("\n" + "="*60)
        print("🚀 EXPORT TASK STARTED")
        print(f"   Force Re-export: {force_reexport}")
        print(f"   Database: {DB_PATH}")
        print(f"   Output Dir: {OUTPUT_DIR}")
        print("="*60 + "\n")
        
        if DB_PATH is None:
            raise Exception("Database not initialized")
        
        export_status["running"] = True
        export_status["progress"] = 10
        export_status["message"] = "Connecting to Telegram..."
        export_status["error"] = None
        
        print("📱 Creating Telegram client...")
        # Create client
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        
        print("🔐 Starting client and authenticating...")
        await client.start(phone=PHONE)
        
        export_status["message"] = "Fetching messages from Telegram..."
        export_status["progress"] = 30
        
        print(f"🔄 Starting export (force_reexport={force_reexport})...")
        
        # Run export with db_path parameter
        await export_saved_messages(
            client=client,
            db_path=DB_PATH,
            from_date=None,
            force_reexport=force_reexport,
            output_dir=OUTPUT_DIR
        )
        
        print("✅ Export function completed")
        
        await client.disconnect()
        print("📴 Client disconnected")
        
        export_status["running"] = False
        export_status["progress"] = 100
        export_status["message"] = "Export completed successfully!"
        
        print("\n" + "="*60)
        print("✅ EXPORT TASK COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        export_status["running"] = False
        export_status["error"] = str(e)
        export_status["message"] = f"Export failed: {str(e)}"
        
        print("\n" + "="*60)
        print("❌ EXPORT TASK FAILED")
        print(f"   Error: {e}")
        print("="*60 + "\n")
        print(f"❌ Export error details: {e}")
        import traceback
        traceback.print_exc()


@app.post("/api/export/start")
async def start_export(background_tasks: BackgroundTasks, force_reexport: bool = False):
    """Start the export process
    
    Query Parameters:
        force_reexport: If true, re-export already exported messages
    """
    global export_status
    
    print(f"🚀 Export start requested (force_reexport={force_reexport})")
    
    if export_status["running"]:
        print("⚠️ Export already running, rejecting request")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Export already running", "detail": "Export already running"}
        )
    
    print("✅ Starting export in background...")
    
    # Start export in background with force_reexport parameter
    background_tasks.add_task(run_export_task, force_reexport)
    
    return {
        "status": "success",
        "message": "Export started"
    }


@app.post("/api/open-folder")
async def open_output_folder():
    """Open the output folder in file explorer"""
    try:
        output_path = Path(OUTPUT_DIR).resolve()
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Open folder based on OS
        if sys.platform == "win32":
            os.startfile(str(output_path))
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(output_path)])
        else:  # linux
            subprocess.run(["xdg-open", str(output_path)])
        
        return {"status": "success", "message": "Folder opened"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("=" * 50)
    print("Telegram Exporter - FastAPI Server")
    print("=" * 50)
    print(f"API Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
