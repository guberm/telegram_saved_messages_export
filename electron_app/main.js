const { app, BrowserWindow, Menu, Tray, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let tray;
let pythonProcess;
let serverReady = false;

// Python server management
function startPythonServer() {
  return new Promise((resolve, reject) => {
    const isPackaged = app.isPackaged;
    
    // Find Python executable
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    // Determine script path
    let scriptPath;
    if (isPackaged) {
      scriptPath = path.join(process.resourcesPath, 'backend', 'web_server.py');
    } else {
      scriptPath = path.join(__dirname, '..', 'web_server.py');
    }
    
    console.log('Starting Python server:', scriptPath);
    
    // Start Python process
    pythonProcess = spawn(pythonCmd, [scriptPath], {
      cwd: path.dirname(scriptPath),
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('Python:', output);
      
      // Check if server is ready
      if (output.includes('Uvicorn running on') || output.includes('Application startup complete')) {
        serverReady = true;
        resolve();
      }
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.error('Python Error:', data.toString());
    });
    
    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      serverReady = false;
    });
    
    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python:', err);
      reject(err);
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      if (!serverReady) {
        reject(new Error('Server startup timeout'));
      }
    }, 10000);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    title: 'Telegram Exporter',
    backgroundColor: '#f5f5f5',
    show: false // Don't show until ready
  });

  // Create menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'File',
      submenu: [
        {
          label: 'Refresh',
          accelerator: 'F5',
          click: () => mainWindow.reload()
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'Alt+F4',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Toggle Developer Tools',
          accelerator: 'F12',
          click: () => mainWindow.webContents.toggleDevTools()
        },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Telegram Exporter',
              message: 'Telegram Messages Exporter',
              detail: 'Version 1.0.0\n\nA modern tool for exporting Telegram messages with Google Drive backup support.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ]);
  
  Menu.setApplicationMenu(menu);

  // Wait for server before loading
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Load React app
  const startURL = 'http://localhost:3000';
  mainWindow.loadURL(startURL);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle minimize to tray
  mainWindow.on('minimize', (event) => {
    if (tray) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  
  // Check if icon exists, otherwise skip tray
  if (!fs.existsSync(iconPath)) {
    console.log('Tray icon not found, skipping tray creation');
    return;
  }
  
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        mainWindow.show();
      }
    },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('Telegram Exporter');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
}

// App lifecycle
app.whenReady().then(async () => {
  try {
    // Start Python backend
    await startPythonServer();
    console.log('Python server started successfully');
    
    // Wait a bit for React dev server (in development)
    if (!app.isPackaged) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    createWindow();
    createTray();
    
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start the application:\n${error.message}\n\nPlease make sure Python is installed and all dependencies are available.`
    );
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
});

app.on('quit', () => {
  // Kill Python process
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});
