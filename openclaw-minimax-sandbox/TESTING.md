# OpenClaw sandbox checks

This guide covers the MiniMax endpoint profile and the OpenShell allow/deny exercises for the pod-only OpenClaw deployment. Run the commands from a terminal that can resolve and reach the OpenShift gateway Route. The gateway Route requires its mTLS client bundle; keep TLS verification enabled.

The model profile in `inputs/model-profile.yaml` grants `/usr/local/bin/node` access to `api.minimax.io:443` under `/v1/**`. The default-deny and read-only network policies are in `inputs/module2-deny.yaml` and `inputs/module2-readonly.yaml`.

## Connect to the gateway

Install the pinned OpenShell 0.1.2 CLI and place the current mTLS client bundle under `client-config/openshell/gateways/openclaw-pod-route/mtls/` (`ca.crt`, `tls.crt`, `tls.key`, all mode 600). These local credentials and the platform-specific CLI binary are ignored by Git.

```bash
cd /path/to/openclaw-minimax-sandbox
export LAB_DIR="$PWD"
export INPUTS_DIR="$LAB_DIR/inputs"
export POD_CONFIG_HOME="$LAB_DIR/client-config"
export POD_OPENSHELL_BIN="$HOME/.local/bin/openshell"
export GATEWAY=openclaw-pod-route
export WORKSPACE=default

oshell() {
  XDG_CONFIG_HOME="$POD_CONFIG_HOME" "$POD_OPENSHELL_BIN" \
    --gateway "$GATEWAY" --workspace "$WORKSPACE" "$@"
}

oshell status
oshell sandbox list
```

## Verify the MiniMax allow profile

Confirm the model provider is applied and the expected model is selected:

```bash
oshell sandbox provider status openclaw-lab2 openclaw-model-token --wait --timeout 30
oshell sandbox exec -n openclaw-lab2 --no-tty -- \
  openclaw config get agents.defaults.model
```

Send a harmless completion request from the permitted Node executable. The API key comes from the attached OpenShell provider and is never printed:

```bash
oshell sandbox exec -n openclaw-lab2 --no-tty -- /usr/local/bin/node --input-type=module -e '
const key = process.env.VLLM_API_KEY;
if (!key) throw new Error("VLLM_API_KEY is missing");
const r = await fetch("https://api.minimax.io/v1/chat/completions", {
  method: "POST",
  headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
  body: JSON.stringify({
    model: "MiniMax-M2.7",
    messages: [{role: "user", content: "Reply with the word OK"}],
    max_tokens: 20
  })
});
const data = await r.json();
console.log(`HTTP ${r.status}; model=${data.model}`);
if (!r.ok || data.model !== "MiniMax-M2.7") process.exit(1);
'
```

Pass: HTTP 200 and response model `MiniMax-M2.7`.

## Verify prohibited destinations and paths

Probe a host outside the profile and a path outside `/v1/**`, one at a time:

```bash
oshell sandbox exec -n openclaw-lab2 --no-tty -- /usr/local/bin/node --input-type=module -e '
try {
  const r = await fetch("https://api.openai.com/v1/models", {signal: AbortSignal.timeout(10000)});
  console.log(`UNEXPECTED response: HTTP ${r.status}`);
  process.exitCode = 1;
} catch {
  console.log("Request failed; check OpenShell logs for the matching policy denial.");
}
'

oshell sandbox exec -n openclaw-lab2 --no-tty -- /usr/local/bin/node --input-type=module -e '
try {
  const r = await fetch("https://api.minimax.io/v2/chat/completions", {signal: AbortSignal.timeout(10000)});
  console.log(`UNEXPECTED response: HTTP ${r.status}`);
  process.exitCode = 1;
} catch {
  console.log("Request failed; check OpenShell logs for the matching policy denial.");
}
'

oshell logs openclaw-lab2 --since 2m --level info
```

Also check that the model profile's binary binding blocks `curl` from using the MiniMax endpoint:

