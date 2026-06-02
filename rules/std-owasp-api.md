# Standard: OWASP API Security Top 10

For REST/GraphQL/gRPC APIs. **Distinct from the web Top 10** — APIs fail differently
(object-level authZ, mass assignment, resource exhaustion). Pair with
`@rules/topic-authn-authz.md` and `@rules/std-owasp.md`.

1. **API1 Broken Object Level Authorization (BOLA):** the #1 API risk. Verify the caller
   owns/may access *this specific object* on every request — never trust an ID from the
   client. Test with another user's IDs.
2. **API2 Broken Authentication:** strong auth on every endpoint; correct token validation;
   no unauthenticated sensitive endpoints; protect token/credential flows.
3. **API3 Broken Object Property Level Authorization:** combines mass assignment + excessive
   data exposure. Bind inputs to explicit allow-listed fields (DTOs); return only fields the
   caller may see — never serialize whole DB objects.
4. **API4 Unrestricted Resource Consumption:** rate-limit, paginate, cap payload/page sizes,
   set timeouts and complexity limits (esp. GraphQL query depth/cost); quota per client.
5. **API5 Broken Function Level Authorization:** enforce role/permission per operation; don't
   rely on hidden/undocumented endpoints; deny by default.
6. **API6 Unrestricted Access to Sensitive Business Flows:** protect abuse-prone flows
   (signup, purchase, comment) against automation — bot detection, throttling, step-up.
7. **API7 SSRF:** validate/allow-list any server-side fetch from client-supplied URLs; block
   internal/metadata addresses (see `@rules/std-cwe.md` CWE-918).
8. **API8 Security Misconfiguration:** hardened defaults, TLS, disable unused methods/verbose
   errors, correct CORS (`@rules/topic-web-frontend.md`), patched stack.
9. **API9 Improper Inventory Management:** maintain an API inventory + versioning; retire old/
   beta endpoints; document every exposed endpoint; no shadow/zombie APIs.
10. **API10 Unsafe Consumption of 3rd-Party APIs:** validate and sanitize data from upstream
    APIs as untrusted; set timeouts; don't blindly follow redirects.

## Practices
- Define the contract (OpenAPI/GraphQL schema/protobuf); validate requests/responses against
  it; generate clients from it.
- Authn/authz at a gateway *and* in the service (defense in depth); consistent error shape;
  structured audit logging (`@rules/topic-logging-observability.md`).
