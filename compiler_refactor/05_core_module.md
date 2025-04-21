# Step 5 – Build `core.py` (AgentCompiler)

**Objective:** Centralise orchestration logic in a class with a narrow
surface: compile one agent file, or compile all agents in a directory,
returning structured `CompileResult` objects.

---

## Public interface

```python
class AgentCompiler:
    def compile_agent(self, path: Path) -> CompileResult: ...
    def compile_all(self, base_dir: Path) -> list[CompileResult]: ...
```

No IO (print / typer) in this layer – caller handles UX.

---

## Actions

1. **Create file** `cli/compiler/core.py`

Key implementation notes:

* Depends on helper modules introduced earlier:
  ```python
  from .loader import load_raw_config
  from .validator import validate
  from .metadata import extract_registry_metadata
  from .registry_bridge import update_registry
  from .models import CompileResult
  ```
* Each method catches exceptions **once**, wraps them into `CompileResult`
  instead of printing.
* `compile_all` collects all results and returns list.

2. **Add `models.py`** (if not yet added)

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CompileResult:
    slug: str
    success: bool
    error: Optional[Exception]
    config_path: Path
```

3. **Unit tests** (`tests/unit/test_core_compiler.py`)

* Use tmpdir to create minimal YAML → assert `CompileResult.success`.
* Inject stub for `registry_bridge.update_registry` via monkeypatch so no disk IO.

---

## Deliverables

* `cli/compiler/core.py` with `AgentCompiler` class.
* `cli/compiler/models.py` for `CompileResult`.
* New tests.

---

## Risks & Mitigations

* **Risk:** Silent failure swallowed by CompileResult.  
  **Mitigation:** Log at ERROR level inside exception handler; propagate error
  object in result.

* **Risk:** Performance overhead for large agent sets.  
  **Mitigation:** Logic equivalent to prior; no regression expected.
