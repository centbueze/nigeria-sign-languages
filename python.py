from flask import Flask, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO("best.pt")  # your trained model

@app.route('/upload', methods=['POST'])
def upload():
    # Decode image from ESP32
    img = cv2.imdecode(np.frombuffer(request.data, np.uint8), cv2.IMREAD_COLOR)

    # Run YOLO inference
    results = model.predict(img, imgsz=320)

    if len(results[0].boxes) > 0:
        top_class = int(results[0].boxes.cls[0])
        return jsonify({
            "sign": model.names[top_class],
            "confidence": float(results[0].boxes.conf[0])
        })
    return jsonify({"status": "no_sign_detected"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
