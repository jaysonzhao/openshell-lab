# Red Hat AI Agent Security Workshop: verification steps

This checklist covers all eight modules in the workshop source at the pinned checkout. Run checks only after that module's deployment prerequisites are satisfied. A green apply/install command is not a pass by itself: verify the runtime behavior and its evidence.

## Current cluster status

- The current OpenShift context is the user-supplied `cluster-hrmkd` cluster. The login used `--insecure-skip-tls-verify`; confirm the target before running changes with `oc whoami --show-server`.
- Modules 1 and 2 are deployed and verified. Module 2's automated security script passed 14/14 checks.
- Modules 3–8 are not deployed yet. SAW/model provider credentials and an OIDC identity are prerequisites; Module 8 also needs a separate OpenAI-compatible model endpoint and key. Module 7 depends on the SAW/capstone services and seeded telemetry.
- Never copy bearer/API keys into this checklist or evidence notes. Do not inspect Secret `.data` values.

## 0. Confirm the target and tool context

```bash
oc whoami
oc whoami --show-server
oc get nodes
openshell --version
helm version --short
```

Confirm the server is `https://api.cluster-hrmkd.dyn.redhatworkshops.io:6443`, the expected account is logged in, and workers are Ready before doing cluster-scoped checks.

OpenShell commands assume the same local CLI profile and gateway port-forward used during deployment. In a new terminal, reuse that profile; a fresh profile will not know `local-gateway`.

Set the names supplied by the SAW deployment before Modules 3–7:

```bash
export SAW_NS='<SAW namespace>'
export SAW_GATEWAY='<SAW gateway name>'
export SAW_WORKSPACE='<workspace name>'
export SAW_SANDBOX='<OpenClaw sandbox name>'
export GITOPS_NS=openshift-gitops
```

## Module 1 — Basic OpenShell

1. Check the gateway, storage, service, and Sandbox API:

   ```bash
   oc get crd sandboxes.agents.x-k8s.io
   oc -n openshell get statefulset,pods,svc,pvc
   oc -n openshell rollout status statefulset/openshell
   ```

   Pass when the gateway pod is Ready, its PVC is Bound, the Service exists, and the CRD is present.

2. Check the client-to-gateway connection and both views of the test sandbox:

   ```bash
   openshell --gateway local-gateway status
   openshell --gateway local-gateway sandbox list
   oc -n openshell get sandboxes,pods
   ```

   Pass when the CLI reports Connected, `policy-lab` is Ready, and its pod is Running.

3. If repeating the tunnel exercise, stop the port-forward and confirm `openshell status` fails; restart it and confirm status recovers. Keep the gateway private; do not create a Route for the unauthenticated raw gateway.

4. Run the bundled infrastructure verifier:

   ```bash
   make -C /Users/haozhao/Documents/ChatGPT/agentworkspace/rhai-agent-security/automation \
     openshell-verify RAW_GATEWAY_NAME=local-gateway
   ```

## Module 2 — Policy and runtime security

1. Review the effective policy before testing. The installed default policy includes provider presets, so record those rules and test a destination outside them:

   ```bash
   openshell --gateway local-gateway policy get openclaw-lab --full
   openshell --gateway local-gateway sandbox exec -n openclaw-lab -- \
     curl -sS -o /dev/null -w 'HTTP %{http_code}\n' --max-time 15 https://example.com
   openshell --gateway local-gateway logs openclaw-lab --since 2m
   ```

   Pass when the request is denied before an HTTP response and the gateway audit log identifies the destination, calling binary, and denial.

2. Check the read-only GitHub policy on `policy-lab`, then prove allowed and denied actions:

   ```bash
   openshell --gateway local-gateway policy get policy-lab --full
   openshell --gateway local-gateway sandbox exec -n policy-lab -- \
     curl -sS -o /dev/null -w 'GET HTTP %{http_code}\n' \
     https://api.github.com/repos/NVIDIA/OpenShell
   openshell --gateway local-gateway sandbox exec -n policy-lab -- \
     curl -sS -o /dev/null -w 'POST HTTP %{http_code}\n' -X POST \
     https://api.github.com/repos/octocat/hello-world/issues
   openshell --gateway local-gateway logs policy-lab --since 2m
   ```

   Pass when GET is allowed (normally HTTP 200; distinguish GitHub rate limiting from policy denial), POST is denied (HTTP 403), and the audit event records the L7 method decision. A Python request to the same host should be denied because the rule is bound to `/usr/bin/curl`.

