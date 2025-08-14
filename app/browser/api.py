import logging
from typing import Any, Callable, Dict, List, Type

import requests
from flask import Flask, jsonify, request, session

from app.browser.browser_manager import BrowserManager

__all__ = ["configure_browser_api"]

# Configure logging format and level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("api.log")],
)

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
    Configures Flask routes for browser profile management with comprehensive logging.

    :param app: Flask app instance
    :param logger: Logger instance
    :param BrowserManagerClass: Class for managing browser profiles
    :param AGENT_ADDRESS: Address of the agent to send start commands
    :param get_user_profiles_fn: Function to get user profiles
    :param save_user_profiles_fn: Function to save user profiles
    :param transform_profiles_fn: Function to transform profiles
    """
    logger.info("Initializing browser API routes")
    manager = BrowserManagerClass()
    logger.debug(f"BrowserManager initialized: {manager}")

    def start_browser(ws_url: str, user_id: str) -> None:
        """Helper function to start browser with detailed logging"""
        url = f"{AGENT_ADDRESS}/api/start_browser"
        params = {"ws_url": ws_url, "user_uuid": user_id}

        logger.info(f"Initiating browser start request to agent at {url}")
        logger.debug(f"Request params: {params}")

        try:
            response = requests.post(url, params=params)
            logger.debug(f"Agent response status: {response.status_code}")

            response.raise_for_status()
            response_data = response.json()
            logger.info("Browser started successfully with agent")
            logger.debug(f"Agent response data: {response_data}")

        except requests.exceptions.RequestException:
            logger.error(f"Failed to start browser at {url}")
            logger.debug(
                f"Request details - URL: {url}, Params: {params}", exc_info=True
            )
            logger.exception("Browser start request failed")
            raise

    @app.route("/api/browser/profiles", methods=["GET"])
    def get_profiles() -> Any:
        """Endpoint to fetch browser profiles with comprehensive logging"""
        logger.info("GET /api/browser/profiles request received")

        api_url: str = request.args.get("api_url")
        browser_type: str = request.args.get("type")

        logger.debug(f"Request parameters - api_url: {api_url}, type: {browser_type}")

        if not api_url:
            logger.warning("Missing required parameter: api_url")
            return (
                jsonify(
                    success=False,
                    error="API URL is required",
                    details={"missing_parameter": "api_url"},
                ),
                400,
            )

        try:
            logger.info(
                f"Fetching profiles from {api_url} for browser type {browser_type}"
            )
            profiles: List[Dict[str, Any]] = manager.fetch_profiles(
                api_url, browser_type
            )

            logger.info(f"Successfully retrieved {len(profiles)} profiles")
            logger.debug(
                f"Profile data sample: {profiles[:1] if profiles else 'No profiles'}"
            )  # Log first profile for sample

            return jsonify(
                success=True,
                profiles=profiles,
                metadata={
                    "count": len(profiles),
                    "browser_type": browser_type,
                    "source_api": api_url,
                },
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {api_url}")
            logger.debug(
                f"Request details - URL: {api_url}, Type: {browser_type}", exc_info=True
            )
            return (
                jsonify(
                    success=False,
                    error=str(e),
                    details={
                        "api_url": api_url,
                        "browser_type": browser_type,
                        "error_type": "request_exception",
                    },
                ),
                500,
            )

        except Exception:
            logger.exception("Unexpected error while fetching profiles")
            return (
                jsonify(
                    success=False,
                    error="Internal server error",
                    details={
                        "api_url": api_url,
                        "browser_type": browser_type,
                        "error_type": "unexpected",
                    },
                ),
                500,
            )

    @app.route("/api/browser/start", methods=["POST"])
    def start_profile() -> Any:
        """Endpoint to start a browser profile with detailed operation logging"""
        logger.info("POST /api/browser/start request received")

        user_id: str = session.get("user_id")
        if not user_id:
            logger.warning("Unauthenticated request - missing user_id in session")
            logger.debug(f"Session data: {dict(session)}")
            return (
                jsonify(
                    success=False,
                    error="Authentication required",
                    details={"missing": "user_id"},
                ),
                401,
            )

        data: Dict[str, Any] = request.get_json() or {}
        logger.debug(f"Request data: {data}")

        api_url: str = data.get("api_url")
        profile_id: str = data.get("profile_id")
        browser_type: str = data.get("type")

        # Validate required data with detailed logging
        missing_fields = [
            field for field in ["api_url", "profile_id", "type"] if not data.get(field)
        ]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return (
                jsonify(
                    success=False,
                    error="Missing required fields",
                    details={"missing_fields": missing_fields, "received_data": data},
                ),
                400,
            )

        try:
            logger.info(f"Starting profile {profile_id} for user {user_id}")
            logger.debug(f"Operation details - API: {api_url}, Type: {browser_type}")

            result: Dict[str, Any] = manager.start_profile(
                user_id=user_id,
                api_url=api_url,
                profile_id=profile_id,
                browser_type=browser_type,
            )

            ws_url: str = result.get("ws_url")
            if not ws_url:
                logger.error("No WebSocket URL returned from profile start")
                logger.debug(f"Full start result: {result}")
                return (
                    jsonify(
                        success=False,
                        error="Failed to retrieve WebSocket URL",
                        details={
                            "profile_id": profile_id,
                            "browser_type": browser_type,
                            "api_url": api_url,
                            "result_data": result,
                        },
                    ),
                    500,
                )

            logger.info("Profile started successfully, connecting to WebSocket")
            logger.debug(f"WebSocket URL: {ws_url}")

            start_browser(ws_url=ws_url, user_id=user_id)

            logger.info(
                f"Browser profile {profile_id} fully initialized for user {user_id}"
            )
            return jsonify(
                success=True,
                ws_url=ws_url,
                details={
                    "profile_id": profile_id,
                    "browser_type": browser_type,
                    "user_id": user_id,
                },
            )

        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            logger.debug("Error details for ValueError", exc_info=True)
            return (
                jsonify(
                    success=False,
                    error=str(e),
                    details={
                        "error_type": "value_error",
                        "input_parameters": {
                            "user_id": user_id,
                            "api_url": api_url,
                            "profile_id": profile_id,
                            "browser_type": browser_type,
                        },
                    },
                ),
                400,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.debug("Request details for failed operation", exc_info=True)
            return (
                jsonify(
                    success=False,
                    error=str(e),
                    details={"error_type": "request_exception", "target_api": api_url},
                ),
                500,
            )

        except Exception:
            logger.exception("Unexpected error during profile start")
            return (
                jsonify(
                    success=False,
                    error="Internal server error",
                    details={
                        "error_type": "unexpected",
                        "profile_id": profile_id,
                        "user_id": user_id,
                    },
                ),
                500,
            )

    @app.route("/api/browser/status", methods=["GET"])
    def browser_status() -> Any:
        """Endpoint to check browser status with detailed session logging"""
        logger.info("GET /api/browser/status request received")

        user_id: str = session.get("user_id")
        if not user_id:
            logger.warning("Status check failed - no user_id in session")
            logger.debug(f"Session contents: {dict(session)}")
            return (
                jsonify(
                    success=False,
                    error="Authentication required",
                    details={"missing": "user_id"},
                ),
                401,
            )

        try:
            logger.debug(f"Checking status for user {user_id}")
            profiles: List[Dict[str, Any]] = get_user_profiles_fn(user_id)
            connected = len(profiles) > 0
            active_profiles = len(profiles)

            logger.info(
                f"Status check complete - connected: {connected}, profiles: {active_profiles}"
            )
            logger.debug(f"Profile details: {profiles}")

            return jsonify(
                connected=connected,
                active_profiles=active_profiles,
                details={
                    "user_id": user_id,
                    "profile_count": active_profiles,
                    "has_active_connection": connected,
                },
            )

        except Exception:
            logger.exception("Failed to check browser status")
            return (
                jsonify(
                    success=False,
                    error="Status check failed",
                    details={"user_id": user_id, "error_type": "status_check_failure"},
                ),
                500,
            )

    @app.route("/api/browser/disconnect", methods=["POST"])
    def disconnect_all() -> Any:
        """Endpoint to disconnect all profiles with operation logging"""
        logger.info("POST /api/browser/disconnect request received")

        user_id: str = session.get("user_id")
        if not user_id:
            logger.warning("Disconnect attempt without user_id")
            return (
                jsonify(
                    success=False,
                    error="Authentication required",
                    details={"missing": "user_id"},
                ),
                401,
            )

        try:
            logger.info(f"Disconnecting all profiles for user {user_id}")

            # Get current profiles before disconnecting for logging
            pre_disconnect_profiles = get_user_profiles_fn(user_id)
            logger.debug(f"Pre-disconnect profiles: {len(pre_disconnect_profiles)}")

            manager.disconnect_all(user_id)

            # Verify disconnection
            post_disconnect_profiles = get_user_profiles_fn(user_id)
            if post_disconnect_profiles:
                logger.warning(
                    f"Disconnect incomplete - remaining profiles: {len(post_disconnect_profiles)}"
                )
            else:
                logger.info("All profiles successfully disconnected")

            return jsonify(
                success=True,
                message="Disconnect completed",
                details={
                    "user_id": user_id,
                    "disconnected_profiles": len(pre_disconnect_profiles),
                    "remaining_profiles": len(post_disconnect_profiles),
                },
            )

        except Exception:
            logger.exception("Failed to disconnect profiles")
            return (
                jsonify(
                    success=False,
                    error="Disconnect failed",
                    details={"user_id": user_id, "error_type": "disconnect_failure"},
                ),
                500,
            )

    logger.info("Browser API routes configuration completed")
