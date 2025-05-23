import redis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_redis(config):
    redis_client = redis.Redis(
        host=config.HOST,
        port=config.PORT,
        db=config.DB,
        decode_responses=config.DECODE_RESPONSES,
    )
    return redis_client
