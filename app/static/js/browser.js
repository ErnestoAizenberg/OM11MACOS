import { state } from './state.js';
import { makeRequest } from './api.js';
import { showNotification } from './notifications.js';
import { updateBrowserStatus } from './ui.js';

// DOM elements for browser modal
const browserModal = document.getElementById('browserModal');
const browserApiUrlInput = document.getElementById('browserApiUrl');
const browserTypeSelect = document.getElementById('browserType');
const fetchProfilesBtn = document.getElementById('fetchProfilesBtn');
const profilesList = document.getElementById('browserProfilesList');
const startProfilesBtn = document.getElementById('startProfilesBtn');
const browserStatusMessage = document.getElementById('browserStatusMessage');
const closeBrowserModalBtn = document.getElementById('closeBrowserModalBtn');

// Browser types configuration
const BROWSER_TYPES = [
  { id: 'octo', name: 'Octo Browser' },
  { id: 'undetectable', name: 'Undetectable' },
  { id: 'vision', name: 'Vision Browser' },
  { id: 'linken', name: 'Linken Sphere' }
];
// Initialize browser modal
export function initBrowserModal() {
  // Populate browser types
  browserTypeSelect.innerHTML = BROWSER_TYPES.map(
    type => `<option value="${type.id}">${type.name}</option>`
  ).join('');

  // Set up event listeners
  fetchProfilesBtn.addEventListener('click', fetchProfiles);
  startProfilesBtn.addEventListener('click', startProfiles);
  closeBrowserModalBtn.addEventListener('click', closeBrowserModal);
}

// Open browser modal
function openBrowserModal() {
  browserModal.classList.remove('hidden');
  updateBrowserStatus('connecting');
}

// Close browser modal
function closeBrowserModal() {
  browserModal.classList.add('hidden');
}

// Fetch profiles from API
async function fetchProfiles() {
  const apiUrl = browserApiUrlInput.value.trim();
  const browserType = browserTypeSelect.value;

  if (!apiUrl) {
    showNotification('Please enter API URL', 'error');
    return;
  }

  try {
    const response = await makeRequest(
      `/api/browser/profiles?api_url=${encodeURIComponent(apiUrl)}&type=${browserType}`
    );

    if (response.success) {
      renderProfilesList(response.profiles);
      browserStatusMessage.textContent = `${response.profiles.length} profiles found`;
    } else {
      showNotification(response.error || 'Failed to fetch profiles', 'error');
    }
  } catch (error) {
    showNotification('Network error while fetching profiles', 'error');
    console.error('Fetch profiles error:', error);
  }
}

// Render profiles list with checkboxes
function renderProfilesList(profiles) {
  profilesList.innerHTML = profiles
    .map(
      profile => `
      <div class="flex items-center mb-2">
        <input type="checkbox" id="profile_${profile.id}" value="${profile.id}" class="mr-2">
        <label for="profile_${profile.id}">${profile.name} (${profile.id})</label>
      </div>
    `
    )
    .join('');
}

// Start selected profiles
async function startProfiles() {
  const apiUrl = browserApiUrlInput.value.trim();
  const browserType = browserTypeSelect.value;
  const selectedProfiles = Array.from(
    document.querySelectorAll('#browserProfilesList input[type="checkbox"]:checked')
  ).map(checkbox => checkbox.value);

  if (selectedProfiles.length === 0) {
    showNotification('Please select at least one profile', 'error');
    return;
  }

  try {
    const results = await Promise.all(
      selectedProfiles.map(profileId =>
        makeRequest('/api/browser/start', 'POST', {
          api_url: apiUrl,
          type: browserType,
          profile_id: profileId
        })
      )
    );

    const successfulStarts = results.filter(r => r.success).length;
    const failedStarts = results.filter(r => !r.success);

    if (failedStarts.length > 0) {
      showNotification(
        `${successfulStarts} profiles started, ${failedStarts.length} failed`,
        'warning'
      );
    } else {
      showNotification(`All ${successfulStarts} profiles started successfully`, 'success');
    }

    updateBrowserStatus('connected');
    browserStatusMessage.textContent = `${successfulStarts} profiles active`;
    closeBrowserModal();
  } catch (error) {
    showNotification('Error starting profiles', 'error');
    console.error('Start profiles error:', error);
  }
}

// Modified toggle function to open modal instead of direct connection
export async function toggleBrowserConnection() {
  if (state.browserStatus === 'connected') {
    updateBrowserStatus('connecting');
    const result = await makeRequest('/api/browser/disconnect', 'POST');
    
    if (result.success) {
      updateBrowserStatus('disconnected');
      showNotification('All browser profiles disconnected');
    } else {
      updateBrowserStatus('connected');
      showNotification(`Failed to disconnect: ${result.error || 'Unknown error'}`, 'error');
    }
  } else {
    openBrowserModal();
  }

  const observer = new MutationObserver(() => {
    updateModalTheme();
  });
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
  });
}

function updateModalTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'night';
  if (isDark) {
    browserModal.classList.add('dark');
  } else {
    browserModal.classList.remove('dark');
  }
}