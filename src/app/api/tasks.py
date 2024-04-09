from typing import Any
from uuid import UUID

from app.celery import celery
from app.utils.dlc_project_creator import DLCProjectCreator
from app.utils.training import TrainingConfigAdapter


@celery.task
def train_network_task(training_ds_base64: str, training_config: dict[Any, Any], model_uid: UUID):
    config_adapter = TrainingConfigAdapter(training_config)
    project_creator = DLCProjectCreator(model_uid, training_ds_base64, config_adapter)
    project_path = project_creator.create_project()

    import deeplabcut
    deeplabcut.train_network(project_path, maxiters=config_adapter.maxiters, displayiters=1)
