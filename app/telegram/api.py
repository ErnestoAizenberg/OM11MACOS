import requests
import logging
from flask import Flask, jsonify, request, session

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set to DEBUG for more detailed logs
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class TelegramClient:
    """Handles communication with the Telegram API microservice."""

    def __init__(self, api_base_url: str, logger: logging.Logger):
        self.api_base_url = api_base_url
        self.logger = logger

    def set_webhook(self, bot_token: str, user_id: str, chat_id: str) -> bool:
        """Set webhook for Telegram bot."""
        url = f"{self.api_base_url}/api/telegram/set_webhook"
        payload = {
            "bot_token": bot_token,
            "chat_id": chat_id,
            "user_id": user_id,
        }
        try:
            self.logger.info(
                f"Setting webhook for user_id={user_id} with chat_id={chat_id}"
            )
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            success = data.get("success", False)
            if success:
                self.logger.info("Webhook set successfully.")
            else:
                self.logger.warning(
                    "Failed to set webhook: response indicates failure."
                )
            return success
        except requests.RequestException as e:
            self.logger.exception(f"Exception occurred while setting webhook: {e}")
            return False

    def test_connection(self, bot_token: str, chat_id: str) -> bool:
        """Test connection by trying to get bot info or similar."""
        url = f"{self.api_base_url}/api/telegram/test_connection"
        payload = {"bot_token": bot_token, "chat_id": chat_id}
        try:
            self.logger.info(f"Testing connection for bot_token={bot_token}")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            success = data.get("success", False)
            if success:
                self.logger.info("Connection test succeeded.")
            else:
                self.logger.warning("Connection test failed.")
            return success
        except ConnectionError:
            self.logger.error(
                f"ConnectionError: Please ensure the Telegram service is running at {self.api_base_url}"
            )
            return False
        except requests.RequestException as e:
            self.logger.exception(f"Connection test exception: {e}")
            return False

    def send_message(self, message: str, user_uuid: str) -> bool:
        """Sending message in TG."""
        url = f"{self.api_base_url}/api/telegram/send_message"
        payload = {
            "user_id": user_uuid,
            "message_text": message,
        }
        try:
            self.logger.info(f"Sending message to user_id={user_uuid}")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            success = data.get("success", False)
            if success:
                self.logger.info("Message sent successfully.")
            else:
                self.logger.warning(
                    "Failed to send message: response indicates failure."
                )
            return success
        except ConnectionError:
            self.logger.error(
                f"ConnectionError: Please ensure the Telegram service is running at {self.api_base_url}"
            )
            return False
        except requests.RequestException as e:
            self.logger.exception(f"Sending message exception: {e}")
            return False

    def disconnect(self, user_id: str) -> bool:
        """Handle disconnect logic."""
        url = f"{self.api_base_url}/api/telegram/disconnect"
        payload = {"user_id": user_id}
        try:
            self.logger.info(f"Disconnecting user_id={user_id}")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            success = data.get("success", False)
            if success:
                self.logger.info("User disconnected successfully.")
            else:
                self.logger.warning("Failed to disconnect user.")
            return success
        except requests.RequestException as e:
            self.logger.exception(f"Exception during disconnect: {e}")
            return False

    def get_status(self, user_id: str) -> dict:
        """Get connection status."""
        url = f"{self.api_base_url}/api/telegram/status"
        params = {"user_id": user_id}
        try:
            self.logger.info(f"Fetching status for user_id={user_id}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Status retrieved: {data}")
            return data
        except (ConnectionError, ConnectionRefusedError):
            self.logger.error(
                f"ConnectionError: Please ensure the Telegram service is running at {self.api_base_url}"
            )
            return {"success": False, "error": "Connection error"}
        except requests.RequestException as e:
            self.logger.exception(f"Failed to fetch status: {e}")
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

        logger.info(f"Received request to setup webhook for user_id={user_id}")

        if not bot_token or not chat_id:
            logger.warning("Missing bot_token or chat_id in request data.")
            return (
                jsonify(
                    {"success": False, "error": "Bot token and chat ID are required."}
                ),
                400,
            )

        # Test connection
        # may be not that needed, service can test connection itself
        """
        if not telegram_client.test_connection(bot_token, chat_id):
            logger.error("Failed to connect to Telegram during test connection.")
            return (
                jsonify({"success": False, "error": "Failed to connect to Telegram"}),
                400,
            )
        """
        # Set webhook
        success = telegram_client.set_webhook(
            bot_token=bot_token,
            chat_id=chat_id,
            user_id=user_id,
        )
        if success:
            logger.info("Webhook set successfully.")
            return jsonify({"success": True, "message": "Webhook set successfully"})
        else:
            logger.error("Failed to set webhook.")
            return jsonify({"success": False, "error": "Failed to set webhook"}), 500

    @app.route("/api/telegram/disconnect", methods=["POST"])
    def disconnect():
        #data = request.get_json()
        user_id = session.get("user_id")
        logger.info(f"Received disconnect request for user_id={user_id}")
        success = telegram_client.disconnect(user_id)
        if success:
            logger.info("User disconnected successfully.")
            return jsonify({"success": True, "message": "Disconnected successfully"})
        else:
            logger.warning("Failed to disconnect user.")
            return jsonify({"success": False, "error": "Failed to disconnect"}), 500

    @app.route("/api/telegram/status", methods=["GET"])
    def status():
        user_id = session.get("user_id")
        logger.info(f"Received status request for user_id={user_id}")
        status_info = telegram_client.get_status(user_id)
        return jsonify(status_info)