3. For the live policy exercise, add a temporary rule for `http-echo`, verify POST succeeds, restore the quickstart policy, then verify the same POST is denied. Check the effective policy after each change and keep the sandbox identity unchanged.

4. For filesystem isolation, use a disposable sandbox with the hard Landlock policy. Verify a permitted `/tmp` write succeeds and a `/var/tmp` write fails with `Permission denied`; confirm the sandbox process is unprivileged and gateway startup logs report Landlock `HardRequirement` with rules applied. Do not treat SELinux context output as proof of Landlock.

5. Run the complete workshop assertion script:

   ```bash
   make -C /Users/haozhao/Documents/ChatGPT/agentworkspace/rhai-agent-security/automation \
     openshell-security-test SANDBOX_NAME=policy-lab
   ```

   Pass when it reports all expected checks passed with zero unexpected results. The deployed run passed 14/14.

## Module 3 — Install Secure Agent Workspace (SAW)

This module is not deployed yet. Before installation, confirm this is the intended dedicated workshop cluster, supply the required SAW provider credential and chosen OIDC subject, and complete the control-node preflight (including `virtctl` and the image-mirroring prerequisites). Do not proceed with default `alice` identity assumptions on a shared cluster.

After install, require all of these before moving on:

```bash
oc -n "$SAW_NS" wait --for=condition=complete \
  "job/${SAW_GATEWAY}-setup" --timeout=5400s
test "$(oc -n "$SAW_NS" get "vmi/$SAW_GATEWAY" -o jsonpath='{.status.phase}')" = Running
oc -n "$GITOPS_NS" get applications.argoproj.io
oc -n "$SAW_NS" get job,vm,vmi,pods
```

Pass when the setup Job is Complete, the VMI is Running, and the owning Argo CD applications are Synced and Healthy. If not, inspect the Job logs and Argo CD state before retrying.

## Module 4 — Validate and operate SAW

1. Authenticate to the SAW gateway through the workshop OIDC login, then verify identity and membership in the assigned workspace.
2. Check reconciliation and runtime state:

   ```bash
   oc -n "$SAW_NS" get job,vm,vmi,route
   oc -n "$GITOPS_NS" get applications.argoproj.io
   openshell gateway select "$SAW_GATEWAY"
   openshell --gateway "$SAW_GATEWAY" status
   openshell --gateway "$SAW_GATEWAY" sandbox list --workspace "$SAW_WORKSPACE"
   openshell --gateway "$SAW_GATEWAY" sandbox get "$SAW_SANDBOX" --workspace "$SAW_WORKSPACE"
   ```

   Pass when the gateway is Connected, the setup Job is Complete, the VMI is Running, and expected workspace sandboxes are Ready.

3. Launch `openclaw tui` with the workshop Make target and verify the agent answers through the SAW sandbox. Confirm the gateway-reported version and effective sandbox policy. Do not infer success from a running VM alone.

## Module 5 — Agent capabilities and governance

1. Verify the agent's permitted `/sandbox` action from outside the agent and inspect the effective policy:

   ```bash
   openshell --gateway "$SAW_GATEWAY" sandbox exec -n "$SAW_SANDBOX" \
     --workspace "$SAW_WORKSPACE" -- cat /sandbox/haiku.txt
   openshell --gateway "$SAW_GATEWAY" policy get "$SAW_SANDBOX" \
     --workspace "$SAW_WORKSPACE" --full
   ```

2. Run the denied filesystem probe and inspect recent gateway events:

   ```bash
   openshell --gateway "$SAW_GATEWAY" sandbox exec -n "$SAW_SANDBOX" \
     --workspace "$SAW_WORKSPACE" -- touch /var/tmp/saw-boundary-probe
   openshell --gateway "$SAW_GATEWAY" logs "$SAW_SANDBOX" \
     --workspace "$SAW_WORKSPACE" --since 2m
   ```

   Pass when the write fails; the location is world-writable, so the failure demonstrates the Landlock boundary. The denial is kernel-silent, so use the failed write itself as evidence.

3. List governance provider profiles. Attempt to create an unvended `custom` provider; pass when the interceptor rejects it. Do not persist a profile change to the read-only workshop checkout.
4. Open the dashboard Route and verify Control UI chat plus tool activity. Confirm the sandbox gateway daemon listens on loopback port 18789 and device approval works through the documented flow. Keep token-bearing dashboard URLs private.

