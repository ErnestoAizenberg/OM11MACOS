import { state } from './state.js';
import { elements } from './elements.js';
import { makeRequest } from './api.js';

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