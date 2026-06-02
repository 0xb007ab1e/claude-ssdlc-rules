# Topic: Open-Source License Compliance

Dependency *license* obligations — distinct from supply-chain *security*
(`@rules/std-supplychain.md`). Using a dependency means accepting its license; getting this
wrong creates legal risk and can force code disclosure.

## Know your licenses
- **License classes:**
  - **Permissive** (MIT, BSD, Apache-2.0, ISC) — generally safe; usually require attribution;
    Apache-2.0 adds a patent grant + NOTICE handling.
  - **Weak copyleft** (LGPL, MPL, EPL) — file/library-level share-alike; dynamic linking usually
    OK, but modifications to the licensed files must be shared.
  - **Strong copyleft** (GPL, AGPL) — derivative works must be released under the same license.
    **AGPL extends this to network/SaaS use** — serving it can trigger source-disclosure
    obligations. Flag AGPL/GPL explicitly for SaaS.
  - **Proprietary / source-available / "no license"** — no grant by default = not usable; treat
    unlicensed deps as off-limits until cleared.
- Watch **transitive** dependencies — a permissive top-level dep can pull in copyleft.

## Policy & enforcement
- Maintain an **allow-list / deny-list** of licenses for the project's distribution model
  (e.g. SaaS vs. shipped binary vs. internal). Typically: allow permissive; review weak copyleft;
  deny AGPL/GPL for proprietary distribution unless legal-approved.
- **Automate the check in CI** (license scanner: FOSSA, ScanCode, `cargo deny`, `pip-licenses`,
  license-checker, Syft); **block** on a disallowed or unknown license. Wire into
  `@rules/workflow-cicd.md` alongside SCA.
- Generate license data in the **SBOM** (it already lists components — add license per component;
  `@rules/std-supplychain.md`).

## Obligations
- **Attribution:** ship the required notices/licenses (a THIRD-PARTY-NOTICES / NOTICE file) for
  permissive + many copyleft licenses. Keep it generated and current.
- **Your own license:** set the project's `LICENSE` deliberately and ensure inbound contributions
  are compatible (CLA/DCO where appropriate — `@rules/workflow-git.md`).
- Re-check on dependency changes; a version bump can change a license.

## References
- **SPDX** license list — spdx.org/licenses; **choosealicense.com**; **TLDRLegal**.
  Index: `@rules/reference-style-guides.md`.
