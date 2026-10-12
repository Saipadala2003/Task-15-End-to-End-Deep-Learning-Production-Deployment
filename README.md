# Task 15: End-to-End Deep Learning Production Deployment

Production-style CIFAR-10 image classification using **PyTorch CNN + Flask REST API + Streamlit + Docker + Docker Compose + Kubernetes/Minikube**.

## Architecture

User -> Streamlit UI -> Flask REST API -> PyTorch CNN -> class + confidence

Operational layer:
- Docker containerization
- Docker Compose local validation
- Kubernetes Deployments and Services
- Readiness/liveness probes
- Resource requests and limits
- Replica scaling
- Horizontal Pod Autoscaler
- Metrics Server
- Rolling updates
- Health and lightweight application metrics

## Recorded validation

- PyTorch CNN training: 5 epochs
- Recorded final CIFAR-10 test accuracy: **75.40%**
- Local Streamlit inference example: **bird, 48.68% confidence**
- The example image was an abstract multi-colour image, so the prediction is demonstration evidence rather than a controlled CIFAR-10 benchmark.

## Repository structure

```text
.
├── train_model.py
├── model/
│   └── README.txt
├── api/
│   ├── app.py
│   ├── model_def.py
│   ├── requirements.txt
│   └── Dockerfile
├── ui/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── namespace.yaml
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── ui-deployment.yaml
│   ├── ui-service.yaml
│   ├── hpa.yaml
│   └── servicemonitor-note.yaml
├── scripts/
├── monitoring/
├── screenshots/
└── docker-compose.yml
```

## Quick start on Windows PowerShell

### 1. Create environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r api\requirements.txt
```

### 2. Train the model

```powershell
python train_model.py --epochs 5 --batch-size 128
```

This creates:

```text
model/cifar10_cnn.pth
```

The trained binary is intentionally not committed to source control. Generate it locally before building the API image.

### 3. Build Docker images

```powershell
docker build -f api\Dockerfile -t task15-cifar-api:v1 .
docker build -f ui\Dockerfile -t task15-cifar-ui:v1 .
```

### 4. Run with Docker Compose

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8501
```

### 5. Start Minikube

```powershell
minikube start --driver=docker --cpus=4 --memory=6144
minikube addons enable metrics-server
```

### 6. Load local images into Minikube

Because the manifests use `imagePullPolicy: Never`, the locally built images must be present inside Minikube:

```powershell
minikube image load task15-cifar-api:v1
minikube image load task15-cifar-ui:v1
minikube image ls | findstr task15
```

### 7. Deploy Kubernetes resources

```powershell
kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\api-deployment.yaml
kubectl apply -f k8s\api-service.yaml
kubectl apply -f k8s\ui-deployment.yaml
kubectl apply -f k8s\ui-service.yaml
kubectl apply -f k8s\hpa.yaml
```

### 8. Verify

```powershell
kubectl get all -n task15
kubectl get pods -n task15 -o wide
kubectl get hpa -n task15
kubectl top pods -n task15
```

### 9. Open Streamlit

```powershell
minikube service task15-ui -n task15
```

### 10. API health and metrics

```powershell
kubectl port-forward svc/task15-api 5000:5000 -n task15
```

In another PowerShell window:

```powershell
curl.exe http://127.0.0.1:5000/health
curl.exe http://127.0.0.1:5000/metrics
```

### 11. Rolling update

```powershell
docker build -f api\Dockerfile -t task15-cifar-api:v2 .
minikube image load task15-cifar-api:v2
kubectl set image deployment/task15-api api=task15-cifar-api:v2 -n task15
kubectl set env deployment/task15-api APP_VERSION=v2 -n task15
kubectl rollout status deployment/task15-api -n task15
kubectl get rs -n task15
kubectl rollout history deployment/task15-api -n task15
```

## Important troubleshooting

If a Pod reports:

```text
ErrImageNeverPull
Container image "...:v1" is not present with pull policy of Never
```

load the images again:

```powershell
minikube image load task15-cifar-api:v1
minikube image load task15-cifar-ui:v1
kubectl rollout restart deployment/task15-api -n task15
kubectl rollout restart deployment/task15-ui -n task15
```

If HPA reports that CPU metrics are unavailable, verify Metrics Server:

```powershell
minikube addons enable metrics-server
kubectl get pods -n kube-system | Select-String metrics
kubectl top nodes
```

## Final validation status

The source, local training, Docker/Compose configuration, Kubernetes manifests, monitoring commands and report evidence are included. The last captured Minikube troubleshooting state showed local images were not loaded into Minikube, causing `ErrImageNeverPull`. The repository therefore does not claim successful final Kubernetes runtime validation.

## Report

The Task 15 academic report is maintained separately as a PDF submission artifact.
