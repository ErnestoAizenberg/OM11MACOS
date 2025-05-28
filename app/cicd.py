from flask import current_app

def clear_template_cache():
    with current_app.app_context():
        current_app.jinja_env.cache = None
