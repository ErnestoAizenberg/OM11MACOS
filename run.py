import importlib
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from typing import Optional

from config import APIURLConfig, Config, MailConfig, RedisConfig


# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class AppRunner:
    def __init__(self, title: str = "Open Manus Agent", run_ui: bool = False):
        self.title = title
        self.run_ui = run_ui
        self.flask_thread: Optional[threading.Thread] = None
        self.webview_thread: Optional[threading.Thread] = None
        self.app_config = Config()
        self.redis_config = RedisConfig()
        self.api_url_config = APIURLConfig()
        self.mail_config = MailConfig()
        self.should_exit = threading.Event()

    def create_flask_app(self):
        """Создание и настройка Flask приложения"""
        from app import create_app

        return create_app(
            app_config=self.app_config,
            api_url_config=self.api_url_config,
            mail_config=self.mail_config,
        )

    def run_flask(self):
        """Запуск Flask приложения с обработкой ошибок"""
        try:
            app = self.create_flask_app()
            logger.info(
                f"Starting Flask server on {self.app_config.get('HOST')}:{self.app_config.get('PORT')}"
            )
            app.run(
                debug=self.app_config.get("DEBUG"),
                port=self.app_config.get("PORT"),
                host=self.app_config.get("HOST"),
                use_reloader=False,
            )
        except Exception as e:
            logger.error(f"Flask application failed: {e}")
            self.should_exit.set()
            sys.exit(1)

    def create_window(self, host: str, port: int):
        """Создание окна WebView"""
        import webview

        try:
            webview.create_window(
                title=self.title,
                url=f"http://{host}:{port}",
                width=1200,
                height=800,
                min_size=(800, 600),
            )
            webview.start()
        except Exception as e:
            logger.error(f"WebView error: {e}")
            self.should_exit.set()

    def start_webview(self, host: str, port: int):
        """Запуск WebView интерфейса"""
        try:
            import webview

            logger.info(f"Starting WebView for {host}:{port}")
            self.webview_thread = threading.Thread(
                target=self.create_window, args=(host, port), daemon=True
            )
            self.webview_thread.start()
        except ImportError:
            logger.warning("WebView package not available, running in headless mode")
            self.run_ui = False

    def check_dependencies(self):
        """Проверка необходимых зависимостей"""
        if self.run_ui:
            try:
                importlib.util.find_spec("webview")
            except ImportError as e:
                logger.warning(f"WebView dependency missing: {e}")
                self.run_ui = False

    def run_redis(self):
        """Запуск Redis сервера при необходимости"""
        redis_run = os.getenv("REDIS_RUN", "false").lower() == "true"
        if not redis_run:
            return

        try:
            if shutil.which("redis-server") is None:
                logger.warning("Redis server not found in PATH")
                return

            logger.info("Starting Redis server...")
            subprocess.run(
                ["redis-server", "--daemonize", "yes"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.warning(f"Failed to start Redis: {e}")

    def cleanup(self):
        """Очистка ресурсов при завершении"""
        self.should_exit.set()
        logger.info("Cleanup completed")

    def run(self):
        """Основной метод запуска приложения"""
        try:
            self.check_dependencies()
            self.run_redis()

            # Запуск Flask в отдельном потоке
            self.flask_thread = threading.Thread(target=self.run_flask, daemon=True)
            self.flask_thread.start()

            # Даем время Flask на запуск
            time.sleep(2)

            if self.run_ui:
                self.start_webview(
                    host=self.app_config.get("HOST", "localhost"),
                    port=self.app_config.get("PORT", 9911),
                )

            # Основной цикл ожидания
            while not self.should_exit.is_set():
                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            self.cleanup()
            logger.info("Application stopped")


if __name__ == "__main__":
    # Парсинг аргументов командной строки
    run_ui = "--ui" in sys.argv or "-u" in sys.argv

    # Запуск приложения
    app = AppRunner(run_ui=run_ui)
    app.run()
