from typing import Any
from uuid import UUID

from app.celery import celery
from app.utils.dlc_project_creator import DLCProjectCreator
from app.utils.training import TrainingConfigAdapter, notify_model_finished_training


@celery.task
def train_network_task(training_ds_base64: str, training_config: dict[Any, Any], model_uid: UUID):
    config_adapter = TrainingConfigAdapter(training_config)
    project_creator = DLCProjectCreator(model_uid, training_ds_base64, config_adapter)
    project_path = project_creator.create_project()

    import deeplabcut
    display_iters = 100
    if config_adapter.maxiters > 100:
        display_iters = config_adapter.maxiters // 100
    deeplabcut.train_network(project_path, maxiters=config_adapter.maxiters, displayiters=display_iters)

    notify_model_finished_training(model_uid)