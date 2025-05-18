import requests
import logging
from flask import Flask, jsonify, request, session


class TelegramClient:
    """Handles communication with the Telegram API microservice."""

    def __init__(self, api_base_url: str, logger: logging.Logger):
        self.api_base_url = api_base_url
        self.logger = logger

    def set_webhook(self, bot_token: str, user_id: str) -> bool:
        """Set webhook for Telegram bot."""
        try:
            url = f"{self.api_base_url}/api/telegram/set_webhook"
            response = requests.post(
                url,
                json={
                    "bot_token": bot_token,
                    "user_id": user_id,
                },
            )

            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except requests.RequestException:
            self.logger.exception("Failed to set webhook")
            return False

    def test_connection(self, bot_token: str, chat_id: str) -> bool:
        """Test connection by trying to get bot info or similar."""
        try:
            url = f"{self.api_base_url}/api/telegram/test_connection"
            response = requests.post(
                url, json={"bot_token": bot_token, "chat_id": chat_id}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except ConnectionError:
            self.logger.error(
                f"ConnectionError, Please make sure that telegram service runs on URL: {self.api_base_url}"
            )
            return False
        except requests.RequestException:
            self.logger.exception("Connection test failed")
            return False

    def send_message(self, message: str, user_uuid: str) -> bool:
        """Sending message in TG."""
        try:
            url = f"{self.api_base_url}/api/telegram/send_message"
            response = requests.post(
                url,
                json={
                    "user_id": user_uuid,
                    "message_text": message,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except ConnectionError:
            self.logger.error(
                f"ConnectionError, Please make sure that telegram service runs on URL: {self.api_base_url}"
            )
            return False
        except requests.RequestException:
            self.logger.exception("Sending message failed")
            return False

    def disconnect(self, user_id: str) -> bool:
        """Handle disconnect logic."""
        try:
            url = f"{self.api_base_url}/api/telegram/disconnect"
            response = requests.post(url, json={"user_id": user_id})
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except requests.RequestException:
            self.logger.exception("Failed to disconnect")
            return False

    def get_status(self, user_id: str) -> dict:
        """Get connection status."""
        try:
            url = f"{self.api_base_url}/api/telegram/status"
            response = requests.get(url, params={"user_id": user_id})
            response.raise_for_status()
            return response.json()
        except (
            ConnectionError,
            ConnectionRefusedError,
            requests.exceptions.RequestException,
        ):
            self.logger.error(
                f"ConnectionError, Please make sure that telegram service runs on URL: {self.api_base_url}"
            )
            return {"success": False, "error": "Connection error"}
        except requests.RequestException as e:
            self.logger.exception("Failed to fetch status")
            return {"success": False, "error": str(e)}


def init_telegram_api(
    app: Flask,
    login_required: callable,
    logger: logging.Logger,
    telegram_client: TelegramClient,
):
    @app.route("/api/telegram/connect", methods=["POST"])
    def setup_webhook():
        data = request.get_json()
        user_id = session.get("user_id")
        bot_token = data.get("bot_token")
        chat_id = data.get("chat_id")

        if not bot_token or chat_id:
            return (
                jsonify({"success": False, "error": "Failed to connect to Telegram"}),
                400,
            )
        # Test connection
        if not telegram_client.test_connection(bot_token, chat_id):
            return (
                jsonify({"success": False, "error": "Failed to connect to Telegram"}),
                400,
            )

        # Set webhook
        success = telegram_client.set_webhook(
            bot_token=bot_token,
            chat_id=chat_id,
            user_id=user_id,
        )
        if success:
            return jsonify({"success": True, "message": "Webhook set successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to set webhook"}), 500

    @app.route("/api/telegram/disconnect", methods=["POST"])
    def disconnect():
        data = request.get_json()
        user_id = data.get("user_id")
        success = telegram_client.disconnect(user_id)
        if success:
            # Remove configs if stored
            return jsonify({"success": True, "message": "Disconnected successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to disconnect"}), 500

    @app.route("/api/telegram/status", methods=["GET"])
    def status():
        user_id = request.args.get("user_id")
        status_info = telegram_client.get_status(user_id)
        return jsonify(status_info)
