# Task 15 Recorded Results

## Model training

The recorded five-epoch run achieved:

| Epoch | Test Accuracy |
|---|---:|
| 1 | 56.97% |
| 2 | 66.64% |
| 3 | 70.20% |
| 4 | 74.60% |
| 5 | 75.40% |

The checkpoint was saved as model/cifar10_cnn.pth.

## Local application validation

A Docker/Streamlit validation run successfully exercised the inference path. One uploaded abstract multi-colour image was classified as:

- Predicted class: bird
- Confidence: 48.68%
- Model version: v1

Because the image was not a controlled CIFAR-10 benchmark sample, this prediction is demonstration evidence and not a model-quality benchmark.

## Kubernetes status

The final captured Kubernetes troubleshooting state showed:

- API Pods: ErrImageNeverPull
- UI Pods: ErrImageNeverPull
- Cause: local images task15-cifar-api:v1 and task15-cifar-ui:v1 were not present inside Minikube while imagePullPolicy: Never was configured.
- HPA metrics were also unavailable until Metrics Server is healthy.

To continue:

    minikube image load task15-cifar-api:v1
    minikube image load task15-cifar-ui:v1
    kubectl rollout restart deployment/task15-api -n task15
    kubectl rollout restart deployment/task15-ui -n task15
    kubectl get pods -n task15 -w
