# Step 3 – Introduce `loader.py` & `validator.py`

**Objective:** Separate raw file I/O / YAML parsing from Pydantic validation.

---

## Actions

### 3.1  Create `loader.py`

*Path:* `cli/compiler/loader.py`

```python
"""Low‑level helpers for reading agent config files from disk."""

from pathlib import Path
from typing import Dict, Any
import yaml, logging

logger = logging.getLogger(__name__)


class ConfigLoadError(RuntimeError):
    """Raised when YAML cannot be read or parsed."""


def load_raw_config(path: Path) -> Dict[str, Any]:
    """Return YAML as `dict` or raise `ConfigLoadError`."""
    if not path.exists():
        raise ConfigLoadError(f"File not found: {path}")
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise ConfigLoadError(f"YAML parse error in {path}: {e}") from e
    if not isinstance(data, dict):
        raise ConfigLoadError(f"Config at {path} is not a mapping")
    logger.debug("Loaded raw YAML for %s", path)
    return data
```

### 3.2  Create `validator.py`

```python
"""Validation helpers wrapping the Pydantic model."""

from typing import Dict, Any
import logging
from pydantic import ValidationError

from ..models import GlobalAgentConfig

logger = logging.getLogger(__name__)


class ConfigValidationError(RuntimeError):
    """Raised when a config dict fails schema validation."""


def validate(config_dict: Dict[str, Any]) -> GlobalAgentConfig:
    try:
        model = GlobalAgentConfig.model_validate(config_dict)
    except ValidationError as e:
        logger.error("Validation failed: %s", e)
        raise ConfigValidationError("Pydantic validation failed") from e
    return model
```

### 3.3  Update legacy compiler

Replace inline YAML‑load & Pydantic calls with:

```python
from cli.compiler.loader import load_raw_config
from cli.compiler.validator import validate

raw = load_raw_config(config_path)
agent_config = validate(raw)
```

### 3.4  Add tests

* `tests/unit/test_loader_validator.py`
  * happy path (valid YAML returns dict & model)
  * file‑not‑found, YAML error, validation error → exceptions raised

---

## Deliverables

* Two new helper modules.
* Updated import usage inside legacy file.
* Unit tests for loader and validator.

---

## Risks & Mitigations

* **Risk:** Extra import latency impacts CLI startup.  Mitigated because new
  modules are small and pure Python.
* **Risk:** Forgotten vendorised YAML options.  Mitigated by reusing
  `yaml.safe_load` as before.
