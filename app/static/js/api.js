import { showNotification } from './notifications.js';

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