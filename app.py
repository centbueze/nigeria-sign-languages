from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import requests
from ultralytics import YOLO
import threading
import time

app = Flask(__name__)

# Load your trained model
model = YOLO("best.pt")

# ESP32 details (this is from your Serial Monitor)
ESP32_IP = "10.88.255.220"   # ← Your ESP32’s IP
CAPTURE_URL = f"http://{ESP32_IP}/capture"

# Global variables to store latest prediction
latest_prediction = {"sign": "None", "confidence": 0.0, "timestamp": 0}

def predict_sign():
    """Continuously get images from ESP32 and run prediction"""
    global latest_prediction
    
    while True:
        try:
            # Get image from ESP32
            response = requests.get(CAPTURE_URL, timeout=3)
            if response.status_code == 200:
                # Convert to numpy array
                img_array = np.frombuffer(response.content, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Run YOLO prediction
                    results = model.predict(frame, imgsz=320, conf=0.25, verbose=False)
                    
                    if results and len(results) > 0:
                        # Get top prediction
                        boxes = results[0].boxes
                        if boxes is not None and len(boxes) > 0:
                            # Get the detection with highest confidence
                            confidences = boxes.conf.cpu().numpy()
                            class_ids = boxes.cls.cpu().numpy()
                            
                            max_idx = np.argmax(confidences)
                            sign = results[0].names[int(class_ids[max_idx])]
                            confidence = float(confidences[max_idx])
                            
                            # Update global prediction
                            latest_prediction = {
                                "sign": sign,
                                "confidence": confidence,
                                "timestamp": time.time()
                            }
                            print(f"Predicted: {sign} ({confidence:.2f})")
            
            time.sleep(0.1)  # ~10 FPS
            
        except Exception as e:
            print(f"Prediction error: {e}")
            time.sleep(1)

@app.route('/')
def index():
    """Main page showing live results"""
    return render_template('index.html')

@app.route('/api/prediction')
def get_prediction():
    """API endpoint to get latest prediction"""
    return jsonify(latest_prediction)

@app.route('/video_feed')
def video_feed():
    """Video feed from ESP32 (optional)"""
    def generate():
        while True:
            try:
                response = requests.get(CAPTURE_URL, timeout=3)
                if response.status_code == 200:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + 
                           response.content + b'\r\n')
                time.sleep(0.1)
            except:
                time.sleep(1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Start prediction thread
    prediction_thread = threading.Thread(target=predict_sign, daemon=True)
    prediction_thread.start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)
