import uuid
from functools import wraps

from flask import jsonify, session

from app.logs import logger


def generate_uuid_32():
    return str(uuid.uuid4()).replace("-", "")


# Helper decorator for authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            logger.info("User is unauthorized")
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function
