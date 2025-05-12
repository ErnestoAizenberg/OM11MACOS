import logging
from datetime import datetime
from typing import Any, Callable, Dict

from flask import Flask, jsonify, request, session

from app.agent.agent_manager import AgentManager


def configure_agent_settings(
    app: Flask,
    logger: logging.Logger,
    login_required: Callable[[], Any],
    agent_manager: AgentManager,
) -> None:
    @app.route("/api/settings", methods=["POST"])
    @login_required
    def save_settings() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            data: Dict[str, Any] = request.get_json()
            required_settings = ["debugMode", "autoStart", "notifications"]
            if not all(setting in data for setting in required_settings):
                return (
                    jsonify({"success": False, "error": "Missing required settings"}),
                    400,
                )

            settings: Dict[str, Any] = {
                "debugMode": bool(data["debugMode"]),
                "autoStart": bool(data["autoStart"]),
                "notifications": bool(data["notifications"]),
                "updated_at": datetime.now().isoformat(),
            }
            agent_manager.save_settings(user_id, settings)

            logger.info(f"Settings updated for user {user_id}")
            return jsonify({"success": True})

        except Exception as e:
            logger.error(f"Error saving settings for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/settings", methods=["GET"])
    @login_required
    def get_settings() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            settings: Dict[str, Any] = agent_manager.get_settings(user_id)
            return jsonify({"success": True, "settings": settings})
        except Exception as e:
            logger.error(f"Error getting settings for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
