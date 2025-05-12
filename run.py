from app import create_app
from config import Config, RedisConfig
import subprocess

if __name__ == "__main__":
    app = create_app(
        app_config=Config(),
        redis_config=RedisConfig(),
    )
    subprocess.run(
       [
            "redis-server",
            "--daemonsize"
            "yes"
        ],
        check=True
     )
    app.run(
        debug=app.config.get("DEBUG"),
        port=app.config.get("PORT"),
    )
