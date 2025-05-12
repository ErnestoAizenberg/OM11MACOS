import logging
from typing import List

import requests


class ManusClient:
    def __init__(self, agent_url: str, logger: logging.Logger):
        self.agent_url = agent_url
        self.logger = logger

    def execute_command(self, message: str, user_uuid: str) -> List[str]:
        params = {"message": message, "user_uuid": user_uuid}
        try:
            response = requests.get(
                f"{self.agent_url}/api/execute_command/", params=params
            )
            response.raise_for_status()
            command_list: List[str] = response.json()
            if not isinstance(command_list, list):
                self.logger.error("Invalid response format")
                return []
            return command_list
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return []
