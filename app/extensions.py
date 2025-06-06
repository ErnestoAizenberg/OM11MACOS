import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],
)

db = SQLAlchemy()


def init_redis(config):
    redis_client = redis.Redis(
        host=config.HOST,
        port=config.PORT,
        db=config.DB,
        decode_responses=config.DECODE_RESPONSES,
    )
    return redis_client
