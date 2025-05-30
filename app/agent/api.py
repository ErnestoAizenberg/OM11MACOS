from logging import Logger
from typing import Callable, Dict, List, Tuple

from flask import Flask, Response, abort, jsonify, request, session

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
    def execute_command() -> Tuple[Response, int]:
        """API to execute command from macOS interface, it sends logs to Telegram if TG is connected."""
        user_uuid: str = session.get("user_id")
        try:
            data_dict: dict = request.get_json()
            if not isinstance(data_dict, dict):
                logger.error("execute_command received invalid data")
                abort(400)
            message: str = data_dict.get("command")
            user_command_entry: Dict = agent_manager.save_command(
                user_id=user_uuid,
                command=message,
                timestamp=None,
                status=None,
                is_user=True,
            )
            logger.debug(user_command_entry)

            # Check if user has a connected browser
            user_is_connected: bool = manus_client.agent_status(user_id=user_uuid)
            if not user_is_connected:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Connected browser is not found, connect a browser first",
                        }
                    ),
                    400,
                )

            # Execute command
            output_chain: List[str] = manus_client.execute_command(
                message=message, user_uuid=user_uuid
            )
            # Format data; real-time streaming will be implemented soon
            joined_list: str = "".join(output_chain)
            logger.info(f"Command executed for user {user_uuid[:4]}...: {joined_list}")

            command_output: Dict = agent_manager.save_command(
                user_id=user_uuid,
                command=joined_list,
                timestamp=None,
                status=None,
                is_user=False,
            )
            logger.debug(command_output)

            # Send message in Telegram
            for chain in output_chain:
                status: bool = telegram_client.send_message(
                    user_uuid=user_uuid,
                    message=chain,
                )
                if status:
                    logger.info(f"Telegram message to {user_uuid} sent successfully")
                else:
                    logger.error(f"Telegram message to {user_uuid} failed to send")
            return jsonify({"success": True, "output": joined_list})
        except Exception as e:
            logger.error(f"Error executing command for user {user_uuid}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/command/history", methods=["GET"])
    @login_required
    def get_command_history() -> Tuple[Response, int]:
        user_id: str = session.get("user_id")
        try:
            history: list = agent_manager.get_command_history(user_id)
            logger.info(f"user: {user_id[:4]}... get {len(history)} history msg")
            return jsonify({"success": True, "command_history": history})
        except Exception as e:
            logger.error(f"Error getting command history for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route("/api/agent/start", methods=["POST"])
    @login_required
    def start_agent() -> Tuple[Response, int]:
        user_id: str = session.get("user_id")
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
    def stop_agent() -> Tuple[Response, int]:
        user_id: str = session.get("user_id")
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
    def agent_status() -> Tuple[Response, int]:
        user_id: str = session.get("user_id")
        try:
            status: str
            pid: int
            status, pid = agent_manager.get_agent_status(user_id)
            return jsonify({"success": True, "status": status, "pid": pid})
        except Exception as e:
            logger.error(f"Error getting agent status for user {user_id}: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
