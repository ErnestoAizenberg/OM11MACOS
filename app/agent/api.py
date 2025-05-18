from logging import Logger
from typing import Callable, List

from flask import Flask, abort, jsonify, request, session

from app.agent.agent_manager import AgentManager
from app.agent.manus_client import ManusClient
from app.telegram.api_client import TelegramClient


def configure_agent_api(
    app: Flask,
    logger: Logger,
    agent_manager: AgentManager,
    manus_client: ManusClient,
    telegram_client: TelegramClient,
    login_required: Callable,
) -> None:
    @app.route("/api/command", methods=["POST"])
    @login_required
    def execute_command() -> "jsonify":
        """API to execute command from macos interface, it send logs to telegram if TG is connected"""
        user_uuid: str = session["user_id"]
        try:
            data_dict: dict = request.get_json()
            if isinstance(data_dict, dict):
                message: str = data_dict.get("command")
                ### Stream realisation will be aplied soon enougth
                output_chain: List[str] = manus_client.execute_command(
                    message=message, user_uuid=user_uuid
                )
                for chain in output_chain:
                    status = telegram_client.send_message(
                        user_uuid=user_uuid,
                        message=chain,
                    )  # posibly it should to be authorised some way
                    if not status:
                        logger.error(
                            f"Telegram message to {user_uuid} sended unsuccessfully"
                        )
                    else:
                        logger.info(
                            f"Telegram message to {user_uuid} sended successfully"
                        )

                joined_list = "".join(output_chain)
                logger.info(
                    f"Command executed for user {user_uuid[:4]}...: {joined_list}"
                )
                return jsonify(
                    {
                        "success": True,
                        "output": joined_list,
                    }
                )
            else:
                logger.error("execute_command received invalid data")
                abort(400)
        except Exception as e:
            logger.error(f"Error executing command for user {user_uuid}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/command/history", methods=["GET"])
    @login_required
    def get_command_history() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            history: list = agent_manager.get_command_history(user_id)
            logger.info(f"user: {user_id[:4]}... get {len(history)} history msg")
            return jsonify({"success": True, "command_history": history})
        except Exception as e:
            logger.error(f"Error getting command history for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/agent/start", methods=["POST"])
    @login_required
    def start_agent() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            pid: int = agent_manager.start_agent(user_id)
            if not pid:
                return (
                    jsonify({"success": False, "error": "Agent already running"}),
                    400,
                )
            logger.info(f"Agent started for user {user_id} with PID {pid}")
            return jsonify({"success": True, "pid": pid})
        except Exception as e:
            logger.error(f"Error starting agent for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/agent/stop", methods=["POST"])
    @login_required
    def stop_agent() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            success: bool = agent_manager.stop_agent(user_id)
            if not success:
                return jsonify({"success": False, "error": "Agent not running"}), 400
            logger.info(f"Agent stopped for user {user_id}")
            return jsonify({"success": True})
        except Exception as e:
            logger.error(f"Error stopping agent for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/agent/status", methods=["GET"])
    @login_required
    def agent_status() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            status: str
            pid: int
            status, pid = agent_manager.get_agent_status(user_id)
            return jsonify({"success": True, "status": status, "pid": pid})
        except Exception as e:
            logger.error(f"Error getting agent status for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
