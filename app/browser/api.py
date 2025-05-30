import logging
from typing import Any, Callable, Dict, List, Type

import requests
from flask import Flask, jsonify, request, session

from app.browser.browser_manager import BrowserManager

__all__ = ["configure_browser_api"]


UserProfile = Dict[str, Any]
UserProfilesGetter = Callable[[str], List[UserProfile]]
UserProfilesSaver = Callable[[str, List[UserProfile]], None]
UserProfilesTransformer = Callable[[List[UserProfile]], List[UserProfile]]


def configure_browser_api(
    app: Flask,
    logger: logging.Logger,
    BrowserManagerClass: Type[BrowserManager],
    AGENT_ADDRESS: str,
    get_user_profiles_fn: UserProfilesGetter,
    save_user_profiles_fn: UserProfilesSaver,
    transform_profiles_fn: UserProfilesTransformer,
) -> None:
    """
    Configures Flask routes for browser profile management.

    :param app: Flask app instance
    :param logger: Logger instance
    :param BrowserManagerClass: Class for managing browser profiles
    :param AGENT_ADDRESS: Address of the agent to send start commands
    :param get_user_profiles_fn: Function to get user profiles
    :param save_user_profiles_fn: Function to save user profiles
    :param transform_profiles_fn: Function to transform profiles
    """

    manager = BrowserManagerClass()

    def start_browser(ws_url: str) -> None:
        url = f"http://{AGENT_ADDRESS}/api/browser/start/"
        payload = {"ws_url": ws_url}
        logger.debug(f"Starting request to {url} with payload: {payload}")

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(
                f"Successfully started browser with response: {response.json()}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start browser at {url}: {e}")

    @app.route("/api/browser/profiles", methods=["GET"])
    def get_profiles() -> Any:
        api_url: str = request.args.get("api_url")
        browser_type: str = request.args.get("type")

        if not api_url:
            logger.warning(
                "Missing 'api_url' parameter in /api/browser/profiles request."
            )
            return jsonify(success=False, error="API URL is required"), 400

        try:
            profiles: List[Dict[str, Any]] = manager.fetch_profiles(
                api_url, browser_type
            )
            logger.info(f"Fetched {len(profiles)} profiles for api_url: {api_url}")
            return jsonify(success=True, profiles=profiles)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching profiles from {api_url}: {e}")
            return jsonify(success=False, error=str(e)), 500
        except Exception as e:
            logger.exception("Unexpected error while fetching profiles.")
            return jsonify(success=False, error=str(e)), 500

    @app.route("/api/browser/start", methods=["POST"])
    def start_profile() -> Any:
        user_id: str = session.get("user_id")
        if not user_id:
            logger.warning("User session missing 'user_id'.")
            return jsonify(success=False, error="User not authenticated"), 401

        data: Dict[str, Any] = request.get_json() or {}
        api_url: str = data.get("api_url")
        profile_id: str = data.get("profile_id")
        browser_type: str = data.get("type")

        # Validate required data
        missing_fields = [
            field for field in ["api_url", "profile_id", "type"] if not data.get(field)
        ]
        if missing_fields:
            logger.warning(
                f"Missing fields in /api/browser/start request: {missing_fields}"
            )
            return (
                jsonify(
                    success=False, error=f"Missing fields: {', '.join(missing_fields)}"
                ),
                400,
            )

        try:
            result: Dict[str, Any] = manager.start_profile(
                user_id=user_id,
                api_url=api_url,
                profile_id=profile_id,
                browser_type=browser_type,
            )
            ws_url: str = result.get("ws_url")
            if not ws_url:
                logger.error("start_profile did not return 'ws_url'.")
                return (
                    jsonify(success=False, error="Failed to retrieve WebSocket URL"),
                    500,
                )

            start_browser(ws_url)
            logger.info(
                f"Started browser profile for user {user_id} with profile {profile_id}"
            )
            return jsonify(success=True, ws_url=ws_url)
        except ValueError as e:
            logger.error(f"ValueError in /api/browser/start: {e}")
            return jsonify(success=False, error=str(e)), 400
        except requests.exceptions.RequestException as e:
            logger.error(f"RequestException during start_profile: {e}")
            return jsonify(success=False, error=str(e)), 500
        except Exception as e:
            logger.exception("Unexpected error during start_profile.")
            return jsonify(success=False, error=str(e)), 500

    @app.route("/api/browser/status", methods=["GET"])
    def browser_status() -> Any:
        user_id: str = session.get("user_id")
        if not user_id:
            logger.warning("User session missing 'user_id' in /api/browser/status")
            return jsonify(success=False, error="User not authenticated"), 401

        try:
            profiles: List[Dict[str, Any]] = get_user_profiles_fn(user_id)
            connected = len(profiles) > 0
            active_profiles = len(profiles)
            logger.info(f"User {user_id} has {active_profiles} active profiles.")
            return jsonify(connected=connected, active_profiles=active_profiles)
        except Exception as e:
            logger.exception("Error retrieving user profiles.")
            return jsonify(success=False, error=str(e)), 500

    @app.route("/api/browser/disconnect", methods=["POST"])
    def disconnect_all() -> Any:
        user_id: str = session.get("user_id")
        if not user_id:
            logger.warning("User session missing 'user_id' in /api/browser/disconnect")
            return jsonify(success=False, error="User not authenticated"), 401

        try:
            manager.disconnect_all(user_id)
            logger.info(f"All profiles disconnected for user {user_id}")
            return jsonify(success=True, message="All profiles disconnected")
        except Exception as e:
            logger.exception("Error disconnecting all profiles.")
            return jsonify(success=False, error=str(e)), 500
