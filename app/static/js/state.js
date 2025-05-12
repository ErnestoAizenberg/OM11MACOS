// App State
export const state = {
  agentStatus: 'offline',
  telegramStatus: 'disconnected', // 'disconnected' | 'connecting' | 'connected' | 'error'
  browserStatus: 'disconnected',
  settings: {
    debugMode: false,
    autoStart: false,
    notifications: true
  },
  commandHistory: [],
  theme: document.documentElement.getAttribute('data-theme') || 'night'
};