# Step 1 – Safety Net & Legacy Shim

**Objective:** Introduce a no‑risk safety layer so that the entire refactor
can be merged incrementally without breaking downstream users or tests.

---

## Actions

1. **Create package directory**
   ```bash
   mkdir -p cli/compiler
   ```

2. **Copy current implementation**
   ```bash
   cp cli/compiler.py cli/compiler/legacy.py
   ```

3. **Add legacy re‑export**
   *Inside `cli/compiler/__init__.py`:*
   ```python
   """Temporary façade to keep public API stable during refactor."""
   from importlib import import_module as _imp

   _legacy = _imp("cli.compiler.legacy")

   # Re‑export compile_agents
   compile_agents = _legacy.compile_agents  # type: ignore
   __all__ = ["compile_agents"]
   ```

4. **Wire module path for backward compatibility**
   Add a shim in the original `cli/compiler.py`:*  
   ```python
   """Do **not** import this module directly.  Use `cli.compiler` instead."""
   from cli.compiler.legacy import *  # noqa: F401,F403  (re‑export public symbols)
   import warnings, logging
   logging.getLogger(__name__).warning("cli/compiler.py is deprecated; use cli.compiler.*")
   ```

5. **Run the test suite**  
   Ensure no failures — behaviour is unchanged.

---

## Deliverables

* `cli/compiler/legacy.py` – verbatim copy of existing code.
* `cli/compiler/__init__.py` – façade re‑export.
* Updated root‑level `cli/compiler.py` that re‑exports from legacy and warns.

---

## Risks & Mitigations

* **Risk:** Import‑path confusion (duplicate symbols).  
  **Mitigation:** Use `__all__` and explicit re‑export.

* **Risk:** Tooling (pytest, linters) flags the wildcard re‑export.  
  **Mitigation:** Add `# noqa` comments only on the shim file.

* **Roll‑back plan:** Delete `cli/compiler` package and revert shim — a
  one‑line git revert.
