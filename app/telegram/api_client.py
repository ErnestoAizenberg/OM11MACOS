import logging


class TelegramClient:
    """For talking with OM11TG microservice"""

    def __init__(self, tg_api_url: str, logger: logging.Logger):
        self.tg_api_url = tg_api_url
        self.logger = logger

    def send_message(self, message: str, user_uuid: str) -> bool:
        pass
