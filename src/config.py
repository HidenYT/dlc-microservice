import os
from dotenv import load_dotenv
load_dotenv()


class FlaskConfig:
    UPLOADS_DIR_NAME = "uploads"
    DATASETS_DIR_PATH = os.path.join(UPLOADS_DIR_NAME, "datasets")
    NETWORKS_DIR_PATH = os.path.join(UPLOADS_DIR_NAME, "networks")
    VIDEOS_DIR_PATH = os.path.join(UPLOADS_DIR_NAME, "videos")
    DUMMY_VIDEO_PATH = os.path.join(UPLOADS_DIR_NAME, "dummy.mp4")

    DB_ENGINE = os.getenv('DB_ENGINE')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f"{DB_ENGINE}+psycopg://{DB_USER}:{DB_PASSWORD}@"f"{DB_HOST}:{DB_PORT}/{DB_NAME}"


class CeleryConfig:
    broker_url = os.getenv('REDIS_URL')