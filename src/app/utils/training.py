import datetime
from typing import Any, Literal
from uuid import UUID
from werkzeug.exceptions import NotFound
from sqlalchemy import select
import os
import glob
import csv

from app.api.models import DLCNeuralNetwork
from app.database import db


class TrainingConfigAdapter:
    
    training_fraction: float

    net_type: Literal["resnet_50", 
                      "resnet_101", 
                      "resnet_152", 
                      "mobilenet_v2_1.0",
                      "mobilenet_v2_0.75",
                      "mobilenet_v2_0.5",
                      "mobilenet_v2_0.35",
                      "efficientnet-b0",
                      "efficientnet-b1",
                      "efficientnet-b2",
                      "efficientnet-b3",
                      "efficientnet-b4",
                      "efficientnet-b5",
                      "efficientnet-b6",]
    
    maxiters: int

    def __init__(self, config: dict[Any, Any]):
        self.training_fraction = 1-config["test_fraction"]
        self.maxiters = config["num_epochs"]
        self.net_type = config["backbone_model"]

def notify_model_finished_training(model_uid: UUID):
    q = select(DLCNeuralNetwork).where(DLCNeuralNetwork.uid == model_uid)
    model = db.session.execute(q).scalar_one()
    model.celery_training_task_id = None
    model.currently_training = False
    model.finished_training_at = datetime.datetime.now()
    db.session.commit()

def get_model_training_stats(model_uid: UUID) -> "dict[str, dict[str, dict[str, float]]]":
    q = select(DLCNeuralNetwork).where(DLCNeuralNetwork.uid == model_uid)
    model = db.session.execute(q).scalar()
    if model is None:
        raise NotFound(f"A model with uid {model_uid} does not exist.")
    project_path = model.network_folder_path
    stat_file_path = glob.glob(os.path.join(
        project_path, 
        "dlc-models", 
        "iteration-0", 
        "*", 
        "train", 
        "learning_stats.csv"
    ))
    print(stat_file_path)
    if not (stat_file_path and os.path.exists(stat_file_path[0])): return {}
    stat_file_path = stat_file_path[0]
    with open(stat_file_path, "r") as stats_file:
        reader = csv.reader(stats_file)
        result = {
            "loss": {},
            "lr": {}
        }
        for row in reader:
            epoch_n = row[0]
            result["loss"][epoch_n] = row[1]
            result["lr"][epoch_n] = row[2]
    return result