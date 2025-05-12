import { state } from './state.js';
import { makeRequest } from './api.js';
import { showNotification } from './notifications.js';
import { updateAgentStatus } from './ui.js';

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