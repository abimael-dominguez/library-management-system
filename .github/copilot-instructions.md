# Project Architecture: Clean Architecture (Strict)

All code generated, refactored, or suggested by Copilot in this repository **must** follow Clean Architecture. No exceptions. If a user request conflicts with these rules, warn and propose a compliant alternative first.

## Project Structure

```
<service>/
  src/
    domain/
      entities/         # Business objects, aggregates, value objects
      services/         # Domain logic that doesn't belong to a single entity
      exceptions/       # Domain-specific errors
      interfaces/       # ABCs for domain-level contracts (repositories, core service boundaries)
    application/
      use_cases/        # One class per use case; orchestrates domain objects
      interfaces/       # ABCs for technical integration ports (email, storage, external APIs)
      dtos/             # Input/output data transfer objects for use cases
    infraestructure/
      adapters/         # Implementations of domain/application ABCs (repos, API clients, controllers)
      api/              # HTTP routes, request/response handling (inbound adapters)
      config/           # Framework bootstrapping, settings, environment
      persistence/      # DB sessions, migrations, ORM models
      llm_providers/    # LLM client implementations (outbound adapters)
  tests/
    unit/
    integration/
```

## Layer Definitions

### Domain (`src/domain/`)
Pure business logic with **zero external dependencies** — no frameworks, no ORMs, no third-party libraries.

