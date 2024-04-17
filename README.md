# DLC microservice

Веб-приложение, предоставляющее API для доступа к функционалу библиотеки <a href="http://www.mackenziemathislab.org/deeplabcut">DeepLabCut</a> для обучения нейронных сетей с целью определения ключевых точек на теле животного.

## Обучение нейросети
Запрос запускает обучение модели на переданном датасете с указанными настройками. В ответ возвращает JSON, содержащий UUID обучаемой модели и id задачи в Celery.
<details>
<summary>
Подробнее
</summary>

Метод: `POST`

Путь: `/api/train-network`

### Поля принимаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|training_dataset|string|Обязательный|Закодированный в формате base64 датасет формата 7z|
|training_config|JSON|Обязательный|Содержит настройки обучения нейросети (описаны далее)|

#### Поля объекта в поле training_config
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|test_fraction|number|Обязательный|Доля изображений в тестовой выборке.|
|num_epochs|number|Обязательный|Целое число - количество эпох обучения.|
|backbone_model|string|Обязательный|Кодировщик. Должен быть указан один из: "resnet_50", "resnet_101", "resnet_152", "mobilenet_v2_1.0","mobilenet_v2_0.75", "mobilenet_v2_0.5", "mobilenet_v2_0.35", "efficientnet-b0", "efficientnet-b1", "efficientnet-b2", "efficientnet-b3", "efficientnet-b4", "efficientnet-b5", "efficientnet-b6".|

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|model_uid|string|Обязательный|UUID обучаемой модели.|
|task_id|string|Обязательный|id задачи Celery.|

### Пример
Запрос:
```JSON
{
    "training_dataset": "N3q8ryccAAQ1zQE5HGgLAQAAAAAZAAAAAAAAAN",
    "training_config": {
        "test_fraction": 0.2,
        "num_epochs": 2,
        "backbone_model": "mobilenet_v2_1.0",
    }
}
```
Ответ:
```JSON
{
    "model_uid": "0c4c2c8d-c33d-48db-8090-c5ca4bd332c4",
    "task_id": "9809bbf1-7158-401d-a37d-9bb407ba9b22"
}
```
</details>

## Получение статистики обучения
Возвращает JSON с различными данными о модели: loss на тренировочных данных и learning rate.
<details>
<summary>
Подробнее
</summary>

Метод: `GET`

Путь: `/api/learning-stats`

### Параметры запроса
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|model_uid|string|Обязательный|UUID модели. Можно передавать UUID как обучаемой, так и уже обученной модели. |

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|loss|JSON|Обязательный|JSON объект, содержащий номера эпох в качестве ключей и соответствующие им значения функции потерь на тренировочной выборке в качестве значений.|
|lr|JSON|Обязательный|JSON объект, содержащий номера эпох в качестве ключей и соответствующие им значения learning rate в качестве значений.|

### Пример №1 (модель обучалась 2 эпохи)
Запрос:

`http://127.0.0.1:5000/api/learning-stats?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
    "loss": {
        "0": 4.385681629180908,
        "1": 1.4176582098007202
    },
    "lr": {
        "0": 0.0001,
        "1": 0.0001
    }
}
```
### Пример №2 (модель начала обучение, но не завершила ещё ни одной эпохи)
Запрос:

`http://127.0.0.1:5000/api/learning-stats?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
}
```

### Пример №3 (модель обучалась 200 эпох, поэтому эпохи выводятся с большим шагом)
Запрос:

`http://127.0.0.1:5000/api/learning-stats?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
    "loss": {
        "100": 4.385681629180908,
        "200": 1.4176582098007202
    },
    "lr": {
        "100": 0.0001,
        "200": 0.0001
    }
}
```
</details>

## Запуск нейросети на видео
Запускает выбранную обученную нейросеть на передаваемом видео. Возвращает JSON с id результата, который можно будет получить позднее, а также id задачи Celery.
<details>
<summary>
Подробнее
</summary>

Метод: `POST`

Путь: `/api/video-inference`

### Поля принимаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|video_base64|string|Обязательный|Закодированное в формате base64 видео.|
|file_name|string|Обязательный|Название видео с расширением файла.|
|model_uid|string|Обязательный| Строка с UUID обученной модели.|

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|results_id|number|Обязательный|Целое число - id результата запуска, по которому необходимо запросить результат.|

