# Topic: Tailnet Dev Access

Local **dev/preview** services on a Tailscale-connected host must be reachable from the owner's own
devices over the **tailnet** (private WireGuard mesh) — at `http://<host>:<port>` (MagicDNS name,
e.g. `parrot:8502`) — and **never** the public internet. Applies to every project's dev/preview
servers (web apps, APIs, dashboards, notebooks, etc.).

## Binding
- Bind dev service ports to the host's **Tailscale interface IP** (e.g. `100.x.y.z:PORT:PORT`), so
  they resolve at `http://<host>:<port>` from tailnet devices (phone/laptop) — true port-to-port.
- **Also keep a `127.0.0.1:PORT` binding** for local tooling/agents on the host (e.g. a gateway,
  tests, scripts that hit the service over loopback).
- **Never** bind dev services to `0.0.0.0` (that also exposes them on the LAN/other interfaces) and
  **never** use Tailscale **Funnel** (public internet) for development. Tailnet-IP bind = private.
- The Tailscale IP is stable per node; if it changes (`tailscale ip -4`), update the binding.

## App auth + CORS
- Tailnet ≠ no-auth: keep the app's own authentication on — it's reachable by any device/user on the
  tailnet, gated by Tailscale ACLs. Use least-privilege ACLs on multi-user tailnets.
- If a web UI makes **browser-side cross-port/cross-origin API calls**, add the tailnet origin(s)
  (`http://<host>:<ui-port>`) to the app's CORS allowlist (otherwise the browser blocks the calls).

## Don't
- No public exposure (Funnel / `0.0.0.0` / public-router port-forward) for dev services.
- Don't rely on the network for confidentiality alone; transport is WireGuard-encrypted, but the
  app still authenticates and authorizes (`@rules/std-zero-trust.md`).

> Compose pattern: map **both** `127.0.0.1:PORT:PORT` and `100.x.y.z:PORT:PORT`. Pairs with
> `@rules/topic-local-dev.md`. Index: `@rules/reference-style-guides.md`.
