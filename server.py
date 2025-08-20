from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np

app = Flask(__name__)
model = YOLO(r'C:/Users/user/Desktop/hand_gesture/output/nsl_yolo_train2/weights/best.pt')

@app.route('/detect', methods=['POST'])
def detect():
    image_data = request.data
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    results = model(image)
    names = model.names
    boxes = results[0].boxes
    classes = boxes.cls.cpu().numpy().astype(int)

    if len(classes) > 0:
        label = names[classes[0]]
    else:
        label = "Unknown"

    return jsonify({"label": label})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
