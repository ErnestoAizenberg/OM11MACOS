from typing import Callable

import redis
from flask import Flask

from app.agent.agent_manager import AgentManager
from app.agent.api import configure_agent_api
from app.agent.manus_client import ManusClient
from app.agent.settings.api import configure_agent_settings
from app.browser.api import configure_browser_api
from app.browser.browser_manager import (
    BrowserManager,
    get_user_profiles,
    save_user_profiles,
    transform_profiles,
)
from app.extensions import init_redis
from app.logs import logger
from app.telegram.api import init_telegram_api
from app.telegram.api_client import TelegramClient
from app.utils import login_required
from config import RedisConfig

AGENT_URL = "http://localhost:5001"

init_redis: Callable[[RedisConfig], redis.Redis]
init_telegram_api: Callable


def create_app(app_config, redis_config: RedisConfig) -> Flask:
    app = Flask(__name__)
    redis_client = init_redis(redis_config)

    # Memory habdler for OM Agent
    agent_manager = AgentManager(redis_client)

    # For talking with OM11 microservice
    manus_client = ManusClient(
        logger=logger,
        agent_url=AGENT_URL,
    )
    # For talking with OM11TG microservice
    TG_API_URL = "hardcode"
    telegram_client_instance = TelegramClient(logger=logger, tg_api_url=TG_API_URL)

    # For holding user-agent settings, may be shouldb't be part of this micro.
    configure_agent_settings(
        app=app,
        logger=logger,
        agent_manager=agent_manager,
        login_required=login_required,
    )

    # Initialize part of api, which is used to handle UI and communicate with OM11 microservice
    configure_agent_api(
        app=app,
        logger=logger,
        agent_manager=agent_manager,
        manus_client=manus_client,
        telegram_client=telegram_client_instance,
        login_required=login_required,
    )

    # Initialize part of api, which is used to handle UI and communicate with browsers, hasn't bias yet
    configure_browser_api(
        app,
        BrowserManager,
        get_user_profiles,
        save_user_profiles,
        transform_profiles,
    )

    # Initialize part of api, which is used to handle UI and communicate with OM11TG microservice
    init_telegram_api(
        app=app,
        login_required=login_required,
        logger=logger,
    )

    return app