```bash
oshell sandbox exec -n openclaw-lab2 --no-tty -- /usr/bin/curl \
  -sS --max-time 10 -o /dev/null -w 'HTTP %{http_code}\n' \
  https://api.minimax.io/v1/models
oshell logs openclaw-lab2 --since 2m --level info
```

Require a new matching policy event for the denied host/path/binary. A failed request alone can also mean DNS or upstream failure; an upstream HTTP 401/403 is not proof of a policy denial.

## Run the separate default-deny/read-only exercises

Keep this provider-free sandbox separate from `openclaw-lab2`. Check `oshell sandbox list` first and create it only if `policy-lab-pod` does not already exist:

```bash
export OPENCLAW_IMAGE='image-registry.openshift-image-registry.svc:5000/openshell-openclaw/openclaw-sandbox@sha256:b5e0f8664b43c61d1b17cfead4a3ef4e26c9beacc46b4c176ac0d8210746a5bc'

oshell sandbox create --name policy-lab-pod --detach --no-auto-providers \
  --from "$OPENCLAW_IMAGE" --policy "$INPUTS_DIR/module2-deny.yaml" \
  --env HOME=/sandbox -- sleep infinity
```

With default deny, a GitHub GET should fail and produce a matching event:

```bash
oshell sandbox exec -n policy-lab-pod --no-tty -- \
  /usr/bin/curl -fsS --max-time 10 https://api.github.com/zen
oshell logs policy-lab-pod --since 2m --level info
```

Apply the narrow read-only policy. The same curl GET should now succeed:

```bash
oshell policy set policy-lab-pod --policy "$INPUTS_DIR/module2-readonly.yaml" --wait
oshell sandbox exec -n policy-lab-pod --no-tty -- \
  /usr/bin/curl -fsS --max-time 10 https://api.github.com/zen
```

Then test the prohibited POST and a Node GET (the read-only profile binds access to `/usr/bin/curl`):

```bash
oshell sandbox exec -n policy-lab-pod --no-tty -- /usr/bin/curl \
  -sS --max-time 10 -X POST -d '{"lab":"deny-test"}' \
  -o /dev/null -w 'HTTP %{http_code}\n' https://api.github.com/zen

oshell sandbox exec -n policy-lab-pod --no-tty -- /usr/local/bin/node -e '
fetch("https://api.github.com/zen", {signal: AbortSignal.timeout(10000)})
  .then(r => { console.log(`UNEXPECTED response: HTTP ${r.status}`); process.exitCode = 1; })
  .catch(() => console.log("Request failed; confirm the Node binary denial in OpenShell logs."));
'
oshell logs policy-lab-pod --since 2m --level info
```

After the exercise, restore default deny:

```bash
oshell policy set policy-lab-pod --policy "$INPUTS_DIR/module2-deny.yaml" --wait
```

Treat a denial as proven only when a fresh OpenShell event matches the tested destination, method, or binary. Do not infer a policy pass from an HTTP status alone.

## OpenClaw chat and tool checks

After the OpenClaw UI is reachable and its device is paired, ask it to create `/sandbox/demo/add.cjs` and `/sandbox/demo/add.test.cjs`, then independently verify the files and run:

```bash
oshell sandbox exec -n openclaw-lab2 --no-tty -- node --test /sandbox/demo/add.test.cjs
```

The config denies OpenClaw's `group:web` and `browser` tools. Ask it to use web search or a browser and confirm it cannot invoke those tools; verify the tool result rather than relying on its explanation. The hard Landlock policy should also prevent writing under `/var/tmp`; verify any such test from inside the sandbox and ensure unexpected files are removed.

The mTLS Route is the OpenShell control endpoint, not the OpenClaw UI. A successful MiniMax API probe proves provider access, not a paired OpenClaw chat. Complete the UI/device-pairing step before claiming the interactive coding and tool-denial checks passed.
