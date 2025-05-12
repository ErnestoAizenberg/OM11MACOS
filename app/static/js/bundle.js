// Bundled by Pure Python JS Bundler
(function() {

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/app.js
const __module_app = (() => {
  const exports = {};
  const module = { exports };

const {state} = __module_state;
const {elements} = __module_elements;
const {initializeUI} = __module_ui;
const {toggleAgentStatus} = __module_agent;
const {toggleTelegramConnection, setupTelegramModal} = __module_telegram;
const {toggleBrowserConnection} = __module_browser;
const {sendCommand, renderCommandHistory, loadCommandHistory, clearCommandHistory, addCommandToHistory} = __module_commands;
const {toggleTheme, loadTheme} = __module_theme;
const {saveSettings} = __module_api;
const {initializeAutoRefresh} = __module_autorefresh;

// Event Listeners
export function setupEventListeners() {
  elements.startAgentBtn?.addEventListener('click', toggleAgentStatus);
  elements.connectTelegramBtn?.addEventListener('click', toggleTelegramConnection);
  elements.connectBrowserBtn?.addEventListener('click', toggleBrowserConnection);
  elements.sendCommandBtn?.addEventListener('click', sendCommand);
  elements.commandInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendCommand();
  });
  elements.clearHistoryBtn?.addEventListener('click', clearCommandHistory);
  elements.themeToggleBtn?.addEventListener('click', toggleTheme);

  elements.debugModeToggle?.addEventListener('change', (e) => {
    state.settings.debugMode = e.target.checked;
    saveSettings(state.settings);
  });

  elements.autoStartToggle?.addEventListener('change', (e) => {
    state.settings.autoStart = e.target.checked;
    saveSettings(state.settings);
  });

  elements.notificationsToggle?.addEventListener('change', (e) => {
    state.settings.notifications = e.target.checked;
    saveSettings(state.settings);
  });
}

// Initialize
document.addEventListener("DOMContentLoaded", function() {
  initializeUI();
  setupEventListeners();
  setupTelegramModal();
  initializeAutoRefresh();
  toggleTelegramConnection();
});

  return module.exports;
}})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/autorefresh.js
const __module_autorefresh = (() => {
  const exports = {};
  const module = { exports };

import { loadCommandHistory } from __module_commands;

let refreshInterval;
let activityTimeout;
const activityTimeoutDuration = 15000;

export function startAutoRefresh(interval = 5000) {
  if (refreshInterval) return;

  loadCommandHistory();
  refreshInterval = setInterval(loadCommandHistory, interval);
  resetActivityTimeout();
}

export function resetActivityTimeout() {
  if (activityTimeout) clearTimeout(activityTimeout);
  activityTimeout = setTimeout(stopAutoRefresh, activityTimeoutDuration);
}

export function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

export function addUserActivityListeners() {
  window.addEventListener('mousemove', resetActivityTimeout);
  window.addEventListener('keydown', resetActivityTimeout);
  window.addEventListener('scroll', resetActivityTimeout);
  window.addEventListener('touchstart', resetActivityTimeout);
}

export function initializeAutoRefresh() {
  addUserActivityListeners();
  startAutoRefresh();
}

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/browser.js
const __module_browser = (() => {
  const exports = {};
  const module = { exports };

const {state} = __module_state;
const {makeRequest} = __module_api;
const {showNotification} = __module_notifications;
const {updateBrowserStatus} = __module_ui;

export async function toggleBrowserConnection() {
  if (state.browserStatus === 'connected') {
    updateBrowserStatus('connecting');
    const result = await makeRequest('/api/browser/status', 'GET');
    
    if (result.success) {
      updateBrowserStatus('disconnected');
      showNotification('Browser disconnected successfully');
    } else {
      updateBrowserStatus('connected');
      showNotification(`Failed to disconnect browser: ${result.error || 'Unknown error'}`, 'error');
    }
  } else {
    updateBrowserStatus('connecting');
    const result = await makeRequest('/api/browser/connect', 'POST');
    
    if (result.success) {
      updateBrowserStatus('connected');
      showNotification('Browser connected successfully');
    } else {
      updateBrowserStatus('disconnected');
      showNotification(`Failed to connect browser: ${result.error || 'Unknown error'}`, 'error');
    }
  }
}

  return module.exports;
}})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/agent.js
const __module_agent = (() => {
  const exports = {};
  const module = { exports };

const {state} = __module_state;
const {makeRequest} = __module_api;
const {showNotification} = __module_notifications;
const {updateAgentStatus} = __module_ui;

export async function toggleAgentStatus() {
  if (state.agentStatus === 'online') {
    updateAgentStatus('connecting');
    const result = await makeRequest('/api/agent/stop', 'POST');
    
    if (result.success) {
      updateAgentStatus('offline');
      showNotification('Agent stopped successfully');
    } else {
      updateAgentStatus('online');
      showNotification(`Failed to stop agent: ${result.error || 'Unknown error'}`, 'error');
    }
  } else {
    updateAgentStatus('connecting');
    const result = await makeRequest('/api/agent/start', 'POST');
    
    if (result.success) {
      updateAgentStatus('online');
      showNotification('Agent started successfully');
    } else {
      updateAgentStatus('offline');
      showNotification(`Failed to start agent: ${result.error || 'Unknown error'}`, 'error');
    }
  }
}

  return module.exports;
}})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/telegram.js
const __module_telegram = (() => {
  const exports = {};
  const module = { exports };

import { makeRequest } from __module_api;
import { showNotification } from __module_notifications;
import { updateTelegramStatus } from __module_ui;

export async function toggleTelegramConnection() {
  const result = await makeRequest('/api/telegram/status', 'GET');
  if (!result.success) {
    console.log("Error while accessing api in toggleTelegramConnection function")
  }
  if (result.status === 'connected') {
    updateTelegramStatus('connected');
  } else {
    updateTelegramStatus('disconnected');
  }
}

export async function sendDisconnectRequest() {
  const result = await makeRequest('/api/telegram/disconnect', 'GET');
  if (result.status) {
    showNotification('Telegram disconnected successfully.')
  } else {
    showNotification(`Failed to disconnect Telegram: ${result.error || 'Unknown error'}`, 'error');
  }
}

export function setupTelegramModal() {
  const connectTelegramBtn = document.getElementById("openTelegramConnectMenu");
  const telegramModal = document.getElementById("telegramModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const submitTelegramBtn = document.getElementById("connectTelegramBtn");
  const statusMessage = document.getElementById("status-message");
  
  connectTelegramBtn?.addEventListener("click", () => telegramModal.classList.remove("hidden"));
  closeModalBtn?.addEventListener("click", () => telegramModal.classList.add("hidden"));

  submitTelegramBtn?.addEventListener("click", async function() {
    const botToken = document.getElementById('bot-token').value.trim();
    const chatId = document.getElementById('chat-id').value.trim();
    const webhookUrl = document.getElementById('webhook-url').value.trim();
    const updateMethod = document.querySelector('input[name="update-method"]:checked').value;

    if (!botToken || !chatId) {
      showStatus('Заполните обязательные поля', 'error');
      return;
    }

    showStatus('Проверяем подключение к Telegram...', 'info');

    try {
      const response = await fetch('/api/telegram/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bot_token: botToken,
          chat_id: chatId,
          webhook_url: webhookUrl || null,
          update_method: updateMethod
        })
      });

      const data = await response.json();

      if (data.success) {
        showStatus(`✅ ${data.message} | User ID: ${data.user_id}`, 'success');
        localStorage.setItem('telegram_bot_user_id', data.user_id);
        toggleTelegramConnection();
      } else {
        showStatus(`❌ ${data.error}`, 'error');
      }
    } catch (error) {
      showStatus(`❌ Ошибка сети: ${error.message}`, 'error');
    }
  });

  function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `${type === 'success' ? 'text-green-600' : 'text-red-600'} mt-2`; 
    statusMessage.classList.remove("hidden");
    
    setTimeout(() => {
      statusMessage.classList.add("hidden");
    }, 7000);
  }
}

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/ui.js
const __module_ui = (() => {
  const exports = {};
  const module = { exports };

import { state } from __module_state;
import { elements } from __module_elements;
import { loadCommandHistory } from __module_commands;
import { loadTheme } from __module_theme;

// Initialize UI from state
export function initializeUI() {
  // Set initial status indicators
  updateAgentStatus(state.agentStatus);
  updateTelegramStatus(state.telegramStatus);
  updateBrowserStatus(state.browserStatus);
  
  // Set initial toggle states
  elements.debugModeToggle.checked = state.settings.debugMode;
  elements.autoStartToggle.checked = state.settings.autoStart;
  elements.notificationsToggle.checked = state.settings.notifications;
  
  // Load command history
  loadCommandHistory();
  loadTheme();
}

export function updateAgentStatus(status) {
  state.agentStatus = status;
  const indicator = elements.agentStatusIndicator;
  const text = elements.agentStatusText;
  
  switch(status) {
    case 'online':
      indicator.className = 'w-3 h-3 rounded-full bg-green-500 mr-2';
      text.textContent = 'Agent Online';
      elements.startAgentBtn.innerHTML = '<i class="fas fa-stop mr-2"></i> Stop Agent';
      break;
    case 'offline':
      indicator.className = 'w-3 h-3 rounded-full bg-red-500 mr-2';
      text.textContent = 'Agent Offline';
      elements.startAgentBtn.innerHTML = '<i class="fas fa-play mr-2"></i> Start Agent';
      break;
    case 'connecting':
      indicator.className = 'w-3 h-3 rounded-full bg-yellow-500 mr-2';
      text.textContent = 'Connecting...';
      elements.startAgentBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Connecting';
      break;
  }
}

export function updateTelegramStatus(status) {
  state.telegramStatus = status;
  const indicator = elements.telegramStatusIndicator;
  const text = elements.telegramStatusText;
  const button = elements.connectTelegramBtn;

  switch(status) {
    case 'connected':
      indicator.className = 'w-3 h-3 rounded-full bg-green-500 mr-2';
      text.textContent = 'Connected';
      button.innerHTML = '<i class="fas fa-unlink mr-2"></i> Disconnect Telegram';
      button.id = 'disconnectTelegramBtn';
      break;
    case 'disconnected':
      indicator.className = 'w-3 h-3 rounded-full bg-red-500 mr-2';
      text.textContent = 'Disconnected';
      button.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Connect Telegram';
      break;
    case 'connecting':
      indicator.className = 'w-3 h-3 rounded-full bg-yellow-500 mr-2';
      text.textContent = 'Connecting...';
      button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Connecting';
      break;
  }
}

export function updateBrowserStatus(status) {
  state.browserStatus = status;
  const indicator = elements.browserStatusIndicator;
  const text = elements.browserStatusText;
  
  switch(status) {
    case 'connected':
      indicator.className = 'w-3 h-3 rounded-full bg-green-500 mr-2';
      text.textContent = 'Connected';
      elements.connectBrowserBtn.innerHTML = '<i class="fas fa-unlink mr-2"></i> Disconnect Browser';
      break;
    case 'disconnected':
      indicator.className = 'w-3 h-3 rounded-full bg-red-500 mr-2';
      text.textContent = 'Disconnected';
      elements.connectBrowserBtn.innerHTML = '<i class="fas fa-globe mr-2"></i> Connect Browser';
      break;
    case 'connecting':
      indicator.className = 'w-3 h-3 rounded-full bg-yellow-500 mr-2';
      text.textContent = 'Connecting...';
      elements.connectBrowserBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Connecting';
      break;
  }
}

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/commands.js
const __module_commands = (() => {
  const exports = {};
  const module = { exports };

const {state} = __module_state;
const {elements} = __module_elements;
const {makeRequest} = __module_api;

export function addCommandToHistory(response, isUser = true) {
  const timestamp = new Date();
  state.commandHistory.push({
    command: response,
    isUser,
    timestamp
  });
  
  if (state.commandHistory.length > 50) {
    state.commandHistory.shift();
  }
  
  renderCommandHistory();
}

export function clearCommandHistory() {
  state.commandHistory = [];
  elements.commandHistoryContainer.innerHTML = '';
}

export async function loadCommandHistory() {
  try {
    const data = await makeRequest('/api/command/history');
    
    if (data.success && Array.isArray(data.command_history)) {
      state.commandHistory = data.command_history;
      renderCommandHistory();
    }
  } catch (error) {
    console.error("Error fetching command history:", error);
  }
}

export function renderCommandHistory() {
  elements.commandHistoryContainer.innerHTML = '';
  
  state.commandHistory.forEach(item => {
    if (typeof item.command !== 'string') return;

    const bubbleClass = item.isUser ? 'chat-start' : 'chat-end';
    const bubbleType = item.isUser ? 'chat-bubble-primary' : '';
    const timeString = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat ${bubbleClass} mb-2`;
    messageDiv.innerHTML = `
      <div class="chat-bubble ${bubbleType}">${item.command}</div>
      <div class="chat-footer opacity-50 text-xs">${timeString}</div>
    `;
    
    elements.commandHistoryContainer.appendChild(messageDiv);
  });
  
  elements.commandHistoryContainer.scrollTop = elements.commandHistoryContainer.scrollHeight;
}

export async function sendCommand() {
  const command = elements.commandInput.value.trim();
  if (!command) return;
  
  addCommandToHistory(command, true);
  elements.commandInput.value = '';
  
  try {
    const result = await makeRequest('/api/command', 'POST', { command });
    
    if (result.success) {
      addCommandToHistory(result.output, false);
    } else {
      addCommandToHistory(`Error: ${result.error || 'Command execution failed'}`, false);
    }
  } catch (error) {
    addCommandToHistory(`Network error: ${error.message}`, false);
  }
}

  return module.exports;
}})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/api.js
const __module_api = (() => {
  const exports = {};
  const module = { exports };

import { showNotification } from __module_notifications;

export async function makeRequest(endpoint, method = 'GET', body = null) {
  try {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(endpoint, options);
    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
    return { success: false, error: 'Network error' };
  }
}

export async function saveSettings(settings) {
  const result = await makeRequest('/api/settings', 'POST', settings);
  
  if (result.success) {
    showNotification('Settings saved successfully');
  } else {
    showNotification(`Failed to save settings: ${result.error || 'Unknown error'}`, 'error');
  }
}

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/notifications.js
const __module_notifications = (() => {
  const exports = {};
  const module = { exports };

import { state } from __module_state;

export function showNotification(message, type = 'info') {
  if (!state.settings.notifications) return;
  
  const notification = document.createElement('div');
  notification.className = `toast toast-top toast-end`;
  
  let alertClass = 'alert-info';
  if (type === 'error') alertClass = 'alert-error';
  else if (type === 'success') alertClass = 'alert-success';
  
  notification.innerHTML = `
    <div class="alert ${alertClass} shadow-lg">
      <div>
        <span>${message}</span>
      </div>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/theme.js
const __module_theme = (() => {
  const exports = {};
  const module = { exports };

import { state } from __module_state;
import { elements } from __module_elements;

export function toggleTheme() {
  const newTheme = state.theme === 'night' ? 'light' : 'night';
  state.theme = newTheme;
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('openmanus-theme', newTheme);
  
  const icon = elements.themeToggleBtn.querySelector('i');
  icon.className = newTheme === 'night' ? 'fas fa-adjust' : 'fas fa-moon';
}

export function loadTheme() {
  const savedTheme = localStorage.getItem('openmanus-theme');
  if (savedTheme) {
    state.theme = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const icon = elements.themeToggleBtn.querySelector('i');
    icon.className = savedTheme === 'night' ? 'fas fa-adjust' : 'fas fa-moon';
  }
}

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/elements.js
const __module_elements = (() => {
  const exports = {};
  const module = { exports };

// DOM Elements
export const elements = {
  agentStatusIndicator: document.getElementById('agentStatusIndicator'),
  agentStatusText: document.getElementById('agentStatusText'),
  startAgentBtn: document.getElementById('startAgentBtn'),
  connectTelegramBtn: document.getElementById('connectTelegramBtn'),
  connectBrowserBtn: document.getElementById('connectBrowserBtn'),
  debugModeToggle: document.getElementById('debugModeToggle'),
  autoStartToggle: document.getElementById('autoStartToggle'),
  notificationsToggle: document.getElementById('notificationsToggle'),
  commandInput: document.getElementById('commandInput'),
  sendCommandBtn: document.getElementById('sendCommandBtn'),
  commandHistoryContainer: document.getElementById('commandHistoryContainer'),
  clearHistoryBtn: document.getElementById('clearHistoryBtn'),
  telegramStatusIndicator: document.getElementById('telegramStatusIndicator'),
  telegramStatusText: document.getElementById('telegramStatusText'),
  browserStatusIndicator: document.getElementById('browserStatusIndicator'),
  browserStatusText: document.getElementById('browserStatusText'),
  themeToggleBtn: document.getElementById('themeToggleBtn')
};

  return module.exports;
})();

// Module: /storage/emulated/0/gitserver/om11/om11/static/js/state.js
const __module_state = (() => {
  const exports = {};
  const module = { exports };

// App State
export const state = {
  agentStatus: 'offline',
  telegramStatus: 'disconnected',
  browserStatus: 'disconnected',
  settings: {
    debugMode: false,
    autoStart: false,
    notifications: true
  },
  commandHistory: [],
  theme: document.documentElement.getAttribute('data-theme') || 'night'
};

  return module.exports;
})();


// Запуск приложения
const __main = __module_app;
if (typeof window !== 'undefined') window.app = __main;
if (typeof module !== 'undefined' && module.exports) module.exports = __main;

})();
