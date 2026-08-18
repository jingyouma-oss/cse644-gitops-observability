param([int]$Requests = 300)
$ErrorActionPreference = 'Stop'
$Pod = kubectl -n gitops-demo get pod -l app=gitops-app -o jsonpath='{.items[0].metadata.name}'
1..$Requests | ForEach-Object {
  kubectl -n gitops-demo exec $Pod -- wget -qO- http://gitops-app:8888/ | Out-Null
  if ($_ % 20 -eq 0) {
    kubectl -n gitops-demo exec $Pod -- wget -qO- http://gitops-app:8888/not-found | Out-Null
  }
}
Write-Host "Generated $Requests successful requests plus controlled 404 activity."

