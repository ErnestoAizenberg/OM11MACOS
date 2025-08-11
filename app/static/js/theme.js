import { state } from './state.js';
import { elements } from './elements.js';

export function toggleTheme() {
  const newTheme = state.theme === 'night' ? 'light' : 'night';
  state.theme = newTheme;
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('openmanus-theme', newTheme);

  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const moonIcon = themeToggleBtn.querySelector('#moon-icon'); // Используем ID вместо класса
  const adjustIcon = themeToggleBtn.querySelector('#adjust-icon'); // Используем ID вместо класса

  if (newTheme === 'night') {
    moonIcon.style.display = 'none';
    adjustIcon.style.display = 'block';
  } else {
    moonIcon.style.display = 'block';
    adjustIcon.style.display = 'none';
  }
}

export function loadTheme() {
  const savedTheme = localStorage.getItem('openmanus-theme');
  if (savedTheme) {
    state.theme = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const moonIcon = themeToggleBtn.querySelector('#moon-icon');
    const adjustIcon = themeToggleBtn.querySelector('#adjust-icon');

    if (savedTheme === 'night') {
      moonIcon.style.display = 'none';
      adjustIcon.style.display = 'block';
    } else {
      moonIcon.style.display = 'block';
      adjustIcon.style.display = 'none';
    }
  }
}
