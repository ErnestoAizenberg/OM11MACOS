import logging
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


class SQLiteStorage:
    """Потокобезопасное хранилище на основе SQLite с поддержкой Redis-подобного интерфейса"""

    def __init__(self, db_path: str = "agent_manager.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Контекстный менеджер для безопасной работы с соединением"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    @contextmanager
    def _get_cursor(self):
        """Контекстный менеджер для безопасной работы с курсором"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def _init_db(self):
        """Инициализация структуры базы данных"""
        with self._get_cursor() as cursor:
            # Таблица для хранения пользовательских данных
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id TEXT NOT NULL,
                    field TEXT NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, field)
                )
            """
            )

            # Таблица для хранения истории команд (оптимизированная структура)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS command_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    is_user INTEGER,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user_data(user_id)
                )
            """
            )

            # Индексы для ускорения запросов
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_data ON user_data(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_command_history_user ON command_history(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_command_history_timestamp ON command_history(timestamp)"
            )

    def hset(self, key: str, field: str, value: Any) -> int:
        """Установка значения поля хеша"""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO user_data (user_id, field, value)
                VALUES (?, ?, ?)
            """,
                (key, field, str(value)),
            )
            return cursor.rowcount

    def hget(self, key: str, field: str) -> Optional[str]:
        """Получение значения поля хеша"""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                SELECT value FROM user_data
                WHERE user_id = ? AND field = ?
            """,
                (key, field),
            )
            result = cursor.fetchone()
            return result["value"] if result else None

    def hexists(self, key: str, field: str) -> bool:
        """Проверка существования поля хеша"""
        return self.hget(key, field) is not None

    def hdel(self, key: str, field: str) -> int:
        """Удаление поля хеша"""
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM user_data
                WHERE user_id = ? AND field = ?
            """,
                (key, field),
            )
            return cursor.rowcount

    def save_command(self, user_id: str, command_data: Dict) -> str:
        """Специальный метод для сохранения команды в оптимизированную таблицу"""
        command_id = str(uuid4())
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO command_history (id, user_id, is_user, command, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    command_id,
                    user_id,
                    command_data.get("isUser"),
                    command_data["command"],
                    command_data.get("status", "pending"),
                    command_data.get("timestamp", datetime.now().isoformat()),
                ),
            )
        return command_id

    def get_command_history(
        self, user_id: str, limit: Optional[int] = None
    ) -> List[Dict]:
        """Получение истории команд с возможностью ограничения количества"""
        with self._get_cursor() as cursor:
            query = """
                SELECT id, is_user as isUser, command, status, timestamp
                FROM command_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """
            params = (user_id,)

            if limit is not None:
                query += " LIMIT ?"
                params = (user_id, limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_data(self, days_to_keep: int = 30):
        """Очистка устаревших данных"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        with self._get_cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM command_history
                WHERE timestamp < ?
            """,
                (cutoff_date,),
            )
            cursor.execute(
                """
                DELETE FROM user_data
                WHERE updated_at < ? AND field NOT IN ('settings', 'created_at')
            """,
                (cutoff_date,),
            )


