import base64
from dataclasses import dataclass
from io import BytesIO
import os
from uuid import UUID
from datetime import datetime
from flask import current_app
import py7zr


@dataclass
class DatasetInfo:
    path: str
    labels_csv_path: str

def generate_dataset_folder_name(model_uuid: UUID) -> str:
    return "{dt}-{uuid}".format(
        dt=datetime.now().strftime("%H.%M.%S.%f-%d.%m.%Y"),
        uuid=model_uuid,
    )

def get_model_folder_path(model_uid: UUID) -> str:
    return "-" + os.path.join(current_app.config["NETWORKS_DIR_PATH"], str(model_uid))