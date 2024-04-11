import datetime
import json
from typing import Any
from uuid import UUID, uuid4
from flask import request
from celery.result import AsyncResult
from sqlalchemy import select
from werkzeug.exceptions import NotFound, Conflict

from app.api.models import DLCNeuralNetwork, InferenceResults
from app.api.tasks import analyze_video_task, train_network_task
from app.utils.datasets import get_model_folder_path
from app.utils.training import get_model_training_stats
from . import bp
from app.database import db


@bp.post("/train-network")
def train_network_view():
    data: dict[Any, Any] = request.json # type: ignore 

    training_dataset = data["training_dataset"]

    training_config = data["training_config"]

    model_uid = uuid4()
    model = DLCNeuralNetwork()
    model.uid = model_uid
    model.started_training_at = datetime.datetime.now()
    model.network_folder_path = get_model_folder_path(model_uid)
    model.training_config = json.dumps(training_config)
    model.currently_training = True

    process: AsyncResult = train_network_task.delay(training_dataset, training_config, model_uid)
    model.celery_training_task_id = process.id
    
    db.session.add(model)
    db.session.commit()

    return {"model_uid": model_uid, "task_id": process.id}

@bp.get("/learning-stats")
def learning_stats_view():
    model_uid = request.args.get("model_uid")
    if model_uid is None:
        raise NotFound("You should provide model_uid in order to retrieve leraning stats of a model")
    return get_model_training_stats(UUID(model_uid))

@bp.post("/video-inference")
def analyze_video_view():
    data: dict = request.json
    
    video_base64 = data["video_base64"]

    file_name = data["file_name"]

    model_uid = data["model_uid"]
    
    q_model = select(DLCNeuralNetwork).where(DLCNeuralNetwork.uid == model_uid)
    nn = db.session.scalar(q_model)
    if nn is None:
        raise NotFound(f"No model with uid {model_uid}")
    if nn.currently_training:
        raise Conflict(f"Model with uid {model_uid} is currently being trained so it can not run inference")
    inference_results = InferenceResults()
    inference_results.network_uid = model_uid
    inference_results.started_inference_at = datetime.datetime.now()
    inference_results.currently_running_inference = False
    db.session.add(inference_results)
    db.session.commit()
    analyze_video_task.delay(video_base64, file_name, model_uid, inference_results.id)
    return {"results_id": inference_results.id}