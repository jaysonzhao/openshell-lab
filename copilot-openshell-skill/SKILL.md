---
name: add-copilot-to-openshell
description: Add and use GitHub Copilot CLI as a new sandbox on an already deployed OpenShell pod gateway on OpenShift or Kubernetes. Use to reuse the existing gateway, install or verify a compatible Copilot image, configure endpoint-bound authentication and explicit egress, run interactive or one-off prompts, transfer files, resume sessions, demonstrate coding and tests, inspect audit events, validate containment, and remove only added resources. Supports the workshop OpenShell 0.0.103 baseline and version-gated adaptation for newer gateways.
---

# Add GitHub Copilot CLI to an OpenShell Pod Gateway

## Single-file preparation

This portable edition combines the full deployment workflow, daily usage, validation, research sources, scripts, container recipe, and coding demo in one file. Read the combined sections directly. No separate reference download is required.

Before executing commands that refer to scripts or assets, extract the five embedded runtime files with Python 3. Replace both paths below with actual paths. Use a new destination directory, then set `SKILL_DIR` to it. The installed skill is not changed by making this download.

```bash
python3 - /path/to/SKILL.md /path/to/copilot-openshell-skill <<'PYEXTRACT'
from pathlib import Path, PurePosixPath
import re, sys
src, root = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8")
root.mkdir(parents=True, exist_ok=True)
root = root.resolve()
pattern = r"<!-- BEGIN FILE: ([^\n]+) -->\n````[^\n]*\n(.*?)\n````\n<!-- END FILE -->"
files = re.findall(pattern, text, re.S)
if len(files) != 5:
    raise SystemExit("Expected exactly five embedded runtime files")
pending = [(root / "SKILL.md", text)]
for relative, content in files:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or path.parts[0] not in ("scripts", "assets"):
        raise SystemExit("Invalid embedded path")
    target = root.joinpath(*path.parts)
    if root not in target.resolve().parents:
        raise SystemExit("Embedded path escapes destination")
    pending.append((target, content))
for target, content in pending:
    if target.exists() and target.read_text(encoding="utf-8") != content:
        raise SystemExit("Refusing to overwrite different content: " + str(target))
for target, content in pending:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    if target.suffix == ".py" and target.parent.name == "scripts":
        target.chmod(0o755)
print("Ready:", root)
PYEXTRACT
export SKILL_DIR=/path/to/copilot-openshell-skill
```

Runtime prerequisites remain the authenticated OpenShift/OpenShell tools described below; the policy renderer also needs Python 3 with PyYAML. Substitute this extracted directory wherever a command says `/absolute/path/to/this-skill` or `/absolute/path/to/installed-skill`.

## Combined contents

