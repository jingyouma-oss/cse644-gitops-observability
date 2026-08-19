$ErrorActionPreference = 'Continue'
kubectl delete -f "$PSScriptRoot/../bootstrap/argocd-application.yaml" --ignore-not-found
kubectl delete namespace gitops-demo --ignore-not-found
kubectl delete namespace argocd --ignore-not-found
kubectl get namespace gitops-demo argocd
