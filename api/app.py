from io import BytesIO
from pathlib import Path
import os
import time

import torch
from PIL import Image
from flask import Flask, jsonify, request
from torchvision import transforms

from model_def import CIFAR10CNN

CLASSES = (
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
)

MODEL_PATH = Path(os.getenv("MODEL_PATH", "/app/model/cifar10_cnn.pth"))
APP_VERSION = os.getenv("APP_VERSION", "v1")
DEVICE = torch.device("cpu")

model = CIFAR10CNN().to(DEVICE)
checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(checkpoint["state_dict"])
model.eval()

preprocess = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2470, 0.2435, 0.2616))
])

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
REQUEST_COUNT = 0
TOTAL_PREDICTION_SECONDS = 0.0

@app.get("/")
def root():
    return jsonify({
        "application": "Task 15 CIFAR-10 Production API",
        "version": APP_VERSION,
        "endpoints": ["/health", "/metrics", "/predict"]
    })

@app.get("/health")
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "model_loaded": True,
        "version": APP_VERSION
    })

@app.get("/metrics")
def metrics():
    avg = TOTAL_PREDICTION_SECONDS / REQUEST_COUNT if REQUEST_COUNT else 0.0
    return jsonify({
        "success": True,
        "requests_total": REQUEST_COUNT,
        "average_prediction_seconds": round(avg, 6),
        "version": APP_VERSION
    })

@app.post("/predict")
def predict():
    global REQUEST_COUNT, TOTAL_PREDICTION_SECONDS

    if "file" not in request.files:
        return jsonify({"success": False, "error": "Use form field 'file'."}), 400

    started = time.perf_counter()
    try:
        image = Image.open(BytesIO(request.files["file"].read())).convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1)[0]
            idx = int(probs.argmax().item())
            confidence = float(probs[idx].item())

        elapsed = time.perf_counter() - started
        REQUEST_COUNT += 1
        TOTAL_PREDICTION_SECONDS += elapsed

        return jsonify({
            "success": True,
            "version": APP_VERSION,
            "predicted_class": CLASSES[idx],
            "confidence_percent": round(confidence * 100, 2),
            "latency_ms": round(elapsed * 1000, 2),
            "probabilities": {
                CLASSES[i]: float(probs[i].item()) for i in range(10)
            }
        })
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
