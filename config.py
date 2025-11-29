import os

from dotenv import load_dotenv

load_dotenv("instance/.env")


class APIURLConfig:
    """
    Class holding API URL configurations.
    """

    OM11: str = os.getenv("OM11_API_URL", '')
    OM11TG: str = os.getenv("OM11TG_API_URL", '')

    def get(self, key, default=None):
        return getattr(self, key, default)


class MailConfig:
    MAIL_SERVER = (os.getenv("MAIL_SERVER", "smtp.gmail.com"),)
    MAIL_PORT = (int(os.getenv("MAIL_PORT", 587)),)
    MAIL_USE_TLS = (os.getenv("MAIL_USE_TLS", "true").lower() == "true",)
    MAIL_USERNAME = (os.getenv("MAIL_USERNAME"),)
    MAIL_PASSWORD = (os.getenv("MAIL_PASSWORD"),)


class Config:
    """
    Basic Flask configuration class.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "your_very_secret_key_here")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ["true", "1", "t"]
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "https://example.com")
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "5000"))

    OAUTH2_PROVIDERS = {
        "google": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
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

    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = int(os.getenv("REDIS_PORT", "6379"))
    DB = int(os.getenv("REDIS_DB", "0"))
    DECODE_RESPONSES = True

    def get(self, key, default=None):
        return getattr(self, key, default)
