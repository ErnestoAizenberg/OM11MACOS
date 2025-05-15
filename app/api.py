from flask import render_template


def configure_api(app):
    @app.route('/')
    def index():
        return render_template('index.html')
