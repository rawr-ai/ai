# Compiler Refactor — Overview

This folder contains the working specification for modularising
`cli/compiler.py`.  The **goal** is to break the single ~500 line module into
independent, testable components while preserving the public behaviour
(`compile_agents()` callable and its Typer command).

---

## Current responsibilities

1. CLI / user interaction (Typer + pretty printing)
2. Config discovery (delegates partially to `config_loader`)
3. File I/O & YAML parsing
4. Validation (`pydantic` `GlobalAgentConfig`)
5. Metadata extraction (`extract_registry_metadata`)
6. Registry persistence (read / write global registry)
7. Orchestration / error aggregation (single vs. all agents)

---

## Target package layout

```
cli/compiler/
│  __init__.py          (public façade)
│  cli.py               (Typer entry‑points only)
│  core.py              (orchestrator – AgentCompiler class)
│  loader.py            (filesystem + YAML helper)
│  validator.py         (pydantic wrapper)
│  metadata.py          (extract metadata helpers)
│  registry_bridge.py   (thin wrapper around registry_manager)
│  models.py            (CompileResult dataclass, error types)
legacy.py               (temporary shim while refactoring)
```

Flow: **cli → core → (loader → validator → metadata) + registry_bridge**.

---

## Neutral data object

```python
@dataclass
class CompileResult:
    slug: str
    success: bool
    error: Exception | None = None
    config_path: Path
```

---

## Incremental steps

1. Safety net & legacy shim
2. Carve out `metadata.py`
3. Introduce `loader.py` & `validator.py`
4. Implement `registry_bridge.py`
5. Create the `core.py` orchestrator
6. Re‑build `cli.py` (Typer interface)
7. Deprecate legacy façade

Each numbered file in this directory provides a **detailed, actionable plan**
for the corresponding step.
