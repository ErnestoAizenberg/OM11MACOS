// telegram.js
import { makeRequest } from './api.js';
import { showNotification } from './notifications.js';
import { state } from './state.js';
import { elements } from './elements.js';

export const TelegramManager = {
  state: {
    status: 'disconnected',
    lastError: null,
    userToken: null,
    userId: null
  },

  // Основной метод инициализации
  init() {
    this.setupEventListeners();
    this.checkStatus()
      .then(() => console.debug('Telegram status checked'))
      .catch(err => console.error('Status check failed:', err));
    return this;
  },

  // Настройка всех обработчиков событий
  setupEventListeners() {
    // Проверяем существование элементов перед добавлением обработчиков
    if (elements.openTelegramConnectMenu) {
      elements.openTelegramConnectMenu.addEventListener('click', () => this.openModal());
    } else {
      console.warn('Open Telegram button not found');
    }

    if (elements.closeModalBtn) {
      elements.closeModalBtn.addEventListener('click', () => this.closeModal());
    }

    if (elements.connectTelegramBtn) {
      elements.connectTelegramBtn.addEventListener('click', () => this.handleConnectionSubmit());
    }

    // Обработчик для переключения между Polling/Webhook
    const updateMethodRadios = document.querySelectorAll('input[name="update-method"]');
    if (updateMethodRadios.length > 0) {
      updateMethodRadios.forEach(radio => {
        radio.addEventListener('change', (e) => this.toggleWebhookField(e.target.value));
      });
    }
  },

  // Открытие модального окна
  openModal() {
    if (elements.telegramModal) {
      elements.telegramModal.classList.remove('hidden');
      this.checkStatus();
    } else {
      console.error('Telegram modal not found');
    }
  },

  // Закрытие модального окна
  closeModal() {
    if (elements.telegramModal) {
      elements.telegramModal.classList.add('hidden');
      this.clearStatus();
    }
  },

  // Проверка статуса подключения
  async checkStatus() {
    try {
      this.setState('connecting');
      const result = await makeRequest('/api/telegram/status', 'GET');
      
      if (result.success && result.status === 'connected') {
        this.setState('connected', {
          userToken: result.user_token,
          userId: result.user_id
        });
      } else {
        this.setState('disconnected', {
          lastError: result.error || 'Not connected'
        });
      }
      return this.state;
    } catch (error) {
      console.error("Status check failed:", error);
      this.setState('error', { lastError: error.message });
      throw error;
    }
  },

  // Установка состояния
  setState(status, data = {}) {
    this.state = { ...this.state, status, ...data };
    this.updateUI();
    state.telegramStatus = status;
    return this.state;
  },

  // Обновление интерфейса
  updateUI() {
    if (!elements.telegramStatusIndicator || !elements.telegramStatusText || !elements.connectTelegramBtn) {
      console.warn('Telegram UI elements not found');
      return;
    }

    const { status } = this.state;
    
    switch(status) {
      case 'connected':
        elements.telegramStatusIndicator.className = 'w-3 h-3 rounded-full bg-green-500 mr-2';
        elements.telegramStatusText.textContent = 'Connected';
        elements.connectTelegramBtn.innerHTML = '<i class="fas fa-unlink mr-2"></i> Disconnect';
        elements.connectTelegramBtn.onclick = () => this.disconnect();
        break;
        
      case 'disconnected':
        elements.telegramStatusIndicator.className = 'w-3 h-3 rounded-full bg-red-500 mr-2';
        elements.telegramStatusText.textContent = 'Disconnected';
        elements.connectTelegramBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Connect';
        elements.connectTelegramBtn.onclick = () => this.openModal();
        break;
        
      case 'connecting':
        elements.telegramStatusIndicator.className = 'w-3 h-3 rounded-full bg-yellow-500 mr-2';
        elements.telegramStatusText.textContent = 'Connecting...';
        elements.connectTelegramBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Connecting';
        elements.connectTelegramBtn.onclick = null;
        break;
        
      case 'error':
        elements.telegramStatusIndicator.className = 'w-3 h-3 rounded-full bg-red-500 mr-2';
        elements.telegramStatusText.textContent = 'Error';
        break;
    }
  },

  // Обработка подключения
  async handleConnectionSubmit() {
    if (!this.validateForm()) return;

    const connectionData = {
      bot_token: elements.botTokenInput?.value.trim(),
      chat_id: elements.chatIdInput?.value.trim(),
      webhook_url: elements.webhookUrlInput?.value.trim() || null,
      update_method: document.querySelector('input[name="update-method"]:checked')?.value
    };

    this.showStatus('Connecting to Telegram...', 'info');

    try {
      const result = await this.connect(connectionData);
      
      if (result.status === 'connected') {
        this.showStatus('Successfully connected!', 'success');
        setTimeout(() => this.closeModal(), 1500);
      } else {
        this.showStatus(`Error: ${result.lastError || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      this.showStatus(`Network error: ${error.message}`, 'error');
    }
  },

  // Валидация формы
  validateForm() {
    if (!elements.botTokenInput?.value.trim() || !elements.chatIdInput?.value.trim()) {
      this.showStatus('Please fill all required fields', 'error');
      return false;
    }
    return true;
  },

  // Подключение к Telegram
  async connect(connectionData) {
    try {
      this.setState('connecting');
      const result = await makeRequest('/api/telegram/connect', 'POST', connectionData);
      
      if (result.success) {
        this.setState('connected', {
          userToken: result.user_token,
          userId: result.user_id
        });
        showNotification('Telegram connected successfully');
      } else {
        this.setState('error', {
          lastError: result.error || 'Connection failed'
        });
      }
      return this.state;
    } catch (error) {
      console.error("Connection failed:", error);
      this.setState('error', { lastError: error.message });
      throw error;
    }
  },

  // Отключение от Telegram
  async disconnect() {
    try {
      if (confirm('Are you sure you want to disconnect Telegram?')) {
        this.setState('disconnecting');
        const result = await makeRequest('/api/telegram/disconnect', 'POST');
        
        if (result.success) {
          this.setState('disconnected', {
            userToken: null,
            userId: null
          });
          showNotification('Telegram disconnected');
        } else {
          this.setState('error', {
            lastError: result.error || 'Disconnect failed'
          });
        }
      }
      return this.state;
    } catch (error) {
      console.error("Disconnect failed:", error);
      this.setState('error', { lastError: error.message });
      throw error;
    }
  },

  // Показать статус
  showStatus(message, type = 'info') {
    if (!elements.statusMessage) return;
    
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message ${type}`;
    elements.statusMessage.classList.remove('hidden');
    
    if (type !== 'loading') {
      setTimeout(() => this.clearStatus(), 5000);
    }
  },

  // Очистить статус
  clearStatus() {
    if (elements.statusMessage) {
      elements.statusMessage.classList.add('hidden');
    }
  },

  // Переключение поля Webhook
  toggleWebhookField(method) {
    const webhookField = document.getElementById('webhookField');
    if (!webhookField) return;
    
    if (method === 'webhook') {
      webhookField.classList.remove('hidden');
    } else {
      webhookField.classList.add('hidden');
    }
  }
};