- [Core workflow](#core-workflow)
- [Deployment procedure](#deployment)
- [Daily usage](#usage)
- [Validation, demonstration and rollback](#validation)
- [Research and primary sources](#research)
- [Embedded scripts and demo files](#embedded-files)

## Core workflow

Add one new Copilot sandbox to the deployed pod gateway. Reuse its operator, Service, storage, gateway registration and cluster. Install the agent inside the sandbox image; the gateway remains the control plane. Keep existing OpenClaw and policy-lab sandboxes intact.

## Load resources

- Read [Research section](#research) for primary-source findings and audited versions.
- Follow [Deployment section](#deployment) for image inspection/build, profile import, credentials and sandbox creation.
- Follow [Validation section](#validation) for the real coding demonstration, diagnostics, evidence and rollback.
- Read [Usage section](#usage) for copy-and-paste daily usage: interactive chat, one-off requests, file upload/download, edits/tests, session resume, and operator audit views.
- Run `scripts/render_config.py` to generate a dedicated provider profile and matching sandbox policy without contacting or changing a cluster.
- Run `scripts/verify_addon.py` against the named sandbox after deployment. Add `--model-smoke` only when ready to validate live inference.
- Copy `assets/Dockerfile` when an agent image must be built; use `assets/demo/` as the small coding exercise.

## Establish the existing target

Default names from the earlier workshop: namespace `openshell`, Service `openshell`, registered gateway `local-gateway`, workspace `default`, new sandbox `copilot-lab`, new provider `copilot-token`, custom profile ID `copilot-cli`. Treat these as defaults to verify, never as proof that a gateway exists.

Inspect before any mutation:

```bash
oc whoami
oc whoami --show-server
oc -n openshell get statefulset,pods,svc,pvc
openshell --version
openshell gateway list
openshell --gateway local-gateway --workspace default status
openshell --gateway local-gateway --workspace default sandbox list
```

If the original local tunnel is unavailable, inspect Service endpoints/ports and start an owned loopback tunnel in another terminal:

```bash
oc -n openshell port-forward --address 127.0.0.1 svc/openshell 8080:8080
```

Register the existing endpoint only if its registration is absent. Do not replace another `local-gateway` registration silently. The raw workshop gateway is unauthenticated HTTP; keep it internal and reach it through loopback forwarding. Do not install a new gateway or expose this gateway with a Route.

Record the target cluster, gateway pod/image/version, CLI version, selected workspace, and existing sandbox/provider inventory. The CLI baseline is `0.0.103`, matching raw gateway `0.0.103`. For another version, inspect its own `--help` and versioned documentation before adapting commands. Do not upgrade the gateway or enable global provider settings to add this agent.

Use explicit gateway and workspace on every lifecycle, provider, policy and exec command. If several gateways are plausible and the intended target cannot be identified, prepare the deployment assets and ask only for the target selection before mutation.

## Select the image and discover the binary

OpenShell's community base image documents Copilot as preinstalled, but verify the selected image. Start a disposable, provider-free probe on this gateway with a generated policy; run `copilot --version`, `copilot --help`, `command -v copilot`, `readlink -f` and native package-path inspection. Record actual executable paths and CPU architecture.

Prefer a compatible digest-pinned base image already used by this gateway. The earlier workshop candidate is:

```text
ghcr.io/nvidia/openshell-community/sandboxes/base@sha256:aeef1c63f00e2913ea002ccb3aaf925f338b5c5d70e63576f0d95c16a138044e
```

This digest identifies the candidate image, not a verified Copilot version in the user's cluster. If the image lacks Copilot or has an unsuitable release, build a derived image with the bundled Dockerfile. The audited fallback install pins `@github/copilot@1.0.105`; npm installation requires Node.js >=22. Build/push from the control node or an OpenShift binary build and use the resulting registry digest. Do not run package installation on the gateway pod or grant runtime npm/apt access just to install the agent.

Never use `--from .` for a remote gateway unless its driver explicitly supports that local-build path. The Kubernetes driver needs an image reference pullable by its nodes.

## Generate the dedicated policy/profile

Use GitHub subscription-based service routing appropriate to the account. `common` selects `api.githubcopilot.com`; `individual`, `business` and `enterprise` select their respective exact tier host. Do not add common/fallback hosts when the enterprise intentionally restricts subscription tiers.

```bash
python3 /absolute/path/to/this-skill/scripts/render_config.py \
  --out ./copilot-addon --route common \
  --binary /ACTUAL/READONLY/PATH/TO/COPILOT
```

Pass repeated `--binary` values for the observed native executable and launcher. Bind `/usr/bin/node` only if the chosen installation actually uses Node for outbound requests. Avoid writable executable paths and broad `/**` binary grants. The generator enables the selected Copilot API endpoint and read-only GitHub authentication/user-management API paths. It excludes Git push and separate package, telemetry, experimentation and update hosts. Disable built-in MCP in the client launch; the Copilot service host grant is not an RPC-level restriction on every API served at that host.

The dedicated `copilot-cli` profile includes the credential's endpoint bindings as well as discovery metadata. A network allow rule alone does not authorize placeholder resolution. A profile alone does not grant network access when provider policy composition is disabled. Explicitly apply the generated sandbox policy, leaving the existing global provider-mode setting unchanged.

Some client releases need additional documented hosts/paths. Use a denied event and the version's official documentation to justify each exact addition. Update both credential binding and network policy when authentication requires it; leave `tls: terminate` for inspected credential-bearing HTTPS. Never fix a placeholder problem with `tls: skip` or disabled certificate validation.

## Authenticate through a provider

For the container workflow, default to a personal-account fine-grained GitHub token with the **Copilot Requests** account permission, an eligible Copilot plan, and organization policy allowing CLI use. Classic PATs are not supported by current Copilot CLI. A generic Actions `GITHUB_TOKEN` or an existing Git-operation token is not automatically suitable.

Use `COPILOT_GITHUB_TOKEN` as the dedicated credential. Read it securely into the control-node environment or the gateway's supported secret-driver integration. Use the bare-key form `--credential COPILOT_GITHUB_TOKEN`; do not put the token value in argv, YAML, an image layer, a shell transcript, or `sandbox --env`. The gateway provides a placeholder to the agent and resolves it on matching outbound HTTP requests. Do not claim this property was verified until the real provider-backed request succeeds and the sandbox-value test passes.

Use a custom workspace-scoped `copilot-cli` profile to avoid mutating the built-in profile and to include required authentication endpoints/binary paths. Import it using this version's command. On `0.0.103`, use `provider profile lint -f`, then `provider profile import -f`. If a same-ID custom profile or same-name provider exists, inspect it and compare required fields; reuse only a matching intended resource. Do not overwrite or delete it to make an install rerun succeed.

## Create and launch the new sandbox

Follow the Deployment section to import the profile and create the provider first. Then:

```bash
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" sandbox create \
  --name "$SANDBOX" --from "$COPILOT_IMAGE" \
  --provider "$PROVIDER" --no-auto-providers \
  --policy "$ADDON_DIR/copilot-policy.yaml" \
  --env HOME=/sandbox \
  --env COPILOT_HOME=/sandbox/.copilot \
  --env COPILOT_CACHE_HOME=/sandbox/.cache/copilot \
  --env XDG_CONFIG_HOME=/sandbox/.config \
  --env XDG_CACHE_HOME=/sandbox/.cache \
  --env COPILOT_AUTO_UPDATE=false \
  --no-tty -- true
```

Use `GATEWAY`, `WORKSPACE`, `SANDBOX`, `PROVIDER`, `COPILOT_IMAGE` and `ADDON_DIR` from the verified deployment inputs. Check that the new name is unused first. Existing same-name state requires inspection/adoption, not automatic recreation. Poll exec readiness with a bounded timeout, then inspect effective policy and provider metadata.

Launch the terminal UI through this gateway:

```bash
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" sandbox exec \
  -n "$SANDBOX" --workdir /sandbox --tty -- \
  copilot --no-auto-update --disable-builtin-mcps
```

Check the installed Copilot help before using those flags. Keep its normal tool approvals. Do not use `--allow-all`, `--allow-all-tools`, `--yolo`, or broad path/URL approvals for the demonstration. Use only synthetic code/context intended for the selected inference service.

## Validate and demonstrate

Run the verifier and the full the Validation section sequence. Require:

1. Existing gateway pod identity and unrelated sandbox inventory remain unchanged.
2. Copilot runs as the sandbox user in the new pod, with the recorded version/image digest and effective policy.
3. Live provider-backed prompt returns `COPILOT_GATEWAY_OK`; success is more than `copilot --version`.
4. Sandbox credential is present but differs from the real control-node token, checked with a boolean result without printing either value.
5. An approved sandbox-path write succeeds; an outside-path write fails with appropriate attribution.
6. A request to an undeclared host fails with a matching OpenShell denial. Curl cannot use the Copilot-only endpoint; the Copilot process can complete a real request.
7. Copilot fixes the bundled calculator defect; tests pass, original test-file checksum is unchanged, and an independent operator check verifies the result.

Observe `openshell term` or per-sandbox logs beside Copilot's terminal UI. Record destination, binary and decision for network claims. HTTP 401/403 can mean an allowed connection with failed auth; a nonzero command alone does not prove enforcement. Landlock filesystem denials need not emit a runtime network event; rule out ordinary permissions/SELinux before attributing the cause.

Modern Copilot also has optional local sandboxing. Inspect its configured state if it blocks startup in the container; do not grant privileged SCC, host mounts, or bypass enterprise managed policy to accommodate nested sandboxing. OpenShell and Copilot permission settings are separate layers.

## Handover and scoped removal

Leave the working add-on running. Deliver gateway/workspace/name, image/Copilot versions, effective profile and policy paths, authentication/rotation method, the Usage section with verified target names, coding-demo steps, actual results, remaining gaps and owned-resource rollback commands. Include at least an interactive launch, one-off prompt, code-edit/test, resume, file export, and audit-view example. Never claim a live deployment when only offline tests ran.

On requested removal, export the demo workspace, delete only the added sandbox, then remove its provider if no other sandbox uses it. Remove the custom profile only after confirming it is unreferenced. Stop only this run's owned tunnel and remove only its dedicated build/image objects when requested. Preserve the gateway StatefulSet, PVC, Service, operator, registration, existing providers, global inference routes and unrelated sandboxes.

## Deployment

### Contents

1. Inventory and image probe
2. Derive an image when needed
3. Import a dedicated profile and create credentials
4. Create the Copilot sandbox
5. Authentication alternatives and persistence

### 1. Inventory and image probe

Set verified, non-secret inputs in the control-node shell:

```bash
export GATEWAY=local-gateway WORKSPACE=default SANDBOX=copilot-lab PROVIDER=copilot-token
export ADDON_DIR="$PWD/copilot-addon"
export SKILL_DIR=/absolute/path/to/this-skill
export COPILOT_IMAGE='FULL-PULLABLE-IMAGE@sha256:ACTUAL-DIGEST'
```

Check `oc -n openshell get pod,svc,endpoints,pvc` and confirm the intended existing gateway. Record gateway pod UID, current imageID and ready state. Match the control-node CLI to this raw gateway's release. If registration is absent, `openshell gateway add http://127.0.0.1:8080 --local --name local-gateway` registers the already-running, locally forwarded endpoint; it does not deploy the gateway.

Run `sandbox create --help`, `sandbox exec --help`, `provider create --help` and `provider profile --help`. The examples target 0.0.103. Require `--workspace`, `--no-auto-providers`, non-secret `--env`, and explicit provider/policy options or adapt using that release's source. Use Kubernetes image pull authentication for the sandbox's service account when its registry is private; verify the gateway's sandbox template/driver pull-secret mechanism rather than putting registry passwords in the agent environment.

Generate an initial candidate policy using known readonly launcher/native package paths, then create an unused `copilot-image-probe` sandbox with the same image, `--policy`, `--no-auto-providers --no-tty -- true`. Attach no credential provider. Inspect:

```bash
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" sandbox exec \
  -n copilot-image-probe --no-tty -- sh -lc \
  'id; uname -m; command -v copilot; readlink -f "$(command -v copilot)"; copilot --version; node --version'
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" sandbox exec \
  -n copilot-image-probe --no-tty -- copilot --help
```

Find npm's native package executable under `/usr/lib/node_modules/@github/copilot/node_modules/@github/` or `/usr/local/lib/...` if the launcher is a JS wrapper. Inspect paths and permissions without printing environment values. Do not treat the launcher symlink as the only possible network caller. Keep paths readonly in the final policy.

Generate the final profile/policy into a new directory using observed paths. The renderer refuses to overwrite different content in an existing output directory; preserve manual edits and policy history. Delete only the disposable probe after recording findings.

The image probe can run with no external credentials. Missing image pulls, absent Copilot, unsupported CPU/native package, incompatible glibc, and Landlock startup failure are distinct problems; do not continue to auth troubleshooting until the executable runs.

### 2. Derive an image when needed

Build with the bundled assets directory as context so `demo/` is included. Use a digest-pinned OpenShell-compatible base that contains Node >=22, npm, the `sandbox` user and the normal image contract. Preserve the base supervisor integration; copying Copilot into an unrelated UBI image is insufficient.

```bash
podman build -f "$SKILL_DIR/assets/Dockerfile" \
  --build-arg OPENSHELL_BASE_IMAGE="$BASE_IMAGE" \
  --build-arg COPILOT_VERSION=1.0.105 \
  -t "$YOUR_REGISTRY/copilot-openshell:1.0.105" "$SKILL_DIR/assets"
podman push "$YOUR_REGISTRY/copilot-openshell:1.0.105"
```

Resolve and use the pushed digest. On OpenShift, an equivalent binary Docker BuildConfig can build the same directory if the build API and registry are enabled. Create dedicated `copilot-addon` build/image objects; do not alter the gateway Deployment/StatefulSet. In a build working copy rename Dockerfile only if the builder requires it. No GitHub token belongs in build args or layers.

Prefer image-time installation to runtime npm. Runtime policy intentionally excludes `registry.npmjs.org`, OS package servers and release-download hosts. A build needs its own registry/npm egress, separate from the agent runtime. Re-probe the resulting image; a successful build does not prove the token or model works.

For an existing suitable preinstalled Copilot image, skip rebuilding and upload the demo files later. Record the actual Copilot version rather than upgrading merely because a newer release exists.

### 3. Profile and credential provider

The custom profile ID `copilot-cli` avoids modifying built-in `copilot` metadata. It declares only `COPILOT_GITHUB_TOKEN`, separating this credential from general `GH_TOKEN` Git operations. Its static bindings cover the selected Copilot host and explicit GitHub API auth paths. Verify the rendered files with the installed CLI/schema:

```bash
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" provider profile lint \
  -f "$ADDON_DIR/copilot-cli.yaml"
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" provider list-profiles
```

If the custom ID is absent, import it:

```bash
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" provider profile import \
  -f "$ADDON_DIR/copilot-cli.yaml"
```

Profile import is create-only. If it exists, export it and compare endpoints, methods, credential env names, binaries and scope. Reuse a matching resource; an unexpected wider/different profile needs a separate ID or an intentional scoped update with its resource version. Do not overwrite a shared profile. If import is rejected by an unexpected gateway governance mechanism, report the actual error; do not bypass it or switch to an unauthenticated gateway without authorization.

For an interactive Linux control node, securely read the fine-grained personal-account token. Disable shell tracing first and avoid logging the session:

```bash
set +x
read -r -s -p 'Copilot Requests token: ' COPILOT_GITHUB_TOKEN
printf '\n'
export COPILOT_GITHUB_TOKEN
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" provider create \
  --name "$PROVIDER" --type copilot-cli --credential COPILOT_GITHUB_TOKEN
```

The bare argument is the environment key, not its value. It avoids leaking the value in the process command line. A real deployment executor may instead inject the environment securely without a terminal prompt. If a same-name provider exists, inspect metadata and references before adoption. Use `provider update "$PROVIDER" --credential COPILOT_GITHUB_TOKEN` for an intentional token rotation, preserving other providers and accounting for attached consumers.

The CLI's `--from-existing` custom-profile discovery behavior differs by provider-mode/version. The explicit bare-key form works around legacy command-discovery assumptions in 0.0.103. Do not set `providers_v2_enabled` globally for this add-on.

Keep the host token available only until the verifier's in-memory real-token/placeholder comparison, then `unset COPILOT_GITHUB_TOKEN`. Do not retrieve the real key from gateway storage to write it into a sandbox. The gateway's configured credential store and access controls govern stored-provider persistence; do not call it Vault-backed or encrypted at rest without checking this raw deployment.

### 4. Create the sandbox

Check `sandbox list --names` for conflicts, then use the creation block in SKILL.md. The `HOME`/Copilot/XDG directories are writable under `/sandbox`; core binaries stay readonly. Secrets are only attached by `--provider`.

Poll an explicit `sandbox exec -n "$SANDBOX" --timeout 15 --no-tty -- true` until success or a bounded deadline; inspect the gateway and sandbox pod events if it never becomes ready. Use `sandbox get`, `policy get --full` and `provider list -o json` to record effective state. Check that only the intended provider is attached.

Run `copilot --version` and help again on the final sandbox. Check `--no-auto-update` and `--disable-builtin-mcps` support. Start the terminal UI using `--tty`. Begin in `/sandbox`, use `/user` to inspect the account without publishing it, and choose an available model through `/model` if the default is unavailable. Do not confuse a Copilot model-entitlement error with a gateway deployment failure.

The CLI may need exact additional service paths for its release. Inspect denied events for destination/binary/method, compare the official allowlist, then amend the dedicated profile and policy. A GitHub network allowlist is broader than what this single demo needs. Do not import the cloud-agent recommended firewall list wholesale into a local sandbox policy.

Keep the OpenShell-generated proxy/CA configuration. Validate custom corporate CA trust in the selected CLI; use `NODE_EXTRA_CA_CERTS` for Node-based clients when needed. Do not overwrite proxy variables with an unrelated corporate proxy without checking whether that bypasses OpenShell inspection. Never use `NODE_TLS_REJECT_UNAUTHORIZED=0` or raw TLS skip for credential-bound API requests.

### 5. Alternatives and persistence

OAuth device login is optional if a suitable provider token cannot be used. The browser authorization belongs to the actual user. Open only the documented device flow; add its exact `github.com` auth endpoints for Copilot's binary and keep them separate from general repo writes. Headless keychain fallback can persist a real token under `.copilot`; disclose and protect that storage, and do not claim gateway-only credentials for this variation. Do not automate the user's device approval or collect device codes into evidence.

Native provider-backed token auth is the default skill path. Actual Git operations, repository writes, remote MCP tools, plugins, LSP downloads and telemetry need separate deliberate policy additions and minimum repository permissions; they are not required for the local calculator demo.

Sandbox persistence depends on this gateway's driver and storage configuration. The gateway's SQLite PVC does not itself make every sandbox file durable. Verify workspace storage or export changed files before replacing/removing the new sandbox. Record re-creation and token-rotation steps; never promise survival across pod/node loss without testing it.

## Usage

### Contents

1. Set your target
2. Bring code into the sandbox
3. Interactive work
4. One-off prompts
5. Repair code and run tests
6. Continue or resume a session
7. Export your work
8. Inspect OpenShell decisions
9. Usage boundaries

Use these commands on the control node after the add-on passes installation checks. Replace the target values with the deployed names. Examples use the OpenShell 0.0.103 command grammar and Copilot options documented on 2026-10-28. Check `copilot --help` and `/help` in the installed version before using newer options.

### 1. Set your target

```bash
export GATEWAY=local-gateway WORKSPACE=default SANDBOX=copilot-lab
export PROJECT=/sandbox/copilot-demo
export SKILL_DIR=/absolute/path/to/installed-skill
oshell() {
  command openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" "$@"
}
oshell status
oshell sandbox get "$SANDBOX"
```

Keep the pod gateway's loopback port-forward running if its registration uses `127.0.0.1:8080`. No host-installed Copilot is needed for these examples: `copilot` executes inside the named sandbox. Reconnecting does not require re-creating its provider or pasting the real token into the container.

### 2. Bring code into the sandbox

For the bundled exercise in a derived image:

```bash
oshell sandbox exec -n "$SANDBOX" --no-tty -- \
  sh -c 'test ! -e /sandbox/copilot-demo && cp -r /opt/copilot-demo /sandbox/copilot-demo'
```

If the directory already exists, inspect it and preserve edits; do not rerun a reset over your work. If using a preinstalled image, upload the bundled fixture directory from the control node:

```bash
oshell sandbox upload "$SANDBOX" "$SKILL_DIR/assets/demo/" "$PROJECT"
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --no-tty -- ls -la
```

For your own project, use a clean export containing only the files intended for inference. Set `PROJECT` to another directory and upload it with the same command shape. Check the destination layout after upload. `.gitignore` filtering is useful but does not replace checking for secrets before upload. The default add-on uses file transfer; it does not need Git clone or GitHub repository credentials inside the sandbox.

### 3. Interactive work

```bash
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --tty -- \
  copilot --no-auto-update --disable-builtin-mcps
```

Ask for an explanation, edit, test, or review. Approve individual tool actions as needed. The model sees the code/context you provide and sends it to the configured Copilot service.

| Task | Example request |
| --- | --- |
| Understand code | Explain calculator.py and identify its incorrect behavior. Do not edit files. |
| Fix a defect | Fix add in calculator.py, keep test_calculator.py unchanged, and run the tests. |
| Add tests | Create additional edge-case tests for a separate copy of this small calculator. |
| Review changes | Review the current code for correctness and explain any remaining risks. |
| Write documentation | Create a short USAGE.md explaining how to run the calculator tests. |
| Draft an OpenShift manifest | Generate a Deployment and Service YAML for this sample Python app. Save files for review; do not apply them to a cluster. |

Useful interactive commands, when available in the installed version:

| Command | Use |
| --- | --- |
| `/help` | Inspect the commands this version supports |
| `/model` | Choose an account-authorized model |
| `/user` | Check which Copilot account is active |
| `/plan` | Ask for an implementation plan before edits; keep reviewing actual permissions |
| `/diff` | Inspect proposed/current changes when supported |
| `/usage` | See the session's usage information |
| `/compact` | Reduce accumulated conversation context |
| `/clear` | Begin a fresh conversation |
| `/exit` | Leave Copilot while retaining the sandbox |

An interactive account/model choice is separate from OpenShell's gateway registration and workspace. Exiting the CLI normally does not delete the sandbox created with this skill.

### 4. One-off prompts

Run a bounded command without a terminal UI:

```bash
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --timeout 120 --no-tty -- \
  copilot --no-auto-update --disable-builtin-mcps \
  --deny-tool shell --deny-tool write \
  -p 'Explain calculator.py and identify the bug. Do not edit files or execute commands.'
```

The `shell`/`write` denials keep those Copilot operations unavailable for this analysis request. These CLI permission settings supplement the OpenShell policy. A prompt asking for no edits alone is not an enforcement control.

For scripting, check support for `--silent` to suppress the normal usage summary, or `--output-format=json` for JSONL events. Redirect output on the control node only when you intend to save the model's response:

```bash
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --timeout 120 --no-tty -- \
  copilot --no-auto-update --disable-builtin-mcps \
  --deny-tool shell --deny-tool write --silent \
  -p 'Summarize this small calculator in three sentences.' > calculator-review.txt
```

`calculator-review.txt` is a local control-node output. Preserve exit status; a file being created does not mean the model request succeeded. For edit/test requests, use interactive mode unless you have deliberately configured narrowly scoped tool permissions suitable for unattended execution. Do not solve headless permission failures with allow-all flags.

### 5. Repair code and run tests

Use the full Validation section demonstration for installation acceptance. For normal operation, ask Copilot interactively to make the change, review its edits and approve the specific test invocation. Independently run tests afterward:

```bash
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --timeout 60 --no-tty -- \
  python3 -m unittest -v
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --no-tty -- \
  cat calculator.py
```

The operator's direct test result is separate from Copilot's account of what happened. Keep the demo's original test checksum unchanged during the repair exercise.

### 6. Continue or resume a session

Resume the most recent session for this working directory:

```bash
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --tty -- \
  copilot --no-auto-update --disable-builtin-mcps --continue
```

Select a saved session interactively:

```bash
oshell sandbox exec -n "$SANDBOX" --workdir "$PROJECT" --tty -- \
  copilot --no-auto-update --disable-builtin-mcps --resume
```

For a known session, use `--resume=ACTUAL-SESSION-ID` as reported by Copilot. Do not combine `--resume` and `--continue`. Session history depends on the sandbox's configured state directory/storage. Keeping a gateway PVC does not by itself guarantee the sandbox history survives pod replacement.

### 7. Export your work

Download a single edited file or a directory:

```bash
oshell sandbox download "$SANDBOX" "$PROJECT/calculator.py" ./calculator-fixed.py
oshell sandbox download "$SANDBOX" "$PROJECT" ./copilot-demo-output
```

Choose a new local destination to avoid overwriting existing work. Inspect the exported files, then use your normal source-control review process outside the sandbox. Export needed changes before removing or replacing the sandbox.

### 8. Inspect OpenShell decisions

Show recent events:

```bash
oshell logs "$SANDBOX" --since 10m --level info
oshell policy get "$SANDBOX" --full
```

For the live operator view, open another terminal with the same target variables/function:

```bash
oshell term
```

Select the Copilot sandbox and its event view. Correlate an observed action with destination, binary, method and allow/deny result. Copilot's internal tool-approval prompt is a separate control; it is not an OpenShell denial event.

### 9. Usage boundaries

The default policy supports the Copilot service and a small local-code workflow. Package installation, Git push, repository MCP tools, cluster API access, remote delegation and new external services require separate deliberate configuration. Do not give the agent kubeconfig or Kubernetes service-account credentials merely to write manifests. A model denial, a Copilot permission refusal, an OpenShell deny event and an upstream 401 are different observations.

Keep the normal provider attached and rotate it through the control-plane workflow. Do not run `/login` inside a provider-backed sandbox just to fix missing profile/binary/endpoint policy; that can create a separate on-disk real-token path. Use the deployment diagnostics first.

## Validation

### Contents

1. Runtime acceptance
2. Small coding demonstration
3. Failure diagnosis
4. Scoped rollback

### 1. Runtime acceptance

Create a private evidence directory (`umask 077`). Record cluster/gateway/workspace, gateway pod UID and imageID, sandbox/policy/provider metadata, CLI/Copilot versions, selected service route, and start time. Compare the prior inventory with the final one. Expect one added sandbox/pod plus its dedicated provider/profile and any deliberately created build objects; investigate unrelated changes before claiming isolation of this add-on operation.

```bash
python3 "$SKILL_DIR/scripts/verify_addon.py" \
  --gateway "$GATEWAY" --workspace "$WORKSPACE" --sandbox "$SANDBOX" \
  --service-host api.githubcopilot.com --model-smoke \
  --output /private/evidence/copilot-verification.json
```

Use the selected tier host instead when appropriate. Keep the real host token available for the verifier's private hash comparison, then unset it. Only a boolean comparison is reported; neither token nor fingerprint belongs in the evidence. A different nonempty value is consistent with a placeholder, but only successful provider-backed inference proves that it resolves usefully.

Inspect full effective policy and attachment metadata independently. A verifier exit zero means its requested checks passed, not that all deployment requirements are complete. `NOT_VERIFIED` remains an outstanding gate. The script's curl tests require fresh matching OpenShell events after the commands; if the log format differs, parse the installed version's OCSF events and document the exact assertion. Do not weaken the test to equate any timeout/DNS failure with a policy denial.

Interpret filesystem probes narrowly. Confirm the sandbox user is not root, `/sandbox` writes succeed, `/var/tmp` is world-writable, and the outside write fails. Check mandatory Landlock startup/effective compatibility, SELinux context and ordinary permissions before attributing the denial to a specific kernel control. Kernel version alone is insufficient.

Open `openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" term` in a second terminal and select the new sandbox's events. Keep Copilot's terminal UI in the first terminal. Show the real inference result and operator-visible decisions together. No browser service or public Route is required.

### 2. Coding demonstration

Use a fresh `/sandbox/copilot-demo` directory. For the derived image, copy `/opt/copilot-demo` there. For a preinstalled image, use the installed CLI's `sandbox upload` command as documented by `--help`, or stream the two bundled source files through sandbox exec stdin. Do not upload the host home directory, kubeconfig, project secrets, SSH keys, or a whole real repository for this synthetic demonstration.

1. Run `python3 -m unittest -v` from `/sandbox/copilot-demo`. Confirm the intentionally defective calculator fails before asking Copilot to repair it.
2. Record a SHA-256 checksum of `test_calculator.py` outside the agent session. Keep the control-node original test fixture as the reference.
3. Start Copilot in that directory with updates and built-in MCP disabled. Ask:

   > Repair the add function in calculator.py so it adds both arguments. Keep test_calculator.py unchanged, run the unit tests, and explain the fix. Work only in this demo directory and use no network tools or GitHub repository actions.

4. Approve only necessary file edits and the specific test command in Copilot's normal permission prompts. Do not turn on allow-all permissions.
5. Inspect the changed calculator and rerun tests independently through `openshell sandbox exec`, outside the model's response.
6. Verify the test-file checksum is unchanged. Use an independent operator command to import the function and check additional cases, for example `(19, -7) → 12` and `(-0.5, 0.25) → -0.25`. Do not let Copilot's claimed test output serve as the sole evidence.
7. Record the small source diff, test results, gateway event evidence and achieved boundaries. Leave the demo working.

If the model refuses a tool request, distinguish Copilot's permission dialog from OpenShell enforcement. A request may fail in either layer. To demonstrate the outer boundary, use direct operator sandbox exec probes with matching runtime policy/evidence, rather than assuming an agent refusal came from OpenShell.

### 3. Diagnose the first failing layer

| Symptom | Inspect / fix |
| --- | --- |
| CLI cannot reach gateway | Existing Service endpoints, owned port-forward, gateway pod readiness, target registration and version match |
| `unknown subcommand profile` or missing flags | Match the CLI to the gateway; use the selected release's grammar; do not install a new gateway |
| Pod Pending/ImagePullBackOff | Image digest, architecture, registry pull credentials, node capacity and sandbox controller events |
| `copilot` missing / native loader error | Probe image, Node >=22 for npm install, glibc/musl/architecture; rebuild only the agent image |
| Sandbox cannot start with hard requirement | Check runtime Landlock capability; record a deliberate reduced-assurance variation or fix nodes; do not silently disable it |
| 401/403 from GitHub/Copilot | Fine-grained personal token, Copilot Requests, entitlement, organization policy, expiry and actual endpoint binding |
| `credential_endpoint_mismatch` | Dedicated profile binding must cover the observed exact host/port/path; matching egress alone is insufficient |
| Token rejected before any outbound request | Check whether this CLI release validates token format locally and is compatible with OpenShell placeholders; use a compatible agent build or supported provider integration instead of injecting the real token into the sandbox |
| Denied network / binary mismatch | Inspect native executable path and endpoint/method in new denial event; update only this profile/policy |
| Certificate/proxy failure | Preserve OpenShell proxy and CA configuration; trust required corporate CA; do not skip TLS inspection/verification |
| Prompt mode hangs | Model access/quota, TTY vs `-p`, permission prompts, disabled MCP state and bounded exec timeout |
| GitHub MCP/plugin failure | Baseline disables these integrations; add them only when requested, with their own permissions and endpoints |
| Copilot's inner sandbox unavailable | Inspect current enterprise/local settings and nested-runtime prerequisites; avoid privileged SCC, host mounts or bypassing managed rules |
| Existing provider/profile name collision | Compare type, bindings, ownership and consumers; adopt a match or choose distinct names; never delete shared state to continue |

GitHub CLI authentication may use a real keychain/plaintext file; provider-backed sandbox auth uses placeholders. Do not merge these into one unsupported claim about secret storage. A Copilot subscription failure is not fixed by supplying a generic MaaS key. BYOK requires its own explicit configuration and streaming/tool-capable model checks.

### 4. Scoped rollback

Retain the running add-on after success. Before requested removal, export any wanted demo changes. List provider attachments/consumers using the installed version's inspection commands. Then remove the added sandbox:

```bash
openshell --gateway "$GATEWAY" --workspace "$WORKSPACE" sandbox delete "$SANDBOX"
```

Delete `$PROVIDER` only when created exclusively for this add-on and unused elsewhere. Remove custom `copilot-cli` only when unreferenced and owned by this task, using this version's `provider profile delete`. Revoke the real GitHub token separately if requested; deleting gateway metadata is not GitHub-side revocation.

Stop a port-forward only after checking its recorded PID still belongs to this run's exact command. Remove only dedicated build/image resources when requested. Do not run workshop teardown, Helm gateway uninstall, namespace deletion, operator removal, or gateway/PVC/Service deletion for this add-on.

## Research

Research date: 2026-10-28. Scope: add a Copilot sandbox to the user's existing OpenShell pod gateway. No SAW or VM deployment is required.

### Primary evidence

| Source | Finding used |
| --- | --- |
| [NVIDIA supported agents](https://docs.nvidia.com/openshell/v0.0.116/about/supported-agents) | Copilot CLI is documented in the community base image; confirm the selected image rather than assuming every base tag is equivalent |
| [OpenShell 0.0.103 source](https://github.com/NVIDIA/OpenShell/tree/v0.0.103) | Audited tag resolves to `c825b1f8efac457f3ca3c6f9e06fb068e8ce3ecc`; matching CLI/provider/policy command grammar and placeholder binding inspected |
| [0.0.103 Copilot profile](https://github.com/NVIDIA/OpenShell/blob/v0.0.103/providers/copilot.yaml) | Built-in type `copilot`, credential env names, Copilot API hosts and binary metadata |
| [0.0.103 provider reference](https://github.com/NVIDIA/OpenShell/blob/v0.0.103/docs/sandboxes/manage-providers.mdx) | Explicit provider attachment, bare-key credential input, custom profiles, provider-mode differences and endpoint-bound placeholders |
| [Community base image source](https://github.com/NVIDIA/OpenShell-Community/tree/edb65583a32c9ebb0fe8b6c709949e19ece08e52/sandboxes/base) | Inspected Dockerfile installs Node 22 and Copilot `1.0.16`; image policy contains Copilot entries. A current release is not necessarily what the image embeds |
| [GitHub CLI installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) | Official `@github/copilot` npm distribution, Node >=22 and standalone release alternatives |
| [GitHub authentication](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli) | Container env authentication, token priority, fine-grained user PAT/Copilot Requests, no classic PAT; headless OAuth can persist plaintext if keychain unavailable |
| [GitHub CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | Interactive/programmatic modes, normal permissions, built-in MCP controls, update controls; feature-check installed help |
| [Copilot allowlist](https://docs.github.com/en/copilot/reference/copilot-allowlist-reference) | Service routing, authentication/user-management paths, and difference between GitHub.com, tier-specific routes and GHE.com |
| [GitHub network settings](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/network-settings) | Proxy settings and extra CA trust; retain the OpenShell proxy and certificate verification |
| [Copilot release 1.0.105](https://github.com/github/copilot-cli/releases/tag/v1.0.105) | Published 2026-10-28; fallback build pins npm package version `1.0.105` rather than moving latest |

### Source findings that affect deployment

- The earlier workshop pins raw OpenShell `0.0.103`. Current NVIDIA latest documentation describes newer releases and command names. In the audited tag, profile commands are under `openshell provider profile`; do not copy a newer top-level `openshell profile` command without checking this client.
- The built-in Copilot profile's service endpoints do not include all GitHub auth/user-management paths. The custom add-on profile explicitly binds the dedicated credential to the API paths it needs, including `/user` and `/copilot_internal/**`, and the selected Copilot service host. This is a deployment design based on source inspection; prove it with the actual installed Copilot version and account.
- In `0.0.103`, profile-based network composition depends on `providers_v2_enabled`. Static credential binding applies in either mode. Explicit sandbox policy avoids changing a gateway-wide setting.
- Copilot service calls need POST/generation access. The workshop's read-only GitHub/curl policy is not a Copilot policy.
- Node wrappers and native npm platform binaries can have different paths. Inspect the image and bind actual readonly executable paths. A general Node allow rule grants capability to other code using that interpreter; do not describe it as program-specific identity.
- A provider placeholder is not a valid real token on its own. Successful inspected HTTPS and endpoint binding are required. Do not switch to an opaque TLS tunnel to make placeholder auth work.
- GitHub Copilot's optional inner sandbox and OpenShell's outer sandbox are distinct. Unsupported inner sandboxing is not a reason to make the Kubernetes sandbox privileged.

### Optional inference variation

[GitHub BYOK documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models) describes direct OpenAI-compatible, Azure and Anthropic providers. Models need streaming and tool calling. BYOK and `COPILOT_OFFLINE=true` can avoid GitHub auth/service calls, but this is a separate optional configuration, not the default subscription deployment. Do not silently repoint the existing gateway's global inference route or reuse a MaaS key as a Copilot subscription token. If requested, build a separate endpoint-bound BYOK profile exposing `COPILOT_PROVIDER_API_KEY`, configure the exact URL/model variables supported by the installed CLI, and validate streaming/tool use independently.

### What this research does not prove

Source inspection and offline asset tests do not prove the user's cluster image, account entitlement, proxy trust, model access, token binding or Copilot's current session works. Mark those properties with runtime evidence. Do not describe this add-on as a new gateway, a GPU workload, or an OpenShift AI dependency.

## Embedded files

Extract these files with the preparation command above. Their contents are unchanged from the tested skill resources.

### scripts/render_config.py

<!-- BEGIN FILE: scripts/render_config.py -->
````python
#!/usr/bin/env python3
"""Render non-secret Copilot policy/profile assets; never contact a gateway."""
import argparse
import json
from pathlib import Path, PurePosixPath
import yaml

ROUTES = {
    'common': 'api.githubcopilot.com',
    'individual': 'api.individual.githubcopilot.com',
    'business': 'api.business.githubcopilot.com',
    'enterprise': 'api.enterprise.githubcopilot.com',
}


def binary(value):
    p = PurePosixPath(value)
    if not p.is_absolute() or '..' in p.parts or any(c in value for c in '\n\r\t '):
        raise argparse.ArgumentTypeError('Use an absolute readonly executable path without traversal or whitespace')
    if any(c in value for c in '*?[]'):
        raise argparse.ArgumentTypeError('Resolve the actual executable; wildcard binary grants are not accepted')
    if not value.startswith(('/usr/', '/opt/', '/bin/')) or value.endswith(('/', '/**', '/*')):
        raise argparse.ArgumentTypeError('Bind an executable under /usr, /opt, or /bin; do not grant a whole directory')
    return value


def documents(route, binaries, hard=True):
    binaries = list(dict.fromkeys(binaries))
    service = {'host': ROUTES[route], 'port': 443, 'protocol': 'rest',
               'tls': 'terminate', 'access': 'read-write', 'enforcement': 'enforce'}
    auth_network = {'host': 'api.github.com', 'port': 443, 'protocol': 'rest',
                    'tls': 'terminate', 'enforcement': 'enforce', 'rules': [
                        {'allow': {'method': 'GET', 'path': '/user'}},
                        {'allow': {'method': 'GET', 'path': '/copilot_internal/**'}},
                    ]}
    policy = {
        'version': 1,
        'filesystem_policy': {
            'include_workdir': True,
            'read_only': ['/usr', '/lib', '/proc', '/dev/urandom', '/app', '/etc', '/var/log', '/opt'],
            'read_write': ['/sandbox', '/tmp', '/dev/null'],
        },
        'landlock': {'compatibility': 'hard_requirement' if hard else 'best_effort'},
        'process': {'run_as_user': 'sandbox', 'run_as_group': 'sandbox'},
        'network_policies': {
            'copilot-service': {'name': 'copilot-service', 'endpoints': [service],
                                 'binaries': [{'path': x} for x in binaries]},
            'copilot-auth': {'name': 'copilot-auth', 'endpoints': [auth_network],
                              'binaries': [{'path': x} for x in binaries]},
        },
    }
    auth_bindings = [
        {'host': 'api.github.com', 'port': 443, 'path': path, 'protocol': 'rest',
         'tls': 'terminate', 'access': 'read-only', 'enforcement': 'enforce'}
        for path in ('/user', '/copilot_internal/**')
    ]
    # Profile policy can compose into a sandbox when gateway provider v2 is already enabled.
    # Preserve the same restrictions in both layers rather than relying on a global toggle.
    for entry in auth_bindings:
        entry.pop('access')
        entry['rules'] = [{'allow': {'method': 'GET', 'path': entry['path']}}]
    profile = {
        'id': 'copilot-cli', 'display_name': 'GitHub Copilot CLI add-on',
        'description': 'Copilot service and narrowly scoped GitHub authentication',
        'category': 'agent',
        'credentials': [{'name': 'api_token', 'description': 'Personal account Copilot Requests token',
                         'env_vars': ['COPILOT_GITHUB_TOKEN'], 'required': True,
                         'auth_style': 'bearer', 'header_name': 'authorization'}],
        'discovery': {'credentials': ['api_token']},
        'endpoints': [dict(service)] + auth_bindings,
        'binaries': binaries,
    }
    return policy, profile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--route', choices=ROUTES, default='common')
    p.add_argument('--binary', type=binary, action='append', required=True)
    p.add_argument('--best-effort-landlock', action='store_true',
                   help='Explicit reduced-assurance variation; requires recording the deviation')
    a = p.parse_args()
    policy, profile = documents(a.route, a.binary, not a.best_effort_landlock)
    a.out.mkdir(parents=True, exist_ok=True)
    outputs = {'copilot-policy.yaml': policy, 'copilot-cli.yaml': profile}
    rendered_outputs = {name: yaml.safe_dump(content, sort_keys=False) for name, content in outputs.items()}
    for name, rendered in rendered_outputs.items():
        path = a.out / name
        if path.exists() and path.read_text() != rendered:
            p.error(f'{path} already has different content; choose a new output directory')
    for name, rendered in rendered_outputs.items():
        path = a.out / name
        path.write_text(rendered)
    print(json.dumps({'rendered': [str(a.out / x) for x in outputs],
                      'service_host': ROUTES[a.route], 'gateway_mutations': 0}, indent=2))


if __name__ == '__main__':
    main()

````
<!-- END FILE -->

### scripts/verify_addon.py

<!-- BEGIN FILE: scripts/verify_addon.py -->
````python
#!/usr/bin/env python3
"""Verify a named Copilot add-on through an existing gateway; never install/delete resources."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HOSTS = ('api.githubcopilot.com', 'api.individual.githubcopilot.com',
         'api.business.githubcopilot.com', 'api.enterprise.githubcopilot.com')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gateway', required=True)
    p.add_argument('--workspace', default='default')
    p.add_argument('--sandbox', default='copilot-lab')
    p.add_argument('--service-host', choices=HOSTS, default=HOSTS[0])
    p.add_argument('--model-smoke', action='store_true')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.output and a.output.exists():
        p.error('Evidence output already exists; choose a new filename')
    prefix = ['openshell', '--gateway', a.gateway, '--workspace', a.workspace]
    results = []

    def run(args, timeout=35):
        try:
            r = subprocess.run(prefix + args, capture_output=True, text=True, timeout=timeout)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return 124, '', 'Command timed out'
        except FileNotFoundError:
            return 127, '', 'OpenShell CLI not installed'

    def remote(args, timeout=35):
        return run(['sandbox', 'exec', '-n', a.sandbox, '--workdir', '/sandbox',
                    '--timeout', str(max(1, timeout - 5)), '--no-tty', '--'] + args, timeout)

    def result(name, passed, note):
        results.append({'check': name, 'status': 'PASS' if passed else 'FAIL', 'note': note})

    rc, _, _ = run(['status'])
    result('existing-gateway-reachable', rc == 0, 'Uses the explicitly named existing gateway')
    if rc:
        print(json.dumps({'all_requested_checks_passed': False, 'results': results}, indent=2))
        return 1
    rc, version, _ = remote(['copilot', '--version'])
    result('copilot-executable', rc == 0 and bool(re.search(r'\d+\.\d+\.\d+', version)),
           'Copilot version command returned successfully' if rc == 0 else 'Inspect the image/runtime')
    rc, identity, _ = remote(['id', '-un'])
    result('nonroot-sandbox-identity', rc == 0 and identity.strip() == 'sandbox',
           'Expected the configured sandbox user')
    rc, _, _ = remote(['sh', '-c', 'umask 077; p=/sandbox/.copilot-addon-probe-$$; : > "$p" && rm -f "$p"'])
    result('allowed-workspace-write', rc == 0, 'Created and removed only a disposable probe file')
    rc, mode, _ = remote(['stat', '-c', '%a', '/var/tmp'])
    mode_ok = rc == 0 and mode.strip() == '1777'
    rc, _, _ = remote(['sh', '-c',
        'p=/var/tmp/.copilot-addon-probe-$$; if touch "$p"; then rm -f "$p"; exit 0; else exit 1; fi'])
    result('outside-path-write-denied', mode_ok and rc != 0 and rc != 124,
           'Requires allowed-path control and mode 1777; inspect SELinux before attributing specifically to Landlock')

    token = os.environ.get('COPILOT_GITHUB_TOKEN')
    if token:
        rc, digest, _ = remote(['python3', '-c',
            'import hashlib,os; v=os.environ.get("COPILOT_GITHUB_TOKEN",""); '
            'print(hashlib.sha256(v.encode()).hexdigest() if v else "MISSING")'])
        observed = digest.strip()
        ok = rc == 0 and bool(re.fullmatch('[0-9a-f]{64}', observed)) and observed != hashlib.sha256(token.encode()).hexdigest()
        result('credential-is-present-and-not-real-host-token', ok,
               'Compared only hashes in memory; no token or hash emitted. Pair with successful live inference.')
    else:
        results.append({'check': 'credential-is-present-and-not-real-host-token', 'status': 'NOT_VERIFIED',
                        'note': 'Host token unavailable for a private comparison'})

    rc, _, _ = remote(['sh', '-c', 'command -v curl >/dev/null'])
    curl_available = rc == 0
    _, before, _ = run(['logs', a.sandbox, '--since', '2m'])
    baseline = Counter(before.splitlines())
    attempts = []
    for host in ('example.com', a.service_host):
        rc, _, _ = remote(['curl', '-fsS', '--connect-timeout', '5', '--max-time', '10',
                            'https://' + host + '/'], 20)
        attempts.append((host, curl_available and rc not in (0, 124)))
    # Gateway activity arrives asynchronously. Bound the wait, then require new evidence.
    time.sleep(6)
    rc, after, _ = run(['logs', a.sandbox, '--since', '2m'])
    fresh = []
    for line in after.splitlines():
        if baseline[line]:
            baseline[line] -= 1
        else:
            fresh.append(line)
    for host, failed in attempts:
        evidence = any(host in line and re.search(r'denied|deny|blocked', line, re.I)
                       and 'curl' in line.lower() for line in fresh)
        result('curl-denied-' + host, failed and rc == 0 and evidence,
               'Requires a new matching host/curl denial event; connectivity failure alone is insufficient')

    if a.model_smoke:
        rc, help_text, _ = remote(['copilot', '--help'])
        needed = ('--no-auto-update', '--disable-builtin-mcps', '--deny-tool')
        supported = rc == 0 and all(flag in help_text for flag in needed)
        if supported:
            rc, reply, _ = remote(['copilot', '--no-auto-update', '--disable-builtin-mcps',
                                   '--deny-tool', 'shell', '--deny-tool', 'write', '-p',
                                   'Reply with COPILOT_GATEWAY_OK. Do not use any tools.'], 150)
            result('live-model-smoke', rc == 0 and 'COPILOT_GATEWAY_OK' in reply,
                   'Real provider-backed inference; no prompt/response or credential emitted by this verifier')
        else:
            result('live-model-smoke', False, 'Installed Copilot lacks required tested options; adapt explicitly')
    else:
        results.append({'check': 'live-model-smoke', 'status': 'NOT_VERIFIED',
                        'note': 'Re-run with --model-smoke when the account and provider are ready'})

    report = {'gateway': a.gateway, 'workspace': a.workspace, 'sandbox': a.sandbox,
              'all_requested_checks_passed': all(x['status'] != 'FAIL' for x in results),
              'all_listed_checks_verified': all(x['status'] == 'PASS' for x in results),
              'still_require': ['gateway/unrelated-sandbox before-after inventory',
                               'effective policy/profile/provider attachment inspection',
                               'independent calculator demo and unchanged test checksum'],
              'results': results}
    rendered = json.dumps(report, indent=2)
    if a.output:
        fd = os.open(a.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(rendered + '\n')
    print(rendered)
    return 0 if report['all_requested_checks_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

````
<!-- END FILE -->

### assets/Dockerfile

<!-- BEGIN FILE: assets/Dockerfile -->
````dockerfile
ARG OPENSHELL_BASE_IMAGE
FROM ${OPENSHELL_BASE_IMAGE}
USER root
ARG COPILOT_VERSION=1.0.105
ENV COPILOT_AUTO_UPDATE=false
RUN test -n "$COPILOT_VERSION" \
    && node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)' \
    && npm_config_ignore_scripts=false npm install --global "@github/copilot@${COPILOT_VERSION}" \
    && copilot --version
COPY demo/ /opt/copilot-demo/
RUN chmod -R a+rX /opt/copilot-demo
USER sandbox
WORKDIR /sandbox

````
<!-- END FILE -->

### assets/demo/calculator.py

<!-- BEGIN FILE: assets/demo/calculator.py -->
````python
"""Synthetic coding exercise: repair addition without changing the tests."""


def add(a, b):
    return a - b

````
<!-- END FILE -->

### assets/demo/test_calculator.py

<!-- BEGIN FILE: assets/demo/test_calculator.py -->
````python
import unittest
from calculator import add


class AdditionTests(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(7, 5), 12)

    def test_negative(self):
        self.assertEqual(add(-4, -9), -13)

    def test_zero(self):
        self.assertEqual(add(0, 8), 8)

    def test_decimal(self):
        self.assertAlmostEqual(add(1.25, 2.5), 3.75)


if __name__ == '__main__':
    unittest.main()

````
<!-- END FILE -->
