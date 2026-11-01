#!/usr/bin/env bash
# Read-only inventory; absence of an installable component is reported, not fixed.
set -euo pipefail
failed=0
for tool in oc kubectl helm git make jq curl openssl python3 ssh lsof virtctl podman openshell; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'MISSING_TOOL %s\n' "$tool"
    failed=1
  fi
done
if (( failed )); then exit 1; fi
python3 -c 'import yaml' || { echo 'MISSING Python PyYAML'; exit 1; }
version=$(openshell --version | awk '{print $NF}')
if [[ "$version" != 0.0.103 ]]; then
  printf 'FAIL OpenShell client expected 0.0.103; observed %s\n' "$version"
  exit 1
fi
oc whoami
oc whoami --show-server
oc get clusterversion version -o jsonpath='{.status.desired.version}{"\n"}'
oc get nodes -o custom-columns=NAME:.metadata.name,CPU:.status.allocatable.cpu,MEMORY:.status.allocatable.memory,KERNEL:.status.nodeInfo.kernelVersion
oc get storageclass
for check in 'create subscriptions.operators.coreos.com' 'use scc/privileged'; do
  # Intentional word splitting: each check is a fixed two-word permission.
  result=$(oc auth can-i $check -n openshift-operators || true)
  printf 'PERMISSION %s: %s\n' "$check" "$result"
  [[ "$result" == yes ]] || failed=1
done
for crd in applications.argoproj.io sandboxes.agents.x-k8s.io virtualmachines.kubevirt.io datascienceclusters.datasciencecluster.opendatahub.io nemoguardrails.trustyai.opendatahub.io mlflows.mlflow.opendatahub.io; do
  if oc get crd "$crd" -o name >/dev/null 2>&1; then
    printf 'PRESENT %s\n' "$crd"
  else
    printf 'NEEDS_INSTALL %s\n' "$crd"
  fi
done
oc get subscriptions.operators.coreos.com -A -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,CHANNEL:.spec.channel,CSV:.status.installedCSV
printf '%s\n' 'NEXT: verify default storage, spare VM capacity, catalog channels, KVM/emulation, and live credentials using the runbook.'
exit "$failed"
