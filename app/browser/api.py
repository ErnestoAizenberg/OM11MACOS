from typing import Any, Callable, Dict, List

import requests
from flask import Flask, jsonify, request, session


def configure_browser_api(
    app: Flask,
    BrowserManager: Any,
    get_user_profiles: Callable[[str], List[Dict[str, Any]]],
    save_user_profiles: Callable[[str, List[Dict[str, Any]]], bool],
    transform_profiles: Callable[[List[Dict[str, Any]]], Any],
) -> None:
    manager = BrowserManager()

    @app.route("/api/browser/profiles", methods=["GET"])
    def get_profiles() -> "jsonify":
        # user_id: str = session["user_id"]
        api_url: str = request.args.get("api_url")
        browser_type: str = request.args.get("type")

        if not api_url:
            return jsonify(success=False, error="API URL is required"), 400

        try:
            profiles: List[Dict[str, Any]] = manager.fetch_profiles(
                api_url, browser_type
            )
            return jsonify(success=True, profiles=profiles)
        except requests.exceptions.RequestException as e:
            return jsonify(success=False, error=str(e)), 500

    @app.route("/api/browser/start", methods=["POST"])
    def start_profile() -> "jsonify":
        user_id: str = session["user_id"]
        data: Dict[str, Any] = request.get_json()

        try:
            result: Dict[str, Any] = manager.start_profile(
                user_id=user_id,
                api_url=data.get("api_url"),
                profile_id=data.get("profile_id"),
                browser_type=data.get("type"),
            )
            return jsonify(success=True, ws_url=result["ws_url"])
        except ValueError as e:
            return jsonify(success=False, error=str(e)), 400
        except requests.exceptions.RequestException as e:
            return jsonify(success=False, error=str(e)), 500

    @app.route("/api/browser/status", methods=["GET"])
    def browser_status() -> "jsonify":
        user_id: str = session["user_id"]
        profiles: List[Dict[str, Any]] = get_user_profiles(user_id)
        return jsonify(connected=len(profiles) > 0, active_profiles=len(profiles))

    @app.route("/api/browser/disconnect", methods=["POST"])
    def disconnect_all() -> "jsonify":
        user_id: str = session["user_id"]
        try:
            manager.disconnect_all(user_id)
            return jsonify(success=True, message="All profiles disconnected")
        except Exception as e:
            return jsonify(success=False, error=str(e)), 500
