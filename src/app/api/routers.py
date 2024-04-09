import datetime
import json
import os
from typing import Any
from uuid import uuid4
from flask import current_app, request
from celery.result import AsyncResult

from app.api.models import DLCNeuralNetwork
from app.api.tasks import train_network_task
from app.utils.datasets import get_model_folder_path
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