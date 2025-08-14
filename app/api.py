from flask import render_template, session


def configure_api(
    app,
    logger,
    user_repo,
    generate_uuid_32: callable,
    agent_manager,  # Добавлен параметр AgentManager
):
    @app.route("/dashboard")
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
            session["user_id"] = generate_uuid_32()
            agent_manager.initialize_user(
                session["user_id"]
            )  # Используем AgentManager вместо Redis
            logger.info(
                f"New session initialized for user {session['user_id']} using SQLite"
            )
