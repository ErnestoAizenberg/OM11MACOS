from typing import Any, Dict, List

import requests
from flask import Flask, jsonify, request, session

from app.browser.browser_manager import (
    BrowserManager,
    get_user_profiles,
    save_user_profiles,
    transform_profiles,
)

__all__ = ["configure_browser_api"]


def configure_browser_api(
    app: Flask,
    BrowserManager: type(BrowserManager),
    AGENT_ADDRESS: str,
    get_user_profiles: get_user_profiles,
    save_user_profiles: save_user_profiles,
    transform_profiles: transform_profiles,
) -> None:
    manager = BrowserManager()

    def start_browser(ws_url):
        url = "http://AGENT_ADDRESS/api/browser/start/"
        payload = {"ws_url": ws_url}

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Success:", response.json())
            else:
                print("Failed with status code:", response.status_code)
                print("Response:", response.text)
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)

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
            start_browser(result["ws_url"])
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
