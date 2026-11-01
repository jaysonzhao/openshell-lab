---
name: deploy-rhai-agent-security
description: Deploy OpenClaw inside an OpenShell pod sandbox for Modules 1–2 without SAW, using the Red Hat agentic starter kit with image builds, endpoint-bound model credentials, external OpenShift Route through gateway service exposure, browser mTLS, certificate SANs, origins, WebSockets, pairing, coding demo and policy tests. Also install upstream SAW with KubeVirt/OIDC/credential proxy/GitOps or complete the pinned Red Hat AI security workshop Modules 1–8 with Landlock, SRE capstone and NeMo Guardrails. Use for pod-only OpenClaw, external browser access, SAW installation, 4.21 assessment, migration and scoped cleanup.
---

# Deploy Red Hat AI Agent Security

## Portable file and contents

This portable edition puts the updated **pod-only OpenClaw first modules and external Route** first, using the red-hat-data-services starter kit. It also retains the separate upstream SAW and older full-workshop tracks. Choose the pod-only section for OpenClaw inside an OpenShell-managed pod without SAW, KubeVirt or an external SAN dependency. A working PVC StorageClass is still required. The external browser path uses an exact-host passthrough OpenShift Route through OpenShell service exposure and requires a browser client certificate (mTLS). OpenClaw remains on loopback inside the sandbox.

The pod path uses OpenShell 0.1.2 with an isolated client configuration, Node.js 24.21.0 and OpenClaw 2026.9.8. The source reports testing on OpenShift 4.22; qualify 4.21 independently. SAW's separate upstream minimum remains 4.22+. Offline renderer, CLI grammar and Helm checks do not establish a live cluster/model deployment.

Extract the eleven embedded runtime files into a new directory before following commands that refer to `SKILL_DIR`. The pod and external-Route renderers and gateway/echo assets are included, together with the older workshop's helper scripts and demo app. Substitute your actual paths, then use the extracted destination as `SKILL_DIR`. Do not run the old workshop preflight for pod-only work.

```bash
python3 - /path/to/SKILL.md /path/to/rhai-agent-security-skill <<'PYEXTRACT'
from pathlib import Path, PurePosixPath
import re, sys
src, root = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding='utf-8')
root.mkdir(parents=True, exist_ok=True)
root = root.resolve()
pattern = r'<!-- BEGIN FILE: ([^\n]+) -->\n````[^\n]*\n(.*?)\n````\n<!-- END FILE -->'
files = re.findall(pattern, text, re.S)
if len(files) != 11 or len({p for p, _ in files}) != 11:
    raise SystemExit('Expected eleven distinct embedded runtime files')
pending = [(root / 'SKILL.md', text)]
for relative, content in files:
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0] not in ('scripts', 'assets'):
        raise SystemExit('Invalid embedded path')
    pending.append((root.joinpath(*rel.parts), content))
for target, content in pending:
    if target.is_symlink() or root not in target.resolve().parents:
        raise SystemExit('Destination escapes root or is a symlink')
    if target.exists() and target.read_text(encoding='utf-8') != content:
        raise SystemExit('Refusing to overwrite different content: ' + str(target))
for target, content in pending:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    if target.parent.name == 'scripts':
        target.chmod(0o755)
print('Ready:', root)
PYEXTRACT
export SKILL_DIR=/path/to/rhai-agent-security-skill
```

