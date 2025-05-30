from flask import render_template, session


def configure_api(
    app,
    logger,
    redis_client,
    user_repo,
    generate_uuid_32: callable,
):
    @app.route("/")
    def index():
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            user = user_repo.get(user_id)

        user_activity = [
            {
                "text": "Logged in from New York",
                "date": "May 12, 2025",
            },
            {
                "text": "Updated profile information",
                "date": "May 10, 2025",
            },
            {"text": "Placed a new order", "date": "May 8, 2025"},
        ]

        return render_template(
            "index.html",
            user_id=user_id,
            user=user,
            user_activity=user_activity,
        )

    @app.before_request
    def before_request():
        logger.info(f"user_id in session={session.get('user_id')}")
        if "user_id" not in session:
            # session["user_id"] = generate_uuid_32()
            # redis_client.hset(
            #    f"user:{session['user_id']}", "created_at", datetime.now().isoformat()
            # )
            # logger.info(f"New session initialized for user {session['user_id']}")
            pass
