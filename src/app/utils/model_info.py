from uuid import UUID
from sqlalchemy import select
from werkzeug.exceptions import NotFound
import json
from app.database import db
from app.api.models import DLCNeuralNetwork

def get_model_info(model_uid: UUID) -> "dict[str, str | float | int | None]":
    q = select(DLCNeuralNetwork).where(DLCNeuralNetwork.uid == model_uid)
    model = db.session.scalar(q)
    if model is None:
        raise NotFound(f"A model with uid {model_uid} does not exist.")
    info = json.loads(model.training_config)
    info["currently_training"] = model.currently_training
    info["started_training_at"] = model.started_training_at
    info["finished_training_at"] = model.finished_training_at
    return info