### Пример
Запрос:
```JSON
{
    "file_name": "rabbit.mp4",
    "model_uid": "0c4c2c8d-c33d-48db-8090-c5ca4bd332c4",
    "video_base64": "N3q8ryccAAQ1zQE5HGgLAQAAAAAZAAAAAAAAAN"
}
```
Ответ:
```JSON
{
    "results_id": 2
}
```
</details>

## Получение информации о нейросети
Принимает uid нейросети и возвращает информацию о ней: настройки обучения, обучается ли она в данный момент, даты и время начала и окончания обучения.
<details>
<summary>
Подробнее
</summary>

Метод: `GET`

Путь: `/api/model-info`

### Параметры запроса
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|model_uid|string|Обязательный|UUID модели. |

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|backbone_model|string|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|num_epochs|string|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|test_fraction|number|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|currently_training|boolean|Обязательный|true, если в данный момент модель обучается. false - если нет.|
|started_training_at|string|Обязательный|Строка с датой и временем начала последнего обучения нейросети. Может быть null.|
|finished_training_at|string|Обязательный|Строка с датой и временем окончания последнего обучения нейросети. Может быть null, если модель в данный момент обучается.|

### Пример
Запрос:

`http://127.0.0.1:5000/api/model-info?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
    "backbone_model": "mobilenet_v2_1.0",
    "currently_training": true,
    "finished_training_at": null,
    "num_epochs": 2,
    "started_training_at": "Sun, 31 Mar 2024 12:58:33 GMT",
    "test_fraction": 0.2
}
```

</details>

## Получение результатов анализа видео
Принимает список id результатов через запятую и возвращает информацию о каждом из них: id и json с ключевыми точками для каждого кадра.
<details>
<summary>
Подробнее
</summary>

Метод: `GET`

Путь: `/api/inference-results`

### Параметры запроса
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|ids|string|Обязательный|Через запятую id результатов, полученных при запросе к `/api/video-inference`. Пример: `?ids=1,2,5`|

### Поля возвращаемого JSON
Возвращается JSON, состоящий из списка объектов. Каждый объект состоит из поля id - id результата, и поля keypoints. В поле keypoints содержится объект, поля которого - номера кадров видео, а значения - JSON объекты. В этих вложенных JSON объектах ключи - названия ключевых точек, а значения - массивы, каждый состоящий из двух элементов - координат X и Y соответствующей ключевой точки на соответствующем кадре. Если точка не видна на кадре, обе её координаты будут равны `null`.

### Пример 1 - запрос одного результата
Запрос:

`http://127.0.0.1:5000/api/inference-results?ids=15`

Ответ:
```JSON
[
    {
        "id": 15,
        "keypoints":
        {
            "0": {
                "Ankle left": [
                    840.6176147460938,
                    491.8916931152344
                ],
                "Ankle right": [
                    719.988037109375,
                    480.0779724121094
                ]
            },
            "1": {
                "Ankle left": [
                    840.88037109375,
                    490.9996032714844
                ],
                "Ankle right": [
                    720.0138549804688,
                    480.0594177246094
                ]
            }
        }
    }
]
```
### Пример 2 - запрос нескольких результатов
Запрос:

`http://127.0.0.1:5000/api/inference-results?ids=15,25`

Ответ:
```JSON
[
    {
        "id": 15,
        "keypoints":
        {
            "0": {
                "Ankle left": [
                    840.6176147460938,
                    491.8916931152344
                ],
                "Ankle right": [
                    719.988037109375,
                    480.0779724121094
                ]
            },
            "1": {
                "Ankle left": [
                    840.88037109375,
                    490.9996032714844
                ],
                "Ankle right": [
                    720.0138549804688,
                    480.0594177246094
                ]
            }
        }
    },
    {
        "id": 16,
        "keypoints":
        {
            "0": {
                "Ear left": [
                    558.4687878987164,
                    719.988037109375
                ],
                "Ear right": [
                    720.0138549804688,
                    840.8803710937586
                ]
            },
            "1": {
                "Ear left": [
                    580.8649846321368,
                    710.8949848893553
                ],
                "Ear right": [
                    700.8778478408707,
                    900.6854894306508
                ]
            }
        }
    }
]
```
</details>