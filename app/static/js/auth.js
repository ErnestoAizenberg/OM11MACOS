document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const dropdownButton = document.getElementById('auth-dropdown-button');
  const dropdownPanel = document.getElementById('auth-dropdown-panel');
  const authForm = document.getElementById('auth-form');
  const toggleAuth = document.getElementById('toggle-auth');
  const formTitle = document.getElementById('auth-form-title');
  const nameField = document.getElementById('name-field');
  const passwordInput = document.getElementById('password');
  const buttonText = document.getElementById('button-text');
  const errorMessage = document.getElementById('error-message');
  const successMessage = document.getElementById('success-message');
  const toggleMessage = document.getElementById('toggle-message');
  const forgotPassword = document.getElementById('forgot-password');
  const authError = document.getElementById('auth-error');
  const authSuccess = document.getElementById('auth-success');

  let isLogin = true;

  // Toggle dropdown
  dropdownButton.addEventListener('click', function() {
    dropdownPanel.classList.toggle('hidden');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function(event) {
    if (!dropdownButton.contains(event.target) && !dropdownPanel.contains(event.target)) {
      dropdownPanel.classList.add('hidden');
    }
  });

  // Toggle between login/signup
  toggleAuth.addEventListener('click', function() {
    isLogin = !isLogin;

    if (isLogin) {
      formTitle.textContent = 'Sign in to your account';
      nameField.classList.add('hidden');
      passwordInput.minLength = 6;
      buttonText.textContent = 'Sign In';
      toggleMessage.textContent = "Don't have an account? ";
      toggleAuth.textContent = 'Sign up';
      forgotPassword.classList.remove('hidden');
    } else {
      formTitle.textContent = 'Create new account';
      nameField.classList.remove('hidden');
      passwordInput.minLength = 8;
      buttonText.textContent = 'Sign Up';
      toggleMessage.textContent = 'Already have an account? ';
      toggleAuth.textContent = 'Sign in';
      forgotPassword.classList.add('hidden');
    }

    // Clear messages
    authError.classList.add('hidden');
    authSuccess.classList.add('hidden');
  });

  // Form submission
  authForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = document.getElementById('submit-button');
    const originalButtonText = submitButton.innerHTML;

    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = `
      <svg class="w-4 h-4 mr-2 -ml-1 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>${isLogin ? 'Signing in...' : 'Creating account...'}</span>
    `;

    // Hide previous messages
    authError.classList.add('hidden');
    authSuccess.classList.add('hidden');

    // Prepare form data
    const formData = {
      email: document.getElementById('email').value,
      password: document.getElementById('password').value
    };

    if (!isLogin) {
      formData.name = document.getElementById('name').value;
    }

    try {
      const endpoint = isLogin ? '/api/login' : '/api/signup';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Something went wrong');
      }

      // Show success message
      successMessage.textContent = isLogin
        ? 'Login successful! Redirecting...'
        : 'Account created successfully!';
      authSuccess.classList.remove('hidden');

      // For login, redirect after delay
      if (isLogin) {
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      } else {
        // For signup, switch to login form after delay
        setTimeout(() => {
          isLogin = true;
          formTitle.textContent = 'Sign in to your account';
          nameField.classList.add('hidden');
          passwordInput.minLength = 6;
          buttonText.textContent = 'Sign In';
          toggleMessage.textContent = "Don't have an account? ";
          toggleAuth.textContent = 'Sign up';
          forgotPassword.classList.remove('hidden');
          authSuccess.classList.add('hidden');
        }, 3000);
      }
    } catch (error) {
      // Show error message
      errorMessage.textContent = error.message;
      authError.classList.remove('hidden');
    } finally {
      // Reset button state
      submitButton.disabled = false;
      submitButton.innerHTML = originalButtonText;
    }
  });
});
