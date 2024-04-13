import base64
from datetime import datetime
import glob
import os
from typing import Iterable, Literal, Sequence
from uuid import uuid4
from flask import current_app
import pandas as pd
import requests
from sqlalchemy import select
import json

from app.database import db
from app.api.models import InferenceResults

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

def find_ready_unsent_analysis_results() -> Sequence[InferenceResults]:
    q = select(InferenceResults).where(
        InferenceResults.results_json != None,
        InferenceResults.sent_back == False
    )
    return db.session.scalars(q).all()

def send_analysis_results_back(results: Iterable[InferenceResults]) -> None:
    result_dict = {
        "sender": "DeepLabCut", 
        "results": []
    }
    for obj in results:
        result_dict["results"].append({
            "id": obj.id,
            "keypoints": json.loads(obj.results_json)
        })
    response = requests.request(
        method="POST",
        url=current_app.config["SEND_RESULTS_URL"],
        json=result_dict,
        headers={
            "Authorization": f"Bearer {current_app.config['SEND_RESULTS_TOKEN']}"
        }
    )
    if response.status_code == 200:
        for obj in results:
            obj.sent_back = True
        db.session.commit()