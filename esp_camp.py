from flask import Flask, render_template, redirect, send_file, request
import requests
import io
import threading
import time

ESP32_IP = "http://10.135.220.220"
capturing = False
capture_thread = None

app = Flask(__name__)

# Background thread to capture images repeatedly
def continuous_capture():
    while capturing:
        try:
            requests.get(f"{ESP32_IP}/capture", timeout=3)
            print("Captured image")
        except:
            print("ESP32 not reachable during capture")
        time.sleep(1)  # 1 image per second

@app.route("/")
def index():
    return render_template("index.html", capturing=capturing)

@app.route("/start")
def start_capture():
    global capturing, capture_thread
    if not capturing:
        capturing = True
        capture_thread = threading.Thread(target=continuous_capture)
        capture_thread.start()
    return redirect("/")

@app.route("/stop")
def stop_capture():
    global capturing
    capturing = False
    return redirect("/")

@app.route("/image/<int:img_id>")
def get_image(img_id):
    try:
        r = requests.get(f"{ESP32_IP}/image?img={img_id}")
        if r.status_code == 200:
            return send_file(io.BytesIO(r.content), mimetype='image/jpeg')
        return "Image not found", 404
    except:
        return "ESP32 not reachable", 500

@app.route("/download_all")
def download_all():
    images = []
    for i in range(5):  # Adjust max number if needed
        try:
            r = requests.get(f"{ESP32_IP}/image?img={i}")
            if r.status_code == 200:
                with open(f"image_{i}.jpg", "wb") as f:
                    f.write(r.content)
                images.append(f"image_{i}.jpg")
        except:
            continue
    return f"Downloaded {len(images)} images"

@app.route("/delete_all")
def delete_all():
    for i in range(5):  # Adjust based on ESP32 logic
        try:
            requests.get(f"{ESP32_IP}/delete?img={i}")
        except:
            continue
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
