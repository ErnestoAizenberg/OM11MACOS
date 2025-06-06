document.addEventListener('DOMContentLoaded', function() {
  // ======================
  // Configuration Constants
  // ======================
  const CONFIG = {
    DEBUG_MODE: true,
    SUBMISSION_COOLDOWN: 2000, // 2 seconds
    DEBOUNCE_DELAY: 300,
    REDIRECT_DELAY: 1500,
    FORM_SWITCH_DELAY: 3000,
    MIN_PASSWORD_LENGTH: {
      LOGIN: 6,
      SIGNUP: 8
    },
    API_ENDPOINTS: {
      LOGIN: '/api/login',
      SIGNUP: '/api/signup'
    },
    UI_TEXT: {
      LOGIN: {
        title: 'Sign in to your account',
        button: 'Sign In',
        toggleMessage: "Don't have an account? ",
        toggleAction: 'Sign up',
        submitting: 'Signing in...',
        success: 'Login successful! Redirecting...'
      },
      SIGNUP: {
        title: 'Create new account',
        button: 'Sign Up',
        toggleMessage: 'Already have an account? ',
        toggleAction: 'Sign in',
        submitting: 'Creating account...',
        success: 'Account created successfully!'
      }
    }
  };

  // ======================
  // DOM Element References
  // ======================
  const DOM = {
    dropdown: {
      button: document.getElementById('auth-dropdown-button'),
      panel: document.getElementById('auth-dropdown-panel')
    },
    form: document.getElementById('auth-form'),
    toggleAuth: document.getElementById('toggle-auth'),
    fields: {
      formTitle: document.getElementById('auth-form-title'),
      nameField: document.getElementById('name-field'),
      password: document.getElementById('password'),
      email: document.getElementById('email'),
      name: document.getElementById('name'),
      buttonText: document.getElementById('button-text')
    },
    messages: {
      error: document.getElementById('error-message'),
      success: document.getElementById('success-message'),
      toggle: document.getElementById('toggle-message'),
      authError: document.getElementById('auth-error'),
      authSuccess: document.getElementById('auth-success')
    },
    links: {
      forgotPassword: document.getElementById('forgot-password')
    },
    submitButton: document.getElementById('submit-button')
  };


  debugLog('Toggle Auth Element:', DOM.toggleAuth);

  // ======================
  // Application State
  // ======================
  const STATE = {
    authMode: 'login', // 'login' or 'signup'
    isSubmitting: false,
    lastSubmissionTime: 0,
    initialized: false,
    dropdownVisible: false
  };

  // ======================
  // Utility Functions
  // ======================

  /**
   * Debug logger with timestamp and context
   * @param {...any} messages - Messages to log
   */
  function debugLog(...messages) {
    if (CONFIG.DEBUG_MODE) {
      console.log(`[Auth][${new Date().toISOString()}]`, ...messages);
    }
  }

  /**
   * Debounce function to limit rapid executions
   * @param {Function} fn - Function to debounce
   * @param {number} delay - Delay in milliseconds
   * @returns {Function} Debounced function
   */
  function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  /**
   * Toggle dropdown visibility with animation
   */
// Получение элементов
const dropdownButton = document.getElementById('auth-dropdown-button');
const dropdownPanel = document.getElementById('auth-dropdown-panel');

function toggleDropdown() {
  const isHidden = dropdownPanel.classList.contains('hidden');

  if (isHidden) {
    // Показываем
    dropdownPanel.classList.remove('hidden');
    // Анимация появления
    dropdownPanel.classList.remove('opacity-0', 'scale-95');
    dropdownPanel.classList.add('opacity-100', 'scale-100');

    // Обновляем aria-expanded
    dropdownButton.setAttribute('aria-expanded', 'true');

    console.log('Dropdown shown');
  } else {
    // Скрываем
    dropdownPanel.classList.remove('opacity-100', 'scale-100');
    dropdownPanel.classList.add('opacity-0', 'scale-95');

    // После анимации можно скрывать полностью, но для простоты
    // можно оставить так, или через setTimeout
    // например, через 200ms добавить 'hidden', чтобы дать время анимации
    setTimeout(() => {
      dropdownPanel.classList.add('hidden');
    }, 200);

    // Обновляем aria-expanded
    dropdownButton.setAttribute('aria-expanded', 'false');

    console.log('Dropdown hidden');
  }
  updateFormUI();
}

// Обработчик клика
dropdownButton.addEventListener('click', toggleDropdown);
  // ======================
  // Form Management
  // ======================

  /**
   * Initialize form state and UI
   */
  function initializeForm() {
    if (STATE.initialized) {
      debugLog('Form already initialized');
      return;
    }

    updateFormUI();
    STATE.initialized = true;
    debugLog('Form initialized in', STATE.authMode, 'mode');
  }

  /**
   * Update UI based on current auth mode
   */
  function updateFormUI() {
    const isLogin = STATE.authMode === 'login';
    const uiText = CONFIG.UI_TEXT[isLogin ? 'LOGIN' : 'SIGNUP'];

    // Update text content
    DOM.fields.formTitle.textContent = uiText.title;
    DOM.fields.buttonText.textContent = uiText.button;
    DOM.messages.toggle.textContent = uiText.toggleMessage;
    DOM.toggleAuth.textContent = uiText.toggleAction;

    // Toggle visibility
    DOM.fields.nameField.classList.toggle('hidden', isLogin);
    DOM.links.forgotPassword.classList.toggle('hidden', !isLogin);

    // Update password requirements
    DOM.fields.password.minLength = isLogin 
      ? CONFIG.MIN_PASSWORD_LENGTH.LOGIN 
      : CONFIG.MIN_PASSWORD_LENGTH.SIGNUP;

    // Clear messages
    hideMessages();
  }

  /**
   * Toggle between login and signup modes
   */
  function toggleAuthMode() {
    debugLog('Current auth mode before toggle:', STATE.authMode);
    STATE.authMode = STATE.authMode === 'login' ? 'signup' : 'login';
    debugLog('New auth mode after toggle:', STATE.authMode);
    
    // Reset form fields
    DOM.form.reset();
    updateFormUI();
  }

  // ======================
  // Validation & Error Handling
  // ======================

  /**
   * Validate form inputs
   * @returns {Object} Validation result {isValid: boolean, errors: string[]}
   */
  function validateForm() {
    const errors = [];
    const { email, password, name } = DOM.fields;
    const isLogin = STATE.authMode === 'login';

    // Email validation
    if (!email.value.trim()) {
      errors.push('Email is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      errors.push('Please enter a valid email address');
    }

    // Password validation
    if (!password.value) {
      errors.push('Password is required');
    } else if (password.value.length < (isLogin ? CONFIG.MIN_PASSWORD_LENGTH.LOGIN : CONFIG.MIN_PASSWORD_LENGTH.SIGNUP)) {
      errors.push(`Password must be at least ${isLogin ? CONFIG.MIN_PASSWORD_LENGTH.LOGIN : CONFIG.MIN_PASSWORD_LENGTH.SIGNUP} characters`);
    }

    // Name validation for signup
    if (!isLogin && !name.value.trim()) {
      errors.push('Name is required');
    }

    return {
      isValid: errors.length === 0,
      errors: errors.length > 0 ? errors.join('\n') : null
    };
  }

  /**
   * Display error message
   * @param {string|Error} error - Error message or object
   * @param {string} [context] - Context for debugging
   */
  function showError(error, context = '') {
    const message = typeof error === 'string' ? error : error.message || 'An unexpected error occurred';
    
    DOM.messages.error.textContent = message;
    DOM.messages.authError.classList.remove('hidden');
    DOM.messages.authSuccess.classList.add('hidden');
    
    debugLog(`Error${context ? ` in ${context}` : ''}:`, error);
  }

  /**
   * Display success message
   * @param {string} message - Success message
   */
  function showSuccess(message) {
    DOM.messages.success.textContent = message;
    DOM.messages.authSuccess.classList.remove('hidden');
    DOM.messages.authError.classList.add('hidden');
    debugLog('Success:', message);
  }

  /**
   * Hide all messages
   */
  function hideMessages() {
    DOM.messages.authError.classList.add('hidden');
    DOM.messages.authSuccess.classList.add('hidden');
  }

  // ======================
  // UI State Management
  // ======================

  /**
   * Update UI state during submission
   * @param {boolean} submitting - Whether form is submitting
   */
  function setSubmissionState(submitting) {
    STATE.isSubmitting = submitting;
    DOM.submitButton.disabled = submitting;

    const text = CONFIG.UI_TEXT[STATE.authMode === 'login' ? 'LOGIN' : 'SIGNUP'].submitting;

    if (submitting) {
      DOM.submitButton.innerHTML = `
        <svg class="w-4 h-4 mr-2 -ml-1 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>${text}</span>
      `;
      debugLog('Submission started');
    } else {
      DOM.submitButton.innerHTML = `<span id="button-text">${CONFIG.UI_TEXT[STATE.authMode === 'login' ? 'LOGIN' : 'SIGNUP'].button}</span>`;
      debugLog('Submission ended');
    }
  }

  // ======================
  // API Communication
  // ======================

  /**
   * Handle API response errors
   * @param {Response} response - Fetch response object
   * @returns {Promise<Object>} Parsed error data
   */
  async function handleApiError(response) {
    try {
      const errorData = await response.json();
      return new Error(errorData.message || `API request failed with status ${response.status}`);
    } catch (parseError) {
      return new Error(`Server error: ${response.status} ${response.statusText}`);
    }
  }

  /**
   * Submit authentication data to server
   * @returns {Promise<Object>} Response data
   */
  async function submitAuthData() {
    debugLog("Submiting form!");
    const endpoint = STATE.authMode === 'login' 
      ? CONFIG.API_ENDPOINTS.LOGIN 
      : CONFIG.API_ENDPOINTS.SIGNUP;

    const formData = {
      email: DOM.fields.email.value.trim(),
      password: DOM.fields.password.value
    };

    if (STATE.authMode === 'signup') {
      formData.name = DOM.fields.name.value.trim();
    }

    debugLog('Submitting to', endpoint, 'with data:', { ...formData, password: '***' });

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
      credentials: 'include'
    });

    if (!response.ok) {
      throw await handleApiError(response);
    }

    return response.json();
  }

  /**
   * Handle successful authentication
   * @param {Object} data - Response data
   */
function handleAuthSuccess(data) {
  const isLogin = STATE.authMode === 'login';
  const successMessage = CONFIG.UI_TEXT[isLogin ? 'LOGIN' : 'SIGNUP'].success;
  
  showSuccess(successMessage);

  if (isLogin) {
    debugLog('Redirecting to dashboard...');
    setTimeout(() => {
      window.location.href = data.redirectUrl || '/dashboard';
    }, CONFIG.REDIRECT_DELAY);
  } else {
    debugLog('Switching to login form...');
    // Immediately update the state
    STATE.authMode = 'login';
    
    // Only delay the UI updates
    setTimeout(() => {
      updateFormUI();
      hideMessages();
    }, CONFIG.FORM_SWITCH_DELAY);
  }
}
  // ======================
  // Event Handlers
  // ======================

  /**
   * Handle form submission
   * @param {Event} e - Submit event
   */
  async function handleSubmit(e) {
    debugLog("Handling submit, STATE:", STATE);
    e.preventDefault();
    initializeForm();

    // Prevent rapid submissions
    const now = Date.now();
    if (now - STATE.lastSubmissionTime < CONFIG.SUBMISSION_COOLDOWN) {
      debugLog('Submission throttled - too frequent attempts');
      return;
    }
    STATE.lastSubmissionTime = now;

    // Validate form
    const validation = validateForm();
    if (!validation.isValid) {
      showError(validation.errors, 'form validation');
      debugLog("returning...");
      return;
    }

    try {
      setSubmissionState(true);
      const responseData = await submitAuthData();
      debugLog('Authentication successful:', responseData);
      handleAuthSuccess(responseData);
    } catch (error) {
      showError(error, 'authentication');
    } finally {
      setSubmissionState(false);
    }
  }

  // ======================
  // Initialization
  // ======================

  /**
   * Initialize event listeners
   */
	function initEventListeners() {
	  // Initialize form immediately
	  initializeForm();
	  
	  // Dropdown toggle
	  DOM.dropdown.button.addEventListener('click', toggleDropdown);
	  
	  // Auth mode toggle
	  DOM.toggleAuth.addEventListener('click', debounce(toggleAuthMode, CONFIG.DEBOUNCE_DELAY));
	  
	  // Form submission
	  DOM.form.addEventListener('submit', handleSubmit);
	  
	  debugLog('Event listeners initialized');
	}
  // Start the application
  initEventListeners();
  debugLog('Authentication system initialized');
});
