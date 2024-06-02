from ultralytics import YOLO
import os, requests, json

roboflowkey = os.environ.get("ROBOFLOW_API_KEY")
model = YOLO("yolov8n.pt")
response = requests.get(
    f"https://api.roboflow.com/auto-time/autotime/7/yolov8?api_key={roboflowkey}"
)
print(json.dumps(json.loads(response.content), indent=4))
link = json.loads(response.content)["export"]["link"]
data = requests.get(link)
with open("data.zip", "wb") as f:
    f.write(data.content)
os.makedirs("dataset")
import zipfile

with zipfile.ZipFile("data.zip", "r") as zip_ref:
    zip_ref.extractall("dataset")
model.info()
results = model.train(
    data="data/data.yaml",
    epochs=100,
    task="detect",
    batch=-1,
)
# B1IovfYIG6d7q9rSBBG1
