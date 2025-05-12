import { state } from './state.js';
import { elements } from './elements.js';
import { loadCommandHistory } from './commands.js';
import { loadTheme } from './theme.js';

// Initialize UI from state
export function initializeUI() {
  // Set initial status indicators
  updateAgentStatus(state.agentStatus);
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