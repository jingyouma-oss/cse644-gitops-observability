# CSE644 Assignment 03 — GitOps and Application Observability

**Student:** Jingyou Ma  
**GitHub username:** `jingyouma-oss`  
**Kubernetes:** KinD v0.32.0 on Docker Desktop, Kubernetes v1.36.1  
**GitOps:** Argo CD v3.5.1  
**Application image:** `jingyouma/cse644-gitops-app:3.0.0`  
**Repository:** <https://github.com/jingyouma-oss/cse644-gitops-observability>

This repository extends the Python port-8888 application from Assignments 01 and 02. Argo CD treats `manifests/` on `main` as the authoritative desired state. Prometheus scrapes application-owned metrics every five seconds, and Grafana provisions a version-controlled dashboard without manual UI configuration.

## Architecture

```text
GitHub main/manifests
        │ desired state
        ▼
Argo CD ──automated sync, prune, self-heal──> namespace gitops-demo
                                                │
                    ┌───────────────────────────┼────────────────────┐
                    ▼                           ▼                    ▼
          gitops-app Service:8888       Prometheus:9090       Grafana:3000
                    │ 2 Pods                  │ scrape /metrics      │
                    └─────────────────────────┘                      │
                                                 Prometheus datasource
                                                            + provisioned dashboard
```

## Repository layout

- `app/`: original application source and Dockerfile.
- `manifests/`: Argo-managed application, Prometheus, Grafana, scrape configuration, provisioning and dashboard.
- `bootstrap/`: the Argo CD `Application` object that points to this repository.
- `scripts/`: repeatable traffic generation and cleanup.
- `evidence/`: focused proof aligned with every grading outcome.

## Prerequisites

- Docker Desktop with Linux containers
- Local KinD cluster and `kubectl`
- Git and GitHub CLI
- Argo CD installed in namespace `argocd`

## Initial deployment

Build and publish the fixed application version:

```powershell
docker build -t jingyouma/cse644-gitops-app:3.0.0 ./app
docker push jingyouma/cse644-gitops-app:3.0.0
kind load docker-image jingyouma/cse644-gitops-app:3.0.0 --name cse644
```

Install the pinned Argo CD release and create only the bootstrap `Application` object manually:

```powershell
kubectl create namespace argocd
kubectl apply --server-side --force-conflicts -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.5.1/manifests/install.yaml
kubectl wait -n argocd --for=condition=Available deployment --all --timeout=300s
kubectl apply -f ./bootstrap/argocd-application.yaml
```

After bootstrap, Argo CD—not direct `kubectl apply`—creates and maintains the assignment resources.

## Validation and local access

```powershell
kubectl -n argocd get application cse644-gitops-observability
kubectl -n gitops-demo get deployment,pod,service,configmap
kubectl -n gitops-demo port-forward service/gitops-app 18888:8888
kubectl -n gitops-demo port-forward service/prometheus 19090:9090
kubectl -n gitops-demo port-forward service/grafana 13000:3000
```

- Application: <http://localhost:18888/>
- Prometheus targets: <http://localhost:19090/targets>
- Grafana dashboard: <http://localhost:13000/d/cse644-gitops-observability>

## GitOps workflow, failure, and recovery

The actual revision sequence is retained in Git and explained by focused evidence:

1. **Initial desired state:** Argo creates the application and observability stack from `main/manifests`.
2. **Meaningful Git change:** `APP_MESSAGE` changes in Git; Argo reconciles it and the live response changes.
3. **Live-state drift:** a direct manual replica change makes the cluster differ from Git. `selfHeal: true` restores the Git-declared replica count.
4. **Controlled Git failure:** Git temporarily declares a nonexistent image tag, causing `ImagePullBackOff`. Argo and Kubernetes evidence identify the bad image.
5. **Git-based recovery:** the image tag is corrected in Git. Argo syncs the correction and restores Healthy/Synced state without an unmanaged repair.

## Observability approach

The application exposes Prometheus text metrics at `/metrics` without an external instrumentation dependency:

- `cse644_http_requests_total{path,status}` reveals traffic volume, endpoint mix and controlled 404 behavior.
- `rate(cse644_http_requests_total[1m])` reveals traffic intensity over time and increases during load generation.
- `cse644_inflight_requests` indicates concurrent work per scraped endpoint.
- `cse644_app_info{student,version}` identifies the workload and deployed version.
- Prometheus `up{job="cse644-gitops-app"}` proves scrape health.

Grafana is configured entirely from Git using provisioning ConfigMaps. Its dashboard includes request rate by path, total requests, target health, status-code activity and in-flight requests. Anonymous access is limited to Viewer for this disposable local-only environment; no administrator password is committed.

Generate visible activity:

```powershell
./scripts/generate-load.ps1 -Requests 300
```

## Technical decisions and limitations

- One small KinD node keeps the assignment practical for a local laptop.
- Prometheus uses two-hour ephemeral retention because long-term durability is outside this assignment.
- Static Service DNS is sufficient for this single application; production would normally use Kubernetes service discovery and stronger RBAC.
- Grafana is provisioned as code and intentionally local-only. Production requires authentication, TLS, persistent storage and secret-managed credentials.
- Argo CD automated sync, prune and self-heal make Git authoritative; direct live edits are intentionally overwritten.

## Cleanup and verification

```powershell
./scripts/cleanup.ps1
kubectl get namespace gitops-demo argocd
```

Successful cleanup reports both namespaces as not found. The KinD cluster may remain for other coursework; delete it separately with `kind delete cluster --name cse644` only if it is no longer needed.

## Security

This repository contains no GitHub tokens, kubeconfig files, private keys, real Secret values or Grafana administrator passwords. Do not add generated credentials or Argo CD initial admin secrets to evidence.

