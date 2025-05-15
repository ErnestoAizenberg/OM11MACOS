from datetime import datetime
from flask import render_template, session


def configure_api(
        app,
        logger,
        redis_client,
        generate_uuid_32: callable,
    ):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.before_request
    def before_request():
        # Initialize session if not exists
        if 'user_id' not in session:
            session['user_id'] = generate_uuid_32()
            redis_client.hset(
                f"user:{session['user_id']}", 'created_at',
                datetime.now().isoformat()
            )
            logger.info(
                f"New session initialized for user {session['user_id']}"
            )
