# user_manager.py
import json
from datetime import datetime
from typing import Dict


class AgentManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def initialize_user(self, user_id):
        """Инициализация нового пользователя в Redis."""
        self.redis_client.hset(
            f"user:{user_id}", "created_at", datetime.now().isoformat()
        )

    def save_command(
        self, user_id, command, timestamp=None, status=None, is_user=None
    ) -> Dict:
        command_history_raw = self.redis_client.hget(
            f"user:{user_id}", "command_history"
        )
        command_history = json.loads(command_history_raw) if command_history_raw else []
        command_entry = {
            "isUser": is_user or None,
            "command": command,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": status or "pending",
        }
        command_history.append(command_entry)
        self.redis_client.hset(
            f"user:{user_id}", "command_history", json.dumps(command_history)
        )
        return command_entry

    def get_command_history(self, user_id):
        """Получение истории команд пользователя."""
        command_history_raw = self.redis_client.hget(
            f"user:{user_id}", "command_history"
        )
        return json.loads(command_history_raw) if command_history_raw else []

    def save_settings(self, user_id, settings):
        """Сохранение настроек пользователя в Redis."""
        self.redis_client.hset(f"user:{user_id}", "settings", json.dumps(settings))

    def get_settings(self, user_id):
        """Получение настроек пользователя."""
        settings_raw = self.redis_client.hget(f"user:{user_id}", "settings")
        return json.loads(settings_raw) if settings_raw else {}

    # Методы для управления агентом
    def start_agent(self, user_id):
        """Запуск агента и обновление статуса."""
        if self.redis_client.hexists(f"user:{user_id}", "agent_pid"):
            return False  # Агент уже работает
        agent_pid = 12345  # Сюда должен идти реальный PID
        self.redis_client.hset(f"user:{user_id}", "agent_pid", agent_pid)
        self.redis_client.hset(f"user:{user_id}", "agent_status", "online")
        return agent_pid

    def stop_agent(self, user_id):
        """Остановка агента."""
        if not self.redis_client.hexists(f"user:{user_id}", "agent_pid"):
            return False  # Агент не был запущен
        self.redis_client.hdel(f"user:{user_id}", "agent_pid")
        self.redis_client.hset(f"user:{user_id}", "agent_status", "offline")
        return True

    def get_agent_status(self, user_id):
        """Получение статуса агента."""
        status = self.redis_client.hget(f"user:{user_id}", "agent_status") or "offline"
        pid = self.redis_client.hget(f"user:{user_id}", "agent_pid")
        return status, int(pid) if pid else None

    # Методы для управления браузером
    def connect_browser(self, user_id):
        """Соединение браузера."""
        self.redis_client.hset(f"user:{user_id}", "browser_status", "connected")
        return True

    def disconnect_browser(self, user_id):
        """Отключение браузера."""
        self.redis_client.hset(f"user:{user_id}", "browser_status", "disconnected")
        return True

    def get_browser_status(self, user_id):
        """Получение статуса браузера."""
        return (
            self.redis_client.hget(f"user:{user_id}", "browser_status")
            or "disconnected"
        )
