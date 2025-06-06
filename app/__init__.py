import os
from typing import Callable

import redis
from config import APIURLConfig, Config, RedisConfig
from flask import Flask

from app.agent.agent_manager import AgentManager
from app.agent.api import configure_agent_api
from app.agent.manus_client import ManusClient
from app.agent.settings.api import configure_agent_settings

# from app.telegram.api_client import TelegramClient
from app.api import configure_api
from app.auth import auth_bp
from app.browser.api import configure_browser_api
from app.browser.browser_manager import (
    BrowserManager,
    get_user_profiles,
    save_user_profiles,
    transform_profiles,
)
from app.email_auth import configure_email_auth
from app.email_service import EmailService
from app.extensions import db, init_redis, limiter
from app.logs import logger
from app.repos import UserRepo
from app.telegram.api import TelegramClient, init_telegram_api
from app.utils import generate_uuid_32, login_required

init_redis: Callable[[RedisConfig], redis.Redis]
init_telegram_api: Callable


def create_app(
    app_config: Config,
    api_url_config: APIURLConfig,
    redis_config: RedisConfig,
    mail_config,
) -> Flask:
    os.makedirs("instance", exist_ok=True)

    app = Flask(__name__)

    app.secret_key = app_config.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["OAUTH2_PROVIDERS"] = app_config.get("OAUTH2_PROVIDERS")

    app.config["TEMPLATES_AUTO_RELOAD"] = True

    limiter.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    redis_client = init_redis(redis_config)
    user_repo = UserRepo(db.session, logger)

    app.user_repo = user_repo

    # Memory habdler for OM Agent
    agent_manager = AgentManager(redis_client)

    agent_url: str = api_url_config.get("OM11", "")
    # For talking with OM11 microservice
    manus_client = ManusClient(
        logger=logger,
        agent_url=agent_url,
    )
    # For talking with OM11TG microservice
    telegram_client_instance = TelegramClient(
        logger=logger,
        api_base_url=api_url_config.get("OM11TG", ""),
    )
    # email_sender = "sereernest@gmail.com"
    email_service_instance = EmailService(
        smtp_server=mail_config.get("MAIL_SERVER"),
        smtp_port=mail_config.get("MAIL_PORT"),
        smtp_username=mail_config.get("MAIL_USERNAME"),
        smtp_password=mail_config.get("MAIL_PASSWORD"),
        sender=mail_config.get("MAIL_USERNAME"),
        use_tls=mail_config.get("MAIL_USE_TLS"),
    )

    # Fir Holding user_agent_settings
    # It may be not a part of this micro.
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
        app=app,
        logger=logger,
        BrowserManagerClass=BrowserManager,
        AGENT_ADDRESS=api_url_config.get("OM11TG"),
        get_user_profiles_fn=get_user_profiles,
        save_user_profiles_fn=save_user_profiles,
        transform_profiles_fn=transform_profiles,
    )

    # Initialize part of api, which is used to handle UI and communicate with OM11TG microservice
    init_telegram_api(
        app=app,
        login_required=login_required,
        logger=logger,
        limiter=limiter,
        telegram_client=telegram_client_instance,
    )

    # Main app routes
    configure_api(
        app=app,
        logger=logger,
        redis_client=redis_client,
        user_repo=user_repo,
        generate_uuid_32=generate_uuid_32,
    )
    configure_email_auth(
        app=app,
        user_repo=user_repo,
        email_service=email_service_instance,
    )
    app.register_blueprint(auth_bp, url_prefix="")
    return app
