import logging

import requests
from flask import Flask, jsonify, request, session

TELEGRAM_API_SERVICE_URL = "http://localhost:5001"  # URL of Telegram API microservice


def init_telegram_api(app: Flask, login_required: callable, logger: logging.Logger):
    @login_required
    def connect_telegram():
        user_id = session["user_id"]
        data = request.get_json()  # Send data to the Telegram API service
        try:
            response = requests.post(
                f"{TELEGRAM_API_SERVICE_URL}/api/telegram/setup_webhook",
                json={
                    "bot_token": data.get("bot_token"),
                    "chat_id": data.get("chat_id"),
                    "user_id": user_id,
                },
            )
            return jsonify(response.json()), response.status_code
        except Exception as e:
            app.logger.exception("Error connecting to Telegram API service")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/telegram/disconnect", methods=["GET", "POST"])
    @login_required
    def disconnect_telegram():
        user_id = session["user_id"]
        try:
            response = requests.post(
                f"{TELEGRAM_API_SERVICE_URL}/api/telegram/disconnect",
                json={"user_id": user_id},
            )
            return jsonify(response.json()), response.status_code
        except Exception as e:
            app.logger.exception("Error disconnecting Telegram")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/telegram/status", methods=["GET"])
    @login_required
    def telegram_status():
        user_id = session["user_id"]
        try:
            response = requests.get(
                f"{TELEGRAM_API_SERVICE_URL}/api/telegram/status",
                params={"user_id": user_id},
            )
            return jsonify(response.json()), response.status_code
        except Exception as e:
            app.logger.exception("Error fetching Telegram status")
            return jsonify({"success": False, "error": str(e)}), 500