## Module 6 — Secure Agent Workspace boundaries

1. Inspect infrastructure and GitOps ownership:

   ```bash
   oc -n "$SAW_NS" get vm,vmi,dv,job,pods,route
   oc -n "$GITOPS_NS" get applications.argoproj.io
   oc -n "$SAW_NS" get route \
     -o custom-columns=NAME:.metadata.name,HOST:.spec.host,TLS:.spec.tls.termination
   ```

2. Inspect identity and secret-delivery object names without printing secret values:

   ```bash
   openshell --gateway "$SAW_GATEWAY" status
   openshell --gateway "$SAW_GATEWAY" sandbox list --workspace "$SAW_WORKSPACE"
   oc -n "$SAW_NS" get externalsecret,secretstore 2>/dev/null || true
   oc -n "$SAW_NS" get secret -o name
   ```

3. Compare the VM/Sandbox policies with the reference architecture: VM boundary, OIDC identity, Vault/External Secrets delivery, gateway governance, and GitOps ownership. Pass only when evidence comes from cluster resources and effective runtime policy.

## Module 7 — SRE capstone

This requires the SAW capstone, telemetry proxy, seeded incident, and MLflow services; it is not deployed yet.

1. Check all three Ready sandboxes and their policies:

   ```bash
   openshell --gateway "$SAW_GATEWAY" sandbox list
   openshell --gateway "$SAW_GATEWAY" policy get metrics --full
   openshell --gateway "$SAW_GATEWAY" policy get traces --full
   openshell --gateway "$SAW_GATEWAY" policy get analyst --full
   ```

   `metrics` should reach only Prometheus, `traces` only MLflow, and `analyst` neither telemetry endpoint.

2. Probe declared and undeclared telemetry paths from each sandbox. For example, `metrics` should get an HTTP response from Prometheus and be denied before HTTP at the MLflow proxy. Repeat the inverse for `traces`; both paths should be denied for `analyst`. Any HTTP status proves the connection was allowed, including 401; a gateway denial before HTTP proves enforcement.
3. Ask the metrics agent for live `demo` namespace replica metrics. Search the `sre-copilot-fleet` MLflow experiment for incident `INC-4127`, then verify the planted traces and a newly ingested participant trace appear in MLflow itself.
4. Open the console with `oc -n "$SAW_NS" get route incident-console`, record the two-replica baseline, inject the outage, review the agents' recommendation, restore the service, and verify two ready replicas. Keep Kubernetes write access with the human; the agents recommend only.

## Module 8 — NeMo Guardrails model boundary

This module is not deployed yet. It needs a working OpenAI-compatible `/v1` endpoint, exact served model name, and its API key; no key is stored in this checklist.

1. Before installing, verify the endpoint's `/models` returns HTTP 200 with the supplied credential, and confirm the OpenShift AI TrustyAI component is Managed.
2. After install, verify the `NemoGuardrails` CR, config ConfigMap, credential Secret name, and Deployment rollout. Confirm the pod references the API-key environment variable without printing its value; confirm rendered config names the intended model.
3. Port-forward the service and check `/v1/health`. Send a benign prompt and confirm a non-empty model response.
4. Send dummy sensitive inputs (for example, a dummy SSN, credit-card pattern, `api_key`, or model-name leak). Pass when the response is a canned refusal and does not echo the sensitive string; HTTP 200 can be expected for a refusal. Check pod logs for the regex and sensitive-data rail actions.
5. Change one rail in the owned ConfigMap/CR path, wait for operator reconciliation and rollout, and repeat the probe to prove the live change took effect. Do not edit the operator-owned Deployment directly.

## Evidence rule for every module

Record timestamp, cluster/namespace, command or UI action, expected result, observed result, and evidence location. Capture both a positive and a negative control when the module claims enforcement. Redact tokens, API keys, and Secret values. Mark a module **PASS** only when its runtime behavior and required audit/downstream evidence are present; otherwise mark it **BLOCKED** or **FAIL** with the missing prerequisite or evidence.

For the source's complete exercise narrative, use the module pages in `rhai-agent-security/content/modules/ROOT/pages/` and the matching automation under `rhai-agent-security/automation/`.
