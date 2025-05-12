import { state } from './state.js';
import { elements } from './elements.js';

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