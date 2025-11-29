import json
import logging
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import requests

# Configure logging for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for maximum verbosity

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

class UndetectableError(Exception):
    pass

class BrowserManager:
    BROWSER_CONFIGS_DIR = Path("instance/browser_configs")
    REQUEST_TIMEOUT = 30
    CONFIG_CLEANUP_DAYS = 7

    def __init__(self):
        logger.info("Initializing BrowserManager")
        try:
            self.BROWSER_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
            logger.debug(
                f"Created/verified config directory at {self.BROWSER_CONFIGS_DIR}"
            )
        except Exception as e:
            logger.error(f"Failed to create config directory: {str(e)}", exc_info=True)
            raise

    def _log_response_details(self, response: requests.Response) -> None:
        """Log detailed information about the HTTP response."""
        try:
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")

            try:
                if response.text:  # Only try to parse if there's content
                    logger.debug(
                        f"Response body: {response.text[:500]}..."
                    )  # Log first 500 chars
            except Exception as e:
                logger.warning(f"Could not log response body: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to log response details: {str(e)}", exc_info=True)

    def _make_request(
        self, method: str, url: str, **kwargs: Any
    ) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """Generic request method with comprehensive logging and error handling."""
        logger.debug(f"Making {method.upper()} request to {url}")
        try:
            kwargs.setdefault("timeout", self.REQUEST_TIMEOUT)
            response = requests.request(method, url, **kwargs)
            self._log_response_details(response)
            response.raise_for_status()
            return response, None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed to {url}: {str(e)}", exc_info=True)
            if hasattr(e, "response") and e.response:
                self._log_response_details(e.response)
            return None, e
        except Exception as e:
            logger.error(
                f"Unexpected error during request to {url}: {str(e)}", exc_info=True
            )
            return None, e

    def fetch_profiles(self, api_url: str, browser_type: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching profiles for {browser_type} from {api_url}")
        endpoints = {
            "octo": f"{api_url}/api/v1/profile",
            "dolphin": f"{api_url}/profiles",
            "gologin": f"{api_url}/gologin/profiles",
            "undetectable": f"{api_url}/list",
            "vision": f"{api_url}/api/v1/profiles",
            "linken": f"{api_url}/api/profiles",
        }

        endpoint = endpoints.get(browser_type)
        if not endpoint:
            error_msg = f"Unsupported browser type: {browser_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        response, error = self._make_request(
            "GET", endpoint, headers={"Content-Type": "application/json"}
        )

        if error:
            raise error

        if response is None:
            raise ValueError("No response received")

        try:
            profiles = transform_profiles(response.json(), browser_type)
            logger.info(
                f"Successfully fetched {len(profiles)} profiles for {browser_type}"
            )
            return profiles
        except ValueError as e:
            logger.error(
                f"Invalid JSON response from {browser_type}: {str(e)}", exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error processing profiles: {str(e)}", exc_info=True
            )
            raise

    def check_profile(
        self, user_id: str, api_url: str, profile_id: str, browser_type: str
    ) -> None:
        pass
    
    def start_profile(
        self, user_id: str, api_url: str, profile_id: str, browser_type: str
    ) -> Dict[str, Any]:
        logger.info(
            f"Starting profile {profile_id} for user {user_id} (type: {browser_type})"
        )
        if not all([api_url, profile_id, browser_type]):
            error_msg = "Missing required parameters"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            profiles = get_user_profiles(user_id)
            logger.debug(f"Current profiles for user {user_id}: {len(profiles)}")

            start_methods = {
                "octo": self._start_octo_profile,
                "dolphin": self._start_dolphin_profile,
                "gologin": self._start_gologin_profile,
                "undetectable": self._start_undetectable_profile,
                "vision": self._start_vision_profile,
                "linken": self._start_linken_profile,
            }

            if browser_type not in start_methods:
                error_msg = f"Unsupported browser type: {browser_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Calling start method for {browser_type}")
            result = start_methods[browser_type](api_url, profile_id)

            if not result.get("ws_url"):
                error_msg = "No WebSocket URL returned from start method"
                logger.error(error_msg)
                raise ValueError(error_msg)

            new_profile = {
                "id": profile_id,
                "browser": browser_type,
                "ws_url": result["ws_url"],
                "api_url": api_url,
                "started_at": datetime.now().isoformat(),
            }
            profiles.append(new_profile)

            logger.debug(f"Saving updated profiles for user {user_id}")
            save_user_profiles(user_id, profiles)

            logger.info(f"Successfully started profile {profile_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to start profile: {str(e)}", exc_info=True)
            raise

    def disconnect_all(self, user_id: str) -> None:
        logger.info(f"Disconnecting all profiles for user {user_id}")
        try:
            profiles = get_user_profiles(user_id)
            if not profiles:
                logger.debug("No profiles found to disconnect")
                return

            logger.debug(f"Found {len(profiles)} profiles to disconnect")

            success_count = 0
            for profile in profiles:
                try:
                    logger.debug(
                        f"Stopping profile {profile['id']} ({profile['browser']})"
                    )
                    stop_method = getattr(self, f"_stop_{profile['browser']}_profile")
                    stop_method(profile["api_url"], profile["id"])
                    success_count += 1
                    logger.debug(f"Successfully stopped profile {profile['id']}")
                except Exception as e:
                    logger.error(
                        f"Error stopping profile {profile['id']}: {str(e)}",
                        exc_info=True,
                    )

            logger.debug("Clearing user profiles")
            save_user_profiles(user_id, [])

            logger.debug("Cleaning up old configs")
            self._cleanup_old_configs()

            logger.info(
                f"Disconnected {success_count}/{len(profiles)} profiles for user {user_id}"
            )
        except Exception as e:
            logger.error(f"Failed to disconnect all profiles: {str(e)}", exc_info=True)
            raise

    def _start_octo_profile(self, api_url: str, profile_id: str) -> Dict[str, str]:
        logger.debug(f"Starting Octo profile {profile_id}")
        try:
            url = f"{api_url}/api/v1/profile/{profile_id}/start"
            payload = {"headless": False}
            logger.debug(f"POST to {url} with payload: {payload}")

            response, error = self._make_request("POST", url, json=payload)
            if error:
                raise error

            if response is None:
                raise ValueError("No response received")

            ws_url = f"ws://{api_url.split('//')[1]}/ws/{profile_id}"
            logger.debug(f"Octo profile started, WS URL: {ws_url}")
            return {"ws_url": ws_url}
        except Exception as e:
            logger.error(f"Failed to start Octo profile: {str(e)}", exc_info=True)
            raise

    def _start_dolphin_profile(self, api_url: str, profile_id: str) -> Dict[str, str]:
        logger.debug(f"Starting Dolphin profile {profile_id}")
        try:
            url = f"{api_url}/profile/{profile_id}/start"
            logger.debug(f"POST to {url}")

            response, error = self._make_request("POST", url)
            if error:
                raise error

            if response is None:
                raise ValueError("No response received")

            data = response.json()
            if not data.get("ws_url"):
                error_msg = "No WebSocket URL in Dolphin response"
                logger.error(error_msg)
                raise ValueError(error_msg)

            ws_url = data["ws_url"]
            logger.debug(f"Dolphin profile started, WS URL: {ws_url}")
            return {"ws_url": ws_url}
        except Exception as e:
            logger.error(f"Failed to start Dolphin profile: {str(e)}", exc_info=True)
            raise

    def _start_gologin_profile(self, api_url: str, profile_id: str) -> Dict[str, str]:
        logger.debug(f"Starting GoLogin profile {profile_id}")
        try:
            url = f"{api_url}/gologin/profile/{profile_id}/start"
            logger.debug(f"POST to {url}")

            response, error = self._make_request("POST", url)
            if error:
                raise error

            if response is None:
                raise ValueError("No response received")

            data = response.json()
            if not data.get("debuggerAddress"):
                error_msg = "No debuggerAddress in GoLogin response"
                logger.error(error_msg)
                raise ValueError(error_msg)

            ws_url = data["debuggerAddress"]
            logger.debug(f"GoLogin profile started, WS URL: {ws_url}")
            return {"ws_url": ws_url}
        except Exception as e:
            logger.error(f"Failed to start GoLogin profile: {str(e)}", exc_info=True)
            raise

    def _start_undetectable_profile(
        self,
        api_url: str,
        profile_id: str,
        chrome_flags: Optional[str] = None,
        start_pages: Optional[str] = None,
        headless: bool = False,
    ) -> Dict[str, str]:
        logger.debug(f"Starting Undetectable profile {profile_id}")
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            resp = requests.get(f"{api_url}/profile/getinfo/{profile_id}", headers=headers)
            resp_json = resp.json()

            check_undertactable_response(resp_json)
            data = resp_json['data']
            if data.get('status') == "Started":
                ws_url = data["websocket_link"]
                return {"ws_url": ws_url}

            url = f"{api_url}/profile/start/{urllib.parse.quote(profile_id)}"
            
            params: Dict[str, str] = {}
            if headless:
                params["--headless"] = "new"
            if chrome_flags:
                params["chrome_flags"] = chrome_flags

            logger.debug(f"GET to {url} with params: {params}")

            response, error = self._make_request(
                "GET", url, params=params, headers=headers
            )
            
            if error:
                raise error

            if response is None:
                raise ValueError("No response received")

            logger.debug(str(response.json()))

            resp_json = response.json()
            check_undertactable_response(resp_json)
            ws_url = None
            data = resp_json.get('data', {})

            if data.get("websocket_link"):
                ws_url = data["websocket_link"]
   
            if not ws_url:
                error_msg = (
                    "No websocket_link in Undetectable response." + f"Response: {data}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Undetectable profile started, WS URL: {ws_url}")
            return {"ws_url": ws_url}
        except Exception as e:
            logger.error(
                f"Failed to start Undetectable profile: {str(e)}", exc_info=True
            )
            raise

    def _start_vision_profile(self, api_url: str, profile_id: str) -> Dict[str, str]:
        logger.debug(f"Starting Vision profile {profile_id}")
        try:
            url = f"{api_url}/api/v1/profile/{profile_id}/start"
            payload = {"headless": False}
            logger.debug(f"POST to {url} with payload: {payload}")

            response, error = self._make_request("POST", url, json=payload)
            if error:
                raise error

            if response is None:
                raise ValueError("No response received")

            ws_url = f"ws://{api_url.split('//')[1]}/ws/{profile_id}"
            logger.debug(f"Vision profile started, WS URL: {ws_url}")
            return {"ws_url": ws_url}
        except Exception as e:
            logger.error(f"Failed to start Vision profile: {str(e)}", exc_info=True)
            raise

    def _start_linken_profile(self, api_url: str, profile_id: str) -> Dict[str, str]:
        logger.debug(f"Starting Linken profile {profile_id}")
        try:
            url = f"{api_url}/api/profile/{profile_id}/start"
            payload = {"headless": False}
            logger.debug(f"POST to {url} with payload: {payload}")

            response, error = self._make_request("POST", url, json=payload)
            if error:
                raise error

            if response is None:
                raise ValueError("No response received")

            data = response.json()
            if not data.get("wsEndpoint"):
                error_msg = "No wsEndpoint in Linken response"
                logger.error(error_msg)
                raise ValueError(error_msg)

            ws_url = data["wsEndpoint"]
            logger.debug(f"Linken profile started, WS URL: {ws_url}")
            return {"ws_url": ws_url}
        except Exception as e:
            logger.error(f"Failed to start Linken profile: {str(e)}", exc_info=True)
            raise

    def _stop_octo_profile(self, api_url: str, profile_id: str) -> None:
        logger.debug(f"Stopping Octo profile {profile_id}")
        try:
            url = f"{api_url}/api/v1/profile/{profile_id}/stop"
            logger.debug(f"POST to {url}")

            _, error = self._make_request("POST", url)
            if error:
                raise error

            logger.debug(f"Octo profile {profile_id} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop Octo profile: {str(e)}", exc_info=True)
            raise

    def _stop_dolphin_profile(self, api_url: str, profile_id: str) -> None:
        logger.debug(f"Stopping Dolphin profile {profile_id}")
        try:
            url = f"{api_url}/profile/{profile_id}/stop"
            logger.debug(f"POST to {url}")

            _, error = self._make_request("POST", url)
            if error:
                raise error

            logger.debug(f"Dolphin profile {profile_id} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop Dolphin profile: {str(e)}", exc_info=True)
            raise

    def _stop_gologin_profile(self, api_url: str, profile_id: str) -> None:
        logger.debug(f"Stopping GoLogin profile {profile_id}")
        try:
            url = f"{api_url}/gologin/profile/{profile_id}/stop"
            logger.debug(f"POST to {url}")

            _, error = self._make_request("POST", url)
            if error:
                raise error

            logger.debug(f"GoLogin profile {profile_id} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop GoLogin profile: {str(e)}", exc_info=True)
            raise

    def _stop_undetectable_profile(self, api_url: str, profile_id: str) -> None:
        logger.debug(f"Stopping Undetectable profile {profile_id}")
        try:
            url = f"{api_url}/api/profile/{profile_id}/stop"
            logger.debug(f"POST to {url}")

            _, error = self._make_request("POST", url)
            if error:
                raise error

            logger.debug(f"Undetectable profile {profile_id} stopped successfully")
        except Exception as e:
            logger.error(
                f"Failed to stop Undetectable profile: {str(e)}", exc_info=True
            )
            raise

    def _stop_vision_profile(self, api_url: str, profile_id: str) -> None:
        logger.debug(f"Stopping Vision profile {profile_id}")
        try:
            url = f"{api_url}/api/v1/profile/{profile_id}/stop"
            logger.debug(f"POST to {url}")

            _, error = self._make_request("POST", url)
            if error:
                raise error

            logger.debug(f"Vision profile {profile_id} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop Vision profile: {str(e)}", exc_info=True)
            raise

    def _stop_linken_profile(self, api_url: str, profile_id: str) -> None:
        logger.debug(f"Stopping Linken profile {profile_id}")
        try:
            url = f"{api_url}/api/profile/{profile_id}/stop"
            logger.debug(f"POST to {url}")

            _, error = self._make_request("POST", url)
            if error:
                raise error

            logger.debug(f"Linken profile {profile_id} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop Linken profile: {str(e)}", exc_info=True)
            raise

    def _cleanup_old_configs(self) -> None:
        logger.info("Cleaning up old config files")
        try:
            cutoff = datetime.now() - timedelta(days=self.CONFIG_CLEANUP_DAYS)
            logger.debug(f"Removing configs older than {cutoff}")

            removed_count = 0
            for config_file in self.BROWSER_CONFIGS_DIR.glob("*.json"):
                try:
                    file_mtime = datetime.fromtimestamp(config_file.stat().st_mtime)
                    if file_mtime < cutoff:
                        logger.debug(f"Removing old config: {config_file}")
                        config_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.error(
                        f"Error processing config {config_file}: {str(e)}",
                        exc_info=True,
                    )

            logger.info(
                f"Config cleanup completed. Removed {removed_count} old configs"
            )
        except Exception as e:
            logger.error(f"Error during config cleanup: {str(e)}", exc_info=True)
            raise


