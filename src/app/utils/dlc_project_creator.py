import base64
import csv
import glob
from io import BytesIO, TextIOWrapper
from typing import Iterable, Optional
from uuid import UUID
from flask import current_app
import py7zr
import yaml
from yaml import SafeDumper
from app.utils.training import TrainingConfigAdapter
import os


class DLCProjectCreator:
    
    def __init__(self, model_uid: UUID, dataset_base64: str, adapter: TrainingConfigAdapter) -> None:
        self.adapter = adapter
        self.model_uid = model_uid
        self.dataset_base64 = dataset_base64

    
    def _convert_labels_to_dlc_format(self, labels_file_path: str) -> tuple[str, set[str]]:
        '''Создаёт файл `labeled-data/dummy/CollectedData_{username}.csv` из файла
        `labeled-data/dummy/labels.csv` в формате, необходимом для `CollectedData_{username}.csv`.
        
        Возвращает путь к файлу `labeled-data/dummy/CollectedData_{username}.csv`, а также список частей тела из файла разметки.'''
        # Выбираем данные из файла разметки
        with open(labels_file_path, "r") as f:
            reader = iter(csv.reader(f))
            bodyparts = next(reader)[1:]
            next(reader)
            coords: dict[str, list[str]] = {}
            for row in reader:
                coords[row[0]] = [val for val in row[1:]]

        # Создаём файл разметки по формату DLC
        filename = f'CollectedData_{self.model_uid}.csv'
        labels_folder = os.path.dirname(labels_file_path)
        result_path = os.path.join(labels_folder, filename)
        with open(result_path, "w") as f:
            l = (len(bodyparts))
            f.write("scorer" + (f",{self.model_uid}")*l + os.linesep)
            f.write("bodyparts," + ",".join(bodyparts) + os.linesep)
            f.write("coords" + ",x,y"*(l//2) + os.linesep)
            for k, v in coords.items():
                f.write(f"labeled-data/dummy/{k}," + ",".join(v) + os.linesep)
        return result_path, set(bodyparts)


    def _fill_project_config(self, config_path: str, bodyparts: Iterable[str]):
        '''Изменяет файл `config.yaml`, добавляя поля в `bodyparts` части тела из разметки и удаляя 
        данные из поля `skeleton`.'''
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            data["TrainingFraction"] = [self.adapter.training_fraction]
            data["bodyparts"] = list(bodyparts)
            data["skeleton"] = None
            data["identity"] = None
            SafeDumper.add_representer(
                type(None),
                lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
            )
        with open(config_path, "w") as f:
            f.write(yaml.safe_dump(data, default_flow_style=False))
    
    # def _fill_training_config(self, project_path: str, config_path: str):
    #     with open(config_path, "r") as f:
    #         pose_cfg_path = os.path.join(project_path, "dlc-models", "iteration-0")
    #         pose_cfg_path = glob.glob(os.path.join(pose_cfg_path, "*"))[0]
    #         pose_cfg_path = os.path.join(pose_cfg_path, "train", "pose_cfg.yaml")
    #     with open(pose_cfg_path, "r") as f:
    #         pose_cfg_data = yaml.safe_load(f)
    #         SafeDumper.add_representer(
    #             type(None),
    #             lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
    #         )
    #     with open(pose_cfg_path, "w") as f:
    #         f.write(yaml.safe_dump(pose_cfg_data, default_flow_style=False))


    def create_project(self) -> str:
        # Импорт из функции, так как загрузка библиотеки занимает много времени
        import deeplabcut

        base_folder = current_app.config["NETWORKS_DIR_PATH"]
        dummy_video = current_app.config["DUMMY_VIDEO_PATH"]

        proj_config = deeplabcut.create_new_project("", str(self.model_uid), [dummy_video], working_directory=base_folder)
        project_path = os.path.dirname(proj_config)

        # Распаковка датасета в папку разметки проекта
        labels_folder_path = os.path.join(project_path, 'labeled-data', 'dummy')
        os.makedirs(labels_folder_path, exist_ok=True)
        training_dataset = base64.b64decode(self.dataset_base64)
        buf = BytesIO(training_dataset)
        with py7zr.SevenZipFile(buf) as archive:
            archive.extractall(labels_folder_path)

        # Изменение файла разметки под формат DLC
        labels_file = os.path.join(labels_folder_path, 'labels.csv')
        labels_file, bodyparts = self._convert_labels_to_dlc_format(labels_file)
        deeplabcut.convertcsv2h5(proj_config, scorer=str(self.model_uid), userfeedback=False)

        # Заполняем config.yaml скелетом 
        self._fill_project_config(proj_config, bodyparts)

        deeplabcut.create_training_dataset(proj_config, net_type=self.adapter.net_type)

        # Дозаполняем настройки обучения [Пока не используется]
        # self._fill_training_config(project_path, proj_config)

        return proj_config