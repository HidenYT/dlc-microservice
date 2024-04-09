import os
from flask import Flask
import config

def init_blueprints(app: Flask):
    from . import api
    app.register_blueprint(api.bp)

def create_app_dirs(app: Flask):
    os.makedirs(app.config["UPLOADS_DIR_NAME"], exist_ok=True)
    os.makedirs(app.config["DATASETS_DIR_PATH"], exist_ok=True)
    os.makedirs(app.config["NETWORKS_DIR_PATH"], exist_ok=True)

def create_app(config = config.FlaskConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    create_app_dirs(app)

    from app.database import init_db
    init_db(app)

    init_blueprints(app)

    return app