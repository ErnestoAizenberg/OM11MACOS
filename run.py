import os
import shutil
import subprocess

from app import create_app
from config import APIURLConfig, Config, RedisConfig, mail_config

if __name__ == "__main__":
    app_config = Config()
    app = create_app(
        app_config=app_config,
        api_url_config=APIURLConfig(),
        #redis_config=RedisConfig(),
        mail_config=mail_config,
    )
    """
    redis_run = os.getenv("REDIS_RUN", "true").lower() == "true"
    if redis_run:
        print("Running Redis...")
        try:
            if shutil.which("redis-server") is not None:
                subprocess.run(["redis-server", "--daemonize", "yes"], check=True)
            else:
                raise RuntimeError(
                    "redis server is not installed you can do it via: sudo apt install redis-server or pkg install redis"
                )

        except PermissionError:
            raise RuntimeError(
                "redis server is not installed you can do it via: sudo apt install redis-server or pkg install redis"
            )
    """
    app.run(
        debug=app_config.get("DEBUG"),
        port=app_config.get("PORT"),
    )
