# Evidence Index

All evidence comes from the real local KinD deployment and is intentionally
focused. No credentials, tokens, kubeconfig, private keys, or administrator
passwords are stored here.

| File | Outcome proved |
|---|---|
| `01-environment-and-initial-sync.txt` | Working KinD cluster and initial Argo CD Synced/Healthy deployment |
| `02-git-change-and-self-heal.txt` | Meaningful Git change and reconciliation of live replica drift |
| `03-controlled-failure-and-diagnosis.txt` | Git-introduced invalid-image failure and Kubernetes diagnosis |
| `04-git-recovery.txt` | Correction through Git and restored Synced/Healthy state |
| `05-prometheus-and-grafana.txt` | Prometheus scrape health, activity-dependent metrics, Grafana health |
| `06-grafana-dashboard.png` | Dashboard showing request rate, totals, status activity, and target UP |
| `07-cleanup-and-final-validation.txt` | Cleanup verification followed by reproducible final redeployment |

The commit history provides the revision-level evidence for initial state,
change, controlled failure, recovery, and final documentation.