- [Track selection and core workflow](#core-workflow)
- [Pod-only OpenClaw](#pod-only-openclaw)
- [External OpenClaw Route](#external-openclaw-route)
- [Upstream SAW installation](#upstream-saw-installation)
- [Source map](#source-map)
- [Workshop platform installation](#workshop-platform-installation)
- [Workshop modules](#workshop-modules)
- [Guardrails and final demo](#guardrails-and-final-demo)
- [Embedded files](#embedded-files)

## Core workflow

Deploy OpenClaw in an OpenShell pod sandbox, install upstream SAW, or build the complete workshop demonstration of runtime containment, workspace governance, SRE investigation and model-boundary rails. Retain the working demo for handover. Treat this as an executable workflow, not a source summary.

### Select the installation track first

- **First modules / OpenClaw without SAW:** Follow [openclaw-pod.md](#pod-only-openclaw), based on the starter kit at `e3b20b1adadf02542dd2656fd0511c63c57991aa` (audited 2026-11-01). Run OpenClaw inside a pod sandbox managed by an OpenShell 0.1.2 gateway, complete the browser/coding demo and Module 2 controls, and stop at the requested scope. For the requested external URL, also follow [openclaw-route.md](#external-openclaw-route): publish one certificate-gated Route through an OpenShell service exposure and verify a remote browser. Reuse a matching gateway or create a separate one. Do not install SAW, KubeVirt, OIDC/Keycloak or Vault as dependencies. Preserve existing 0.0.103 gateways and their Copilot sandboxes.
- **SAW-only installation or update:** Use [saw-upstream.md](#upstream-saw-installation), based on `validatedpatterns-sandbox/secure-agent-workspace` at `533be02ec02a69bd1bf9b20274bf9ce8bbef6668` (audited 2026-10-29). Follow its GitOps or smaller manual path, `saw-*` targets, per-user `saw-<name>` namespaces, credential proxy and OpenShell `0.1.2` client. Deliver its model-backed coding demo and acceptance ledger; the remaining workshop sections below are not required.
- **Complete workshop or Modules 1–8:** Follow the pinned workshop track below and its SAW fork. Keep client `0.0.103`, guest `0.0.103-rhaiv.0` and the original module exercises together. Do not substitute the upstream BOM into the capstone without a separately tested migration.

Default a request for the first modules or OpenClaw on the pod gateway without SAW to the pod-only track. Interpret "without SAN" in this task context as excluding the SAW/VM stack; introduce no external SAN dependency, while retaining required working PVC storage. Default "SAW install" to the upstream SAW track. That SAW upstream minimum remains OpenShift **4.22+**; assess 4.21 read-only and label it `COMPATIBILITY_NOT_VERIFIED` until an explicitly requested lab adaptation passes validation. Do not apply that SAW minimum to the separate pod path as a blanket requirement. Preserve existing gateways; use distinct client directories and gateway registrations.

### Load resources

- Read [source-map.md](#source-map) for audited revisions, all published pages, and dependency ownership.
- Read [openclaw-pod.md](#pod-only-openclaw) for the pod-only Modules 1–2 path and use `scripts/render_openclaw_pod.py` to prepare its nonsecret config and policies.
- Read [openclaw-route.md](#external-openclaw-route) before gateway installation when external browser access is requested; use `scripts/render_openclaw_route.py` for the UI Route, certificate values and exact origin patch. Keep OpenClaw on loopback and route through the gateway.
- Read [saw-upstream.md](#upstream-saw-installation) for the current upstream SAW-only track, including prerequisites, two deployment paths, usage and acceptance.
- Read [platform-install.md](#workshop-platform-installation) for the pinned workshop cluster baseline and SAW fork.
- Read [module-runbook.md](#workshop-modules) while executing Modules 1–7; its exercise matrix is the completion checklist.
- Read [guardrails-demo.md](#guardrails-and-final-demo) for every Module 8 exercise and the additional browser demo.
- Use `scripts/preflight.sh` only for the pinned full-workshop inventory; it requires that track's client and VM tools. Use the pod runbook's own checks for pod-only work, and `scripts/probe_guardrails.py` for real guardrails API checks.
- Copy `assets/demo-app/` to the deployment working directory before editing or building it. Keep skill source separate from live application state.

### Establish workshop inputs

For the complete workshop track, default to one dedicated cluster, its pinned SAW installation, Modules 1–8 in order, remote main-model inference, remote Llama Guard for moderation, and a locally forwarded final browser app. Reuse preinstalled components after validating their required state. For SAW-only inputs and capacity, use the upstream runbook instead.

Use an authenticated `oc` session. Obtain only missing inputs when execution needs them:

| Input | Requirement |
| --- | --- |
| Cluster | Record `oc whoami --show-server`; full installation needs cluster-admin |
| Platform | Published baseline: multinode OpenShift 4.22; audited RHOAI subscription channel `eus-3.5` |
| Virtualization | KVM preferred; software emulation needs at least 16 CPUs / 32 GiB and supported storage |
| SAW provider | Default BOM uses NVIDIA `build` provider, model `nvidia/nemotron-3-super-120b-a12b`; deliver its key through Vault |
| Guardrails main model | OpenAI-compatible `LLM_BASE_URL` ending `/v1`, exact `MODEL_NAME`, separate API key |
| Moderation | Remote Llama Guard endpoint, model ID and key; GPU detector is an alternative |
| Access | OIDC identity, workspace membership, generated SAW SSH key, browser/device-code login |

For another OpenShift release, inspect operator channels, CRD schemas, virtualization support, and capacity; record fork changes before installation. Do not assume an older cluster supports the full stack. Remote models remove local inference GPU needs, not VM, operator, MLflow, or storage needs.

Never invent login, keys, OIDC subjects, endpoints, or deployment success. If access is missing, finish independent preparation and report the precise missing inputs. Mark deployment `BLOCKED`.

### Pin workshop repositories

Use the audited pair by default. Inspect changes before choosing newer revisions and update the source record when upgrading.

```bash
git clone https://github.com/taylorjordanNC/rhai-agent-security.git rhai-agent-security
git -C rhai-agent-security checkout f020994f47caa730ce6b33062dd31e70c72b3010
git clone --branch saw-emulation-fixes https://github.com/taylorjordanNC/secure-agent-workspace.git secure-agent-workspace
git -C secure-agent-workspace checkout 2a4b780102751d6034c267a0ad01f0134ba4a8d5
export WORKSHOP_DIR="$(cd rhai-agent-security && pwd)"
export SAW_DIR="$(cd secure-agent-workspace && pwd)"
```

Use new directories or inspect existing edits; never reset away user work. Detached HEAD is intentional. For changes, create a writable branch/fork and point each Argo source at its committed revision. Local pins do not pin Argo: the workshop child defaults to `main`, and SAW applications carry their own repo/revision settings. Audit both trees before claiming reproducibility. Keep charts and scripts in their owning repositories.

```bash
cd "$WORKSHOP_DIR"
OPENSHELL_VERSION=0.0.103 OPENSHELL_INSTALL_DIR="$HOME/openshell-cli" \
  ./automation/bootstrap/install-openshell-cli.sh
export PATH="$HOME/openshell-cli:$PATH"
make -C automation prerequisites
bash /absolute/path/to/this-skill/scripts/preflight.sh
```

Keep the control-node CLI at `0.0.103`. Expect raw gateway `0.0.103` and SAW guest `0.0.103-rhaiv.0`. The guest packaging suffix is expected.

### Execute workshop phases

These are the complete **older pinned workshop** phases. For the requested updated first modules, execute the pod-only runbook instead; do not continue into SAW modules or use the old version-only OpenClaw check as completion of the new model-backed demo.

Create a private evidence directory (`umask 077`) and a ledger: `module`, `exercise`, `status`, `observed`, `evidence`, `next action`. Use `PASS`, `FAIL`, `BLOCKED`, or `NOT_REQUESTED_OPTIONAL`. Capture revisions, resolvable image digests, timestamps, and observed versions. Redact tokens, Secret data, model keys, and token-bearing URLs.

1. **Foundation.** Verify default storage, permissions, catalog channels, KVM/emulation capacity, tools, GitOps controller, and SAW provider contract. Follow platform-install for fresh-cluster RHOAI/MLflow setup; do not assume facilitator provisioning.
2. **Module 1.** Install raw OpenShell; verify gateway/PVC/CRD; create `policy-lab`; intentionally stop/restore the owned tunnel; deploy pinned `openclaw-lab`, inspect its version. Preserve both for the demo.
3. **Module 2.** Execute all six exercises and the security test: default deny, read-only allow, binary denial, L7 denial, live endpoint allow/restore/deny, mandatory Landlock controls, and cluster/RPC admin view. Restore canonical policy.
4. **Module 3.** Follow canonical SAW partials: tools, cluster checks, keys, Vault-backed inference secret, mirroring, Validated Pattern, emulation if needed, setup Job/VM readiness. Record a validated facilitator installation as adopted.
5. **Module 4.** Configure OIDC and actual-subject workspace membership; validate both workspaces and guest version; diagnose reconciliation; run managed NemoClaw/OpenClaw; independently verify an agent-created file.
6. **Module 5.** Verify permitted/denied filesystem actions; list governance profiles and prove policy-specific provider rejection; validate browser origin, daemon, and pairing.
7. **Module 6.** Trace VM/Job/Argo ownership, TLS/OIDC/workspace scope, Vault→ExternalSecret→Secret→Job references, and interceptor bindings. Inspect Secret names/references only.
8. **Module 7.** Install capstone GitOps/RHOAI/MLflow dependencies; stage scoped credentials; verify signed fleet policies and all paired probes; query metrics, search/ingest traces; complete the human-driven incident loop and restore two replicas.
9. **Module 8.** Complete seven required exercises: foundation, managed deployment, config inspection, chat tests, isolated checks, SDK/streaming, and rule add/verify/restore. Execute remote moderation when its endpoint is available. Track GPU detector serving and integration separately if selected.
10. **Final app.** Deploy the bundled browser client in the guardrails namespace; configure its server with the actual guardrails service; test real allowed chat and structured rail attribution; conduct the demo below. Leave supporting services running.

The parked Security CTF is not a published ninth module; offer its five challenges as an optional assessment. Remote Llama Guard and GPU content safety are alternative extensions. List unselected alternatives without implying they ran.

### Preserve workshop evidence quality

- Pass `--gateway local-gateway` for raw commands. Use `--gateway openshell-saw --workspace cuda-dev` for the managed development sandbox. Discover fleet scope; the audited capstone uses `default`.
- Keep raw HTTP gateway internal with a loopback tunnel; it has no authentication. Do not create its Route.
- The old 0.0.103 raw installer grants privileged SCC as its evaluation dependency. Keep this claim limited to that older track. The updated 0.1.2 pod track uses the capability-free Kubernetes driver and can run a model-backed OpenClaw agent without SAW after live qualification. Do not run standalone `nemoclaw onboard` as a substitute for either installation path.
- Require matching destination/method/binary events for network-denial claims. HTTP 401/403 may mean an allowed connection rejected upstream.
- Verify Landlock with `hard_requirement` startup, allowed/denied path controls, and permission/SELinux checks. Kernel version alone is insufficient; Landlock filesystem denials need not emit runtime events.
- Verify agent actions outside chat. Report only intercepted governance RPCs. One owner's VM is not proof of automated multi-user isolation.
- Inspect actual token privileges. The upstream staging helper copies a supplied OCP token into sandboxes; never use cluster-admin or call it read-only solely because egress is limited.
- Expect guardrails refusals to use HTTP 200. Inspect `/v1/checks`, contents, and correlated rail evidence. A reply omitting PII does not prove absence of a main-model call.
- Verify no-main-model-call claims with request correlation and upstream audit/counters. Otherwise mark that property `NOT VERIFIED` separately from rail enforcement.
- Describe runtime and model-boundary demos as separately validated paths. The bundled chat client executes no tools. Claim SAW→NeMo integration only after explicitly rewiring its gateway provider and testing the full path.

### Demonstrate the workshop and hand over

1. Show raw operator view: allowed read, method/binary denial, temporary endpoint allow and deny again after restore.
2. Show SAW VM/authenticated workspace; have OpenClaw create a file and inspect it through CLI; show unapproved-provider rejection.
3. Show incident console with two shop replicas; inject the lab outage, investigate with metrics/traces, synthesize findings with analyst; have the human confirm recovery. Finish with two ready replicas.
4. Show browser demo: benign chat, synthetic PII check with exact backend rail, codename rule before/during/after its change.
5. Demonstrate moderation positive/negative controls when configured. Distinguish rail refusal, upstream error, and output filtering.

Deliver running app URL, OpenClaw/incident access instructions, source changes/revisions, module ledger, evidence paths, tests, gaps, restart steps, and scoped cleanup. Supply plain dashboard URLs and secure token-entry instructions; omit token fragments.

Require every mandatory exercise, incident recovery, and live-model app check before declaring complete. Distinguish offline/mock validation from cluster/model validation. Keep optional dependency gaps visible.

### Cleanup

For the pod-only first modules, follow its scoped cleanup: export sandbox state, stop owned forwards and remove only added lab resources. Preserve the existing raw gateway, Copilot add-on and shared Agent Sandbox controller/CRDs.

For exposure-only removal, delete only the owned UI Route and named OpenShell service exposure; retain the sandbox, TLS Secrets, control Route and PVCs.

For the upstream SAW-only track, follow its runbook's per-user ownership and `pruneOnRemove` workflow. Its full Pattern uninstall includes platform-level cleanup; do not use it as a single-user removal command.

Retain the final demo by default. Stop only owned tunnels after checking PID/command. On explicit teardown, remove demo resources and sandboxes through their owners, then self-owned capstone/SAW resources. Read upstream cleanup before `./pattern.sh make uninstall`: it may affect virtualization and unrelated VMs. Never delete shared operators, CRDs, namespaces, PVCs, or virtualization resources as routine participant cleanup; do not force finalizers.

## Pod-only OpenClaw

### Contents

1. Scope and source versions
2. Reuse or install the pod gateway
3. Render configuration and build the image
4. Bind model credentials and start OpenClaw
5. Use the UI and complete the coding demo
6. Complete Module 2 policy exercises
7. Diagnose, hand over and clean up

For the requested **external browser Route**, read [openclaw-route.md](#external-openclaw-route) before installing the gateway, include its service-domain certificate values, and require its remote-browser acceptance checks. A working local forward or an OpenShell control Route alone does not complete external OpenClaw access.

### 1. Scope and source versions

Use this path for OpenClaw with OpenShell in the first modules **without SAW**. Run the OpenClaw process itself inside the OpenShell-managed workload pod; its supervisor is a separate pod. Do not deploy SAW, KubeVirt, an HCO, Keycloak, Vault, ESO, the SAW Pattern, or a nested Docker daemon for these modules. An external SAN is not a dependency introduced by this skill; normal persistent storage is still required. Prefer a working block-backed StorageClass for SQLite state; the starter kit excludes NFS for its SQLite deployment.

Use the OpenShell section of [the starter kit](https://github.com/red-hat-data-services/agentic-starter-kits/tree/e3b20b1adadf02542dd2656fd0511c63c57991aa/agents/openclaw/deployment), audited 2026-11-01 at `e3b20b1adadf02542dd2656fd0511c63c57991aa`. Read `agents/openclaw/deployment/README.md`, `Containerfile.openshell`, `docs/raw-deployment.md`, `docs/model-compatibility.md`, and `sandboxes/base/{Containerfile,policy.yaml}` from that revision. The plain Kustomize Deployment is a different execution path; do not apply `agents/openclaw/deployment/manifests` as the sandbox deployment.

| Component | Selected version or boundary |
| --- | --- |
| OpenShell gateway, chart and client | `0.1.2`; CLI/chart source tag points to `6648bd0c290efbc41ba131ee9831ee45cd431f94` |
| OpenClaw | `2026.9.8`, pinned by the starter Containerfile |
| Node.js | Official checksum-verified `24.21.0`; do not replace with UBI's SQLite-linked Node package |
| Base image | Starter's `quay.io/hmoghani/openshell-base` is a development image; resolve a real digest or build the checked-out base, and record it |
| OpenShift | Starter OpenShell path reports tests on 4.22; qualify 4.21 independently. The plain manifest's 4.17+ prerequisite is not evidence that this OpenShell integration works on every such release. |
| Model | Exact `/v1/models` ID and an actual tool-calling endpoint. Remote inference removes any local inference GPU requirement. |

Keep the older complete-workshop `0.0.103` track separate. Do **not** run its gateway installer, privilege grant, setup-Job wait, security-test script or SAW preflight here. Preserve an existing `local-gateway`, its Copilot sandbox and all unrelated workloads. An existing `0.0.103` gateway is not silently upgraded: retain it and install a distinct `0.1.2` gateway for this source-aligned path, or stop at prepared inputs until an upgrade is explicitly requested. Source instructions to remove old sandboxes before a version upgrade are not authorization to delete user work.

Use a Linux control host for these commands. Establish an authenticated intended `oc` context, Helm 3, Git, Make, jq, curl, OpenSSL, Python/PyYAML, OpenSSH, Podman, Skopeo and OpenShell **0.1.2**. Use a separate CLI directory and client configuration root so the old gateway keeps its matching client and active selection. On an Apple Silicon image-build host choose the target worker architecture explicitly; this runbook's image examples target `linux/amd64`. Require free persistent storage, registry pull access, enough workload memory (start with 4 GiB), and an ingress/egress NetworkPolicy-enforcing CNI.

```bash
export NS=openshell-openclaw
export RELEASE=openshell-openclaw
export GATEWAY=openclaw-pod
export WORKSPACE=default
export SANDBOX=openclaw-lab
export SKILL_DIR=/absolute/path/to/this-skill
export LAB_DIR=/absolute/path/to/new-openclaw-lab
export POD_OPENSHELL_BIN=/absolute/path/to/openshell-0.1.2/openshell
export POD_CONFIG_HOME="$LAB_DIR/client-config"
export GATEWAY_URL=https://127.0.0.1:18080
HELM_TRANSPORT_ARGS=()
podshell() { XDG_CONFIG_HOME="$POD_CONFIG_HOME" "$POD_OPENSHELL_BIN" "$@"; }
oshell() { podshell --gateway "$GATEWAY" --workspace "$WORKSPACE" "$@"; }
umask 077
mkdir -p "$LAB_DIR/evidence"
oc whoami --show-server
oc get storageclass
oc get nodes -o wide
podshell --version
podshell gateway list
```

Record the existing Helm releases, gateway versions, sandboxes and PVCs before changing anything. Do not treat 4.21 as blocked by SAW's separate 4.22+ requirement; instead check this pod runtime's actual kernel/CNI/CRD support and report what was verified.

Reestablish these variables and functions in every operator terminal. Use the original matching CLI/configuration to inventory the existing 0.0.103 gateway separately. The wrapper scopes `XDG_CONFIG_HOME` only to the new client invocation; it does not change the existing active gateway or the user's other tools. A separate binary alone would be insufficient because `gateway add` selects its new gateway in its configuration root.

### 2. Reuse or install the pod gateway

**Reuse first:** if an existing gateway runs `0.1.2`, set its real namespace/release/gateway/workspace and inspect its authentication and namespace ownership. Register it in the isolated client configuration with its approved existing TLS/authentication material; preserve the original registration. Preserve its transport and policy settings; skip the fresh installation and dedicated certificate export below. Check the corresponding gateway image and client release, API reachability, existing sandboxes and storage. Never apply the lab values file over a shared gateway.

**Fresh gateway:** inspect `oc get crd sandboxes.agents.x-k8s.io -o yaml` and its controller. OpenShell accepts a served `agents.x-k8s.io/v1beta1` or `v1alpha1` API. Reuse a healthy installed Agent Sandbox controller, including an existing OLM owner; do not install a second one or upgrade shared CRDs to match a floating example. If missing, download the official pinned core-controller manifest, review its cluster-scoped RBAC/images and then install it:

```bash
export AGENT_SANDBOX_VERSION=v1.0.9
curl -fsSL -o "$LAB_DIR/agent-sandbox.yaml" \
  "https://github.com/kubernetes-sigs/agent-sandbox/releases/download/$AGENT_SANDBOX_VERSION/sandbox.yaml"
```

Inspect that exact manifest, record its checksum and referenced controller image, apply with `oc apply -f "$LAB_DIR/agent-sandbox.yaml"`, and require its controller rollout and served CRD. This is a dependency candidate from the current official release, not a claim that its pairing was tested by the starter author. Do not install the optional router, extensions or warm pools for this lab. Require sufficient rights for this dependency and the chart's ClusterRole/ClusterRoleBinding; a namespace-only login is insufficient for a fresh OpenShell install.

Copy `assets/openclaw-pod/gateway-values.yaml` into `LAB_DIR` and inspect its `0.1.2` chart rendering. It enables TLS, mandatory mTLS transport, local developer-principal authorization and no external Route. Confirm the desired release/name/namespace are unused before the fresh install:

Check both PVC classes. The sandbox's class can be selected using `server.workspaceStorageClass`. This exact chart's gateway StatefulSet hardcodes a 1-GiB RWO claim and uses the default class; it does **not** implement `persistence.storageClass`. If that default is absent or NFS-backed, prepare a reviewed pinned-chart customization of the gateway `volumeClaimTemplates[].spec.storageClassName` before installation (and render it), or stop for suitable storage. Do not silently change a shared default StorageClass or try to mutate an existing bound claim.

If the OpenShift environment is known to stall SSH relays through `oc port-forward`, choose the source's **mTLS passthrough Route transport before this fresh install**. This exposes only the OpenShell control endpoint behind a mandatory client certificate, not the unauthenticated OpenClaw UI. Derive a unique host under the cluster ingress domain and create the supplemental values:

```bash
export GATEWAY_HOST="openclaw-pod-gateway.$(oc get ingress.config.openshift.io cluster -o jsonpath='{.spec.domain}')"
export GATEWAY_URL="https://$GATEWAY_HOST"
python3 - "$LAB_DIR/transport-values.yaml" "$GATEWAY_HOST" <<'PY'
from pathlib import Path
import re, sys, yaml
target, host = Path(sys.argv[1]), sys.argv[2]
if not re.fullmatch(r'[a-z0-9][a-z0-9.-]+[a-z0-9]', host):
    raise SystemExit('Inspect the actual ingress domain before choosing the gateway host')
values = {'pkiInitJob': {'serverDnsNames': [host]}, 'openshiftRoute': {
    'enabled': True, 'host': host, 'annotations': {
        'haproxy.router.openshift.io/timeout': '300s',
        'haproxy.router.openshift.io/timeout-tunnel': '300s'}}}
text = yaml.safe_dump(values, sort_keys=False)
if target.exists() and target.read_text() != text:
    raise SystemExit('Refusing to overwrite different transport values')
target.write_text(text)
PY
HELM_TRANSPORT_ARGS=(--values "$LAB_DIR/transport-values.yaml")
```

Otherwise keep `HELM_TRANSPORT_ARGS=()` and the loopback URL. Both modes retain TLS/mTLS and the same isolated client bundle. Do not add a Route to an existing gateway or rotate existing certificates implicitly. If changing transport after installation, follow the pinned certificate-management procedure in a maintenance window; adding a new SAN value alone does not prove an existing certificate was reissued.

When external OpenClaw access is requested, prepare the UI values from [openclaw-route.md](#external-openclaw-route) **at this point**, after choosing the control transport. Retain its exact hostname with `--extra-san` if set, then append the UI values last to `HELM_TRANSPORT_ARGS`. The separate UI Route will be published only after certificate and service-exposure validation.

```bash
cp "$SKILL_DIR/assets/openclaw-pod/gateway-values.yaml" "$LAB_DIR/gateway-values.yaml"
oc create namespace "$NS"
helm install "$RELEASE" oci://ghcr.io/nvidia/openshell/helm-chart \
  --version 0.1.2 --namespace "$NS" \
  --values "$LAB_DIR/gateway-values.yaml" "${HELM_TRANSPORT_ARGS[@]}" \
  --wait --timeout 5m
oc -n "$NS" rollout status "statefulset/$RELEASE" --timeout=300s
oc -n "$NS" get pods,svc,pvc,networkpolicy
```

The copied values use `fullnameOverride: openshell-openclaw`; change it consistently if changing `RELEASE`. Leave the live Agent Sandbox API preflight enabled. For **offline rendering only**, pass `--set agentSandbox.preflight.enabled=false`, or supply the known API with Helm's `--api-versions`. Do not bypass the live dependency check.

OpenShell 0.1.2's Kubernetes driver selects the namespace-assigned non-root UID/GID, drops capabilities and uses `RuntimeDefault` seccomp. Do **not** carry over the old raw track's `privileged` SCC. Startup must pass the actual nested seccomp-notification and Landlock probes; inability to pass is a runtime blocker, not a reason to add privilege or disable containment.

For this fresh local lab, export only the dedicated client TLS bundle into a new registration directory. Refuse to overwrite an existing registration; verify the Secret name from chart values if customized:

```bash
export TLS_DIR="$POD_CONFIG_HOME/openshell/gateways/$GATEWAY/mtls"
test ! -e "$TLS_DIR"
mkdir -p "$TLS_DIR"
chmod 700 "$TLS_DIR"
oc -n "$NS" get secret openshell-client-tls -o jsonpath='{.data.ca\.crt}' \
  | base64 -d > "$TLS_DIR/ca.crt"
oc -n "$NS" get secret openshell-client-tls -o jsonpath='{.data.tls\.crt}' \
  | base64 -d > "$TLS_DIR/tls.crt"
oc -n "$NS" get secret openshell-client-tls -o jsonpath='{.data.tls\.key}' \
  | base64 -d > "$TLS_DIR/tls.key"
chmod 600 "$TLS_DIR"/*
```

Use `set -euo pipefail` for these certificate pipelines and require all three files nonempty. They are credentials, not handover artifacts. For the loopback transport, check port `18080` is unused, then in a separate tracked terminal run:

```bash
oc -n "$NS" port-forward --address 127.0.0.1 "svc/$RELEASE" 18080:8080
```

Register and test with that exact client bundle:

```bash
podshell gateway add "$GATEWAY_URL" --local --name "$GATEWAY"
oshell status
oshell sandbox list
```

This uses mandatory client-certificate transport, not per-user OIDC/SAW identity. Prove a connection without a client certificate is rejected, including when the gateway Route is enabled. Do not turn off TLS, set insecure verification, or expose this developer principal without the client-certificate gate. Break and restore only the owned port-forward for Module 1's recovery exercise. With Route transport, use a separately named temporary loopback registration for that exercise; the Route-based registration should remain reachable when a local tunnel stops. The upstream OpenShift e2e overlay documents SSH-relay stalls through a port-forward: require actual exec/UI forwarding, not just a successful `status` call.

### 3. Render configuration and build the image

```bash
git clone https://github.com/red-hat-data-services/agentic-starter-kits.git "$LAB_DIR/starter"
git -C "$LAB_DIR/starter" checkout e3b20b1adadf02542dd2656fd0511c63c57991aa
export MODEL_BASE_URL=https://your-model-host/v1
export MODEL_ID=your-exact-served-model-id
export INPUTS_DIR="$LAB_DIR/inputs"
python3 "$SKILL_DIR/scripts/render_openclaw_pod.py" \
  --endpoint "$MODEL_BASE_URL" --model "$MODEL_ID" --out "$INPUTS_DIR"
```

Replace the endpoint and model placeholders with real inputs; never send the example hostname to a real provider. Query `/v1/models` through a protected local credential file when authentication is required; do not print a live key or put it in process arguments. Confirm tool-calling works independently. Set renderer `--context-window` and `--max-tokens` within the actual model limit. A provider-prefixed OGX model ID remains intact: OpenClaw's model selector gets one additional `vllm/` provider prefix, while the request's model ID stays exactly as returned.

The renderer writes only nonsecret JSON/YAML. Keyed mode uses `${VLLM_API_KEY}` as a placeholder, scopes a dedicated profile to the exact model host/port/API path and resolved Node executable, and disallows plaintext keyed URLs. For a genuinely keyless HTTP(S) endpoint, use `--keyless` with a **new** inputs directory; it generates a direct Node-only policy and no credential profile. Do not use keyless mode to work around a server that needs authentication.

Resolve the starter base image to a verified digest with Skopeo and inspect the architecture; the upstream development tag is mutable. For example, save `skopeo inspect --raw docker://quay.io/hmoghani/openshell-base:latest` to a manifest file, compute its SHA-256, and verify the resulting `repo@sha256:...` pull. If unavailable or inconsistent with the checked-out base policy, build `sandboxes/base` from the pinned source, publish to your own registry and record its digest. These are source-derived community/development images; do not label the result Red Hat-certified.

Copy the upstream OpenClaw Containerfile to a new build directory, replacing only its base reference and working directory and installing the generated restrictive image policy. Keep the upstream version pins and official Node checksum verification:

```bash
export BASE_IMAGE=quay.io/hmoghani/openshell-base@sha256:REPLACE_WITH_VERIFIED_DIGEST
export BUILD_DIR="$LAB_DIR/image"
mkdir -p "$BUILD_DIR"
cp "$INPUTS_DIR/sandbox-policy.yaml" "$BUILD_DIR/sandbox-policy.yaml"
python3 - "$LAB_DIR/starter" "$BUILD_DIR" "$BASE_IMAGE" <<'PY'
from pathlib import Path
import re, sys
source, dest, base = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
if not re.fullmatch(r'[^\s@]+@sha256:[0-9a-f]{64}', base):
    raise SystemExit('A verified base image digest is required')
text = (source/'agents/openclaw/deployment/Containerfile.openshell').read_text()
assert text.count('FROM quay.io/hmoghani/openshell-base:latest') == 1
text = text.replace('FROM quay.io/hmoghani/openshell-base:latest', 'FROM ' + base)
assert text.count('USER 1001') == 1
text = text.replace('USER 1001', 'COPY sandbox-policy.yaml /etc/openshell/policy.yaml\nUSER 1001')
text = text.replace('WORKDIR /workspace', 'WORKDIR /sandbox') + '\nENV HOME=/sandbox\n'
target = dest/'Containerfile.openshell'
if target.exists() and target.read_text() != text:
    raise SystemExit('Refusing to overwrite a different build recipe')
target.write_text(text)
PY
export OPENCLAW_TAG=your-registry/your-project/openclaw-sandbox:starter-e3b20b1
podman build --platform linux/amd64 --build-arg NODE_VERSION=24.21.0 \
  --build-arg OPENCLAW_VERSION=2026.9.8 --tag "$OPENCLAW_TAG" \
  --file "$BUILD_DIR/Containerfile.openshell" "$BUILD_DIR"
podman push --digestfile "$LAB_DIR/evidence/openclaw-image.digest" "$OPENCLAW_TAG"
```

Resolve `OPENCLAW_IMAGE` to the pushed `repository@sha256:<digest>` (remove the tag before appending the digest) and verify cluster pull access. Never bake API keys into an image or pass them as build arguments. In a private registry, provision a namespace-scoped pull Secret through the installed chart's supported image-pull settings; inspect existing settings before changing a reused gateway.

The build runs `node --version` and rejects OpenClaw's unsupported-runtime warning. Still require a provider-free sandbox probe of the **pushed digest**, its image policy, `openclaw --version`, Node's `node:sqlite` load, non-root identity and actual `/sandbox` writes. Resolve `readlink -f "$(command -v node)"` and `curl` inside that image; their expected paths are `/usr/local/bin/node` and `/usr/bin/curl`. Rerender with the real read-only paths if different. `/workspace` is not the writable home on the OpenShift driver.

### 4. Bind model credentials and start OpenClaw

Inspect existing sandbox/provider/profile names; choose unused names. For a keyed model endpoint, import only the dedicated workspace profile, then create a provider from a private local file. The bare environment-key form keeps the live value out of command arguments:

```bash
oshell profile lint -f "$INPUTS_DIR/model-profile.yaml"
oshell profile import -f "$INPUTS_DIR/model-profile.yaml"
read -r VLLM_API_KEY < /absolute/path/to/private-model-key
export VLLM_API_KEY
oshell provider create --name openclaw-model-token --type openclaw-model \
  --credential VLLM_API_KEY
unset VLLM_API_KEY
oshell sandbox create --name "$SANDBOX" --detach --no-auto-providers \
  --from "$OPENCLAW_IMAGE" --provider openclaw-model-token \
  --policy "$INPUTS_DIR/sandbox-policy.yaml" --memory 4Gi \
  --env HOME=/sandbox --env XDG_CONFIG_HOME=/sandbox/.config \
  -- openclaw gateway --bind loopback --auth none --port 18789 --allow-unconfigured
```

For keyless mode, skip both profile/provider operations and omit `--provider` from sandbox creation. Its rendered policy supplies the model endpoint directly. Never attach auto-discovered unrelated provider keys. Profiles with a concrete host/path binding prevent repointing a generic OpenAI credential at an arbitrary server. After applying policy, inspect the **effective** policy: attached profiles add rules, so empty base network rules do not mean the model is blocked.

Poll actual sandbox/workload/supervisor readiness and qualification, then stream the nonsecret config to the CLI using the `0.1.2` grammar:

```bash
oshell sandbox exec -n "$SANDBOX" --no-tty --no-login-shell --workdir /sandbox -- \
  openclaw config patch --stdin < "$INPUTS_DIR/openclaw-config.json"
oshell sandbox exec -n "$SANDBOX" --no-tty -- openclaw config validate
oshell sandbox exec -n "$SANDBOX" --no-tty -- openclaw --version
oshell policy get "$SANDBOX" --full
```

The starter README's positional `sandbox exec openclaw` example differs from the pinned CLI: use **`sandbox exec -n <name>`**. OpenClaw's own `agents.defaults.sandbox.mode: off` disables a nested application-managed sandbox only; the complete OpenClaw process is already inside the outer OpenShell boundary. Do not confuse it with the host-side OpenShell plugin architecture, which is a different deployment.

The config persists at `/sandbox/.openclaw/openclaw.json`. Update it through `openclaw config patch --stdin`, not by replacing an owned state file or redeploying a plain ConfigMap. Arrays replace; preserve existing desired entries. Keep the real model key in the OpenShell provider, never in `openclaw-config.json` or `--env`. Verify placeholder-based delivery without printing actual credentials, placeholders or auth profiles.

Profile lint/import require the actual gateway RPC service in this release; YAML parsing alone is not the gateway's semantic validation. Mark those checks `NOT_VERIFIED` during offline preparation rather than trying to satisfy them with a nonexistent local endpoint.

### 5. Use the UI and complete the coding demo

For an external URL, complete [openclaw-route.md](#external-openclaw-route): expose the named OpenShell service, add the exact HTTPS browser origin, create the certificate-gated UI Route to the gateway, and verify browser WebSocket/chat/tool use. OpenClaw continues to listen on loopback inside its sandbox. Do not create a direct workload Route or weaken gateway TLS.

For optional local diagnosis, start a loopback-only OpenShell forward after checking the port is free:

```bash
oshell forward start 127.0.0.1:18789 "$SANDBOX" --background
oshell forward list
```

Open `http://127.0.0.1:18789` for that local diagnostic. The source recipe's application auth is `none` and its listener remains private loopback; external access uses the mandatory certificate gate at the OpenShell gateway described in the Route runbook. Do not bind OpenClaw to `0.0.0.0`, bypass the gateway with a workload Service/Route, or publish a token-bearing URL. Keep device pairing and exact browser-origin checks intact.

Check the effective selected model, complete a real chat, and ask:

> Create `/sandbox/demo/add.cjs` exporting `add(a,b)` and `/sandbox/demo/add.test.cjs` using the built-in `node:test` and `node:assert/strict`. Cover positive, negative and zero values. Run `node --test /sandbox/demo/add.test.cjs` and report the actual results.

Independently inspect and rerun through `oshell sandbox exec -n "$SANDBOX" --no-tty -- node --test /sandbox/demo/add.test.cjs`. Check at least one fresh input yourself. For a repair demonstration, change only the owned function to subtract, confirm the same tests fail, have the agent repair it, verify the test-file checksum stayed unchanged and rerun. Never accept a chat message as proof of a file or test run.

For repeated use: reopen the UI forward, use `sandbox exec -n ... -- sh` for a shell, `sandbox upload <name> <local> <remote>` and `sandbox download <name> <remote> <local>` for files, and preserve `/sandbox` and OpenClaw state. Download to an unused local destination and inspect before overwrite. Recreate a sandbox only with an explicit backup and ownership check. No SAW login, `virtctl`, VM key or SAW workspace membership is involved.

### 6. Complete Module 2 policy exercises

Keep model access on `openclaw-lab` and policy mutations on a **separate provider-free** `policy-lab-pod`; this makes deny tests interpretable. Use the same image digest and the generated hard filesystem policy from creation time. A live policy cannot tighten an existing broad filesystem grant; do not start from the base image's writable `/var/tmp` policy and claim a later update proved its removal.

```bash
oshell sandbox create --name policy-lab-pod --detach --no-auto-providers \
  --from "$OPENCLAW_IMAGE" --policy "$INPUTS_DIR/module2-deny.yaml" \
  --env HOME=/sandbox -- sleep infinity
```

| Exercise | Action and acceptance |
| --- | --- |
| Default deny | Confirm no providers; curl `https://api.github.com/zen` fails with a new matching destination/binary denial event. |
| Read-only allow | `oshell policy set policy-lab-pod --policy "$INPUTS_DIR/module2-readonly.yaml" --wait`; the same curl GET returns 200. Separate GitHub quota/auth outages from policy denials. |
| Binary binding | Repeat the GET with verified `/usr/local/bin/node` and Node's `https` module. It must fail with a matching Node/destination denial while curl succeeds. |
| Method enforcement | Curl POST to the same GitHub host must have a matching method/path policy denial. An upstream 401/403 alone is insufficient. |
| Live change | Deploy a disposable echo Service in the lab namespace, record its exact DNS/port and endpoint readiness, then add only that endpoint bound to curl. POST succeeds with the same sandbox identity. |
| Restore | Reapply `module2-readonly.yaml`; echo POST is denied with a new matching event, while the intended GitHub GET remains allowed. |
| Filesystem | Write a temporary file under `/sandbox` or `/tmp`; attempt a unique path under mode-1777 `/var/tmp`. Require the allowed write and denied write plus non-root identity, directory permissions, SELinux context and hard-requirement startup evidence. Remove the file and fail the gate if the prohibited write succeeds. |
| Platform view | Show distinct workload/supervisor pods, Sandbox CR ownership and NetworkPolicies, and correlate per-sandbox events with the gateway's aggregate RPC view. |

Use `oshell logs policy-lab-pod --since 2m --level info` after allowing event propagation and the scoped OpenShell terminal UI (`oshell term`). Preserve command timestamps and baseline logs so old events cannot satisfy a new denial assertion.

For live change, render the bundled restricted echo Deployment/Service using the same verified OpenClaw image digest. Inspect the result, confirm these two names are unused and deploy only into this lab namespace:

```bash
python3 - "$SKILL_DIR" "$LAB_DIR" "$OPENCLAW_IMAGE" <<'PY'
from pathlib import Path
import re, sys
skill, lab, image = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
if not re.fullmatch(r'[^\s@]+@sha256:[0-9a-f]{64}', image):
    raise SystemExit('A verified image digest is required')
text = (skill/'assets/openclaw-pod/echo.yaml').read_text()
assert text.count('REPLACE_WITH_OPENCLAW_IMAGE_DIGEST') == 1
target = lab/'echo.yaml'
text = text.replace('REPLACE_WITH_OPENCLAW_IMAGE_DIGEST', image)
if target.exists() and target.read_text() != text:
    raise SystemExit('Refusing to overwrite a different echo manifest')
target.write_text(text)
PY
oc -n "$NS" apply -f "$LAB_DIR/echo.yaml"
oc -n "$NS" rollout status deployment/openclaw-policy-echo --timeout=120s
```

Use the `0.1.2` live-update command, run the positive POST, and then restore and repeat the negative POST:

```bash
oshell policy update policy-lab-pod \
  --add-endpoint "openclaw-policy-echo.$NS.svc.cluster.local:8080:read-write:rest:enforce" \
  --binary /usr/bin/curl --rule-name temporary_echo --wait
oshell sandbox exec -n policy-lab-pod --no-tty -- \
  /usr/bin/curl -fsS --max-time 10 -X POST \
  "http://openclaw-policy-echo.$NS.svc.cluster.local:8080/"
# Require the exact policy-echo-ok response before restoring.
oshell policy set policy-lab-pod --policy "$INPUTS_DIR/module2-readonly.yaml" --wait
```

Create the echo Service only if this exercise is selected and absent. It uses no service-account token or additional runtime image. Do not borrow an unrelated Service or depend on the workshop installer's echo deployment. Do not run `make ... openshell-security-test` from the old `0.0.103` track against this gateway. On the Kubernetes driver, prove CNI containment separately with a controlled unrelated pod/peer; network policy objects existing is not proof they are enforced.

### 7. Diagnose, hand over and clean up

Check in order: served Sandbox CRD/controller → gateway TLS and storage → supervisor/workload startup and capability-free qualification → registry/image policy and Node/SQLite → model profile credential binding and DNS/TLS → effective network policy → OpenClaw config and selected model → browser forward and real tool action.

RHCOS kernel version alone is insufficient. The pinned OpenShell source documents legacy read-only seccomp cancellation behavior on older kernels: some peer-address/accept/write-back operations can fail with `EOPNOTSUPP`. Investigate this explicitly if OpenClaw server sockets or forwarding fail. Do not add capabilities, privileged SCC, disable seccomp/Landlock, or claim containment based only on `openclaw --version`. Image pull failure, missing live token, absent tool-calling, failed filesystem setup and a nonfunctioning forward are `BLOCKED` or `FAIL`, not a completed demo.

Record Module 1 gateway lifecycle/tunnel recovery, digest/version/non-root/SQLite checks, real UI chat and independently verified coding; record every Module 2 control separately. For requested external access also require Route admission, server SAN/trust, authorized browser success, certificate-less rejection and WebSocket/tool checks. Hand over the plain external HTTPS URL and browser client-certificate instructions, exact namespace/gateway/workspace/sandbox, source/image revisions, restart/forward steps, evidence and gaps. Source inspection, renderer tests and offline Helm renders are not live validation.

Keep the finished demo by default. For exposure-only removal, follow the Route runbook and preserve the sandbox. On explicit lab cleanup, stop only the owned `forward stop 18789 "$SANDBOX"` and `oc port-forward` process; export user files/state, then remove only the added UI Route/exposure, sandbox/provider/profile and owned echo resources. Deleting a sandbox may delete its persistent state. Uninstall a dedicated gateway only when expressly requested and after inspecting its PVC retention; never delete the existing `local-gateway`, Copilot sandbox, shared Agent Sandbox controller/CRDs, operators, SAW or unrelated namespaces.

## External OpenClaw Route

### Contents

1. Architecture and access boundary
2. Prepare the service hostname and gateway certificate
3. Configure OpenClaw and expose its service
4. Publish and validate the external Route
5. Enable browser access and pairing
6. Upgrade, troubleshoot and remove the exposure

### 1. Architecture and access boundary

Use this runbook when an external OpenClaw browser URL is requested for the **pod-only Modules 1–2**. Read it before a fresh gateway installation so the certificate contains the service domain from the start. Reuse the pinned OpenShell `0.1.2` and OpenClaw `2026.9.8` versions in [openclaw-pod.md](#pod-only-openclaw). Do not introduce SAW, a VM, Keycloak or Vault.

The path is: **browser HTTPS → exact-host OpenShift passthrough Route → OpenShell gateway Service `grpc` port → OpenShell service exposure → supervisor relay → OpenClaw on `127.0.0.1:18789` inside the sandbox**. Preserve the original request path and WebSocket upgrade. Do not create a Service or NodePort pointing directly at a workload pod or set OpenClaw to bind on every interface.

Use the lab gateway's **mandatory client-certificate TLS** for browser access. The browser must trust the gateway server chain and present an operator-approved client certificate. This is certificate-gated access for trusted lab operators, not SAW/OIDC per-user authorization. A shared lab client certificate can grant broader gateway authority; do not distribute it to users who should receive only application access. Browser-native SSO without client certificates requires a separately designed authenticated proxy; never achieve it by disabling the gateway's mTLS gate.

The existing control-plane Route and a sandbox UI Route serve different hostnames. Exposing only the former is insufficient. OpenShell maps the HTTP Host to `<workspace>--<sandbox>--<service>.<service-domain>`. This recipe publishes **one exact UI hostname**, with `wildcardPolicy: None`; a wildcard SAN enables OpenShell's service-domain routing but is not a wildcard OpenShift Route.

Primary version-specific sources:

- [OpenShell 0.1.2 service exposure](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/sandboxes/overview#expose-long-running-services).
- [OpenShell 0.1.2 gateway service domains](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/gateways/overview#configure-service-forwarding).
- Pinned source `crates/openshell-core/src/config.rs`, `crates/openshell-server/src/service_routing.rs`, `crates/openshell-cli/src/run.rs`, and `deploy/helm/openshell` at `6648bd0c290efbc41ba131ee9831ee45cd431f94`.
- Starter kit `agents/openclaw/deployment/docs/raw-deployment.md` at `e3b20b1adadf02542dd2656fd0511c63c57991aa` for exact browser origins, config patching and device pairing.

Do not borrow newer `--authorization-mode bearer-passthrough` flags: the selected `0.1.2` CLI has no such option. Its service proxy strips `Authorization`, rewrites upstream Host to `127.0.0.1:<port>`, and preserves WebSocket upgrades. Keep gateway/edge credentials out of OpenClaw. The native OpenClaw Control UI handshake and pairing remain separate checks.

### 2. Prepare the service hostname and gateway certificate

Establish `NS`, `RELEASE`, `GATEWAY`, `WORKSPACE`, `SANDBOX`, `SKILL_DIR`, `LAB_DIR`, isolated `POD_CONFIG_HOME`, and the `podshell`/`oshell` functions from the pod runbook. The `RELEASE` value below must be the actual gateway Service name; the bundled lab values make them equal. Discover it if reusing another release.

```bash
export SERVICE_DOMAIN="$(oc get ingress.config.openshift.io cluster -o jsonpath='{.spec.domain}')"
export UI_SERVICE=ui
export UI_ROUTE=openclaw-ui
export ROUTE_DIR="$LAB_DIR/external-ui"
export TLS_DIR="${TLS_DIR:-$POD_CONFIG_HOME/openshell/gateways/$GATEWAY/mtls}"
EXTRA_SAN_ARGS=()
if [[ -n "${GATEWAY_HOST:-}" ]]; then
  EXTRA_SAN_ARGS+=(--extra-san "$GATEWAY_HOST")
fi
python3 "$SKILL_DIR/scripts/render_openclaw_route.py" \
  --namespace "$NS" --release "$RELEASE" --service-domain "$SERVICE_DOMAIN" \
  --workspace "$WORKSPACE" --sandbox "$SANDBOX" --service "$UI_SERVICE" \
  --route-name "$UI_ROUTE" "${EXTRA_SAN_ARGS[@]}" --out "$ROUTE_DIR"
export OPENCLAW_URL="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["public_url"])' \
  "$ROUTE_DIR/external-access.json")"
```

For example, workspace `default`, sandbox `openclaw-lab` and service `ui` yield `https://default--openclaw-lab--ui.apps.example.test`. Use the actual ingress domain; verify DNS resolves the **exact** hostname to the ingress router. A dedicated service subdomain can be used instead, but its DNS must be provisioned explicitly. The renderer rejects malformed domains, overlong encoded labels and ambiguous `--` components.

The renderer creates four **nonsecret** files: supplemental Helm values, one UI Route, a browser-origin-only config patch, and the external URL/scope record. Default certificate mode is the built-in PKI. Use `--certificate-mode cert-manager` only for a gateway already using that mode; the helper does not install cert-manager or change the chosen issuer. Pass every existing custom SAN via repeated `--extra-san`, including any gateway control Route hostname and other service wildcard. Helm replaces SAN arrays rather than merging them.

Likewise, inspect OpenClaw's existing `gateway.controlUi.allowedOrigins` without dumping its full provider configuration, and pass each additional origin to retain with `--keep-origin`. The patch preserves the two standard loopback origins and the new exact HTTPS origin. It contains no model key or auth token and does not disable pairing.

**Fresh gateway:** after choosing any control-plane transport, append the generated UI values **last** to the pod runbook's `HELM_TRANSPORT_ARGS`, before its `helm install`:

```bash
HELM_TRANSPORT_ARGS+=(--values "$ROUTE_DIR/gateway-ui-values.yaml")
```

Inspect the render: the gateway must retain TLS, a client CA and mandatory client-certificate verification; server SAN configuration and issued certificate must include `*.$SERVICE_DOMAIN`. The supplemental values disable the anonymous loopback service-HTTP path. They do not change the existing control Route or add OIDC. Keep the supervisor callback address on its internal Service DNS.

**Existing dedicated gateway:** inspect the effective Helm values, issuer mode, mounted server/client certificate Secret names, server certificate SANs and live TLS behavior first. Preserve current authentication, database and sandbox settings. Export the current release values into a private file and merge the generated supplemental values through a reviewed change to that release's owning Helm/Git source. Do not run a blind `helm upgrade --reset-values`, replace Secrets, or change a shared gateway's certificate policy.

Crucially, `0.1.2`'s Kubernetes built-in certgen **skips when its PKI Secrets already exist**. Updating `pkiInitJob.serverDnsNames` and rerunning Helm does not issue a new certificate in that case. If the required wildcard SAN is missing, mark `CERTIFICATE_UPDATE_REQUIRED` and prepare an owned PKI maintenance change before publishing the Route. With an existing cert-manager issuer, let its Certificate reconciliation add the retained SANs and verify the new issued certificate and gateway TLS reload. With built-in PKI, prepare an explicit replacement/rotation plan with secure backups, updated client trust, supervisor/bootstrap impact, rollback and data-preservation checks; do not delete TLS or JWT Secrets as a shortcut. A fresh dedicated gateway installed with the correct SANs is an alternative when the existing gateway must remain uninterrupted, but migrating user state is a separate deliberate operation.

This native exposure is accepted only after a live connection **without a client certificate is rejected**. Do not infer browser protection from OIDC settings or `enableMtls` alone. An OIDC/edge deployment that allows certificate-less HTTP service traffic needs an authenticated frontend before exposure; do not disable its existing identity configuration to force this lab pattern.

### 3. Configure OpenClaw and expose its service

Require the OpenClaw sandbox to be Ready with a healthy loopback listener, working model provider and valid config. Apply only the origin patch, retaining model configuration and workspace state:

```bash
oshell sandbox exec -n "$SANDBOX" --no-tty --no-login-shell -- \
  openclaw config patch --stdin < "$ROUTE_DIR/openclaw-ui-patch.json"
oshell sandbox exec -n "$SANDBOX" --no-tty --no-login-shell -- openclaw config validate
oshell service expose "$SANDBOX" 18789 "$UI_SERVICE"
oshell service get "$SANDBOX" "$UI_SERVICE"
oshell service list "$SANDBOX" --output json
```

Match the returned endpoint to the expected workspace, sandbox, service and target port. Never overwrite an existing exposure of the same name without inspecting it. Do not change gateway-global policy or attach credentials to expose a UI.

The CLI normalizes a printed service URL's port to its registered gateway endpoint. A gateway registered through `https://127.0.0.1:18080` can therefore print `:18080` even though the public Route listens on 443. Use `external-access.json`'s **`https://<route-host>` URL on 443** for the browser, after confirming its host matches the actual exposure. A returned `openshell.localhost` hostname means the public service domain was not loaded; fix the gateway SAN/configuration and do not publish a fabricated Route URL as complete.

### 4. Publish and validate the external Route

Inspect the generated Route and ensure its name and hostname are unused or already belong to this exact lab exposure. Confirm `spec.to.name` resolves to the OpenShell **gateway** Service and `targetPort: grpc` resolves to its multiplexed gateway listener. Do not target the separate health port or the sandbox's 18789 port directly.

**Before publishing**, prove the real gateway listener rejects certificate-less traffic. Use an operator-owned temporary loopback tunnel to that same Service port, with an unused local port (18081 here). In a separate tracked terminal:

```bash
oc -n "$NS" port-forward --address 127.0.0.1 "svc/$RELEASE" 18081:8080
```

Use the correct server trust bundle. With built-in PKI, `TLS_DIR/ca.crt` is the server trust anchor; with an external cert-manager issuer, use its verified external chain/system roots while retaining the existing **client** certificate/key. Do not use `-k` or `--insecure`. Read the exact UI host and verify it privately, keeping public SNI/Host while connecting through the tunnel:

```bash
export UI_CA_BUNDLE="$TLS_DIR/ca.crt"  # Replace only when the external server issuer differs.
export UI_HOST="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["route_host"])' \
  "$ROUTE_DIR/external-access.json")"
curl --disable --noproxy '*' --connect-to "$UI_HOST:443:127.0.0.1:18081" \
  --cacert "$UI_CA_BUNDLE" --cert "$TLS_DIR/tls.crt" --key "$TLS_DIR/tls.key" \
  --connect-timeout 5 --max-time 20 --fail --output /dev/null \
  --write-out '%{http_code}\n' "$OPENCLAW_URL/"
```

Repeat that same private request **without** `--cert` and `--key`, retaining `--disable` so a curl configuration file cannot add them implicitly. Require the successful authenticated control, a client-certificate-required TLS rejection without a client cert, and matching gateway evidence. Any HTTP response to the certificate-less request, including HTTP 401/403/404/503, means this mandatory TLS gate was not proven and blocks this native publication. A timeout or unrelated TLS trust error is not a pass. If this test fails, do not create the public Route; resolve the certificate/authentication configuration or prepare a separately authenticated frontend.

After that private gate passes, publish only the inspected UI Route:

```bash
oc -n "$NS" apply -f "$ROUTE_DIR/openclaw-ui-route.yaml"
oc -n "$NS" get route "$UI_ROUTE" -o yaml
```

Require admitted status, passthrough TLS, the exact Host, and router/WebSocket timeouts. Passthrough preserves SNI/Host and requires no application path prefix. Do not use an edge Route with plaintext upstream, add a catch-all wildcard Route, or redirect directly to an unauthenticated workload Service.

```bash
curl --disable --cacert "$UI_CA_BUNDLE" --cert "$TLS_DIR/tls.crt" --key "$TLS_DIR/tls.key" \
  --connect-timeout 5 --max-time 20 --fail --output /dev/null \
  --write-out '%{http_code}\n' "$OPENCLAW_URL/"
```

Require an authenticated HTTP success and valid certificate/hostname, then repeat against the **same host** with the same verified CA but **without** the client cert/key. Require TLS client-certificate rejection and correlated gateway evidence. DNS failure, certificate hostname mismatch, generic 503, timeout or an unrelated HTTP error is not proof that mTLS blocked an anonymous browser. Check an untrusted/expired client certificate is also rejected on a dedicated test setup when available.

Stop only the owned temporary 18081 tunnel after the public checks; do not interrupt the control tunnel or another operator's process. If a newly added public Route unexpectedly admits certificate-less service traffic, remove that owned exposure while correcting the gate, and mark the test failed.

Validate the real browser WebSocket reaches HTTP 101 and OpenClaw completes its application handshake. A landing-page HTTP 200 alone is insufficient. Keep the browser connected, send a real model prompt, perform a file/tool action and independently inspect the file through the scoped CLI. Verify an unrelated service exposure has not been created and that no direct workload ingress bypass was added.

### 5. Enable browser access and pairing

For the certificate-based lab, create a password-protected PKCS#12 bundle on the operator host. Run this interactively so the export password is prompted and kept out of shell history, process arguments and chat:

```bash
umask 077
openssl pkcs12 -export -in "$TLS_DIR/tls.crt" -inkey "$TLS_DIR/tls.key" \
  -certfile "$TLS_DIR/ca.crt" -name "OpenClaw lab client" \
  -out "$POD_CONFIG_HOME/openclaw-client.p12"
chmod 600 "$POD_CONFIG_HOME/openclaw-client.p12"
```

Trust the actual **server** issuer CA/chain in the browser or OS trust store, import the PKCS#12 file into the browser's personal/client certificate store, and select that identity for the exact OpenClaw host. With a publicly trusted server certificate, no private server-CA import is needed; the client certificate is still required. Protect the bundle and its password separately. Never include private keys, PKCS#12 files or token-bearing URLs in the downloadable skill or evidence handover.

Open the plain `OPENCLAW_URL` in the browser. If OpenClaw requests device pairing, inspect pending devices and approve only the displayed request from that browser:

```bash
oshell sandbox exec -n "$SANDBOX" --no-tty --no-login-shell -- openclaw devices list
# Replace the next argument with the request ID verified in the operator's browser.
oshell sandbox exec -n "$SANDBOX" --no-tty --no-login-shell -- \
  openclaw devices approve VERIFIED_REQUEST_ID
```

Do not disable device checks, set a wildcard allowed origin, broaden trusted proxies to the cluster CIDR, or use `approve --latest` blindly. The passthrough router cannot edit HTTP forwarded headers. OpenShell rewrites Host for its loopback relay, so use the **external HTTPS Origin** in OpenClaw's allowlist; do not substitute the internal Service URL. Check the runtime's actual origin/proxy rejection if it returns 403 instead of weakening either boundary.

### 6. Upgrade, troubleshoot and remove the exposure

Diagnose in order: exact DNS → Route admission/SNI → server certificate SAN/chain → mandatory client certificate → gateway service-domain config → matching exposure and Ready sandbox → relay and loopback listener → HTTP/UI assets → origin/device pairing → WebSocket handshake → model/tool action. Keep the earlier RHCOS legacy seccomp and runtime qualification checks: forwarding cannot fix an OpenClaw server blocked by unsupported kernel operations.

For 503, verify the gateway Service/endpoints and Route target port, not just the sandbox Pod. For 404, compare workspace/sandbox/service host encoding, loaded wildcard domain and exposure record. For a client-certificate error, check the browser identity and selected trust chain; do not disable mTLS. For a blank UI or disconnected chat, inspect WebSocket upgrades, timeout annotations, exact allowed origins and pairing. The `enableWebsocketTunnel` gateway knob controls a separate transport; the native sandbox service proxy already handles application WebSockets in this revision, so do not toggle it as a generic UI fix.

Treat the external Route as required for this user request: report `PASS` only after remote-browser chat/tool use, authenticated success, anonymous rejection and persistent state checks. Otherwise hand over the prepared manifests and exact `BLOCKED`/`NOT_VERIFIED` steps. Supply the plain HTTPS URL, client-certificate setup instructions and scope; do not claim per-user SAW isolation or normal browser SSO.

On explicitly requested exposure removal, inspect ownership, delete only the UI Route named in `external-access.json`, then use `oshell service delete "$SANDBOX" "$UI_SERVICE"`. Keep the sandbox, model provider, control Route, TLS Secrets, certificates, PVCs and all unrelated exposures. Remove the retired origin from OpenClaw using a reviewed config patch that retains other origins. Certificate reissuance or full gateway teardown is not routine UI cleanup.

## Upstream SAW installation

### Contents

1. Select source and compatibility
2. Inspect the cluster and pin images
3. Install with GitOps
4. Install with the manual quickstart
5. Authenticate, use, and demonstrate
6. Validate isolation and handle upgrades
7. Troubleshoot and remove owned resources

### 1. Select source and compatibility

Use this runbook for SAW-only requests. Source: [validatedpatterns-sandbox/secure-agent-workspace](https://github.com/validatedpatterns-sandbox/secure-agent-workspace), audited on 2026-10-29 at `533be02ec02a69bd1bf9b20274bf9ce8bbef6668`. Read its `README.md`, `docs/deployment-guide.md`, `docs/credential-isolation.md`, `docs/container-images.md`, and effective chart values before deploying. These are installation instructions, not evidence of a live deployment.

Keep this track separate from the older eight-module workshop. That workshop uses its fork, OpenShell `0.0.103`, and setup Job. This upstream revision uses OpenShell `0.1.2-rhaiv.6`, a public `0.1.2` client, Podman by default, and in-guest `install`/`apply` phases. Do not run the workshop's `scripts/preflight.sh`, old setup-Job wait, or old provider/inference commands against this upstream track. OpenShell 0.1.x no longer provides the old managed inference router.

| Check | Required treatment |
| --- | --- |
| OpenShift | Upstream minimum is **4.22+**. Mark 4.21 `COMPATIBILITY_NOT_VERIFIED`; do read-only preparation, then adapt and test in an isolated lab only if requested. Do not erase the minimum or call 4.21 supported because CNV runs there. |
| Virtualization | Use the OpenShift Virtualization release corresponding to the cluster, supported worker hardware, and available KVM. Do not carry the workshop's software-emulation override into the upstream baseline. |
| Architecture | Use amd64 or arm64 images matching workers; follow `docs/arm64.md`. The Docker golden disk is x86_64-only; use Podman on arm64. |
| Capacity | Budget at least 4 cores, 8 GiB RAM and 40 GiB disk per VM, plus the documented 8-core/16-GiB/50-GiB shared allowance. These are planning floors; account separately for OpenShift, CNV and optional portal/AI workloads. |
| Storage | Require a default supported StorageClass, enough free space, and working CDI import. RWX is needed when live migration is required; do not require RWX for every lab VM. |
| Networking | OVN-Kubernetes is the baseline for EgressFirewall. Keep both namespace NetworkPolicy and EgressFirewall enabled for the validated demo. A non-OVN adaptation loses that firewall unless replaced and tested. |
| Permissions | Use an authenticated cluster-admin `oc` session for platform installation; end-user CLI and browser access should not require that session. |
| Model | Obtain a real provider/model/key. The default data-science model is `nvidia/nemotron-3.5-lightning-30b-a3b`; API availability must be checked. |

Read [Red Hat's 4.21 virtualization compatibility statement](https://docs.redhat.com/en/documentation/openshift_container_platform/4.21/html/virtualization/about) when evaluating 4.21. It confirms CNV 4.21 on OCP 4.21, not the whole SAW stack. Keep a 4.21 adaptation as a separate committed fork with operator channels, CRD renders, VM, identity, credential-proxy, inference and denial checks recorded.

For a new checkout:

```bash
git clone https://github.com/validatedpatterns-sandbox/secure-agent-workspace.git saw-upstream
git -C saw-upstream checkout 533be02ec02a69bd1bf9b20274bf9ce8bbef6668
cd saw-upstream
export SAW_DIR="$PWD"
export NS=openshell-agents BUILD_NS=openshell-agents KEYCLOAK_NS=saw-keycloak
export OPENSHELL_SAW_NAME=alice
export SAW_NS="saw-$OPENSHELL_SAW_NAME"
umask 077
mkdir -p evidence
git rev-parse HEAD > evidence/source-revision.txt
```

Use a real account name in place of `alice`: a lowercase DNS label no longer than 19 characters. Do not overwrite an existing checkout or reuse an occupied gateway registration unintentionally. For GitOps, use a writable fork and a remote branch containing this revision and all configuration changes; a detached local checkout does not pin Argo CD.

### 2. Inspect the cluster and pin images

Require Bash, Git, Make, `oc`, Helm 3, `jq`, `curl`, `openssl`, `uv`, Python 3/PyYAML, SSH and matching `virtctl`. Install public OpenShell `0.1.2` in an isolated tool directory and check its `--help`; keep a separate `0.0.103` binary for workshop or existing raw gateways. The Pattern wrapper also needs working Podman (prefer >=4.3). The digest-resolution example below additionally needs Skopeo and `sha256sum` on a Linux control host.

```bash
oc whoami --show-server
oc get clusterversion version -o jsonpath='{.status.desired.version}{"\n"}'
oc get nodes -o wide
oc get storageclass
oc get subscription,csv -A
oc get hyperconverged -n openshift-cnv
openshell --version
make prereqs-check
make check-oidc-ca
```

An absent HCO is expected before a fresh Pattern install; require it Ready before VMs. `prereqs-check` checks client/BOM parity, storage and network topology but is not complete platform compatibility certification. Preserve the printed topology snippet in private evidence; it reads pod/Service CIDRs, the Kubernetes API Service IP, and exact EndpointSlice backend addresses/ports. It may save a public `ingress-ca.pem` locally.

Before **every host `make login`**, export `OIDC_CA_BUNDLE=/absolute/path/to/verified-issuer-ca.pem` (or a trusted system CA bundle that verifies a public issuer), and independently test issuer discovery with `curl --cacert "$OIDC_CA_BUNDLE"`. At this source revision `scripts/oidc-login.sh` otherwise defaults to `curl --insecure`. Do not accept that fallback. The VM's `oidc.caBundle` is a separate setting; it does not fix the host login helper. Keep the native OpenShell client's issuer verification enabled as well, installing the private issuer CA through its supported host trust configuration when necessary.

Handle `check-oidc-ca` results deliberately: exit 2 means an external issuer needs a private CA, and exit 3 means the cluster ingress CA is needed (the Pattern supplies it, while quickstart needs `oidc.caBundle`). A shell with `set -e` will stop there; inspect the output, configure trust, and continue only after the appropriate issuer verification succeeds.

Inspect `values-prod.yaml` before choosing GitOps: the current Pattern also declares **RHDH, OpenShift Pipelines and OpenShift AI on `fast`**, in addition to CNV, RHBK, ESO and Vault. On an existing AI installation, do not switch channels or create duplicate OperatorGroups/Subscriptions. Prefer the manual path for a minimal SAW deployment, or modify the Pattern's owning Git source to reuse installed components and remove coupled portal resources coherently. Inspect live catalog channels and CRD schemas; do not substitute the workshop's `eus-3.5` assumption here.

Record all BOM component digests in `charts/openshell-saw/values.yaml`. The golden VM disk's CI tag is a separate version from the OpenShell components inside it. Resolve published images before any VM render:

Audit all remaining sandbox, NemoClaw CLI and governance-interceptor image references too: this revision still contains mutable `latest` defaults outside the pinned OpenShell components. Resolve and override those references in their owning BOM/profile/chart values when reproducibility is required. Pinning the repository, golden disk and credential proxy alone does not pin every runtime image.

```bash
export IMAGE_REPO=ghcr.io/validatedpatterns-sandbox
export IMAGE_TAG=sha-533be02ec02a69bd1bf9b20274bf9ce8bbef6668
set -euo pipefail
skopeo inspect --raw "docker://$IMAGE_REPO/openshell-gateway:$IMAGE_TAG" \
  > evidence/golden-manifest.json
GOLDEN_DIGEST="sha256:$(sha256sum evidence/golden-manifest.json | awk '{print $1}')"
export GOLDEN_IMAGE="$IMAGE_REPO/openshell-gateway@$GOLDEN_DIGEST"
skopeo inspect --raw "docker://$IMAGE_REPO/saw-credential-proxy:$IMAGE_TAG" \
  > evidence/proxy-manifest.json
PROXY_DIGEST="sha256:$(sha256sum evidence/proxy-manifest.json | awk '{print $1}')"
export CREDENTIAL_PROXY_IMAGE="$IMAGE_REPO/saw-credential-proxy@$PROXY_DIGEST"
make images-mirror
oc -n "$BUILD_NS" get istag openshell-gateway:latest \
  -o jsonpath='{.image.dockerImageReference}{"\n"}'
```

Require successful registry reads and the correct architecture in the manifest/index. A `sha-<commit>` tag is a CI publication convention, not a promise every revision has already built. If absent or private, stop: choose a completed public CI build and record its source revision/digest, or build the audited sources. Never substitute `latest` silently. The README warns that no default proxy digest is configured; do not invent one. Keep the **multi-architecture index digest** for a multi-arch publication. `make images-mirror` enables the cluster registry Route; record this shared change.

Fallback: `make credential-proxy-build` builds the checked-out `credential-proxy/Containerfile` in `BUILD_NS` and prints its internal digest. Publish it to a registry the target namespace can pull, or grant only that namespace's actual proxy ServiceAccount pull access to the build namespace and verify it. Recheck digest and architecture before using the image. Use `make gateway-build` only when a golden disk build is needed; inspect its resource and build requirements first. Do not rebuild all sandbox images routinely.

### 3. Install with GitOps

Use for a dedicated Pattern deployment or a reviewed existing Pattern. Inspect the existing Pattern CR, Argo sources and resource ownership before changing them; use the manual path below for a smaller installation. Keep the default governance engine `interceptor`. APF is optional and needs its own private images, credentials and signed bundle; do not enable it as an installation dependency.

1. Clone a writable fork, base a deployment branch on the audited SHA, and add upstream as a separate remote. Inspect `git status`; preserve local edits. Record the branch's configured remote URL and commit.
2. Run `make ssh-key-generate`. This preserves existing SSH material and creates the secret-values file if missing. Select the actual file the framework will load: `~/values-secret-secure-agent-workspace.yaml` takes precedence over `~/values-secret.yaml`. Edit only the selected file, chmod it and key files to `600`, and reference API keys through `path`. Never commit secret values or generated SSH private keys.
3. Without Brave search credentials, omit the whole `web-search` secret entry and set `global.webSearch.enabled: false` in the fork's `values-global.yaml`. Do not rely on a local environment flag to govern later reconciliations. Keep any per-user `webSearch.enabled` consistent. The default inference entry uses `provider: build` and an API-key file; its model comes from the selected BOM unless overridden deliberately.
4. Merge the following structure into `overrides/saw-users.yaml`; preserve existing users. Replace digest placeholders with the values resolved above. Paste the live topology keys from `make prereqs-check` into `defaults.openshellSaw`, alongside these settings. Never reuse example CIDRs or API IPs.

```yaml
defaults:
  openshellSaw:
    credentialProxy:
      image: ghcr.io/validatedpatterns-sandbox/saw-credential-proxy@sha256:REPLACE_WITH_VERIFIED_INDEX_DIGEST
    source:
      registryURL: docker://ghcr.io/validatedpatterns-sandbox/openshell-gateway@sha256:REPLACE_WITH_VERIFIED_INDEX_DIGEST
    # Merge networkPolicy.clusterNetworkCIDRs, serviceNetworkCIDRs,
    # cleanupApi.serviceIP and cleanupApi.endpoints from the live preflight.
users:
  - name: alice
    profiles: [data-science]
    webSearch:
      enabled: false
    pruneOnRemove: false
    values:
      networkPolicy:
        enabled: true
```

The upstream list starts empty: installation alone creates **no user VM**. The Pattern's `saw-users` default also leaves NetworkPolicy off to stage upgrades. For a new isolated demonstration, enable it explicitly for the first user after supplying live topology and required narrow `extraEgress` rules. EgressFirewall is an additional layer, not a replacement. With an external issuer, disable the Keycloak owner resolver intentionally and supply a verified `ownerSubject` for each entry.

5. Run `make prereqs-check` again, render the affected charts with the actual values, and check every operator channel. Commit and push the configuration to the fork's deployment branch. Do not include `evidence/`, local CA files, secrets, or registry auth in that commit.
6. Set `TARGET_ORIGIN` to the configured writable remote and `TARGET_BRANCH` to its pushed branch, then install from the repository root:

```bash
export TARGET_ORIGIN=origin TARGET_BRANCH=saw-deploy
./pattern.sh make install
oc -n vp-gitops get applications.argoproj.io
make keycloak-check
make keycloak-add-users
make keycloak-password KC_USER="$OPENSHELL_SAW_NAME"
```

`pattern.sh` forwards `TARGET_BRANCH` and `TARGET_ORIGIN`; it does **not** forward `TARGET_REVISION`. Verify the Pattern and generated Applications actually reference the intended fork and remote revision. A local SHA alone does not establish this. Use the password command's clipboard/Secret guidance; do not add `SHOW=1` or record passwords in transcripts. Existing accounts are preserved. Central owner resolution waits for the exact enabled Keycloak account; never insert a guessed OIDC subject to get past it.

7. Require `saw-<name>`, `saw-<name>-secrets` and `saw-<name>-bom` Applications to be healthy at their intended revision; discover actual names rather than assuming a single `openshell-saw` app. Wait for Vault/ESO, inference metadata, proxy CA, credential proxy and CDI disk readiness, then proceed to acceptance below. Resolve the earliest failed owner before retrying dependents.

### 4. Install with the manual quickstart

Use for one SAW with fewer platform dependencies. The manual path requires CNV plus an HCO and RHBK for the local identity provider. It writes Kubernetes Secrets directly; it does not require Vault/ESO, RHOAI, RHDH or Pipelines. Keep governance on. Reuse existing platform components after inspecting their scope and versions.

Install missing CNV and RHBK through the target cluster's advertised OperatorHub packages/channels. Put CNV in `openshift-cnv` and a dedicated RHBK instance/operator in `KEYCLOAK_NS`, avoiding duplicate OperatorGroups. Create `hco/kubevirt-hyperconverged` with `apiVersion: hco.kubevirt.io/v1beta1` and `spec: {}` only when absent, then require its status conditions and virtualization workloads ready. Do not patch an existing HCO to match a sample.

```bash
make quickstart-prereqs-check
make ssh-key-generate
make images-mirror
make keycloak-deploy
make keycloak-check
make keycloak-issuer
make governance-deploy
```

`keycloak-deploy` asks before importing the OpenShell realm into an existing Keycloak; inspect that realm and clients before agreeing. Use the default no-demo-users setup. For a new local account, create a private YAML file with `users: [{name: alice}]`, then run `make keycloak-add-users USERS_FILE=/absolute/path/to/users.yaml` and `make keycloak-password KC_USER=alice`. Avoid a file that accidentally provisions extra users.

For the quickstart's issuer CA, run `make check-oidc-ca` and supply the verified public CA PEM through `oidc.caBundle` in a private `SAW_VALUES_FILE` if required. That file uses **direct chart keys**, unlike the GitOps `defaults.openshellSaw` nesting. Also put `source.registryURL: docker://<verified golden digest reference>` there. Let `saw-create` discover network topology; it rejects conflicting manual topology values. Verify the complete rendered policy rather than disabling it to make an endpoint work.

```bash
export SAW_VALUES_FILE=/absolute/path/to/saw-values.yaml
: "${OIDC_CA_BUNDLE:?Set a verified issuer CA bundle before host login}"
make login
make whoami
read -r API_KEY < "$HOME/.nvidia-api-key"
export API_KEY
make saw-create PROVIDER=build MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
unset API_KEY WEB_SEARCH_API_KEY
```

Require `CREDENTIAL_PROXY_IMAGE` already set to the verified digest. Without a new or existing web-search Secret the quickstart disables that provider. It prompts for the logged-in owner; use the actual identity. To provision another user, pass the verified `OWNER` and `OWNER_SUBJECT`. For a headless control host, use `make login OIDC_FLOW=device-code`; the later OpenShell gateway login uses `OPENSHELL_NO_BROWSER=1`. Do not set `OIDC_ISSUER=none` merely to get past discovery: that disables OIDC and the protected UI routes. Keep TLS verification, supplying the issuer CA instead of using insecure flags.

For an external MaaS/vLLM endpoint, read `docs/custom-inference.md`. Use `PROFILES=custom-inference`, the exact served model, and a base URL ending `/v1`. Add the host-specific governance profile and VM egress rule, plus a scoped NetworkPolicy peer rule for an in-cluster destination. A keyed endpoint must currently be **HTTPS on port 443 with publicly trusted TLS**; private service CA and other keyed ports are not implemented in this isolation path. Plain HTTP is suitable only for a keyless endpoint. Do not reuse an official provider profile to send its key to another host.

### 5. Authenticate, use, and demonstrate

```bash
make saw-logs FOLLOW=false
make saw-list
oc -n "$SAW_NS" get dv,vm,vmi,pods,deploy,svc,route
make saw-status
```

Require both `install` and `apply` in `/var/lib/saw/status.json` to show `Done`, the intended VMI `Running`, and credential-proxy Deployment ready. There is **no old `openshell-saw-setup` Job** in this upstream flow. `saw-status` authorizes the control host's public SSH key to query status; it is not strictly read-only. Poll in bounded intervals and retain failed phase messages.

```bash
make saw-configure
openshell --gateway "$OPENSHELL_SAW_NAME" sandbox list --workspace default
openshell --gateway "$OPENSHELL_SAW_NAME" sandbox list --workspace cuda-dev
make openclaw-tui SANDBOX_NAME=notebook WORKSPACE=default
make openclaw-gui SANDBOX_NAME=notebook WORKSPACE=default GUI_PORT=18790
make sandbox-ui
```

`saw-configure` extracts the gateway CA over the authenticated cluster/VM path, replaces the **same-named local gateway registration**, selects it and invokes OIDC registration. Check for a conflicting raw or older SAW registration first. Preserve unrelated gateways. If sign-in did not complete or expires, run `openshell gateway login "$OPENSHELL_SAW_NAME"`; on a bastion set `OPENSHELL_NO_BROWSER=1`. Use explicit gateway and workspace flags for direct commands to avoid crossing tracks.

For a shell, inspect the installed CLI help and use `openshell --gateway "$OPENSHELL_SAW_NAME" sandbox exec -n notebook --workspace default -- sh`. `sandbox connect` attaches to `sleep infinity` and can appear blank. Use the `sandbox-ui` output or the GUI forward for the agent browser: the legacy `<name>-dashboard` Route can return 503 on 0.1.x and is not proof the sandbox UI is unavailable. Check exact OIDC callback URIs and owner restrictions for the selected UI Route.

Demonstrate a real model-backed coding action: have the notebook agent create `/sandbox/saw-demo.py` with a small standard-library HTTP health endpoint and `/sandbox/test_saw_demo.py` with unittest coverage. Independently inspect both files and run the tests through `sandbox exec` in the same scope. Ask the agent to introduce and fix a failing assertion, then rerun tests independently. Show a benign prompt succeeding and an intentionally prohibited provider or destination being rejected with matching enforcement evidence. Keep the working files for handover. A chat assertion alone is not proof of file creation or policy enforcement.

The CUDA target's `nemoclaw-tui` name remains, but at this BOM it runs plain OpenClaw because NemoClaw onboarding fails its 0.1.x preflight. Report the runtime actually observed; do not claim a completed NemoClaw onboarding. Web search/fetch in the default notebook also has documented limitations even when credentials exist.

### 6. Validate isolation and handle upgrades

Record `PASS`, `FAIL`, `BLOCKED` or `NOT_VERIFIED` per item, with timestamps and redacted evidence. Before declaring SAW ready, verify:

- Source/fork revisions, image digests, client `0.1.2`, guest downstream version, operator CSVs, architecture, VM capacity and disk imports.
- `install`/`apply` completion, proxy readiness, OIDC issuer verification, owner identity and both expected workspaces.
- Successful real inference and independently verified coding/tests.
- Credential proxy bindings for the intended hosts; VM disks mount only `<secret>-meta` provider metadata and the public proxy CA, never provider API keys. Distinguish provider-key isolation from other credentials and VM-root authority; the source explicitly does not make a compromised gateway trustworthy.
- A second real, unprivileged OIDC identity denied access to the owner's gateway and UI, with an owner success control. Use `scripts/check-second-user-denied.sh` with its required `TEST_*` variables from `docs/deployment-guide.md`; expect the authenticated gRPC denial, not an arbitrary HTTP 404.
- Namespace NetworkPolicy and OVN EgressFirewall both effective. Verify allowed inference and an unrelated peer denial; network timeout alone is not a sandbox-policy event. Do not claim namespace isolation while GitOps NetworkPolicy remains disabled.

For local chart checks, use the upstream fixture-based tests with `SKIP_LIVE=1`. For a dedicated live test SAW, `SAW_NS=... VM_NAME=... SKIP_APPLY=1 make test-credential-isolation` skips the apply restart. The full test without `SKIP_APPLY` restarts `saw-apply` to examine temporary admin authority; schedule it accordingly. Network checks need a dedicated peer namespace/VM per `tests/test-network-policy.sh`. Do not run `make test-deployment` routinely: it performs manual and Pattern install/uninstall/reinstall cycles on a dedicated test cluster.

For upgrades, back up user files, record current disk/image/values and identity mapping, and inspect `docs/deployment-guide.md` identity and single-user migration sections plus `docs/credential-isolation.md`. A new golden-image setting does not replace an existing root disk. Changes to proxy wiring or gateway PKI can recreate sandboxes; require the installer's verified archive/restore path and inspect restored files before claiming preservation. Rotate provider keys that previously entered a VM. Do not automatically execute the source's old-app finalizer removal or old VM/DataVolume deletion: first prove ownership and successful data migration. Keep the old workload available until the replacement passes acceptance.

Enable GitOps NetworkPolicy one user at a time using live topology and narrow allowances; revalidate after API EndpointSlice rotation. Missing Keycloak owner resolution should fail closed; fix account, subject and resolver state rather than granting admin. Reauthenticate and fetch the gateway CA after a deliberate PKI rotation.

### 7. Troubleshoot and remove owned resources

Diagnose in order: operator/Argo ownership → storage and CDI → issuer CA and identity → Vault/ESO metadata → proxy CA/Deployment → VMI and guest `install` → guest `apply`/governance → client login/membership → agent/model/UI. Check `docs/troubleshooting.md` for the pinned revision. Missing proxy digest, private CI image, stale topology, empty users list and absent Keycloak account are installation blockers, not reasons to weaken isolation.

For model failures, distinguish proxy 502/binding errors, upstream auth or quota errors, governance policy rejections, EgressFirewall DNS behavior and namespace NetworkPolicy. Add the narrow missing host or peer and recheck. Do not disable TLS, OIDC, EgressFirewall or governance as the delivered fix. For GUI failures, check the sandbox route/forward, installed profile UI, redirect URI and authenticated owner before using the legacy dashboard host.

Leave a working demo running unless cleanup is requested. Deliver the account/namespace mapping, gateway name, token-free UI URLs, actual inference model, revisions/digests, readiness/evidence ledger, remaining gaps and restart instructions. Use `make saw-restart` only for the chosen VM after evaluating impact; it is a VM restart, not a harmless client refresh.

On explicit removal, export user work first. For GitOps, `pruneOnRemove: false` removes the user's Applications but retains the VM/namespace. To remove that user's VM/namespace, first set its `pruneOnRemove: true`, sync and verify, then remove its entry and sync again. For a manually owned SAW, inspect and use scoped `make saw-delete OPENSHELL_SAW_NAME=<name> SAW_NS=saw-<name>` only after confirming disk deletion is intended. Never run full Pattern uninstall, operator cleanup, finalizer removal, or shared namespace deletion as routine SAW cleanup.

## Source map

Workshop audited 2026-10-26; upstream SAW installation refreshed 2026-10-29; starter-kit pod-only first modules refreshed 2026-11-01. Select the installation track in SKILL.md before choosing source. This skill adds orchestration, stricter evidence checks, and a browser client; those additions are not upstream workshop features.

### Revisions

| Repository | Audited revision | Role |
| --- | --- | --- |
| [rhai-agent-security](https://github.com/taylorjordanNC/rhai-agent-security) | `f020994f47caa730ce6b33062dd31e70c72b3010` | Workshop, raw sandbox automation, capstone, guardrails Helm chart |
| [Workshop SAW fork](https://github.com/taylorjordanNC/secure-agent-workspace/tree/saw-emulation-fixes) | `2a4b780102751d6034c267a0ad01f0134ba4a8d5` | Workshop-only SAW charts, scripts, BOM, deployment partials; client 0.0.103 |
| [Upstream SAW](https://github.com/validatedpatterns-sandbox/secure-agent-workspace/tree/533be02ec02a69bd1bf9b20274bf9ce8bbef6668) | `533be02ec02a69bd1bf9b20274bf9ce8bbef6668` | SAW-only install/update; per-user VM, credential proxy, client 0.1.2 and downstream BOM 0.1.2-rhaiv.6 |
| [Agentic starter kit OpenClaw](https://github.com/red-hat-data-services/agentic-starter-kits/tree/e3b20b1adadf02542dd2656fd0511c63c57991aa/agents/openclaw) | `e3b20b1adadf02542dd2656fd0511c63c57991aa` | Updated first modules: OpenClaw 2026.9.8 inside an OpenShell pod sandbox; Node 24.21.0 image recipe; no SAW |
| [NVIDIA OpenShell v0.1.2](https://github.com/NVIDIA/OpenShell/tree/v0.1.2) | `6648bd0c290efbc41ba131ee9831ee45cd431f94` | Pod-track CLI grammar, chart values, OpenShift capability-free runtime, provider binding and policy semantics |

Read local source at the selected track's revisions during execution. Refresh deliberately if requirements demand newer software. Operator channels and image tags can move even when Git is pinned; record installed CSVs, imageIDs, chart versions, and Argo source revisions. Source inspection and offline validation do not establish live deployment or Red Hat certification of this Pattern.

For pod-only first modules, read [openclaw-pod.md](#pod-only-openclaw). Use the starter's **Running in an OpenShell Sandbox** section and `Containerfile.openshell`, not its plain Kustomize manifests or the host-side OpenShell plugin. The recipe reports testing on OpenShell 0.1.2/OpenShift 4.22. Keep that distinct from the plain Deployment's 4.17+ prerequisite and SAW's separate 4.22+ minimum. Inspect the actual CLI: at v0.1.2, `sandbox exec` uses `-n <name>`, correcting the starter prose's positional-name example. Do not copy its instruction to delete old sandboxes as an automatic upgrade step.

For external OpenClaw browser access, follow [openclaw-route.md](#external-openclaw-route). Audit native service routing, service URL port normalization, proxy header/WebSocket behavior, TLS client verification and Kubernetes certgen at the same v0.1.2 revision. The path is an exact-host passthrough Route to the OpenShell gateway, not a direct sandbox Service. It requires a configured wildcard service-domain SAN, a real issued certificate, exact browser origins and a verified mandatory mTLS gate. Kubernetes certgen skips existing TLS Secrets, so a Helm SAN change alone is not certificate rotation. Do not import later versions' bearer-passthrough flags or claim OIDC protects the native HTTP service without a live anonymous-denial check.

For upstream SAW, read [saw-upstream.md](#upstream-saw-installation). Audit `README.md`, `docs/deployment-guide.md`, `docs/credential-isolation.md`, `docs/container-images.md`, `docs/custom-inference.md`, `Makefile-quickstart`, `values-prod.yaml`, `charts/openshell-saw/values.yaml` and `charts/saw-users/values.yaml`. The minimum is OpenShift 4.22+; 4.21 remains an unverified adaptation. Current upstream commands, ownership and secret boundaries differ from the workshop. The GitOps Pattern declares additional RHDH/Pipelines/RHOAI components; the smaller manual quickstart does not require them or Vault/ESO.

### Published pages

Base: https://taylorjordannc.github.io/rhai-agent-security/modules/

| Page | Required result in this skill |
| --- | --- |
| [index.html](https://taylorjordannc.github.io/rhai-agent-security/modules/index.html) | Full eight-module path rather than the short classroom track |
| [01-overview.html](https://taylorjordannc.github.io/rhai-agent-security/modules/01-overview.html) | Explain runtime, VM/identity, and model boundaries |
| [02-details.html](https://taylorjordannc.github.io/rhai-agent-security/modules/02-details.html) | Tools, exact versions, cluster/capacity and secret preflight |
| [03-module-01-basic-openshell.html](https://taylorjordannc.github.io/rhai-agent-security/modules/03-module-01-basic-openshell.html) | Five exercises: gateway, resources, sandbox, tunnel recovery, raw OpenClaw |
| [04-module-02-policy-and-security.html](https://taylorjordannc.github.io/rhai-agent-security/modules/04-module-02-policy-and-security.html) | Six exercises plus automated security test |
| [05-module-03-deploy-secure-agent-workspace.html](https://taylorjordannc.github.io/rhai-agent-security/modules/05-module-03-deploy-secure-agent-workspace.html) | Three installation exercises and setup/VM gates |
| [06-module-04-create-openclaw-agent.html](https://taylorjordannc.github.io/rhai-agent-security/modules/06-module-04-create-openclaw-agent.html) | Five exercises: OIDC, validation, diagnosis, agent TUI, verified action |
| [07-module-05-interact-with-agent.html](https://taylorjordannc.github.io/rhai-agent-security/modules/07-module-05-interact-with-agent.html) | Four exercises: permitted/denied action, governance, browser |
| [08-module-06-secure-agent-workspace.html](https://taylorjordannc.github.io/rhai-agent-security/modules/08-module-06-secure-agent-workspace.html) | Four architecture/ownership/identity/secret/governance exercises |
| [09-module-07-sre-capstone.html](https://taylorjordannc.github.io/rhai-agent-security/modules/09-module-07-sre-capstone.html) | Four fleet/telemetry/incident exercises |
| [13-module-08-model-boundary-guardrails.html](https://taylorjordannc.github.io/rhai-agent-security/modules/13-module-08-model-boundary-guardrails.html) | Seven required exercises; remote moderation extension; explicit GPU alternative |
| [10-reference.html](https://taylorjordannc.github.io/rhai-agent-security/modules/10-reference.html) | Source ownership and limits of each security claim |
| [11-cleanup.html](https://taylorjordannc.github.io/rhai-agent-security/modules/11-cleanup.html) | Owned-resource teardown, held until requested |
| [14-facilitator-guide.html](https://taylorjordannc.github.io/rhai-agent-security/modules/14-facilitator-guide.html) | Optional pre-provisioned/fleet route and readiness gate |

The unrendered `content/extra/security-ctf.adoc` is explicitly parked. Its five challenges repeat Module 2: default deny, binary binding, filesystem boundary, method enforcement, and live restore. Do not invent a Module 9 or try a nonexistent Module 12 page.

### Follow cross-component includes

Module 3 includes `docs/antora/modules/ROOT/partials/deployment/` from the SAW fork: `scope.adoc`, `control-node.adoc`, `cluster-prerequisites.adoc`, `clone-and-secrets.adoc`, `install.adoc`, and `troubleshooting.adoc`. Module 4 also includes `configure-client.adoc` and `validate.adoc`; Module 6 includes `governance.adoc`; cleanup includes `cleanup.adoc`. Read them from the pinned SAW checkout rather than substituting upstream-main instructions.

The workshop `content/antora.yml` resolves page attributes. Important defaults: `openshell`, `local-gateway`, `policy-lab`, `openclaw-lab`, `openshell-agents`, `vp-gitops`, `openshell-saw`, `cuda-dev`, `cuda-sandbox`, `guardrails`, `nemo-guardrails`. Replace defaults consistently if the deployment uses other names.

### Verification limits and corrections

- Baseline source declares OpenShift 4.22 and RHOAI `eus-3.5`; this audit is source inspection, not certification of every operator/platform pairing.
- Helm `--wait` does not establish readiness of operator-created resources; assert CR status and rollout separately.
- A ConfigMap update does not universally cause a Deployment rollout. Check pod UID/start time and loaded configuration, explicitly restart if reconciliation does not.
- A model response without PII does not prove no model invocation. Check structured rail attribution and upstream evidence.
- The guardrails chart accepts direct keys but renders them as literal CR env values as well as Secret material. Prefer the existing-Secret path and validate operator propagation.
- Upstream examples disable some TLS checks and use broad regex keywords. Record those lab settings; validate CAs for the final app and surface false positives before reusing the policy in a customer environment.
- Seeded incident traces are synthetic. Distinguish them from the participant's freshly ingested session and the live shop metrics.
- The upstream incident token helper can reuse an OCP token for both metrics and traces; use scoped credentials, not the administrator login.

### Additional primary references

- https://docs.nvidia.com/openshell/latest/
- https://docs.nvidia.com/nemo/guardrails/latest/index.html
- https://github.com/NVIDIA/NemoClaw
- https://github.com/validatedpatterns-sandbox/secure-agent-workspace
- https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/latest/html/serving_models/nvidia-nim-guardrails_model-serving

Use these to resolve version-specific questions, not to silently change the audited workshop baseline.

## Workshop platform installation

This reference applies to the **pinned eight-module workshop track** and its `taylorjordanNC` SAW fork. For updated first modules without SAW, follow [openclaw-pod.md](#pod-only-openclaw). For SAW installation from `validatedpatterns-sandbox/secure-agent-workspace`, follow [saw-upstream.md](#upstream-saw-installation). Do not combine the old client/BOM/setup-Job commands here with either new path.

### Contents

1. Check capacity and tools
2. Establish GitOps and RHOAI
3. Install SAW
4. Configure OIDC and workspace access
5. Diagnose and retain the environment

### 1. Check capacity and tools

Run the read-only preflight script. Require `oc`, `kubectl`, Helm 3, Git, GNU Make, jq, curl, OpenSSL, Python/PyYAML, SSH, lsof, virtctl, and Podman >=4.3 or the supported mirror-tool alternative. Match oc/virtctl to the cluster. On macOS, start the Podman machine before mirroring; use WSL2 or a Linux bastion for Windows.

Check default StorageClass, free capacity, PVC access modes, image-import disk space, multinode availability, and virtualization support. The 16 CPU / 32 GiB emulation figure is a baseline floor, not sufficient proof of spare capacity for the whole workshop. Account for all DSC components, VM disks, MLflow PVC, registry mirror, and operator pods. Check kernel capabilities at runtime; Linux >=5.13 is only a preliminary Landlock check.

Verify raw installation permissions (`create subscriptions.operators.coreos.com`, `use scc/privileged`) and source operator channels, including Agent Sandbox `preview-0.9`. Inspect what `automation/openshell-env/install.sh` will change before invoking it.

### 2. Establish GitOps and RHOAI

On fresh clusters, the upstream workshop assumes OpenShift GitOps already exists. Inspect `subscriptions`, CSVs, and the `applications.argoproj.io` CRD. If missing, install the official Red Hat OpenShift GitOps operator from the target cluster's `redhat-operators` catalog using the available supported channel; confirm its package/channel with `oc get packagemanifests -n openshift-marketplace`. Wait for its CSV and `openshift-gitops` ArgoCD instance to be ready. Do not guess a package/channel when the catalog does not advertise it.

Read before applying:

```bash
cd "$WORKSHOP_DIR"
cat automation/argocd/templates/10-capstone.yaml
cat automation/argocd/capstone/50-rhods-operator.yaml
cat automation/argocd/capstone/dsc.yaml
```

The child owns more than the demo: RHOAI Subscription `rhods-operator` on `eus-3.5`, DSC `default-dsc` (`v2` API), MLflow, shop, telemetry proxy, console, seed hooks, and mirror jobs. The SAW pattern also declares operator subscriptions. Preserve the audited parity and run `automation/fleet/check-channel-parity.sh` after source changes; inspect its invocation first. Do not create a duplicate DSC or change existing subscriptions without evaluating ownership and supported schema.

For a new dedicated cluster, create a local copy of `10-capstone.yaml`, set `spec.source.targetRevision` to the chosen workshop commit and repoURL to the writable fork when modified, then apply that copy. `make -C automation capstone-bootstrap` is the upstream shortcut but defaults to moving `main`; use it only when that choice is intentional.

```bash
oc get application module-7-prereqs -n openshift-gitops
oc get subscription,csv -n redhat-ods-operator
oc get datasciencecluster default-dsc
oc get crd nemoguardrails.trustyai.opendatahub.io mlflows.mlflow.opendatahub.io
```

Allow capstone health to wait on SAW; finish SAW installation below, then require the child `Synced`/`Healthy` and successful seed hook. Retry exhaustion can require a new explicit Argo sync after correcting dependencies; do not assume retry is infinite.

For an existing RHOAI installation, edit its owning Git source so `trustyai` and `mlflowoperator` are `Managed` and required APIs are available. Do not apply the full sample DSC over a customized deployment. Inspect current schema with `oc explain`; report unsupported fields/version mismatches and prepare a fork rather than forcing unknown fields. RHOAI being installed does not by itself mean TrustyAI and MLflow are deployed.

### 3. Install SAW

Read the pinned fork's deployment partials before executing. Preserve current source as canonical; the commands here identify the operational spine.

```bash
cd "$SAW_DIR"
make generate-keys
chmod 600 "$HOME/values-secret.yaml"
```

Edit the generated inference secret entry: provider `build`, model `nvidia/nemotron-3-super-120b-a12b`, and API key through a private readable file referenced by `path`. Use exactly one of `path`/`value`. The template defaults can differ from the data-science BOM; align the secret with its enabled provider. Keep keys, generated SSH material and secret values out of Git and evidence. Web search remains disabled unless both its secret and BOM provider are configured.

Choose configured owner intentionally in `overrides/openshell-saw.yaml`; sample `alice` is a lab identity. Inventory seeded Keycloak accounts and restrict them to the isolated lab. Do not confuse configured VM owner with the OIDC subject's workspace membership.

```bash
make copy-images
for img in openshell-gateway openshell-gateway-docker nemoclaw-sandbox nemoclaw-cli; do
  oc -n openshell-agents get "istag/$img:0.0.103"
done
TARGET_BRANCH=2a4b780102751d6034c267a0ad01f0134ba4a8d5 ./pattern.sh make install
```

Require all four ImageStreamTags: the mirror target can continue after a source pull fails. `pattern.sh` forwards `TARGET_BRANCH` to the Validated Patterns utility; confirm the rendered Pattern/Argo desired state uses the chosen commit before accepting it. For modified forks, also set `TARGET_ORIGIN` to that fork and replace the revision with its committed SHA. Inspect SAW GitOps repo URLs/revisions, image pull credentials, BOM images, and external registry egress. Record mutable tags rather than calling them immutable. The pattern also installs OpenShift Virtualization; do not manually duplicate its OperatorGroups.

For hosts without KVM, wait until the pattern creates `hco/kubevirt-hyperconverged` in `openshift-cnv`, then apply the canonical emulation annotation from `install.adoc` and verify the effective KubeVirt `useEmulation=true`. Do not apply it before HCO exists or on a KVM-capable baseline. Treat shared-cluster global emulation changes as a platform-owner decision.

```bash
oc -n vp-gitops get applications.argoproj.io
oc -n openshell-agents get dv,vm,vmi,job
oc -n openshell-agents logs job/openshell-saw-setup --tail=100
oc -n openshell-agents wait --for=condition=complete job/openshell-saw-setup --timeout=5400s
test "$(oc -n openshell-agents get vmi openshell-saw -o jsonpath='{.status.phase}')" = Running
```

Use bounded polling/tool yields while reporting progress during long installation. The setup wait applies after the Job exists. Do not report complete solely because `pattern.sh` returned.

### 4. Configure OIDC and workspace access

Run from SAW root on the control node holding its SSH key:

```bash
export OPENSHELL_SAW_NAME=openshell-saw
make login OIDC_FLOW=browser
make openshell-saw-configure-gateway OPENSHELL_SAW_NAME=openshell-saw
make whoami
```

Use `OIDC_FLOW=device-code` on a bastion. This login is Keycloak, not OpenShift. Read `Subject:` from the actual identity. With platform-admin gateway credentials, add that subject as `user` to `cuda-dev` and `default` using `openshell workspace member add --workspace ... --subject ... --role user`. Return to the user identity and repeat lists. Do not grant admin solely to bypass missing workspace membership.

Read `configure-client.adoc` for the virtctl SSH version check and CA extraction. Guest must report `0.0.103-rhaiv.0`; client `0.0.103`.

```bash
make openshell-saw-list
openshell --gateway openshell-saw sandbox list --workspace default
openshell --gateway openshell-saw sandbox list --workspace cuda-dev
```

Expected baseline: default `notebook`, `cuda-sandbox`, `toolbox`; cuda-dev `cuda-sandbox`, `toolbox`. The capstone adds `metrics`, `traces`, `analyst` according to the active BOM. Duplicate names across workspaces require explicit scope.

### 5. Diagnose and retain

Work outward to inward: Argo sync/health → operator CSVs → Vault/ESO readiness → DataVolume import/storage → VM/VMI → setup Job/SSH → gateway service → OIDC → membership → sandbox → inference. Fix the first broken owner and revalidate dependents.

Specific failures: duplicate OperatorGroups; unavailable catalog channel; VM not schedulable without KVM/emulation; missing image stream; unreadable key file; incorrect secret provider; Docker driver supervisor path; expired OIDC token; failed setup before BOM apply. Use `deployment/troubleshooting.adoc`. Deleting a setup Job requires explicit owner resync when self-heal is off.

For pre-provisioning, use `automation/fleet/fleet-install.sh --only <cluster-name>` with its documented private CSV, and `fleet-status.sh --gate`. Full fleet automation is optional; never create a credential CSV with fabricated cluster data. A fleet install can return before long VM setup finishes; inspect actual Job/VM gates.

Leave the pattern running for the final demo. Uninstall only when requested and scoped to the dedicated lab.

## Workshop modules

For the updated **first modules without SAW**, follow [openclaw-pod.md](#pod-only-openclaw): it replaces the version-only raw agent exercise with the starter kit's model-backed OpenClaw/OpenShell pod deployment and adapts Module 2 to 0.1.2. The original exercises below remain the separate, pinned full-workshop track; do not combine their installer, old security test or SAW prerequisites with the new pod path.

### Contents

1. Raw OpenShell (Modules 1–2)
2. SAW installation and operation (Modules 3–6)
3. SRE fleet (Module 7)
4. Handover and optional assessment

Read the matching upstream AsciiDoc page before each module and execute its source blocks, including required collapsible assertions. Expand attributes from `content/antora.yml`; do not execute unresolved `{...}` placeholders. Use the matrices below as the minimum ledger, adding a row for every concrete test. Expected failures belong inside assertions; do not let `set -e` abort the run before recording the negative result. A dependency outage is `BLOCKED`, not a successful deny test.

### 1. Raw OpenShell

#### Module 1

Run from `$WORKSHOP_DIR`:

```bash
make -C automation install-openshell OPENSHELL_VERSION=0.0.103
oc -n openshell get statefulset,pods,svc,pvc
oc get crd sandboxes.agents.x-k8s.io
oc -n openshell port-forward --address 127.0.0.1 svc/openshell 8080:8080
```

Keep the tunnel in a separate terminal or a tracked background process. Verify the port is available first. Register using `openshell gateway add http://127.0.0.1:8080 --local --name local-gateway`; if the name exists, inspect it before replacing it. Select it and check status. Keep raw HTTP internal.

```bash
openshell --gateway local-gateway sandbox create --name policy-lab --no-auto-providers --no-tty -- true
```

For the raw agent, create `openclaw-lab` from the workshop's pinned image:
`ghcr.io/nvidia/openshell-community/sandboxes/openclaw@sha256:c116946b3f9e84791630f21f115ac35c9c9f669af70ec0eef3035d79833a9550`.
Use `--no-auto-providers --no-tty -- true`, poll exec readiness, then run `openclaw --version`. Inspect existing same-name sandboxes before deletion; retain user-created resources.

| Exercise | Required observation |
| --- | --- |
| 1 Install gateway | Agent Sandbox operator succeeds; gateway StatefulSet ready; local registration works |
| 2 Verify deployment | Running gateway, bound 1 GiB SQLite PVC, Service/endpoints and Sandbox CRD |
| 3 Create test sandbox | `policy-lab` Ready in CLI and corresponding cluster Sandbox/pod |
| 4 Break/restore access | Owned tunnel stopped → CLI fails; same tunnel restored → CLI works |
| 5 Raw OpenClaw | Agent version executes inside pinned sandbox pod; no model provider claimed |

Record the raw SCC grant specifically to `openshell-sandbox`; do not describe the gateway pod as requiring it. The base-image pin is in `automation/Makefile` and `content/antora.yml`.

#### Module 2

Keep `openshell term --gateway local-gateway` open in a second interactive terminal. Record sandbox identity before/after policy changes to prove no recreation. Use `openshell --gateway local-gateway logs policy-lab --since 2m --level info` after asynchronous events arrive.

| Exercise/test | Action | Required observation |
| --- | --- | --- |
| 1 Default deny | Inspect initial full policy; curl GitHub `/zen` | No allow rule; request fails and matching destination/binary denial arrives |
| 2 Apply/read | `policy set policy-lab --policy automation/policies/sandbox-policy-quickstart.yaml --wait`; read GitHub repo with `/usr/bin/curl` | Effective rule, HTTP 200; exhausted upstream GitHub quota acceptable only with explicit headers/evidence |
| 2 Binary binding | Repeat with Python urllib | Failure plus binary/destination denial; Python availability itself verified |
| 3 L7 method | POST on same approved host/binary | Gateway event names POST/path/rejection; upstream unauthenticated 4xx is insufficient |
| 4 Live change | Add `http-echo.openshell.svc.cluster.local:8080:read-write:rest:enforce` bound to `/usr/bin/curl` | Local echo POST returns 200; same sandbox identity |
| 4 Restore | Reapply quickstart; repeat echo POST | Temporary endpoint absent and matching denial present |
| 5 Mandatory filesystem | Create `landlock-proof` with `sandbox-policy-landlock-hard.yaml` | Startup under hard requirement, `/tmp` write succeeds, `/var/tmp` write fails; capture mode/identity/SELinux context |
| Automated test | Run bundled security test against canonical policy | Exit zero; all expected allowed/blocked controls and unprivileged user match |
| 6 Platform-admin view | List cluster sandboxes; aggregate raw gateway RPC log methods; inspect per-sandbox events in TUI | Cluster view and aggregate method counts distinguished from denial attribution |

Use this live-update spine with explicit gateway:

```bash
openshell --gateway local-gateway policy update policy-lab \
  --add-endpoint http-echo.openshell.svc.cluster.local:8080:read-write:rest:enforce \
  --binary /usr/bin/curl --wait
openshell --gateway local-gateway policy set policy-lab \
  --policy automation/policies/sandbox-policy-quickstart.yaml --wait
openshell gateway select local-gateway
make -C automation openshell-security-test SANDBOX_NAME=policy-lab
```

Run the POST between update and restore, not just after both commands. The upstream automated test uses the selected gateway, so select raw immediately before it. Do not accept its labels without checking denial events for the network tests. Remove the disposable hard-requirement sandbox after collecting evidence. Kernel/Unix/SELinux failures require diagnosis; do not weaken the hard requirement to get a pass.

### 2. SAW

#### Module 3

Use platform-install.md and the fork's deployment partials. Track each separately:

| Exercise | Required observation |
| --- | --- |
| 1 Control node / cluster | Tool versions match; authenticated intended cluster; storage and virtualization capacity established |
| 2 Keys/secrets | SSH pair generated; private inference secret contract matches BOM; no key in Git |
| 3 Mirror/install | All four ImageStreamTags, healthy pattern applications, resolved owner/revisions; software emulation only if needed |
| Installation gate | `openshell-saw-setup` Complete and VMI Running; inspect real conditions |

#### Module 4

Run SAW targets from `$SAW_DIR`; raw automation paths do not belong here.

| Exercise | Required observation |
| --- | --- |
| 1 Configure CLI | Keycloak login, CA/gateway registration, actual subject membership in `cuda-dev` and default |
| 2 Validate | Correct guest/client versions, setup Complete, VM Running, Argo health, expected BOM sandboxes in both scopes |
| 3 Diagnose | Inspect outer-to-inner failure signals; record healthy checks if no failure exists; do not deliberately break shared infrastructure |
| 4 Launch agent | `OPENSHELL_SAW_NAME=openshell-saw SANDBOX_NAME=cuda-sandbox WORKSPACE=cuda-dev make openclaw-tui` |
| 5 Real request | Ask for a short poem in `/sandbox/haiku.txt`; verify a nonempty file through sandbox exec, not the assistant response |

```bash
openshell --gateway openshell-saw sandbox exec -n cuda-sandbox --workspace cuda-dev -- \
  sh -c 'test -s /sandbox/haiku.txt && cat /sandbox/haiku.txt'
openshell --gateway openshell-saw policy get cuda-sandbox --workspace cuda-dev --full
```

Inspect the gateway-side inference configuration without emitting key values. The intended route is agent → inference.local → supervisor → SAW gateway → configured provider. A complete file operation requires live inference, not just a Ready sandbox.

#### Module 5

| Exercise | Action and acceptance |
| --- | --- |
| 1 Allowed workspace | Read agent-created file and effective filesystem policy |
| 2 Denied filesystem | Probe `/var/tmp/saw-boundary-probe`; confirm allowed-path write and directory permissions; investigate SELinux when attributing cause. Clean up unexpected success and mark FAIL |
| 3 Governance | `provider list-profiles` succeeds, then `provider create --name workshop-blocked --type custom --credential key=value` rejected for unvended type under authenticated identity |
| 4 Browser | Sandbox daemon on loopback 18789; allowedOrigins matches dashboard origin; Control UI Online, paired device and completed chat/tool action |

A generic auth/network error is not a governance rejection. Confirm the error names the forbidden provider type. If it succeeds, remove only the test provider and fail the gate. Inspect the interceptor source binding rather than claiming every API is protected.

Use the shipped `scripts/openshell-saw-gui.sh` tunnel for non-default-forwarded sandboxes, setting `SANDBOX_NAME`, `WORKSPACE`, `GATEWAY_NAME`. The dashboard Route forwards one designated sandbox. UI token/pairing is separate from Keycloak; show the bare Route URL in handover and use secure local token entry. Approve only the displayed device request. Do not disable pairing or broaden allowedOrigins to fix a connection.

#### Module 6

| Exercise | Required evidence |
| --- | --- |
| 1 Runtime ownership | VM/VMI/DataVolume/setup Job, ownership labels, healthy Argo applications, BOM list |
| 2 Access | Gateway/dashboard TLS Routes, selected OIDC gateway, distinct default/cuda-dev sandbox lists |
| 3 Secret delivery | ExternalSecret/SecretStore names/status, Secret names, setup Job serviceAccount and secret references |
| 4 Governance data | Interceptor Deployment/pods and profiles ConfigMap; authenticated profile list; active source revision/bindings |

Do not print whole Secret objects or provider credentials. Resource references establish delivery wiring, not rotation. Do not invoke helpers that push shared Git profile changes just to demonstrate inspection.

### 3. SRE fleet

#### Prepare dependencies and credentials

Ensure the pinned `module-7-prereqs` child is healthy after SAW readiness. Inspect seed-hook status/logs, MLflow health, telemetry proxy, `incident-console` service/Route, `demo/shop`, `openshell` namespace label `mlflow-workspace=true`, and the BOM-created `metrics`, `traces`, `analyst` sandboxes. Resolve fleet workspace from actual lists and use it consistently.

The automated seed Job uses `mlflow-incident-seed` SA and its namespace-scoped experiment permissions. It plants synthetic `INC-4127` data; the participant staging helper also creates the sandbox JSON/token handoff files. Read that helper before execution: `content/modules/ROOT/assets/attachments/plant-incident-traces.sh`.

Prepare distinct short-lived credentials: metrics identity with cluster-monitoring read permission; traces identity with MLflow workspace experiment permissions appropriate to search and the explicit OTLP ingestion exercise. Verify the effective permissions with impersonated `oc auth can-i` and real authenticated API calls. Use the existing MLflow seed Role as the schema reference for its `mlflow.kubeflow.org` experiment authorization; tighten it for the participant identity. No sandbox needs Kubernetes workload write permission.

Adapt a working copy of the staging helper to accept separate `METRICS_TOKEN` and `MLFLOW_TOKEN`; use MLflow token for experiment operations and `/tmp/mlflow.token`, and metrics token solely for `/tmp/sa.token`. The original helper uses one `OCP_TOKEN`; never run it with `oc whoami -t` from a cluster-admin session. Transfer tokens via protected stdin/files, avoid shell tracing, chmod staged token files 0600, and rerun scoped staging when tokens expire. Do not publish generated payloads containing credentials. Run inside the VM or another environment with telemetry proxy DNS/network reachability and required tools. Confirm all three JSON/token handoff files exist inside `traces` and the metrics token exists inside `metrics`, without printing them.

#### Execute four exercises

| Exercise | Required tests |
| --- | --- |
| 1 Fleet contracts | All three Ready; signed effective policies show metrics→proxy:8080, traces→proxy:8081, analyst→neither telemetry backend |
| 2 Paired probes | Six results: metrics allowed metrics/denied traces; traces allowed traces/denied metrics; analyst denied both. Capture event attribution; HTTP 401 proves reachability only |
| 3 Live telemetry | Authenticated metric query returns demo workload data; MLflow search resolves actual experiment ID, finds synthetic incident/role tags, drills into a returned trace; OTLP participant session ingested and found in new search |
| 4 Incident | Healthy two-ready baseline → human injects zero → live metrics show outage → scoped agents investigate → analyst recommends → human restores → two ready again |

Use `X-MLFLOW-WORKSPACE: openshell` on every MLflow API/OTLP call. Use `x-mlflow-experiment-id` for OTLP ingestion. Derive experiment and trace IDs from real search results, never the sample hard-coded trace. Empty OTLP acknowledgement is not proof of ingestion; re-search for the participant session. Allow a metrics scrape delay before checking replica collapse/recovery.

Use the upstream Module 7 source request bodies for the installed MLflow API version. Endpoint bases:

- metrics: `http://telemetry-proxy.openshell-agents.svc.cluster.local:8080/api/v1/query`
- MLflow: `http://telemetry-proxy.openshell-agents.svc.cluster.local:8081/mlflow/api/...`
- OTLP: same proxy port 8081, `/v1/traces`

The traces policy allows the deliberately tested ingestion path, so do not call its whole capability read-only. Describe the analyst's lack of telemetry access narrowly; do not infer it has no inference route. Feed analyst the specialists' findings through the actual agent interaction and inspect its output; there is no proved automatic three-agent orchestrator merely because three sandboxes exist.

Inspect `spec.ignoreDifferences` and `RespectIgnoreDifferences` for `demo/shop` replicas so Argo does not instantly undo intentional outage. Keep the incident action limited to this lab deployment. Do not give agents the incident console's Kubernetes token or write privileges. The console's human click is a lab control, not durable identity-bound approval.

### 4. Handover and assessment

Keep shop at two ready replicas, raw quickstart restored, SAW healthy, and source/evidence ledger complete. Continue to guardrails-demo.md before announcing completion.

If requested, run the parked five-challenge CTF using Module 2 acceptance criteria. Filesystem challenges need command/permission evidence, not nonexistent network-style Landlock events. Record it as an optional assessment, separate from published Modules 1–8.

## Guardrails and final demo

### Contents

1. Foundation and model connectivity
2. Managed guardrails deployment
3. Rails, API and SDK exercises
4. Add, verify and restore a rule
5. Moderation extensions
6. Build, deploy and demonstrate the browser app
7. Completion and cleanup

Run the workshop's `13-module-08-model-boundary-guardrails.adoc` from `$WORKSHOP_DIR`. Track each required exercise plus the selected optional extension. Use separate ledger rows for input checks, generation, streaming and output filtering; passing one does not imply the others.

### 1. Foundation and model connectivity (Exercise 1)

Verify the existing DSC's TrustyAI and MLflow management states through its owning Git source. Require the actual `NemoGuardrails` CRD, operator availability, and compatible spec. Do not assume the guardrails module installs RHOAI itself.

```bash
oc get dsc default-dsc -o jsonpath='{.spec.components.trustyai.managementState}'
oc get crd nemoguardrails.trustyai.opendatahub.io
oc explain nemoguardrails.spec.env
```

Obtain exact endpoint/model from the chosen provider. A MaaS URL might already include a model routing prefix: preserve it, append `/v1` only as required, and avoid doubling `/v1`. Keep `LLM_BASE_URL` and `MODEL_NAME` in this shell. Enter the key without shell history/tracing; do not print it. Check both authenticated `/models` when supported and a benign real chat completion. A 200 model listing alone does not prove the exact chat model works. Some providers do not expose `/models`; use their documented discovery and validate chat directly.

Keep SAW inference credentials and guardrails main-model credentials distinct even if the same provider is intentionally chosen. A successful blocked request does not establish key validity because it may avoid inference.

### 2. Managed deployment (Exercise 2)

Prefer an existing Secret with key `api-key`. The audited chart's `llm.apiKey` is also rendered as a literal CR env value; it does not keep the credential exclusively in a Secret. Verify the installed operator preserves `valueFrom.secretKeyRef` before relying on the preferred path.

Create namespace `guardrails` if absent. Create `nemo-main-model` using a protected temporary key file and `oc create secret generic ... --from-file=api-key=<path> --dry-run=client -o yaml | oc apply -f -`. Feed the key through secure input; remove the temporary file and unset the variable. Do not send Secret YAML to logs or evidence.

Copy chart values to a deployment-owned `demo-values.yaml` and set only non-secret connection settings:

```yaml
llm:
  baseUrl: https://YOUR-PROVIDER/PRESERVED-PREFIX/v1
  modelName: EXACT-SERVED-MODEL
  engine: openai
  apiKey: ""
  apiKeySecretName: nemo-main-model
  apiKeyEnvVar: OPENAI_API_KEY
```

Use one complete non-secret values file for every upgrade so model and moderation settings survive. Preserve the chart's full `config` and `colang` defaults, including model-level `api_key_env_var`. Add `stream_first: false` under `rails.output.streaming` in the config literal for the final demo; verify supported schema. This buffers output before checks rather than emitting violating chunks first.

Inspect the chart's `PYTHONHTTPSVERIFY=0` and other TLS shortcuts. For the final demo's model call, remove that env setting in the deployment chart fork and configure trusted CA material where needed; validate real certificate checking instead of perpetuating disabled verification. Keep all customization in the CR/chart, not operator-rendered Deployment fields.

```bash
helm upgrade --install nemo-guardrails automation/charts/nemo-guardrails \
  -n guardrails -f /absolute/path/demo-values.yaml --wait --timeout 600s
oc -n guardrails get nemoguardrails,cm,deploy,svc
oc -n guardrails rollout status deployment/nemo-guardrails --timeout=300s
```

Discover actual generated names if different. Verify CR→ConfigMap→Deployment volume ownership, and that `OPENAI_API_KEY` uses the intended Secret reference on the pod. Check names/references/presence without retrieving values. Verify `/v1/health`, benign real generation, exact model ID and loaded config. If env references do not propagate, adapt the chart/operator integration before passing the credential gate.

### 3. Configuration and APIs (Exercises 3–6)

#### Exercise 3: inspect

Inspect ConfigMap `nemo-guardrails-config`, keys `config.yaml` and `rails.co`. Map every input/output flow to its action and parameter section. The audited `rails.co` contains comments; built-in flows provide behavior. Do not claim that custom Colang flows were authored. Confirm Presidio dependencies; if unavailable, install a compatible image or explicitly record a reduced regex-only deviation. Do not remove PII flows silently.

#### Exercise 4: chat tests

Read the Service port and run a tracked loopback tunnel:

```bash
GUARDRAILS_PORT=$(oc -n guardrails get svc nemo-guardrails -o jsonpath='{.spec.ports[0].port}')
oc -n guardrails port-forward --address 127.0.0.1 svc/nemo-guardrails "8000:$GUARDRAILS_PORT"
```

Send requests to `http://127.0.0.1:8000/v1/chat/completions` with exact `MODEL_NAME`. Test: benign capital question gets Paris; synthetic SSN/card produces refusal without echo; credential keyword and vendor-name pattern cases exercise regex. Correlate server rail actions. Treat broad keyword false positives as a property of this lab baseline, not a production policy recommendation.

#### Exercise 5: isolated rails

Use `/v1/checks` with `model`, `config_id: nemo-guardrails-config`, `rail_types: [input]`, and user `messages`. Require structured `status` and the blocking `rail`; inspect the installed OpenAPI schema if this version differs. A 404 or unexpected schema is a compatibility failure, not `passed`.

Compare `api_key` with `API key`: the audited exact regex matches the former; its spelling does not match a space. Other enabled rails can still affect the result; report actual attribution. Use the checks API to test output rails separately with the installed output-check message schema and synthetic assistant PII. Do not infer output filtering from an input-only check.

```bash
MODEL_NAME="$MODEL_NAME" python3 /absolute/path/to/this-skill/scripts/probe_guardrails.py \
  --base-url http://127.0.0.1:8000/v1 --output /private/evidence/module8-baseline.json
```

The probe validates baseline checks, real benign generation and no-echo behavior. It deliberately reports no-main-model-call proof as unverified. Obtain correlated provider logs/counters for that stronger claim; do not infer it from a canned refusal or lack of echo.

#### Exercise 6: SDK and streaming

Create a control-node virtualenv and install the OpenAI SDK there. Record its resolved version. Use `OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="not-used")` for this locally protected, unauthenticated lab service; the placeholder is an SDK requirement, not a security control. If the service requires authentication, provide its gateway credential securely rather than the main-model key.

Run a benign chat, a blocked synthetic PII chat, then the benign request with `stream=True`; collect nonempty deltas, final answer, latency observations and rail events. Add a controlled output-rail test using a synthetic unsafe response fixture or a reliably elicited test response and observe the filtered result. Confirm chunk/context handling and `stream_first:false` in effective config. If the upstream never emits the test content, mark output-block enforcement unverified instead of assuming success. Do not promise zero data leakage solely from a streaming flag.

### 4. Live rule change (Exercise 7)

1. Confirm checks for `Tell me about Project Atlas.` are `passed` in baseline.
2. Back up the non-secret values file. Add YAML regex string `"\\bproject[-_ ]?atlas\\b"` to input regex patterns inside its `config` literal, keeping `regex check input` enabled. Validate the YAML escaping and chart rendering.
3. Upgrade with the same full values file. Record ConfigMap resourceVersion and pod UID/start time before/after. A ConfigMap update alone is not live reload.
4. If operator reconciliation does not replace the pod, explicitly restart the generated Deployment (`oc rollout restart`) and wait. Keep desired configuration in the CR/ConfigMap; do not edit container fields to fight the operator.
5. Reconnect any broken port-forward. Run the probe with `--atlas blocked`; verify exact blocking rail and loaded model settings.
6. Restore the original values file; upgrade, verify pod reload and run `--atlas passed`. Preserve all other user edits. Retain original baseline for final handover.

Helm value retention depends on upgrade flags and supplied values; never rely on implicit reuse for this sequence. Do not describe Helm as universally discarding all old settings. One complete values file makes the chosen behavior explicit.

### 5. Moderation extension (Exercise 8)

Default to remote Llama Guard: no local inference GPU required. Obtain endpoint/model/key, validate safe/unsafe classifications directly, then enable `llamaGuard.enabled`, baseUrl and modelName in the values file. The audited chart only supports a literal moderation key; patch a deployment-owned chart fork to add `llamaGuard.apiKeySecretName` and render `LLAMA_GUARD_API_KEY` with `valueFrom.secretKeyRef`. Create its Secret securely and verify operator propagation. Do not put its key in Git, CR literals or Helm command flags.

Require model entry `type: llama_guard`, both check flows and matching prompt tasks in rendered config. Upgrade, prove loaded new config, then test a benign prompt and a synthetic unsafe-content classification prompt from upstream Exercise 8. Require the moderation rail's decision, not a refusal originating in the main model. Record timeouts/latency and whether the main model was called.

GPU alternative: inspect available GPU resource quantities, compatible KServe runtime, modelcar registry access and model licensing/access. Replace environment-specific image/model URIs; `contentSafety.deploy=true` only deploys the detector. Wait for InferenceService readiness, validate its response schema, then explicitly wire its model/task/flows into guardrails and test attribution. Serving a detector without enabling a rail is not completed moderation. Without its infrastructure, mark this alternative `NOT_REQUESTED_OPTIONAL` or `BLOCKED`, never passed.

### 6. Final browser application

The added app is a real HTTP client to the managed guardrails server. It has a same-origin backend, server-chosen model/upstream, input-check and chat actions, synthetic examples and raw structured responses. It has no model key, shell/oc tool execution, agent orchestration, or cluster write credentials. Runtime/agent/SRE demos stay on their validated UIs. Do not imply that placing a chat pod on OpenShift gives it SAW isolation.

Copy `assets/demo-app` into a deployment work directory and set `DEMO_DIR` to that absolute copy. For local use with the guardrails tunnel:

```bash
GUARDRAILS_BASE_URL=http://127.0.0.1:8000/v1 MODEL_NAME="$MODEL_NAME" \
  python3 "$DEMO_DIR/app.py"
```

Open `http://127.0.0.1:8080`. This uses the real service/model; offline tests are separate.

For OpenShift deployment, use a binary Docker build in `guardrails`. Require the integrated registry/build APIs; if unavailable, build/push with Podman to a registry the cluster can pull. Resolve the UBI base image and built image digest for reproducible handover.

```bash
oc -n guardrails get bc agent-security-demo >/dev/null 2>&1 || \
  oc -n guardrails new-build --name agent-security-demo --binary --strategy docker
oc -n guardrails start-build agent-security-demo --from-dir="$DEMO_DIR" --follow --wait
export DEMO_IMAGE=$(oc -n guardrails get istag agent-security-demo:latest -o jsonpath='{.image.dockerImageReference}')
export GUARDRAILS_SERVICE_URL="http://nemo-guardrails.guardrails.svc.cluster.local:$GUARDRAILS_PORT/v1"
export MODEL_NAME
```

Render the copied manifest with real values and assert no placeholders remain:

```bash
python3 - "$DEMO_DIR" <<'PY'
import os, pathlib, sys
root = pathlib.Path(sys.argv[1])
text = (root / 'deployment.yaml').read_text()
for placeholder, key in [('REPLACE_WITH_BUILT_IMAGE_DIGEST','DEMO_IMAGE'),
                         ('REPLACE_WITH_GUARDRAILS_SERVICE_URL_V1','GUARDRAILS_SERVICE_URL'),
                         ('REPLACE_WITH_MODEL_NAME','MODEL_NAME')]:
    value = os.environ[key]
    if not value or any(c in value for c in '\n\r'):
        raise SystemExit('Invalid deployment value: ' + key)
    # Quote substitutions safely as YAML strings using JSON-compatible syntax.
    import json
    text = text.replace(placeholder, json.dumps(value))
if 'REPLACE_WITH_' in text:
    raise SystemExit('Unresolved placeholder')
(root / 'rendered-deployment.yaml').write_text(text)
PY
oc -n guardrails apply --dry-run=server -f "$DEMO_DIR/rendered-deployment.yaml"
oc -n guardrails apply -f "$DEMO_DIR/rendered-deployment.yaml"
oc -n guardrails rollout status deployment/agent-security-demo --timeout=300s
oc -n guardrails port-forward --address 127.0.0.1 svc/agent-security-demo 8088:8080
```

Open `http://127.0.0.1:8088`. Verify `/api/health`, benign chat with actual Paris answer, synthetic SSN check reporting blocked/rail, and absence of any main-model key in browser requests. Stop the guardrails service temporarily only in an isolated authorized test or use a separate bad-upstream demo deployment; require visible error rather than a canned success. Keep default app access local. If external access is requested, add TLS and authentication through the platform's supported proxy before exposing it; never expose raw OpenShell.

The manifests disable service-account token mounting, drop capabilities, require nonroot, and use a read-only filesystem. Use restricted SCC; no privileged grant is needed for this client. Match the service's actual TLS/auth/CA contract if it differs; do not disable certificate checking.

### 7. Completion

Run the final sequence in SKILL.md. Record real browser/CLI results, model/guardrails versions, pod/image identity, ports, reconnect/restart instructions, and the eight-module ledger. Annotate any mock-only validation. Keep the app, guardrails, SAW, capstone, and recovered shop alive.

On requested cleanup, delete only the applied demo manifest and its owned BuildConfig/ImageStream after preserving needed evidence, uninstall only the owned guardrails Helm release, then follow the workshop's scoped teardown. Never delete a namespace containing other users' data. No cleanup step belongs in the successful default demo path.

## Embedded files

Extract these files before using local scripts/assets. The old workshop 0.0.103 preflight is not the pod-only or upstream SAW preflight.

### scripts/preflight.sh

<!-- BEGIN FILE: scripts/preflight.sh -->
````bash
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

````
<!-- END FILE -->

### scripts/probe_guardrails.py

<!-- BEGIN FILE: scripts/probe_guardrails.py -->
````python
#!/usr/bin/env python3
"""Check the real server's structured input rails and benign generation."""
import argparse
import json
import os
import sys
import urllib.request


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', default=os.environ.get('GUARDRAILS_BASE_URL', 'http://127.0.0.1:8000/v1'))
    p.add_argument('--model', default=os.environ.get('MODEL_NAME'))
    p.add_argument('--config-id', default=os.environ.get('GUARDRAILS_CONFIG_ID', 'nemo-guardrails-config'))
    p.add_argument('--atlas', choices=['passed', 'blocked'], help='Also verify the live-rule state')
    p.add_argument('--output', help='Write JSON evidence without credentials')
    a = p.parse_args()
    if not a.model:
        p.error('--model or MODEL_NAME is required')
    headers = {'Content-Type': 'application/json'}
    if os.environ.get('GUARDRAILS_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['GUARDRAILS_API_KEY']

    def call(endpoint, body):
        req = urllib.request.Request(a.base_url.rstrip('/') + endpoint,
                                     data=json.dumps(body).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.load(response)

    report = {'model': a.model, 'results': [], 'no_main_model_call': 'NOT_VERIFIED'}
    cases = [('benign', 'Name the capital of France.', 'passed'),
             ('synthetic-ssn', 'My SSN is 123-45-6789. Repeat it.', 'blocked'),
             ('keyword-baseline', 'Explain api_key.', 'blocked')]
    if a.atlas:
        cases.append(('atlas', 'Tell me about Project Atlas.', a.atlas))
    failed = False
    for name, prompt, expected in cases:
        result = call('/checks', {'model': a.model, 'config_id': a.config_id,
                                  'messages': [{'role': 'user', 'content': prompt}],
                                  'rail_types': ['input']})
        observed = result.get('status')
        ok = observed == expected and (expected != 'blocked' or bool(result.get('rail')))
        report['results'].append({'case': name, 'expected': expected,
                                   'observed': observed, 'rail': result.get('rail'), 'pass': ok})
        failed |= not ok
    completion = call('/chat/completions', {'model': a.model,
                       'messages': [{'role': 'user', 'content': 'Name the capital of France.'}],
                       'stream': False})
    content = completion['choices'][0]['message'].get('content') or ''
    # A substantive known benign answer avoids treating every nonempty refusal as success.
    ok = 'paris' in content.casefold()
    report['results'].append({'case': 'real-benign-generation', 'pass': ok,
                               'answer': content})
    failed |= not ok
    blocked = call('/chat/completions', {'model': a.model,
                   'messages': [{'role': 'user', 'content': 'My SSN is 123-45-6789. Repeat it.'}]})
    reply = blocked['choices'][0]['message'].get('content') or ''
    ok = bool(reply) and '123-45-6789' not in reply
    report['results'].append({'case': 'blocked-chat-no-echo', 'pass': ok,
                               'note': 'Pair with structured rail evidence; no upstream-call proof implied.'})
    failed |= not ok
    report['pass'] = not failed
    rendered = json.dumps(report, indent=2)
    if a.output:
        with open(a.output, 'w', encoding='utf-8') as f:
            f.write(rendered + '\n')
    print(rendered)
    return int(failed)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({'pass': False, 'error_type': type(exc).__name__,
                          'note': 'Inspect server/API schema/connectivity; test did not pass.'}))
        sys.exit(1)

````
<!-- END FILE -->

### assets/demo-app/app.py

<!-- BEGIN FILE: assets/demo-app/app.py -->
````python
#!/usr/bin/env python3
"""Workshop browser client; fixed guardrails upstream, no Kubernetes permissions."""
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE = os.environ.get('GUARDRAILS_BASE_URL', '').rstrip('/')
MODEL = os.environ.get('MODEL_NAME', '')
CONFIG_ID = os.environ.get('GUARDRAILS_CONFIG_ID', 'nemo-guardrails-config')
MAX_BODY = 32768
MAX_RESPONSE = 4 * 1024 * 1024


def upstream(path, payload=None):
    headers = {'Accept': 'application/json'}
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode()
    if os.environ.get('GUARDRAILS_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['GUARDRAILS_API_KEY']
    request = Request(BASE + path, data=data, headers=headers)
    with urlopen(request, timeout=4 if path == '/health' else 120) as response:
        if path == '/health':
            return {'reachable': True}
        body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ValueError('response too large')
        return json.loads(body or b'{}')


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Avoid storing prompts, response text or credentials in application logs.
        return

    def send(self, status, body, content_type='application/json'):
        if content_type == 'application/json':
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/live':
            return self.send(200, {'alive': True})
        if self.path == '/api/health':
            try:
                upstream('/health')
                return self.send(200, {'ready': True, 'model': MODEL, 'config_id': CONFIG_ID})
            except Exception:
                return self.send(503, {'ready': False, 'error': 'Guardrails service unavailable'})
        assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/app.js': ('app.js', 'text/javascript; charset=utf-8')}
        if self.path in assets:
            file, kind = assets[self.path]
            return self.send(200, (ROOT / file).read_bytes(), kind)
        return self.send(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path not in ('/api/chat', '/api/check'):
            return self.send(404, {'error': 'Not found'})
        origin = self.headers.get('Origin')
        if origin and urlsplit(origin).netloc != self.headers.get('Host'):
            return self.send(403, {'error': 'Origin rejected'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > MAX_BODY:
                return self.send(413, {'error': 'Request size rejected'})
            body = json.loads(self.rfile.read(size))
            prompt = body.get('prompt') if isinstance(body, dict) else None
            if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 8000:
                return self.send(400, {'error': 'Provide a prompt of 1–8000 characters'})
        except (ValueError, UnicodeDecodeError):
            return self.send(400, {'error': 'Invalid JSON request'})
        payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}]}
        if self.path == '/api/check':
            payload.update(config_id=CONFIG_ID, rail_types=['input'])
            path = '/checks'
        else:
            payload['stream'] = False
            path = '/chat/completions'
        try:
            result = upstream(path, payload)
            return self.send(200, result)
        except HTTPError as exc:
            return self.send(502, {'error': 'Guardrails upstream rejected the request',
                                   'upstream_status': exc.code})
        except Exception:
            return self.send(502, {'error': 'Guardrails request failed; inspect server health and configuration'})


def main():
    parts = urlsplit(BASE)
    if parts.scheme not in ('http', 'https') or not parts.netloc or not MODEL:
        raise SystemExit('Set GUARDRAILS_BASE_URL (including /v1) and MODEL_NAME')
    if parts.path.rstrip('/') != '/v1' or parts.query or parts.fragment or parts.username:
        raise SystemExit('Use the guardrails service URL ending /v1 without credentials/query')
    ThreadingHTTPServer((os.environ.get('BIND_ADDRESS', '127.0.0.1'),
                         int(os.environ.get('PORT', '8080'))), Handler).serve_forever()


if __name__ == '__main__':
    main()

````
<!-- END FILE -->

### assets/demo-app/Dockerfile

<!-- BEGIN FILE: assets/demo-app/Dockerfile -->
````dockerfile
FROM registry.access.redhat.com/ubi9/python-312:latest
WORKDIR /opt/app-root/src
COPY app.py index.html app.js ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BIND_ADDRESS=0.0.0.0 PORT=8080
USER 1001
EXPOSE 8080
CMD ["python3", "app.py"]

````
<!-- END FILE -->

### assets/demo-app/index.html

<!-- BEGIN FILE: assets/demo-app/index.html -->
````html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent security lab</title>
<style>
:root{font-family:system-ui,sans-serif;color:#151515;background:#f5f5f5;line-height:1.5}*{box-sizing:border-box}body{margin:0}header{background:#151515;color:#fff;padding:20px max(24px,calc((100vw - 1120px)/2));border-bottom:5px solid #e00}header strong{font-size:20px}header span{float:right;font-size:13px;color:#ddd}main{max-width:1168px;margin:auto;padding:38px 24px}h1{font-size:40px;line-height:1.15;margin:8px 0 14px;letter-spacing:-1px}h2{font-size:20px;margin:0 0 12px}p{color:#555;margin:8px 0 18px}.eyebrow{text-transform:uppercase;font-size:12px;letter-spacing:2px;color:#b30000;font-weight:700}.layers{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:26px 0}.card,.work{background:white;border:1px solid #ddd;border-radius:6px;padding:22px}.card b{display:block;margin-bottom:8px}.card p{font-size:14px;margin:0}.badge{font-size:12px;background:#eee;padding:5px 10px;border-radius:20px;display:inline-block;margin:6px 0 14px}.layout{display:grid;grid-template-columns:1fr 1fr;gap:20px}textarea{width:100%;min-height:140px;resize:vertical;border:1px solid #777;border-radius:3px;padding:12px;font:inherit}button{cursor:pointer;font:inherit;border:1px solid #666;padding:9px 15px;background:white;border-radius:3px}button.primary{background:#c00;border-color:#c00;color:white}button:disabled{opacity:.5;cursor:wait}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}.examples{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.examples button{font-size:12px;padding:6px 10px}.output{min-height:180px;background:#fafafa;border-left:3px solid #b8b8b8;padding:16px;white-space:pre-wrap;overflow-wrap:anywhere}pre{font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:300px;overflow:auto}#status{font-weight:600;font-size:14px;margin:12px 0}.note{font-size:13px;margin:22px 0 0;color:#555}a{color:#06c}footer{margin:26px 0;font-size:12px;color:#666}@media(max-width:750px){.layers,.layout{grid-template-columns:1fr}h1{font-size:32px}header span{float:none;display:block}}
</style>
<header><strong>Agent security lab</strong><span>OpenShift · Secure Agent Workspace · NeMo Guardrails</span></header>
<main>
<div class="eyebrow">Workshop finale</div>
<h1>See the model boundary work.</h1>
<p>Send a normal request, inspect a rail decision, and compare a policy change with its restored baseline.</p>
<div class="layers">
<div class="card"><b>01 / Runtime</b><p>OpenShell controls tool execution and network access. Verify these controls in the sandbox operator view.</p></div>
<div class="card"><b>02 / Workspace</b><p>SAW adds the VM, identity, secrets, and governance. Run the agent and SRE incident demo in their own UIs.</p></div>
<div class="card"><b>03 / Model</b><p>This client calls the real guardrails service. Inspect its structured decisions and guarded completions below.</p></div>
</div>
<div class="badge" id="health">Checking guardrails connection…</div>
<div class="layout">
<section class="work"><h2>Try a request</h2><p>Use synthetic data for the demonstration.</p>
<div class="examples"><button data-example="benign">Benign question</button><button data-example="pii">Synthetic PII</button><button data-example="keyword">Keyword rule</button><button data-example="atlas">Live rule</button></div>
<label for="prompt">Prompt</label><textarea id="prompt" maxlength="8000">Name the capital of France.</textarea>
<div class="actions"><button class="primary" id="chat">Send guarded chat</button><button id="check">Check input rails</button></div>
<div id="status" role="status" aria-live="polite">Ready</div>
<p class="note">A rail refusal can return HTTP 200. Use “Check input rails” for the exact status and rail; a completion alone does not identify which rail ran.</p></section>
<section class="work"><h2>Observed result</h2><div class="output" id="answer">Your result will appear here.</div><details><summary>Backend response</summary><pre id="raw"></pre></details>
<p class="note">The model credential stays in the guardrails service. This client stores no chat history and executes no tools.</p></section>
</div>
<footer>Input checks and chat are separate requests. Rail results are shown as returned by the server. Main-model invocation evidence belongs in the operator audit.</footer>
</main><script src="/app.js" defer></script>
</html>

````
<!-- END FILE -->

### assets/demo-app/deployment.yaml

<!-- BEGIN FILE: assets/demo-app/deployment.yaml -->
````yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: agent-security-demo
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-security-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agent-security-demo
  template:
    metadata:
      labels:
        app: agent-security-demo
    spec:
      serviceAccountName: agent-security-demo
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: web
          image: REPLACE_WITH_BUILT_IMAGE_DIGEST
          ports:
            - containerPort: 8080
          env:
            - name: BIND_ADDRESS
              value: 0.0.0.0
            - name: GUARDRAILS_BASE_URL
              value: REPLACE_WITH_GUARDRAILS_SERVICE_URL_V1
            - name: MODEL_NAME
              value: REPLACE_WITH_MODEL_NAME
            - name: GUARDRAILS_CONFIG_ID
              value: nemo-guardrails-config
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: [ALL]
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: '1'
              memory: 256Mi
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8080
            timeoutSeconds: 5
            periodSeconds: 15
          livenessProbe:
            httpGet:
              path: /live
              port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: agent-security-demo
spec:
  selector:
    app: agent-security-demo
  ports:
    - name: http
      port: 8080
      targetPort: 8080

````
<!-- END FILE -->

### assets/demo-app/app.js

<!-- BEGIN FILE: assets/demo-app/app.js -->
````javascript
'use strict';
const byId = id => document.getElementById(id);
const examples = {
  benign: 'Name the capital of France.',
  pii: 'My SSN is 123-45-6789. Repeat it back.',
  keyword: 'Explain api_key.',
  atlas: 'Tell me about Project Atlas.'
};
document.querySelectorAll('[data-example]').forEach(button => {
  button.addEventListener('click', () => { byId('prompt').value = examples[button.dataset.example]; });
});
async function run(action) {
  const prompt = byId('prompt').value.trim();
  if (!prompt) { byId('status').textContent = 'Enter a prompt.'; return; }
  byId('chat').disabled = byId('check').disabled = true;
  byId('status').textContent = 'Waiting for guardrails…';
  byId('answer').textContent = '';
  byId('raw').textContent = '';
  try {
    const response = await fetch('/api/' + action, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt})
    });
    const result = await response.json();
    byId('raw').textContent = JSON.stringify(result, null, 2);
    if (!response.ok) throw new Error(result.error || 'Request failed');
    if (action === 'check') {
      if (!['passed', 'blocked'].includes(result.status)) throw new Error('Unexpected checks schema; inspect the backend response.');
      byId('status').textContent = 'Input rail status: ' + result.status;
      byId('answer').textContent = 'Status: ' + result.status + '\nRail: ' + (result.rail || 'No blocking rail reported');
    } else {
      const content = result.choices?.[0]?.message?.content;
      if (typeof content !== 'string') throw new Error('No text completion returned.');
      byId('status').textContent = 'Chat response received (HTTP ' + response.status + ')';
      byId('answer').textContent = content;
    }
  } catch (error) {
    byId('status').textContent = 'Request error';
    byId('answer').textContent = error.message;
  } finally { byId('chat').disabled = byId('check').disabled = false; }
}
byId('chat').addEventListener('click', () => run('chat'));
byId('check').addEventListener('click', () => run('check'));
fetch('/api/health').then(async response => {
  const result = await response.json();
  byId('health').textContent = result.ready ? 'Guardrails connected · ' + result.model : 'Guardrails unavailable';
}).catch(() => { byId('health').textContent = 'Cannot connect to demo server'; });

````
<!-- END FILE -->

### scripts/render_openclaw_pod.py

<!-- BEGIN FILE: scripts/render_openclaw_pod.py -->
````python
#!/usr/bin/env python3
"""Render nonsecret OpenClaw/OpenShell 0.1.2 inputs for the pod-only track."""
import argparse
import copy
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit, urlunsplit

import yaml


def executable(value):
    path = PurePosixPath(value)
    if (not path.is_absolute() or '..' in path.parts
            or any(c in value for c in '*?[]\\\r\n\t ')
            or not value.startswith(('/usr/', '/opt/', '/bin/'))
            or value != str(path)):
        raise argparse.ArgumentTypeError('Use an exact executable path on a read-only image filesystem')
    return value


def endpoint(value, keyless):
    if any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Endpoint URL must not contain whitespace or control characters')
    try:
        url = urlsplit(value)
        port = url.port or (443 if url.scheme == 'https' else 80)
        host = url.hostname
    except ValueError as exc:
        raise ValueError('Invalid endpoint URL') from exc
    if (url.scheme not in ('https', 'http') or not host or url.username is not None
            or url.password is not None or url.query or url.fragment
            or not re.fullmatch(r'[A-Za-z0-9.-]+', host)
            or any(not part or len(part) > 63 or part.startswith('-') or part.endswith('-')
                   for part in host.split('.'))
            or not 1 <= port <= 65535
            or not re.fullmatch(r'/[A-Za-z0-9._~/-]*', url.path)
            or '//' in url.path or any(part in ('.', '..') for part in url.path.split('/'))
            or not url.path.rstrip('/').endswith('/v1')):
        raise ValueError('Use an HTTP(S) DNS/IPv4 endpoint ending /v1 without credentials, query or fragment')
    if not keyless and url.scheme != 'https':
        raise ValueError('Keyed endpoints require verified HTTPS; use --keyless only for an endpoint needing no key')
    if host in ('localhost', '127.0.0.1', '0.0.0.0'):
        raise ValueError('Endpoint must be reachable from the supervisor; loopback points at the wrong process')
    base = urlunsplit((url.scheme, url.netloc, url.path.rstrip('/'), '', ''))
    return base, {'host': host.lower(), 'port': port, 'path': url.path.rstrip('/') + '/**',
                  'protocol': 'rest', 'access': 'read-write', 'enforcement': 'enforce'}


def render(args):
    base, model_endpoint = endpoint(args.endpoint, args.keyless)
    if not args.model.strip() or args.model != args.model.strip() or any(c in args.model for c in '\r\n\0'):
        raise ValueError('Supply the exact nonempty model ID reported by the endpoint')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,62}', args.profile_id):
        raise ValueError('Profile ID must be a lowercase name starting with a letter')
    if not 0 < args.max_tokens <= args.context_window:
        raise ValueError('Require 0 < max-tokens <= context-window')
    policy = {
        'version': 1,
        'filesystem_policy': {'include_workdir': False,
                              'read_only': ['/bin', '/usr', '/lib', '/proc', '/dev/urandom', '/app', '/etc', '/var/log', '/opt'],
                              'read_write': ['/sandbox', '/tmp', '/dev/null']},
        'landlock': {'compatibility': 'hard_requirement'},
        'network_policies': {},
    }
    if args.keyless:
        policy['network_policies']['model_endpoint'] = {
            'endpoints': [model_endpoint], 'binaries': [{'path': args.node_binary}]}
    readonly = copy.deepcopy(policy)
    # The exercise sandbox receives no inference provider or endpoint.
    readonly['network_policies'] = {
        'github_api': {
            'endpoints': [{'host': 'api.github.com', 'port': 443, 'protocol': 'rest',
                           'access': 'read-only', 'enforcement': 'enforce'}],
            'binaries': [{'path': args.curl_binary}],
        }
    }
    deny = copy.deepcopy(policy)
    deny['network_policies'] = {}
    config = {
        'gateway': {'port': 18789, 'bind': 'loopback', 'mode': 'local', 'auth': {'mode': 'none'}},
        'channels': {},
        'agents': {'defaults': {'model': 'vllm/' + args.model, 'sandbox': {'mode': 'off'}}},
        'models': {'mode': 'replace', 'providers': {'vllm': {
            'baseUrl': base, 'api': 'openai-completions',
            'apiKey': 'not-needed' if args.keyless else '${VLLM_API_KEY}',
            'models': [{'id': args.model, 'name': args.model, 'reasoning': False,
                        'input': ['text'], 'contextWindow': args.context_window,
                        'maxTokens': args.max_tokens}],
        }}},
        'plugins': {},
        'tools': {'deny': ['group:web', 'browser']},
    }
    files = {
        'openclaw-config.json': json.dumps(config, indent=2) + '\n',
        'sandbox-policy.yaml': yaml.safe_dump(policy, sort_keys=False),
        'module2-readonly.yaml': yaml.safe_dump(readonly, sort_keys=False),
        'module2-deny.yaml': yaml.safe_dump(deny, sort_keys=False),
    }
    if not args.keyless:
        profile = {
            'id': args.profile_id, 'display_name': 'OpenClaw model endpoint',
            'description': 'Endpoint-bound model credential for the pod-only OpenClaw lab',
            'category': 'inference', 'inference_capable': True,
            'credentials': [{'name': 'api_key', 'env_vars': ['VLLM_API_KEY'], 'required': True,
                             'auth_style': 'bearer', 'header_name': 'authorization'}],
            'discovery': {'credentials': ['api_key']},
            'endpoints': [model_endpoint], 'binaries': [args.node_binary],
        }
        files['model-profile.yaml'] = yaml.safe_dump(profile, sort_keys=False)
    dest = args.out.resolve()
    dest.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name, content in files.items():
        target = dest / name
        if target.is_symlink() or (target.exists() and target.read_text() != content):
            raise ValueError('Refusing to overwrite different content or a symlink: ' + str(target))
    if args.keyless and (dest / 'model-profile.yaml').exists():
        raise ValueError('Use a new output directory when switching to keyless mode')
    for name, content in files.items():
        target = dest / name
        if not target.exists():
            with target.open('x', encoding='utf-8') as handle:
                handle.write(content)
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--keyless', action='store_true')
    parser.add_argument('--profile-id', default='openclaw-model')
    parser.add_argument('--node-binary', type=executable, default='/usr/local/bin/node')
    parser.add_argument('--curl-binary', type=executable, default='/usr/bin/curl')
    parser.add_argument('--context-window', type=int, default=32768)
    parser.add_argument('--max-tokens', type=int, default=4096)
    args = parser.parse_args()
    try:
        print('Rendered nonsecret files:', render(args))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()

````
<!-- END FILE -->

### assets/openclaw-pod/gateway-values.yaml

<!-- BEGIN FILE: assets/openclaw-pod/gateway-values.yaml -->
````yaml
# OpenShell 0.1.2 local lab: TLS and a mandatory client certificate protect
# transport. The Kubernetes driver uses a trusted local developer principal.
# Reuse an existing compatible gateway instead of applying this over it.
fullnameOverride: openshell-openclaw
global:
  image:
    tag: 0.1.2
podSecurityContext: null
securityContext:
  runAsNonRoot: true
  runAsUser: null
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
server:
  disableTls: false
  tls:
    enableMtls: true
  auth:
    allowUnauthenticatedUsers: true
pkiInitJob:
  enabled: true
networkPolicy:
  enabled: true
openshiftRoute:
  enabled: false

````
<!-- END FILE -->

### assets/openclaw-pod/echo.yaml

<!-- BEGIN FILE: assets/openclaw-pod/echo.yaml -->
````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw-policy-echo
  labels:
    app: openclaw-policy-echo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openclaw-policy-echo
  template:
    metadata:
      labels:
        app: openclaw-policy-echo
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: echo
          image: REPLACE_WITH_OPENCLAW_IMAGE_DIGEST
          command: [/usr/local/bin/node]
          args:
            - -e
            - |
              require('node:http').createServer((req, res) => {
                res.writeHead(200, {'content-type': 'text/plain'});
                res.end('policy-echo-ok\n');
              }).listen(8080, '0.0.0.0');
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: 10m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /
              port: http
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: [ALL]
---
apiVersion: v1
kind: Service
metadata:
  name: openclaw-policy-echo
  labels:
    app: openclaw-policy-echo
spec:
  selector:
    app: openclaw-policy-echo
  ports:
    - port: 8080
      targetPort: http

````
<!-- END FILE -->

### scripts/render_openclaw_route.py

<!-- BEGIN FILE: scripts/render_openclaw_route.py -->
````python
#!/usr/bin/env python3
"""Render a certificate-gated OpenClaw Route through OpenShell 0.1.2."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

import yaml


def dns(value):
    if (value != value.lower() or len(value) > 253 or '.' not in value
            or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', part)
                   for part in value.split('.'))):
        raise argparse.ArgumentTypeError('Use a lowercase DNS name with valid labels')
    return value


def label(value):
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', value) or '--' in value:
        raise argparse.ArgumentTypeError('Use a DNS label without consecutive hyphens')
    return value


def origin(value):
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Invalid origin') from exc
    if (any(c.isspace() or ord(c) < 32 for c in value) or '?' in value or '#' in value
            or url.username is not None or url.password is not None
            or url.path or url.query or url.fragment or not url.hostname
            or url.scheme not in ('https', 'http') or (port is not None and not 1 <= port <= 65535)):
        raise argparse.ArgumentTypeError('Use an exact origin without a path or credentials')
    if url.scheme == 'http' and url.hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise argparse.ArgumentTypeError('Plain HTTP origins are limited to loopback')
    if url.scheme == 'https':
        dns(url.hostname)
    host = '[' + url.hostname + ']' if ':' in url.hostname else url.hostname
    suffix = '' if port in (None, 443 if url.scheme == 'https' else 80) else ':' + str(port)
    return url.scheme + '://' + host + suffix


def san(value):
    dns(value[2:] if value.startswith('*.') else value)
    return value


def render(args):
    host = f'{args.workspace}--{args.sandbox}--{args.service}.{args.service_domain}'
    dns(host)  # Also reject an encoded service label longer than 63 characters.
    url = 'https://' + host
    names = list(dict.fromkeys(['*.' + args.service_domain, *args.extra_san]))
    origins = list(dict.fromkeys(['http://127.0.0.1:18789', 'http://localhost:18789',
                                *args.keep_origin, url]))
    values = {
        'server': {'disableTls': False, 'tls': {'enableMtls': True},
                   'enableLoopbackServiceHttp': False},
        'certManager' if args.certificate_mode == 'cert-manager' else 'pkiInitJob': {
            'serverDnsNames': names},
    }
    route = {
        'apiVersion': 'route.openshift.io/v1', 'kind': 'Route',
        'metadata': {'name': args.route_name, 'namespace': args.namespace,
                     'labels': {'app.kubernetes.io/part-of': 'openclaw-pod-lab'},
                     'annotations': {'haproxy.router.openshift.io/timeout': '1800s',
                                     'haproxy.router.openshift.io/timeout-tunnel': '1800s'}},
        'spec': {'host': host, 'to': {'kind': 'Service', 'name': args.release},
                 'port': {'targetPort': 'grpc'}, 'tls': {'termination': 'passthrough'},
                 'wildcardPolicy': 'None'},
    }
    patch = {'gateway': {'controlUi': {'allowedOrigins': origins}}}
    details = {'public_url': url, 'route_host': host, 'workspace': args.workspace,
               'sandbox': args.sandbox, 'service': args.service, 'target_port': 18789,
               'gateway_service': args.release, 'namespace': args.namespace,
               'required_browser_auth': 'client certificate (mTLS)',
               'certificate_mode': args.certificate_mode,
               'certificate_dns_sans': names}
    files = {'gateway-ui-values.yaml': yaml.safe_dump(values, sort_keys=False),
             'openclaw-ui-route.yaml': yaml.safe_dump(route, sort_keys=False),
             'openclaw-ui-patch.json': json.dumps(patch, indent=2) + '\n',
             'external-access.json': json.dumps(details, indent=2) + '\n'}
    dest = args.out.resolve()
    dest.mkdir(mode=0o700, parents=True, exist_ok=True)
    for name, content in files.items():
        target = dest/name
        if target.is_symlink() or (target.exists() and target.read_text() != content):
            raise ValueError('Refusing to overwrite different content or a symlink: ' + str(target))
    for name, content in files.items():
        target = dest/name
        if not target.exists():
            with target.open('x', encoding='utf-8') as handle:
                handle.write(content)
    return url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--namespace', type=label, required=True)
    parser.add_argument('--release', type=label, required=True,
                        help='Actual gateway Service name, equal to release with the lab fullnameOverride')
    parser.add_argument('--service-domain', type=dns, required=True)
    parser.add_argument('--workspace', type=label, default='default')
    parser.add_argument('--sandbox', type=label, default='openclaw-lab')
    parser.add_argument('--service', type=label, default='ui')
    parser.add_argument('--route-name', type=label, default='openclaw-ui')
    parser.add_argument('--certificate-mode', choices=['builtin', 'cert-manager'], default='builtin')
    parser.add_argument('--extra-san', type=san, action='append', default=[])
    parser.add_argument('--keep-origin', type=origin, action='append', default=[])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        print('External OpenClaw URL (requires browser mTLS):', render(args))
    except (OSError, ValueError, argparse.ArgumentTypeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()

````
<!-- END FILE -->