class AgentManager:
    """Менеджер пользователей и агентов с SQLite-хранилищем"""

    def __init__(self, storage_path: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """Инициализация менеджера

        Args:
            storage_path: Путь к файлу базы данных SQLite (None для памяти)
            logger: Main logger
        """
        self.storage = SQLiteStorage(storage_path if storage_path else ":memory:")
        self.logger = logger if logger else logging.getLogger(__name__)

    def initialize_user(self, user_id: str) -> None:
        """Инициализация нового пользователя"""
        if not self.storage.hexists(f"user:{user_id}", "created_at"):
            self.storage.hset(
                f"user:{user_id}", "created_at", datetime.now().isoformat()
            )
            self.storage.hset(f"user:{user_id}", "command_history", json.dumps([]))
            self.storage.hset(f"user:{user_id}", "settings", json.dumps({}))
            self.storage.hset(f"user:{user_id}", "agent_status", "offline")
            self.storage.hset(f"user:{user_id}", "browser_status", "disconnected")

    def save_command(
        self,
        user_id: str,
        command: str,
        timestamp: Optional[str] = None,
        status: Optional[str] = None,
        is_user: Optional[bool] = None,
    ) -> Dict:
        """Сохранение команды в историю"""
        self.initialize_user(user_id)  # Автоматическая инициализация при необходимости

        command_data = {
            "isUser": is_user,
            "command": command,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": status or "pending",
        }

        # Сохраняем в оптимизированную таблицу
        command_id = self.storage.save_command(user_id, command_data)
        command_data["id"] = command_id

        # Также сохраняем в JSON для обратной совместимости
        history = self.get_command_history(user_id)
        history.append(command_data)
        self.storage.hset(f"user:{user_id}", "command_history", json.dumps(history))

        return command_data

    def update_command_status(self, user_id: str, command_id: str, status: str) -> bool:
        """Обновление статуса команды"""
        with self.storage._get_cursor() as cursor:
            # Обновляем в оптимизированной таблице
            cursor.execute(
                """
                UPDATE command_history
                SET status = ?
                WHERE id = ? AND user_id = ?
            """,
                (status, command_id, user_id),
            )

            # Также обновляем в JSON для обратной совместимости
            history = self.get_command_history(user_id)
            updated = False
            for cmd in history:
                if cmd.get("id") == command_id:
                    cmd["status"] = status
                    updated = True
                    break

            if updated:
                self.storage.hset(
                    f"user:{user_id}", "command_history", json.dumps(history)
                )

            return cursor.rowcount > 0 or updated

    def get_command_history(self, user_id: str) -> List[Dict]:
        """Получение истории команд"""
        # Используем оптимизированную таблицу, если есть данные
        db_history = self.storage.get_command_history(user_id)
        if db_history:
            return db_history

        # Fallback к JSON-хранилищу для обратной совместимости
        history_json = self.storage.hget(f"user:{user_id}", "command_history")
        return json.loads(history_json) if history_json else []

    def save_settings(self, user_id: str, settings: Dict) -> None:
        """Сохранение настроек пользователя"""
        self.initialize_user(user_id)
        self.storage.hset(f"user:{user_id}", "settings", json.dumps(settings))

    def get_settings(self, user_id: str) -> Dict:
        """Получение настроек пользователя"""
        self.initialize_user(user_id)
        settings_json = self.storage.hget(f"user:{user_id}", "settings")
        return json.loads(settings_json) if settings_json else {}

    def start_agent(self, user_id: str) -> Optional[int]:
        """Запуск агента и обновление статуса"""
        self.initialize_user(user_id)

        if self.storage.hexists(f"user:{user_id}", "agent_pid"):
            return None  # Агент уже работает

        agent_pid = self._simulate_process_creation()
        self.storage.hset(f"user:{user_id}", "agent_pid", str(agent_pid))
        self.storage.hset(f"user:{user_id}", "agent_status", "online")
        return agent_pid

    def stop_agent(self, user_id: str) -> bool:
        """Остановка агента"""
        if not self.storage.hexists(f"user:{user_id}", "agent_pid"):
            return False  # Агент не был запущен

        self.storage.hdel(f"user:{user_id}", "agent_pid")
        self.storage.hset(f"user:{user_id}", "agent_status", "offline")
        return True

    def get_agent_status(self, user_id: str) -> Tuple[str, Optional[int]]:
        """Получение статуса агента"""
        self.initialize_user(user_id)
        status = self.storage.hget(f"user:{user_id}", "agent_status") or "offline"
        pid = self.storage.hget(f"user:{user_id}", "agent_pid")
        
        if pid is None and status == "online":
            self.logger.warning(f"Correcting inconsistent agent state for user {user_id}")
            status = "offline"
            self.storage.hset(f"user:{user_id}", "agent_status", "offline")
        elif pid is not None and status == "offline":
            self.logger.warning(f"Correcting inconsistent agent state for user {user_id}")
            status = "online"
            self.storage.hset(f"user:{user_id}", "agent_status", "online")

        return status, int(pid) if pid else None

    def connect_browser(self, user_id: str) -> bool:
        """Соединение браузера"""
        self.initialize_user(user_id)
        self.storage.hset(f"user:{user_id}", "browser_status", "connected")
        return True

    def disconnect_browser(self, user_id: str) -> bool:
        """Отключение браузера"""
        self.initialize_user(user_id)
        self.storage.hset(f"user:{user_id}", "browser_status", "disconnected")
        return True

    def get_browser_status(self, user_id: str) -> str:
        """Получение статуса браузера"""
        self.initialize_user(user_id)
        return self.storage.hget(f"user:{user_id}", "browser_status") or "disconnected"

    def _simulate_process_creation(self) -> int:
        """Симуляция создания процесса (для примера)"""
        import random

        return random.randint(1000, 9999)

    def backup_database(self, backup_path: str) -> bool:
        """Создание резервной копии базы данных"""
        if self.storage.db_path == ":memory:":
            return False

        import shutil

        try:
            with self.storage._lock:
                shutil.copy2(self.storage.db_path, backup_path)
            return True
        except Exception:
            return False

    def cleanup_user_data(self, user_id: str) -> bool:
        """Очистка всех данных пользователя"""
        with self.storage._get_cursor() as cursor:
            # Удаляем из user_data
            cursor.execute(
                "DELETE FROM user_data WHERE user_id = ?", (f"user:{user_id}",)
            )

            # Удаляем из command_history
            cursor.execute("DELETE FROM command_history WHERE user_id = ?", (user_id,))

            return cursor.rowcount > 0