- **entities/**: Pure Python business objects and aggregates.
- **services/**: Cross-entity business logic.
- **exceptions/**: Domain-specific error classes.
- **interfaces/**: ABCs defining contracts the domain needs (e.g., `UserRepository(ABC)`).

### Application (`src/application/`)
Orchestration layer. Depends only on domain.

- **use_cases/**: One class per use case. Receives input via DTOs, delegates to domain and ports.
- **interfaces/**: ABCs for technical integrations (e.g., `EmailSender(ABC)`, `FileStorage(ABC)`).
- **dtos/**: Pydantic models defining input/output shape for use cases.

### Infraestructure (`src/infraestructure/`)
All technical implementations, frameworks, and I/O.

- **adapters/**: Concrete implementations of all ABCs from domain and application.
- **api/**: HTTP route handlers (inbound adapters) — delegate to use cases.
- **config/**: App configuration, DI wiring (composition root), environment loading.
- **persistence/**: ORM models, DB sessions, migrations.
- **llm_providers/**: LLM client implementations (outbound adapters).

## Dependency Rules (Non-Negotiable)

```
domain  ←  application  ←  infraestructure
(inner)                     (outer)
```

1. **Domain imports nothing** from application or infraestructure. Zero external dependencies.
2. **Application imports only from domain.** Never from infraestructure.
3. **Infraestructure imports from both** domain and application to implement their interfaces.
4. **Dependencies always point inward.** Outer layers depend on inner layers, never the reverse.
5. **Dependency Inversion**: Inner layers define ABCs (ports). Outer layers provide implementations (adapters). Use cases depend on ABCs, never on concrete classes.

## Python Conventions

- **Type hints required** on all function signatures and return types.
- **One class per file** for entities, use cases, and interfaces.
- **Naming**: `snake_case` for modules and functions, `PascalCase` for classes.
- **ABCs**: All interface files use `from abc import ABC, abstractmethod`.
- **Tests mirror src structure**: `tests/unit/domain/`, `tests/unit/application/`, `tests/integration/`.
- **Each package has `__init__.py`**.

## SOLID Principles

All code **must** adhere to the SOLID principles. Most are enforced structurally by the Clean Architecture rules above. The one that requires explicit attention:

- **Liskov Substitution Principle (LSP)**: Every concrete implementation of an ABC must be **fully substitutable** for any other implementation of the same ABC — same input/output types, same behavioral contract, no additional preconditions or weakened postconditions.

## Anti-Patterns (Forbidden)

Copilot must **never** generate code that does any of the following:

1. **Business logic in routes/controllers.** Handlers only parse input, call a use case, return output.
2. **Direct DB/ORM calls from domain or application layers.** Use repository interfaces.
3. **Framework types leaking into domain.** No `Request`, `Session`, or `BaseModel` in domain entities.
4. **God classes or fat services.** One responsibility per class. Split if it does more.
5. **Importing infraestructure from domain or application.**
6. **Skipping the use case layer.** Routes → use case → domain, always.
7. **Hardcoding service instantiation inside orchestrators.** Always inject via constructor.
8. **Creating framework objects inside orchestrators.** Inject via params in Phase 1.
9. **Mixing parameter enrichment with execution.** Phase 1 and Phase 3 must be separate.
10. **Positional arguments in `run()`.** Always keyword arguments matching step names.
11. **Raw dictionaries crossing into the application layer.** Convert to Pydantic DTOs at the boundary.

## Copilot Behavior Rules

1. When generating new features, produce the full layer stack: domain → application use case + interface → infraestructure adapter.
2. When a request would violate architecture rules, **warn first** and propose the compliant alternative.
3. When refactoring, move code toward proper layer boundaries — never away from them.
4. When adding tests, place them in the correct mirror directory under `tests/`.

---

## Design Pattern Standard: Interface-Driven Services with Dependency Injection

All multi-step processes, orchestrators, and composed services **must** follow this three-phase pattern. This is a general-purpose design pattern — it applies equally to ETL pipelines, inference engines, API orchestrations, training workflows, or any service composition.

### Core Principles

1. **Interface-first**: Every service defines an ABC in `interfaces/`. One ABC per file. The ABC declares the constructor (with its dependencies) and the main execution method.
2. **Constructor-based dependency injection**: Orchestrator classes receive all collaborating services through `__init__`, referenced by their ABC type — never by concrete class.
3. **Services as parameters**: Callable functions, connectors, framework objects (DB sessions, HTTP clients, etc.) are **injected as parameters** — never instantiated inside the orchestrator or service.

### Mapping to Clean Architecture Layers

This pattern integrates with Clean Architecture as follows:

| Concept | Clean Architecture Layer | Folder |
|---|---|---|
| Orchestrator class | Application (it **is** a use case) | `application/use_cases/` |
| Orchestrator ABC | Application | `application/interfaces/` |
| Domain service ABCs (core contracts) | Domain | `domain/interfaces/` |
| Technical service ABCs (external ports) | Application | `application/interfaces/` |
| Concrete service implementations | Infraestructure | `infraestructure/adapters/` |
| Phase 1 & 2 (param wiring, DI setup) | Infraestructure (composition root) | `infraestructure/config/` |

### Parameter Boundary: Dictionaries vs DTOs

- **Infraestructure layer** (Phase 1 — config wiring): Use **nested dictionaries** for parameter enrichment. This is where runtime objects (sessions, callables, timestamps) are injected into config-loaded structures.
- **Application layer** (Phase 3 — use case execution): Use **Pydantic DTOs** (`application/dtos/`). When parameters cross into the application layer, they must be validated and typed as Pydantic models.
- **Boundary conversion**: The infraestructure config layer is responsible for converting raw dictionaries into DTOs before passing them to the orchestrator's `run()` method.

```python
# infraestructure/config/ — convert dicts to DTOs before calling the use case
from application.dtos.step_1_params import Step1Params

step_1_dto = Step1Params(**conf['process_a_params']['step_1'])
orchestrator.run(step_1_params=step_1_dto, step_2_params=step_2_dto)
```

### Three-Phase Execution Pattern

Whenever code needs to coordinate multiple services, follow these three phases **in order**:

#### Phase 1 — Load & Enrich Parameters (`infraestructure/config/`)

Load static configuration (YAML, env vars, etc.), then **enrich** it at runtime with objects that cannot live in static config (sessions, callables, timestamps). Organize parameters in **nested dictionaries categorized by service/step**.

```python
# Structure: conf['{process_name}_params']['{step}']['{param_group}']['{key}']
conf['process_a_params']['step_1']["source_params"]["db_session"] = session
conf['process_a_params']['step_1']["source_params"]["fetch_callable"] = fetch_func
conf['process_a_params']['step_2']["source_params"]["db_session"] = session
```

**Rules:**
- Top-level key = process/pipeline name.
- Second-level key = step/service name.
- Third-level keys = `source_params`, `destiny_params`, or domain-specific groupings.
- Runtime objects (sessions, callables, timestamps) are injected here, never hardcoded.

#### Phase 2 — Instantiate Orchestrator with Injected Services (`infraestructure/config/`)

Create the orchestrator (use case) by injecting **concrete service instances** through the constructor. Each service implements an ABC from `domain/interfaces/` or `application/interfaces/`.

```python
orchestrator = MyProcess(
    step_1_service=ConcreteStepOneImpl(),   # from infraestructure/adapters/
    step_2_service=ConcreteStepTwoImpl(),   # from infraestructure/adapters/
    step_3_service=ConcreteStepThreeImpl()  # from infraestructure/adapters/
)
```

**Rules:**
- Each constructor argument maps 1:1 to an ABC.
- Services are stateless — all runtime data comes through params.
- Swap implementations to change behavior without modifying the orchestrator.

#### Phase 3 — Execute with Categorized Parameters (`application/use_cases/`)

Call the orchestrator's `run()` method, passing Pydantic DTOs as **keyword arguments**. Each keyword maps to a step/service.

```python
orchestrator.run(
    step_1_params=step_1_dto,
    step_2_params=step_2_dto,
    step_3_params=step_3_dto
)
```

**Rules:**
- One keyword argument per step — always use keyword arguments, never positional.
- The orchestrator calls each service sequentially, passing the corresponding params.
- Output from one service may be injected into the next service's params inside `run()`.

### Orchestrator & Service Rules

1. The ABC defines `__init__` (with service dependencies) and `run` (with step params).
2. The orchestrator stores injected services and orchestrates calls — **no business logic**.
3. Each service ABC has a single-responsibility method with keyword arguments.
4. Log start/end of each service step.

### Testability

- **Unit test each service** in isolation with mock params.
- **Unit test the orchestrator** by injecting mock services and verifying call order/arguments.
- **Integration test** by injecting real services with test configurations.