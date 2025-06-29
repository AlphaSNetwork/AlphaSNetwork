const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 应用信息
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  
  // 主题管理
  getTheme: () => ipcRenderer.invoke('get-theme'),
  setTheme: (theme) => ipcRenderer.invoke('set-theme', theme),
  
  // 文件对话框
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  
  // 事件监听
  onDeepLink: (callback) => {
    ipcRenderer.on('deep-link', (event, url) => callback(url))
  },
  
  onOpenSettings: (callback) => {
    ipcRenderer.on('open-settings', () => callback())
  },
  
  // 移除监听器
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel)
  }
})

// 平台信息
contextBridge.exposeInMainWorld('platform', {
  os: process.platform,
  arch: process.arch,
  version: process.versions
})

// 控制台日志（仅开发模式）
if (process.env.NODE_ENV === 'development') {
  contextBridge.exposeInMainWorld('electronConsole', {
    log: (...args) => console.log('[Renderer]', ...args),
    error: (...args) => console.error('[Renderer]', ...args),
    warn: (...args) => console.warn('[Renderer]', ...args)
  })
}

