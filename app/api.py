from datetime import datetime
from flask import render_template, session


def configure_api(
    app,
    logger,
    redis_client,
    generate_uuid_32: callable,
):
    @app.route("/")
    def index():
        user_id = session.get("user_id", None)
        return render_template("index.html", user_id=user_id)

    @app.before_request
    def before_request():
        logger.info(f"user_id in session={session.get('user_id')}")
        if "user_id" not in session:
            #session["user_id"] = generate_uuid_32()
            #redis_client.hset(
            #    f"user:{session['user_id']}", "created_at", datetime.now().isoformat()
            #)
            #logger.info(f"New session initialized for user {session['user_id']}")
            pass
