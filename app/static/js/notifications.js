import { state } from './state.js';

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