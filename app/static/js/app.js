import { state } from './state.js';
import { elements } from './elements.js';
import { initializeUI } from './ui.js';
import { toggleAgentStatus } from './agent.js';
import { TelegramManager } from './telegram.js';
import { toggleBrowserConnection, initBrowserModal } from './browser.js';
import { sendCommand, renderCommandHistory, loadCommandHistory, clearCommandHistory, addCommandToHistory } from './commands.js';
import { toggleTheme, loadTheme } from './theme.js';
import { saveSettings } from './api.js';
import { initializeAutoRefresh } from './autorefresh.js';


// Event Listeners
export function setupEventListeners() {
  elements.startAgentBtn?.addEventListener('click', toggleAgentStatus);
  // elements.connectTelegramBtn?.addEventListener('click', toggleTelegramConnection);
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
  // setupTelegramModal();
  TelegramManager.init();
  initBrowserModal(); // Add this line
  //initializeAutoRefresh();
  // toggleTelegramConnection();
});
