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
        try:
            subprocess.run(["redis-server", "--daemonize", "yes"], check=True)
        except PermissionError as e:             raise RuntimeError("redis server is not installed you can do it via: sudo apt install redis-server or pkg install redis")
    app.run(
        debug=app.config.get("DEBUG"),
        port=app.config.get("PORT"),
    )



