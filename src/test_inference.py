import base64
import requests
import json

VIDEO_PATH = r"C:\Users\Dmitriy\Downloads\rabbit-new.mp4"

with open(VIDEO_PATH, "rb") as f:
    video_encoded = base64.b64encode(f.read()).decode()
json_dict={
    "file_name": "rabbit.mp4",
    "model_uid": "5866bc54-e14f-4a4c-b729-13dfef25f778",
    "video_base64": video_encoded,
}
print(json.dumps(json_dict)[:100])
response = requests.post("http://127.0.0.1:5000/api/video-inference",
                         json=json_dict,)
print(response.json())