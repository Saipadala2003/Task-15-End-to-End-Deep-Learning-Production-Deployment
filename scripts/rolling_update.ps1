docker build -f api\Dockerfile -t task15-cifar-api:v2 .
minikube image load task15-cifar-api:v2
kubectl set image deployment/task15-api api=task15-cifar-api:v2 -n task15
kubectl set env deployment/task15-api APP_VERSION=v2 -n task15
kubectl rollout status deployment/task15-api -n task15
kubectl get rs -n task15
kubectl rollout history deployment/task15-api -n task15
