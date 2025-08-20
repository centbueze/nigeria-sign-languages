from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np

app = Flask(__name__)

model_path = r'C:/Users/user/Desktop/hand_gesture/output/nsl_yolo_train2/weights/best.pt'
model = YOLO(model_path)

@app.route('/detect', methods=['POST'])
def detect():
    try:
        image_data = request.data
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Failed to decode image"}), 400

        results = model(image)
        names = model.names
        boxes = results[0].boxes
        classes = boxes.cls.cpu().numpy().astype(int)

        label = names[classes[0]] if len(classes) > 0 else "Unknown"

        return jsonify({"label": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
