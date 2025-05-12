import { loadCommandHistory } from './commands.js';

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