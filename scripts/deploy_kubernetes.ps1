docker build -f api\Dockerfile -t task15-cifar-api:v1 .
docker build -f ui\Dockerfile -t task15-cifar-ui:v1 .

minikube start --driver=docker --cpus=4 --memory=6144
minikube addons enable metrics-server
minikube image load task15-cifar-api:v1
minikube image load task15-cifar-ui:v1

kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\api-deployment.yaml
kubectl apply -f k8s\api-service.yaml
kubectl apply -f k8s\ui-deployment.yaml
kubectl apply -f k8s\ui-service.yaml
kubectl apply -f k8s\hpa.yaml

kubectl get all -n task15
kubectl get hpa -n task15
kubectl top pods -n task15
