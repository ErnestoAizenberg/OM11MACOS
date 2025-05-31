document.addEventListener('DOMContentLoaded', function() {
  // Debug flag - set to false in production
  const DEBUG_MODE = true;
  
  // DOM elements cache
  const elements = {
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

  // State management
  let state = {
    isLogin: true,
    isSubmitting: false,
    lastSubmissionTime: 0,
    initialized: false
  };

  // Constants
  const SUBMISSION_COOLDOWN = 2000; // 2 seconds
  const DEBOUNCE_DELAY = 300;
  const REDIRECT_DELAY = 1500;
  const FORM_SWITCH_DELAY = 3000;

  // Debug logger
  function debugLog(...messages) {
    if (DEBUG_MODE) {
      console.log('[Auth Debug]', new Date().toISOString(), ...messages);
    }
  }

  // Initialize form state
  function initializeFormState() {
    if (state.initialized) return;
    
    // Set initial UI state based on isLogin
    updateFormUI();
    state.initialized = true;
    debugLog('Form state initialized');
  }

  // Update UI based on current state
  function updateFormUI() {
    elements.fields.formTitle.textContent = state.isLogin 
      ? 'Sign in to your account' 
      : 'Create new account';
    
    elements.fields.nameField.classList.toggle('hidden', state.isLogin);
    elements.fields.password.minLength = state.isLogin ? 6 : 8;
    elements.fields.buttonText.textContent = state.isLogin ? 'Sign In' : 'Sign Up';
    elements.messages.toggle.textContent = state.isLogin 
      ? "Don't have an account? " 
      : 'Already have an account? ';
    elements.toggleAuth.textContent = state.isLogin ? 'Sign up' : 'Sign in';
    elements.links.forgotPassword.classList.toggle('hidden', !state.isLogin);

    // Clear messages
    elements.messages.authError.classList.add('hidden');
    elements.messages.authSuccess.classList.add('hidden');
  }

  // Error handler
  function handleError(error, context = '') {
    debugLog(`Error in ${context}:`, error);
    elements.messages.error.textContent = error.message || 'An unexpected error occurred';
    elements.messages.authError.classList.remove('hidden');
    elements.messages.authSuccess.classList.add('hidden');
  }

  // Form validation
  function validateForm() {
    const { email, password, name } = elements.fields;
    const errors = [];

    // Email validation
    if (!email.value.trim()) {
      errors.push('Email is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      errors.push('Please enter a valid email address');
    }

    // Password validation
    if (!password.value) {
      errors.push('Password is required');
    } else if (state.isLogin && password.value.length < 6) {
      errors.push('Password must be at least 6 characters');
    } else if (!state.isLogin && password.value.length < 8) {
      errors.push('Password must be at least 8 characters');
    }

    // Name validation for signup
    if (!state.isLogin && !name.value.trim()) {
      errors.push('Name is required');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // UI state management
  function setUIState(submitting = false) {
    state.isSubmitting = submitting;
    elements.submitButton.disabled = submitting;
    
    if (submitting) {
      elements.submitButton.innerHTML = `
        <svg class="w-4 h-4 mr-2 -ml-1 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>${state.isLogin ? 'Signing in...' : 'Creating account...'}</span>
      `;
    } else {
      elements.submitButton.innerHTML = `<span id="button-text">${state.isLogin ? 'Sign In' : 'Sign Up'}</span>`;
    }
  }

  // Toggle between login/signup
  function toggleAuthMode() {
    state.isLogin = !state.isLogin;
    updateFormUI();
    debugLog('Auth mode toggled to:', state.isLogin ? 'Login' : 'Signup');
  }

  // Form submission handler
  async function handleSubmit(e) {
    e.preventDefault();
    initializeFormState(); // Ensure form is properly initialized
    
    // Prevent rapid submissions
    const now = Date.now();
    if (now - state.lastSubmissionTime < SUBMISSION_COOLDOWN) {
      debugLog('Submission throttled - too frequent attempts');
      return;
    }
    state.lastSubmissionTime = now;

    // Validate form
    const validation = validateForm();
    if (!validation.isValid) {
      handleError({ message: validation.errors.join('\n') }, 'form validation');
      return;
    }

    try {
      setUIState(true);
      debugLog('Starting form submission');

      // Prepare form data
      const formData = {
        email: elements.fields.email.value.trim(),
        password: elements.fields.password.value
      };

      if (!state.isLogin) {
        formData.name = elements.fields.name.value.trim();
      }

      debugLog('Submitting data:', { ...formData, password: '***' });

      // API request
      const endpoint = state.isLogin ? '/api/login' : '/api/signup';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        credentials: 'include'
      });

      // Handle response
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (parseError) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        throw new Error(errorData.message || 'Authentication failed');
      }

      const data = await response.json();
      debugLog('API response:', data);

      // Show success
      elements.messages.success.textContent = state.isLogin
        ? 'Login successful! Redirecting...'
        : 'Account created successfully!';
      elements.messages.authSuccess.classList.remove('hidden');
      elements.messages.authError.classList.add('hidden');

      // Handle post-success actions
      if (state.isLogin) {
        debugLog('Redirecting to dashboard...');
        setTimeout(() => {
          window.location.href = data.redirectUrl || '/dashboard';
        }, REDIRECT_DELAY);
      } else {
        debugLog('Switching to login form...');
        setTimeout(() => {
          state.isLogin = true;
          updateFormUI();
          elements.messages.authSuccess.classList.add('hidden');
        }, FORM_SWITCH_DELAY);
      }

    } catch (error) {
      handleError(error, 'form submission');
    } finally {
      setUIState(false);
    }
  }

  // Event listeners with debouncing
  function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // Initialize event listeners
  function initEventListeners() {
    // Initialize form on first interaction
    const initializeOnInteraction = () => {
      initializeFormState();
      document.removeEventListener('click', initializeOnInteraction);
      document.removeEventListener('keydown', initializeOnInteraction);
    };
    document.addEventListener('click', initializeOnInteraction);
    document.addEventListener('keydown', initializeOnInteraction);

    // Dropdown toggle
    elements.dropdown.button.addEventListener('click', () => {
      elements.dropdown.panel.classList.toggle('hidden');
      debugLog('Dropdown toggled');
    });
	elements.dropdown.button.addEventListener('click', () => {
	  const panel = elements.dropdown.panel;

	  // Check if the panel is currently hidden (by class)
	  if (panel.classList.contains('opacity-0')) {
	    // Show the panel
	    panel.classList.remove('opacity-0', 'scale-95');
	    panel.classList.add('opacity-100', 'scale-100');
	    debugLog('Dropdown shown');
	  } else {
	    // Hide the panel
	    panel.classList.remove('opacity-100', 'scale-100');
	    panel.classList.add('opacity-0', 'scale-95');
	    debugLog('Dropdown hidden');
	  }
	});

    // Auth mode toggle
    elements.toggleAuth.addEventListener('click', debounce(toggleAuthMode, DEBOUNCE_DELAY));

    // Form submission
    elements.form.addEventListener('submit', handleSubmit);

    debugLog('Event listeners initialized');
  }

  // Initialize
  initEventListeners();
  debugLog('Authentication module initialized');
});
