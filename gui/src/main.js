const { app, dialog, BrowserWindow, Menu, net } = require('electron'); // eslint-disable-line import/no-extraneous-dependencies
const childProcess = require('child_process');
const path = require('path');
const rq = require('request-promise');
const settings = require('electron-settings');

const darwin = (process.platform === 'darwin');

// TODO: pick an open random port.
const port = 8899;
const mainAddr = `http://localhost:${port}`;

let splashScreenWindow;
let mainWindow;
let subprocess;

function chooseFilename() {
  const fileNames = dialog.showOpenDialog({ title: 'Choose Beancount file' });
  if (fileNames === undefined) {
    return false;
  }
  let values = settings.get('beancount-file');
  if (!values) {
    values = [];
  }
  settings.set('beancount-file', values.concat(fileNames));
  return true;
}

function startFava() {
  const args = [
    '-p',
    port,
  ].concat(settings.get('beancount-file', []));

  let favaPath;
  if (__dirname.match('app.asar')) {
    favaPath = `${app.getAppPath()}/bin/fava`.replace('app.asar', 'app.asar.unpacked');
  } else {
    favaPath = path.join(__dirname, '../bin/fava');
  }

  // click aborts if the locale is not set
  const process = childProcess.execFile(favaPath, args, { env: { LC_ALL: 'en_US.UTF-8' } });

  // process.on('error', () => { console.log('Failed to start Fava.'); });
  // process.stdout.on('data', (data) => { console.log(`Fava stdout: ${data}`); });
  // process.stderr.on('data', (data) => { console.log(`Fava stderr: ${data}`); });
  // process.on('close', (code) => { console.log(`Fava exited with code ${code}`); });

  return process;
}

function loadMainPage() {
  rq(mainAddr)
    .then(() => {
      mainWindow.setBounds(settings.get('bounds', {
        width: 1260,
        height: 800,
      }));
      mainWindow.loadURL(mainAddr);
    })
  .catch(() => {
    loadMainPage();
  });
}

function openBeancountFile() {
  if (!chooseFilename()) {
    return;
  }
  subprocess.kill('SIGTERM');
  subprocess = startFava();
  loadMainPage();
}

const currentVersion = 'v1.4';
const updateURL = 'https://api.github.com/repos/beancount/fava/releases/latest';

function updateCheck() {
  const request = net.request(updateURL);
  request.on('response', (response) => {
    let responseData = '';
    response.on('data', (chunk) => {
      responseData += chunk;
    });
    response.on('end', () => {
      const latestVersion = JSON.parse(responseData).name;
      if (latestVersion.length !== currentVersion.length
          || (+latestVersion.slice(-1) > +currentVersion.slice(-1)
              || +latestVersion.slice(-3) > +currentVersion.slice(-3))) {
        dialog.showMessageBox({
          message: `An update is available online: ${latestVersion} (you have ${currentVersion})`,
          callback: () => {},
        });
      }
    });
  });
  request.on('error', () => {});
  request.end();
}

function resetFiles() {
  settings.set('beancount-file', []);
  openBeancountFile();
}

const menu = Menu.buildFromTemplate([
  {
    label: 'Fava',
    submenu: [
      {
        role: 'quit',
      },
    ],
  },
  {
    label: 'File',
    submenu: [
      {
        label: 'Open Beancount file',
        accelerator: 'CmdOrCtrl+O',
        click: openBeancountFile,
      },
      {
        label: 'Reset files',
        click: resetFiles,
      },
    ],
  },
  {
    label: 'View',
    submenu: [
      {
        label: 'Reload',
        accelerator: 'CmdOrCtrl+R',
        click(item, focusedWindow) {
          if (focusedWindow) focusedWindow.reload();
        },
      },
      {
        label: 'Toggle Developer Tools',
        accelerator: darwin ? 'Alt+Command+I' : 'Ctrl+Shift+I',
        click(item, focusedWindow) {
          if (focusedWindow) focusedWindow.webContents.toggleDevTools();
        },
      },
      {
        type: 'separator',
      },
      {
        role: 'resetzoom',
      },
      {
        role: 'zoomin',
      },
      {
        role: 'zoomout',
      },
      {
        type: 'separator',
      },
      {
        role: 'togglefullscreen',
      },
    ],
  },
  {
    role: 'window',
    submenu: [
      {
        role: 'minimize',
      },
      {
        role: 'close',
      },
    ],
  },
]);

function createSplashScreenWindow() {
  let win = new BrowserWindow({
    width: 500,
    height: 250,
    frame: false,
  });

  win.loadURL(`file://${__dirname}/index.html`);

  win.on('closed', () => {
    win = null;
  });

  return win;
}

function createMainWindow() {
  let win = new BrowserWindow({
    'node-integration': false,
    minWidth: 500,
    width: 500,
    minHeight: 250,
    height: 250,
    show: false,
    titleBarStyle: 'hidden-inset',
  });

  win.once('ready-to-show', () => {
    splashScreenWindow.close();
    win.show();
  });

  win.webContents.on('did-finish-load', () => {
    if (darwin) {
      win.webContents.insertCSS(`
          body header {
            -webkit-app-region: drag;
            padding-left: 80px;
          }

          body header form {
            -webkit-app-region: no-drag;
          }
          `);
    } else {
      win.webContents.insertCSS(`
          body header {
            -webkit-app-region: drag;
          }

          body header form {
            -webkit-app-region: no-drag;
          }
          `);
    }
  });

  win.on('close', () => {
    settings.set('bounds', win.getBounds());
  });

  win.on('closed', () => {
    win = null;
  });

  return win;
}

app.on('activate', () => {
  if (mainWindow === null) {
    mainWindow = createMainWindow();
  }
});

app.on('window-all-closed', () => {
  if (!darwin) {
    app.quit();
  }
});

app.on('quit', () => {
  if (!mainWindow.isDestroyed()) {
    mainWindow.close();
  }
  subprocess.kill('SIGTERM');
});

app.on('ready', () => {
  updateCheck();
  Menu.setApplicationMenu(menu);

  const files = settings.get('beancount-file');
  if (!files || !files.length) {
    chooseFilename();
  }

  splashScreenWindow = createSplashScreenWindow();
  mainWindow = createMainWindow();

  subprocess = startFava();
  loadMainPage();
});
