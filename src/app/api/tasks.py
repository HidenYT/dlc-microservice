import json
import os
from typing import Any
from uuid import UUID
from sqlalchemy import select

from app.api.models import DLCNeuralNetwork, InferenceResults
from app.celery import celery
from app.utils.dlc_project_creator import DLCProjectCreator
from app.utils.training import TrainingConfigAdapter, notify_model_finished_training
from app.database import db
from app.utils.video_analysis import create_analysis_dict_from_csv, find_analysis_csv, save_video_file


@celery.task
def train_network_task(training_ds_base64: str, training_config: dict[Any, Any], model_uid: UUID):
    config_adapter = TrainingConfigAdapter(training_config)
    project_creator = DLCProjectCreator(model_uid, training_ds_base64, config_adapter)
    project_path = project_creator.create_project()

    import deeplabcut
    display_iters = 1
    if config_adapter.maxiters > 100:
        display_iters = config_adapter.maxiters // 100
    deeplabcut.train_network(project_path, maxiters=config_adapter.maxiters, displayiters=display_iters)

    notify_model_finished_training(model_uid)

@celery.task
def analyze_video_task(video_base64: str, video_file_name: str, model_uid: UUID, results_id: int):
    q = select(DLCNeuralNetwork).where(DLCNeuralNetwork.uid == model_uid)
    model = db.session.execute(q).scalar_one()
    saved_video_path = save_video_file(video_base64, video_file_name)
    config_path = os.path.join(model.network_folder_path, "config.yaml")
    import deeplabcut
    deeplabcut.analyze_videos(config_path, [saved_video_path], save_as_csv=True)
    csv_path = find_analysis_csv(saved_video_path)
    results_model = db.session.execute(select(InferenceResults).where(InferenceResults.id == results_id)).scalar_one()
    results_model.results_json = json.dumps(create_analysis_dict_from_csv(csv_path))
    db.session.commit()