def get_user_config_path(user_id: str) -> Path:
    path = BrowserManager.BROWSER_CONFIGS_DIR / f"{user_id}.json"
    logger.debug(f"Config path for user {user_id}: {path}")
    return path


def get_user_profiles(user_id: str) -> List[Dict[str, Any]]:
    logger.debug(f"Getting profiles for user {user_id}")
    config_file = get_user_config_path(user_id)
    if not config_file.exists():
        logger.debug(f"No config file found for user {user_id}")
        return []

    try:
        with open(config_file) as f:
            profiles = json.load(f)
            logger.debug(f"Loaded {len(profiles)} profiles for user {user_id}")
            return profiles
    except json.JSONDecodeError as e:
        logger.error(
            f"Invalid JSON in config file for user {user_id}: {str(e)}", exc_info=True
        )
        return []
    except IOError as e:
        logger.error(
            f"Error reading config file for user {user_id}: {str(e)}", exc_info=True
        )
        return []


def save_user_profiles(user_id: str, profiles: List[Dict[str, Any]]) -> None:
    logger.debug(f"Saving {len(profiles)} profiles for user {user_id}")
    config_file = get_user_config_path(user_id)
    try:
        with open(config_file, "w") as f:
            json.dump(profiles, f, indent=2)
        logger.debug(f"Profiles saved successfully for user {user_id}")
    except IOError as e:
        logger.error(
            f"Error saving profiles for user {user_id}: {str(e)}", exc_info=True
        )
        raise


