const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let pythonProcess = null;

function startPythonBackend() {
    const projectRoot = path.join(__dirname, '..');
    const apiScript = path.join(projectRoot, 'api.py');
    
    // Candidates for Python path
    const candidates = [
        path.join(projectRoot, 'venv', 'bin', 'python3'),
        path.join(projectRoot, 'venv', 'bin', 'python'),
        'python3',
        'python'
    ];
    
    let pythonPath = 'python3';
    for (const cand of candidates) {
        if (cand === 'python3' || cand === 'python') {
            pythonPath = cand;
            break;
        }
        if (fs.existsSync(cand)) {
            pythonPath = cand;
            break;
        }
    }
    
    console.log(`🚀 Spawning Python API backend: ${pythonPath} ${apiScript}`);
    pythonProcess = spawn(pythonPath, [apiScript], {
        cwd: projectRoot,
        stdio: 'inherit',
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    pythonProcess.on('error', (err) => {
        console.error('❌ Failed to start Python backend API:', err);
    });

    pythonProcess.on('close', (code) => {
        console.log(`ℹ️ Python backend process exited with code ${code}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        fullscreen: true,
        frame: true,
        backgroundColor: '#060a14',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.setMenuBarVisibility(false);
    mainWindow.maximize();
    mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    startPythonBackend();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (pythonProcess) {
        console.log('Stopping Python process...');
        pythonProcess.kill('SIGTERM');
        pythonProcess = null;
    }
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('will-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill('SIGTERM');
    }
});

