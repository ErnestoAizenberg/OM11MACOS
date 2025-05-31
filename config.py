# config.py

import argparse
import os

from dotenv import load_dotenv

# Load environment variables from the specified .env file
load_dotenv("instance/.env")


def parse_arguments():
    """
    Parse command-line arguments for configuration overrides.
    """
    parser = argparse.ArgumentParser(description="Flask app with Redis support.")

    parser.add_argument("--server_address", type=str, help="URL of the server.")
    parser.add_argument("--secret_key", type=str, help="Secret key for Flask app.")
    parser.add_argument("--redis_host", type=str, help="Redis server host.")
    parser.add_argument("--redis_port", type=int, help="Redis server port.")
    parser.add_argument("--redis_db", type=int, help="Redis database number.")
    parser.add_argument("--host", type=str, help="Server host.")
    parser.add_argument("--port", type=int, help="Server port.")
    parser.add_argument(
        "--mail_username",
        type=str,
        help="Mail username, which will send emails to users (my_email@example.com)",
    )
    parser.add_argument(
        "--mail_password",
        type=str,
        help="Not your usual password, google on Jun 2025 won't allow you to use it, it should be generated and require 2FA",
    )

    return parser.parse_args()


# Parse command-line arguments
args = parse_arguments()


def get_input(prompt, default=None):
    """
    Prompt the user for input, with an optional default.
    """
    user_input = input(f"{prompt} (default: {default}): ")
    return user_input if user_input else default


class APIURLConfig:
    """
    Class holding API URL configurations.
    """

    OM11 = "https://2de7-35-196-192-57.ngrok-free.app"
    OM11TG = "http://localhost:5001"

    def get(self, key, default=None):
        return getattr(self, key, default)


mail_config = {
    "MAIL_SERVER": os.getenv("MAIL_SERVER") or "smtp.gmail.com",
    "MAIL_PORT": os.getenv("MAIL_PORT") or 587,
    "MAIL_USE_TLS": os.getenv("MAIL_USE_TLS") or True,
    "MAIL_USERNAME": args.mail_username
    or os.getenv("MAIL_USERNAME")
    or "sereernest@gmail.com",
    "MAIL_PASSWORD": args.mail_password or os.getenv("MAIL_PASSWORD"),
}


class DefConfig:
    """
    Placeholder for default configurations.
    """

    pass


class Config:
    """
    Basic Flask configuration class.
    """

    SECRET_KEY = args.secret_key or get_input(
        "Enter secret key", "your_very_secret_key_here"
    )
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() in ["true", "1", "t"]
    SERVER_ADDRESS = args.server_address or get_input(
        "Server address", "https://example.com"
    )
    HOST = args.host or get_input("Host", "localhost")
    PORT = args.port or int(get_input("Port", "5000"))
    OAUTH2_PROVIDERS = {
        "google": {
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "authorize_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://accounts.google.com/o/oauth2/token",
            "userinfo": {
                "url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "email": lambda json: json["email"],
            },
            "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
        },
    }

    def get(self, key, default=None):
        return getattr(self, key, default)


class RedisConfig:
    """
    Redis configuration settings.
    """

    HOST = args.redis_host or get_input("Redis host", "localhost")
    PORT = args.redis_port or int(get_input("Redis port", "6379"))
    DB = args.redis_db or int(get_input("Redis database number", "0"))
    DECODE_RESPONSES = True

    def get(self, key, default=None):
        return getattr(self, key, default)
