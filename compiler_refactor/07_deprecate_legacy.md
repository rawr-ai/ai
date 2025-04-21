# Step 7 – Deprecate Legacy Path & Cleanup

**Objective:** Remove the temporary shim once new modules run in production
without issues.

---

## Preconditions

* New CLI and core pass all unit & integration tests.
* Production (or staging) has run with `ROO_NEW_COMPILER=1` for at least one
  full release cycle.

---

## Actions

1. **Delete files**
   * `cli/compiler/legacy.py`
   * the re‑export shim content in root‑level `cli/compiler.py` (replace with a
     one‑liner importing from new package or delete entirely if no external
     references).

2. **Remove feature flag**
   Delete `ROO_NEW_COMPILER` branches from code & CI scripts.

3. **Update documentation**
   * `cli/docs/*` – replace references to old path.

4. **Git hygiene**
   * `git grep "legacy.py"` should return nothing.

---

## Deliverables

* Clean repository with only the new modular compiler.

---

## Risks & Mitigations

* **Risk:** Undiscovered call sites import from `cli.compiler.legacy`.  
  **Mitigation:** Throw explicit `ImportError` if module imported after deletion.

* **Roll‑back plan:** Revert the deletion commit and re‑enable feature flag.
