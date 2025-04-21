# Step 2 – Carve Out `metadata.py`

**Objective:** Extract the pure function `extract_registry_metadata` from the
monolithic module into its own, single‑responsibility file, together with
unit tests.

---

## Actions

1. **Move the code**
   *New file:* `cli/compiler/metadata.py`
   ```python
   """Helper(s) for transforming a validated GlobalAgentConfig into the
   dictionary persisted in the global registry."""

   import logging
   from typing import Any, Dict

   from ..models import GlobalAgentConfig  # existing Pydantic model

   logger = logging.getLogger(__name__)

   def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
       # >>> paste existing body unchanged <<<
   ```

2. **Adapt imports**
   In `cli/compiler/legacy.py` (and later in new modules) replace
   `from . import compiler` style calls with:
   ```python
   from cli.compiler.metadata import extract_registry_metadata
   ```

3. **Add unit test** (`tests/unit/test_metadata.py`):
   ```python
   from cli.compiler.metadata import extract_registry_metadata
   from cli.models import GlobalAgentConfig

   def test_extract_metadata_minimal():
       cfg = GlobalAgentConfig(slug="foo", name="Foo", roleDefinition="bar")
       md = extract_registry_metadata(cfg)
       assert md["slug"] == "foo"
       assert md["name"] == "Foo"
       # description fallback works
       assert md["description"].startswith("bar")
   ```

4. **Run tests**  
   Ensure green.

---

## Deliverables

* `cli/compiler/metadata.py` containing the function plus logger.
* Modified imports in legacy code.
* New unit test verifying happy path and description‑fallback behaviour.

---

## Risks & Mitigations

* **Risk:** Import path mistakes cause runtime errors.  
  **Mitigation:** Run full CLI fixture compile after change.

* **Risk:** Hidden side‑effects in the original module (should be none).  
  **Mitigation:** Keep function body verbatim; no behaviour change.
