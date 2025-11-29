import uuid
from functools import wraps
from typing import TypeVar, Callable, cast

from flask import Response, jsonify, session, make_response

from app.logs import logger

F = TypeVar('F', bound=Callable[..., Response])

def generate_uuid_32():
    return str(uuid.uuid4()).replace("-", "")


# Helper decorator for authentication
def login_required(f: F) -> F:
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response:
        if "user_id" not in session:
            logger.info("User is unauthorized")
            return make_response(
                jsonify({"success": False, "error": "Unauthorized"}),
                401,
            )
        return f(*args, **kwargs)

    return cast(F, decorated_function) 
