import json
import urllib.parse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class BrowserManager:
    BROWSER_CONFIGS_DIR = Path("instance/browser_configs")
    REQUEST_TIMEOUT = 30
    CONFIG_CLEANUP_DAYS = 7

    def __init__(self):
        self.BROWSER_CONFIGS_DIR.mkdir(exist_ok=True)

    def fetch_profiles(self, api_url: str, browser_type: str) -> List[Dict]:
        endpoints = {
            "octo": f"{api_url}/api/v1/profile",
            "dolphin": f"{api_url}/profiles",
            "gologin": f"{api_url}/gologin/profiles",
            "undetectable": f"{api_url}/list",
            "vision": f"{api_url}/api/v1/profiles",
            "linken": f"{api_url}/api/profiles",
        }

        response = requests.get(
            endpoints[browser_type],
            headers={"Content-Type": "application/json"},
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        return transform_profiles(response.json(), browser_type)

    def start_profile(
        self, user_id: str, api_url: str, profile_id: str, browser_type: str
    ) -> Dict:
        if not all([api_url, profile_id, browser_type]):
            raise ValueError("Missing required parameters")

        profiles = get_user_profiles(user_id)
        start_methods = {
            "octo": self._start_octo_profile,
            "dolphin": self._start_dolphin_profile,
            "gologin": self._start_gologin_profile,
            "undetectable": self._start_undetectable_profile,
            "vision": self._start_vision_profile,
            "linken": self._start_linken_profile,
        }

        result = start_methods[browser_type](api_url, profile_id)
        profiles.append(
            {
                "id": profile_id,
                "browser": browser_type,
                "ws_url": result["ws_url"],
                "api_url": api_url,
                "started_at": datetime.now().isoformat(),
            }
        )

        save_user_profiles(user_id, profiles)
        return result

    def disconnect_all(self, user_id: str):
        profiles = get_user_profiles(user_id)

        for profile in profiles:
            try:
                stop_method = getattr(self, f"_stop_{profile['browser']}_profile")
                stop_method(profile["api_url"], profile["id"])
            except Exception as e:
                logger.error(f"Error stopping profile {profile['id']}: {str(e)}")

        save_user_profiles(user_id, [])
        self._cleanup_old_configs()

    def _start_octo_profile(self, api_url: str, profile_id: str) -> Dict:
        response = requests.post(
            f"{api_url}/api/v1/profile/{profile_id}/start",
            json={"headless": False},
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return {"ws_url": f"ws://{api_url.split('//')[1]}/ws/{profile_id}"}

    def _start_dolphin_profile(self, api_url: str, profile_id: str) -> Dict:
        response = requests.post(
            f"{api_url}/profile/{profile_id}/start", timeout=self.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return {"ws_url": response.json().get("ws_url")}

    def _start_gologin_profile(self, api_url: str, profile_id: str) -> Dict:
        response = requests.post(
            f"{api_url}/gologin/profile/{profile_id}/start",
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return {"ws_url": response.json().get("debuggerAddress")}

    def _start_undetectable_profile(self, api_url: str, profile_id: str, chrome_flags: str = None, start_pages: str = None, headless: bool = False) -> Dict:
        url = f"{api_url}/profile/start/{urllib.parse.quote(profile_id)}"
        params = {}
        if headless:
            params["--headless"] = "new"
        if chrome_flags:
            params["chrome_flags"] = chrome_flags

        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, params, headers=headers, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        return {"ws_url": response.json().get("websocket_link")}

    def _start_vision_profile(self, api_url: str, profile_id: str) -> Dict:
        response = requests.post(
            f"{api_url}/api/v1/profile/{profile_id}/start",
            json={"headless": False},
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return {"ws_url": f"ws://{api_url.split('//')[1]}/ws/{profile_id}"}

    def _start_linken_profile(self, api_url: str, profile_id: str) -> Dict:
        response = requests.post(
            f"{api_url}/api/profile/{profile_id}/start",
            json={"headless": False},
            timeout=self.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return {"ws_url": response.json().get("wsEndpoint")}

    def _stop_octo_profile(self, api_url: str, profile_id: str):
        requests.post(
            f"{api_url}/api/v1/profile/{profile_id}/stop", timeout=self.REQUEST_TIMEOUT
        )

    def _stop_dolphin_profile(self, api_url: str, profile_id: str):
        requests.post(
            f"{api_url}/profile/{profile_id}/stop", timeout=self.REQUEST_TIMEOUT
        )

    def _stop_gologin_profile(self, api_url: str, profile_id: str):
        requests.post(
            f"{api_url}/gologin/profile/{profile_id}/stop", timeout=self.REQUEST_TIMEOUT
        )

    def _stop_undetectable_profile(self, api_url: str, profile_id: str):
        requests.post(
            f"{api_url}/api/profile/{profile_id}/stop", timeout=self.REQUEST_TIMEOUT
        )

    def _stop_vision_profile(self, api_url: str, profile_id: str):
        requests.post(
            f"{api_url}/api/v1/profile/{profile_id}/stop", timeout=self.REQUEST_TIMEOUT
        )

    def _stop_linken_profile(self, api_url: str, profile_id: str):
        requests.post(
            f"{api_url}/api/profile/{profile_id}/stop", timeout=self.REQUEST_TIMEOUT
        )

    """
    def _transform_profiles(
        self, raw_profiles: List[Dict], browser_type: str
    ) -> List[Dict]:
        transformers = {
            "octo": self._transform_octo_profiles,
            "dolphin": self._transform_dolphin_profiles,
            "gologin": self._transform_gologin_profiles,
            "undetectable": self._transform_undetectable_profiles,
            "vision": self._transform_vision_profiles,
            "linken": self._transform_linken_profiles,
        }
        return transformers[browser_type](raw_profiles)
    """

    def _cleanup_old_configs(self):
        cutoff = datetime.now() - timedelta(days=self.CONFIG_CLEANUP_DAYS)
        for config_file in self.BROWSER_CONFIGS_DIR.glob("*.json"):
            if datetime.fromtimestamp(config_file.stat().st_mtime) < cutoff:
                try:
                    config_file.unlink()
                except Exception as e:
                    logger.error(f"Error removing old config {config_file}: {str(e)}")


def get_user_config_path(user_id: str) -> Path:
    return BrowserManager.BROWSER_CONFIGS_DIR / f"{user_id}.json"


def get_user_profiles(user_id: str) -> List[Dict]:
    config_file = get_user_config_path(user_id)
    if not config_file.exists():
        return []

    try:
        with open(config_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading profiles for user {user_id}: {str(e)}")
        return []


def save_user_profiles(user_id: str, profiles: List[Dict]):
    config_file = get_user_config_path(user_id)
    try:
        with open(config_file, "w") as f:
            json.dump(profiles, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving profiles for user {user_id}: {str(e)}")
        raise


def transform_profiles(raw_profiles: List[Dict], browser_type: str) -> List[Dict]:
    transformed = []

    if browser_type == "octo":
        for profile in raw_profiles:
            transformed.append(
                {"id": profile["uuid"], "name": profile["name"], "browser": "octo"}
            )
    elif browser_type == "dolphin":
        for profile in raw_profiles:
            transformed.append(
                {"id": profile["id"], "name": profile["name"], "browser": "dolphin"}
            )
    elif browser_type == "gologin":
        for profile in raw_profiles["data"]:
            transformed.append(
                {"id": profile["id"], "name": profile["name"], "browser": "gologin"}
            )
    elif browser_type == "undetectable":
        for profile_id, profile in raw_profiles.get("data", {}).items():
            transformed.append(
                {
                    "id": profile_id,
                    "name": profile.get("name", "unnamed"),
                    "browser": "undetectable",
                }
            )
    elif browser_type == "vision":
        for profile in raw_profiles:
            transformed.append(
                {"id": profile["id"], "name": profile["name"], "browser": "vision"}
            )
    elif browser_type == "linken":
        for profile in raw_profiles["profiles"]:
            transformed.append(
                {"id": profile["id"], "name": profile["name"], "browser": "linken"}
            )

    return transformed