def transform_profiles(raw_profiles: Any, browser_type: str) -> List[Dict[str, Any]]:
    logger.debug(f"Transforming profiles for {browser_type}")
    transformed = []

    try:
        if browser_type == "octo":
            if not isinstance(raw_profiles, list):
                raise ValueError("Expected list for Octo profiles")

            for profile in raw_profiles:
                transformed.append(
                    {"id": profile["uuid"], "name": profile["name"], "browser": "octo"}
                )
        elif browser_type == "dolphin":
            if not isinstance(raw_profiles, list):
                raise ValueError("Expected list for Dolphin profiles")

            for profile in raw_profiles:
                transformed.append(
                    {"id": profile["id"], "name": profile["name"], "browser": "dolphin"}
                )
        elif browser_type == "gologin":
            if not isinstance(raw_profiles, dict) or "data" not in raw_profiles:
                raise ValueError("Expected data field in GoLogin response")

            for profile in raw_profiles["data"]:
                transformed.append(
                    {"id": profile["id"], "name": profile["name"], "browser": "gologin"}
                )
        elif browser_type == "undetectable":
            if not isinstance(raw_profiles, dict) or "data" not in raw_profiles:
                raise ValueError("Expected data field in Undetectable response")

            data = raw_profiles.get("data", {})
            if isinstance(data, dict):
                for profile_id, profile in data.items():
                    transformed.append(
                        {
                            "id": profile_id,
                            "name": profile.get("name", "unnamed"),
                            "browser": "undetectable",
                        }
                    )
        elif browser_type == "vision":
            if not isinstance(raw_profiles, list):
                raise ValueError("Expected list for Vision profiles")

            for profile in raw_profiles:
                transformed.append(
                    {"id": profile["id"], "name": profile["name"], "browser": "vision"}
                )
        elif browser_type == "linken":
            if not isinstance(raw_profiles, dict) or "profiles" not in raw_profiles:
                raise ValueError("Expected profiles field in Linken response")

            for profile in raw_profiles["profiles"]:
                transformed.append(
                    {"id": profile["id"], "name": profile["name"], "browser": "linken"}
                )
        else:
            error_msg = f"Unsupported browser type for transformation: {browser_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Transformed {len(transformed)} profiles for {browser_type}")
        return transformed
    except KeyError as e:
        logger.error(f"Missing expected field in profile data: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error transforming profiles: {str(e)}", exc_info=True)
        raise


def check_undertactable_response(response: Dict[str, Any]) -> None:
    code = response.get('code')
    if code == 0:
        return
    elif code == 1:
        data = response.get("data")
        if not data:
            raise ValueError("Invalid Undetectable response")
        error = data.get("error")
        if not error:
            raise ValueError(f"UnknownError: error code 1, but error is {error}")
        raise UndetectableError(f"Undetectable browser return error: {error}")