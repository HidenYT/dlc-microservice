import base64
from datetime import datetime
import glob
import os
from uuid import uuid4

from flask import current_app
import pandas as pd

def new_video_file_name(old_video_file_name: str) -> str:
    _, ext = os.path.splitext(old_video_file_name)
    return f"{uuid4()}-{datetime.now().strftime('%S-%M-%H_%d-%m-%Y')}{ext}"

def save_video_file(video_base64: str, video_file_name: str) -> str:
    video_bytes = base64.b64decode(video_base64)
    video_file_path = os.path.join(current_app.config["VIDEOS_DIR_PATH"], new_video_file_name(video_file_name))
    with open(video_file_path, "wb") as f:
        f.write(video_bytes)
    return video_file_path

def find_analysis_csv(video_path: str) -> str:
    no_ext_path, ext = os.path.splitext(video_path)
    return glob.glob(f"{no_ext_path}*.csv")[0]

def create_analysis_dict_from_csv(csv_path: str) -> dict[int, dict[str, list[float]]]:
    df = pd.read_csv(csv_path, header=[1, 2])
    result: dict[int, dict[str, list[float]]] = {}
    for i, row in df.iterrows():
        result[i] = {} 
        for bp in df.columns.get_level_values(0)[1:]:
            x, y, prob = row[bp]
            if prob >= 0.5:
                result[i][bp] = [x, y]
            else:
                result[i][bp] = [None, None]
    return result