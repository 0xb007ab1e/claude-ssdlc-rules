# Topic: Dependency Injection & Inversion of Control

Makes the **Dependency Inversion** principle (master §2) concrete: depend on abstractions and
have dependencies *given* to you, rather than constructing or locating them yourself. Pairs
with `@rules/topic-architecture-patterns.md` (what to invert toward) and `@rules/topic-testing.md`
(why — seams for testing).

## Core idea
- A component **declares what it needs** (via constructor parameters / interfaces) and receives
  it from outside; it does not `new` up its own collaborators or reach for globals/singletons.
- Invert toward **abstractions you own** (ports), not concrete framework/IO types — so business
  logic stays independent of transport, persistence, and vendors.

## How to inject
- **Prefer constructor injection:** dependencies are explicit, required, and can be `final`/
  readonly (immutable, no half-built objects). It makes a class's needs honest — a huge
  constructor is a design smell signalling too many responsibilities (SRP — `@rules/topic-anti-patterns.md`).
- Setter/property injection only for genuinely optional dependencies; **avoid field/reflection
  injection** (hides dependencies, breaks without the container, hard to test).
- **Avoid the Service Locator anti-pattern** — pulling dependencies from a global registry hides
  what a class actually uses and defeats compile-time checking (`@rules/topic-anti-patterns.md`).

## Composition root
- Wire the object graph in **one place** at the application entry point (the *composition root*);
  the rest of the code is unaware of any container. Containers are optional — **manual ("pure")
  DI is explicit and fine**; reach for a container only when wiring volume justifies it, and never
  let it hide dependencies.

## Lifetimes & hazards
- Be deliberate about scope (singleton / scoped / transient). **Captive dependency:** a singleton
  holding a shorter-lived (scoped) dependency leaks/misbehaves — don't.
- Shared singletons must be **stateless or thread-safe** (`@rules/topic-concurrency.md`).
- Inject ambient I/O — **clock, randomness, filesystem, network, env/config** — behind interfaces
  so behavior is deterministic and testable (`@rules/topic-numeric-correctness.md` injectable clock;
  `@rules/topic-architecture-patterns.md` functional core).

## Don't over-abstract
- Not every class needs an interface or injection — introduce a seam where it earns its keep
  (a real boundary, a thing you swap or test). Premature interfaces are their own smell.
- Inject secrets/config via the provided provider, never module-level globals (`@rules/workflow-secrets.md`).

## References
- *Dependency Injection Principles, Practices, and Patterns* (Seemann & van Deursen); Martin
  Fowler — "Inversion of Control Containers and the Dependency Injection pattern".
  Index: `@rules/reference-style-guides.md`.
