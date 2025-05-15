# config.py
import os

from dotenv import load_dotenv

from tools.args_parser import parse_arguments

load_dotenv("instance/.env")
args = parse_arguments()


def get_input(prompt, default=None):
    user_input = input(f"{prompt} (default: {default}): ")
    return user_input if user_input else default


class DefConfig:
    pass

class Config:
    """Basic Flask config."""

    SECRET_KEY = args.secret_key or get_input(
        "Введите секретный ключ", "your_very_secret_key_here"
    )
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() in ["true", "1", "t"]
    SERVER_ADDRESS = args.server_address or get_input(
        ">>адрес сервера", "https://example.com"
    )

    def get(self, key, default=None):
        return getattr(self, key, default)


class RedisConfig:
    """Redis configuration settings."""

    HOST = args.redis_host or get_input("Введите хост Redis", "localhost")
    PORT = args.redis_port or int(get_input("Введите порт Redis", 6379))
    DB = args.redis_db or int(get_input("Введите номер базы данных Redis", 0))
    DECODE_RESPONSES = True

    def get(self, key, default=None):
        return getattr(self, key, default)
