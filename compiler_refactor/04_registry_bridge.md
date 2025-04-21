# Step 4 – Implement `registry_bridge.py`

**Objective:** Isolate direct dependencies on `registry_manager` so that the
compiler core remains testable without writing to disk.

---

## Actions

1. **Create file** `cli/compiler/registry_bridge.py`

```python
"""A minimal abstraction over the existing registry_manager module."""

from pathlib import Path
from typing import Any, Dict
import logging

from .. import registry_manager

logger = logging.getLogger(__name__)


# Re‑export for clarity – consumers import from this façade only


def read_registry(path: Path) -> Dict[str, Any]:
    logger.debug("Reading global registry from %s", path)
    return registry_manager.read_global_registry(path)


def update_registry(agent_config: "GlobalAgentConfig") -> None:  # noqa: F821
    logger.debug("Updating registry with agent %s", agent_config.slug)
    registry_manager.update_global_registry(agent_config)


def write_registry(path: Path, data: Dict[str, Any]) -> None:
    logger.debug("Writing global registry to %s", path)
    registry_manager.write_global_registry(registry_path=path, registry_data=data)
```

2. **Adapt legacy and future code**

Replace direct `registry_manager.*` calls with `registry_bridge.*`.

3. **Stub for tests**

Inside tests you can monkey‑patch `cli.compiler.registry_bridge.update_registry`
to a dummy lambda – removing FS writes during unit testing.

---

## Deliverables

* `registry_bridge.py` file as shown.
* Updated import paths in code.

---

## Risks & Mitigations

* **Risk:** Function signature drift if `registry_manager` changes.  
  **Mitigation:** Keep façade paper‑thin; add mypy type hints to catch breaks.
