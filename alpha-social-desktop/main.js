const { app, BrowserWindow, Menu, shell, ipcMain, dialog, nativeTheme } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

// 保持对窗口对象的全局引用
let mainWindow
let apiServer

// 开发模式检测
const isDev = process.env.NODE_ENV === 'development'

// 应用配置
const APP_CONFIG = {
  name: 'Alpha Social',
  version: '1.0.0',
  description: '去中心化社交网络',
  author: 'Alpha Team',
  website: 'https://alpha-social.com',
  frontendUrl: isDev ? 'http://localhost:5173' : 'http://localhost:3000',
  apiUrl: 'http://localhost:5000'
}

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false, // 先不显示，等加载完成后再显示
    backgroundColor: '#ffffff'
  })

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    
    // 开发模式下打开开发者工具
    if (isDev) {
      mainWindow.webContents.openDevTools()
    }
  })

  // 加载应用
  loadApp()

  // 处理窗口关闭
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 处理外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // 阻止导航到外部网站
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl)
    
    if (parsedUrl.origin !== new URL(APP_CONFIG.frontendUrl).origin) {
      event.preventDefault()
      shell.openExternal(navigationUrl)
    }
  })
}

async function loadApp() {
  try {
    // 检查前端服务是否可用
    const isServerRunning = await checkServer(APP_CONFIG.frontendUrl)
    
    if (isServerRunning) {
      console.log('Frontend server is running, loading app...')
      mainWindow.loadURL(APP_CONFIG.frontendUrl)
    } else {
      console.log('Frontend server not running, showing loading page...')
      mainWindow.loadFile(path.join(__dirname, 'loading.html'))
      
      // 尝试启动服务
      startServices()
    }
  } catch (error) {
    console.error('Failed to load app:', error)
    mainWindow.loadFile(path.join(__dirname, 'error.html'))
  }
}

async function checkServer(url) {
  try {
    const response = await fetch(url)
    return response.ok
  } catch (error) {
    return false
  }
}

function startServices() {
  // 这里可以启动内置的服务
  console.log('Starting Alpha Social services...')
  
  // 模拟服务启动
  setTimeout(() => {
    if (mainWindow) {
      mainWindow.loadURL(APP_CONFIG.frontendUrl)
    }
  }, 3000)
}

// 创建应用菜单
function createMenu() {
  const template = [
    {
      label: 'Alpha Social',
      submenu: [
        {
          label: '关于 Alpha Social',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '关于 Alpha Social',
              message: APP_CONFIG.name,
              detail: `版本: ${APP_CONFIG.version}\n${APP_CONFIG.description}\n\n基于区块链的去中心化社交网络平台`
            })
          }
        },
        { type: 'separator' },
        {
          label: '偏好设置',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            // 打开设置页面
            mainWindow.webContents.send('open-settings')
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: '全选', accelerator: 'CmdOrCtrl+A', role: 'selectall' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { label: '重新加载', accelerator: 'CmdOrCtrl+R', role: 'reload' },
        { label: '强制重新加载', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
        { label: '开发者工具', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: '实际大小', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
        { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
        { label: '缩小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
        { type: 'separator' },
        { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
      ]
    },
    {
      label: '窗口',
      submenu: [
        { label: '最小化', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
        { label: '关闭', accelerator: 'CmdOrCtrl+W', role: 'close' }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '官方网站',
          click: () => {
            shell.openExternal(APP_CONFIG.website)
          }
        },
        {
          label: '用户指南',
          click: () => {
            shell.openExternal(`${APP_CONFIG.website}/guide`)
          }
        },
        {
          label: '反馈问题',
          click: () => {
            shell.openExternal(`${APP_CONFIG.website}/feedback`)
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

// IPC 事件处理
ipcMain.handle('get-app-info', () => {
  return APP_CONFIG
})

ipcMain.handle('get-theme', () => {
  return nativeTheme.shouldUseDarkColors ? 'dark' : 'light'
})

ipcMain.handle('set-theme', (event, theme) => {
  nativeTheme.themeSource = theme
  return theme
})

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options)
  return result
})

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options)
  return result
})

// 应用事件处理
app.whenReady().then(() => {
  createWindow()
  createMenu()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  // 清理资源
  if (apiServer) {
    apiServer.kill()
  }
})

// 安全设置
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault()
    shell.openExternal(navigationUrl)
  })
})

// 处理协议
app.setAsDefaultProtocolClient('alpha-social')

// 处理深度链接
app.on('open-url', (event, url) => {
  event.preventDefault()
  console.log('Deep link:', url)
  
  if (mainWindow) {
    mainWindow.webContents.send('deep-link', url)
  }
})

// 单实例锁定
const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // 当运行第二个实例时，聚焦到主窗口
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })
}

