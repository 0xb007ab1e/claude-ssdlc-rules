# Template: Embedded / Firmware — project CLAUDE.md

For microcontroller/RTOS/bare-metal or embedded Linux firmware. Copy to the project's root
`CLAUDE.md`. Inherits the master automatically.

```markdown
# <DeviceName> — firmware rules

> Inherits the master SSDLC ruleset (~/.claude/CLAUDE.md) automatically.

## Applied rule modules
@~/.claude/rules/lang-cpp.md               # see its "Embedded/firmware note" (MISRA/CERT) — or lang-rust
@~/.claude/rules/topic-cryptography.md     # secure boot, signing, device keys
@~/.claude/rules/std-cwe.md                # memory-safety weaknesses are paramount
@~/.claude/rules/std-supplychain.md        # signed firmware images + SBOM
@~/.claude/rules/workflow-cicd.md
@~/.claude/rules/workflow-vuln-mgmt.md
@~/.claude/rules/topic-license-compliance.md
@~/.claude/rules/workflow-cve-management.md # track CVEs in the RTOS/libs/SoC SDK

## Stack
- MCU/SoC: <...>; RTOS/none: <FreeRTOS / Zephyr / bare-metal / embedded Linux>; toolchain: <...>

## Project-specific rules
- **Memory safety first:** prefer Rust or a MISRA C/CERT C subset; static allocation, bounded
  loops, no dynamic allocation in critical paths; validate ALL input (sensors, radio, serial,
  bus) as untrusted (`@rules/lang-cpp.md`).
- **Secure boot + signed firmware:** verify image signatures before execution; chain of trust
  from a hardware root (`@rules/topic-cryptography.md`, `@rules/std-supplychain.md`).
- **Secure OTA update:** authenticated, integrity-checked, atomic with rollback (A/B
  partitions); never apply unsigned updates; anti-rollback to block downgrade attacks.
- **Device identity & secrets:** per-device keys in secure element/TPM where available; no
  shared/hardcoded keys or debug creds in shipping images.
- **Lock down debug:** disable/secure JTAG/SWD/UART consoles in production; enable MCU
  readout/flash protection.
- **Watchdogs + fail-safe** defaults; defined safe state on fault. Resource-constrained: bound
  CPU/RAM/power; no unbounded buffers.
- **HW-in-the-loop tests** + static analysis (MISRA/CERT) in CI; track CVEs in the RTOS, SoC
  SDK, and bundled libraries (`@rules/workflow-cve-management.md`).
```
