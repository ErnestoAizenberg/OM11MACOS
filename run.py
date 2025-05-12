import os
import subprocess

from app import create_app
from config import Config, RedisConfig

if __name__ == "__main__":
    app = create_app(
        app_config=Config(),
        redis_config=RedisConfig(),
    )
    redis_run = os.getenv("REDIS_RUN", "true").lower() == "true"
    if redis_run:
        print("Running Redis...")
        subprocess.run(["redis-server", "--daemonize", "yes"], check=True)
    app.run(
        debug=app.config.get("DEBUG"),
        port=app.config.get("PORT"),
    )
