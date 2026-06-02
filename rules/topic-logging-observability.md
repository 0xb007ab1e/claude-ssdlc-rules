# Topic: Logging & Observability

Makes OWASP Top 10 #9 and NIST AU controls concrete. Covers logs, metrics, traces, audit,
and alerting. Pairs with master §5 (redaction).

## Structured logging
- Emit **structured** logs (JSON) with a stable schema: timestamp (UTC, ISO-8601), level,
  service, version, trace/correlation ID, event, and context fields.
- Use leveled logging (DEBUG→ERROR); no debug logs in prod by default.
- One correlation/trace ID propagated across services (OpenTelemetry); attach it to every
  log line so a request is traceable end-to-end.
- Logs are an **event stream to stdout/stderr** (12-Factor) — the platform ships/aggregates;
  apps don't manage log files or rotation.

## Redaction (mandatory — master §5)
- **Never log** secrets, tokens, passwords, full PANs, PII/PHI, or auth headers. Scrub by
  default with an allow-list of safe fields; redact at the logging boundary, not ad hoc.
- Mask where a value is needed for debugging (e.g. last-4, hashed identifiers).
- Keep stack traces and internal detail server-side; never return them to clients.

## Security audit trail
- Log security-relevant events: authentication (success/failure), authZ decisions/denials,
  privilege changes, secret/key access, config changes, data export, admin actions.
- Audit logs are **append-only / tamper-evident**, access-controlled, and retained per
  policy/regulation. Ensure non-repudiation (who, what, when, from where).

## Metrics, tracing & alerting
- Export metrics (RED/USE: rate, errors, duration / utilization, saturation, errors) and
  distributed traces. Define SLIs/SLOs for critical paths.
- **Alert** on security and reliability signals: auth-failure spikes, authZ-denial bursts,
  new error classes, latency/error-budget breaches, anomaly in data egress.
- Detection feeds incident response (`@rules/workflow-vuln-mgmt.md`); high-value systems
  forward to a SIEM. Monitoring failures are themselves an alertable condition (fail loud).

## References
- **OpenTelemetry** — opentelemetry.io (semantic conventions); **OWASP Logging Cheat Sheet**.
- **Google SRE** monitoring chapters (sre.google/books). Index: `@rules/reference-style-guides.md`.
