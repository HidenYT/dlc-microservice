from flask import Flask
import config

def init_blueprints(app: Flask):
    from . import api
    app.register_blueprint(api.bp)

def create_app(config = config.FlaskConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    from app.database import init_db
    init_db(app)

    init_blueprints(app)

    return app