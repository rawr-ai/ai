# Current State of Recursive Agent‑Config Loading in RAWR CLI

_Last updated: 2025‑04‑17_

## 1. Scope of analysis
* Config path resolution (`cli/config_loader.py`)
* Recursive discovery & compilation of agent configs in `ai/agents/**` via `rawr compile`
* Test‑suite coverage
* Real‑world execution after deleting the registry

## 2. Key observations

### 2.1 Config loading – **working**
Precedence & absolute‑path handling behave exactly as documented; 15 loader unit tests are green.

### 2.2 Recursive compilation – **partially implemented & broken**

| Area | Problem |
|------|---------|
| File‑name convention | Compiler expects `<slug>.yaml`; repo stores `<slug>/config.yaml`, so every discovered file is named `config.yaml` and the inferred slug is always `"config"`. |
| Registry update | Compiler writes to `final_registry_data['agents'][slug]`, yet registry schema is `{"customModes": [...]}`. Key mismatch raises `KeyError` that is silently swallowed, leaving registry empty. |
| Single‑agent path | `rawr compile <slug>` builds `<slug>.yaml` path and always fails (file not found). |
| Error / exit flow | Failures bubble up to Typer as `click.exceptions.Exit` (code 1) but console output first prints a seemingly successful “registry read” message – confusing UX. |

### 2.3 Real‑world run after deleting registry

```bash
$ rm -rf .rawr_registry
$ rawr compile    # executed in sandbox
Reading global registry from .../.rawr_registry/custom_modes.json...
✅ Global registry read successfully.
--- Compiling All Agents ---
...
❌ Compilation finished. All 18 attempted agent(s) failed. Registry not updated.
Exit code = 1
```

No new `.rawr_registry/custom_modes.json` is produced – confirmation that the compile pathway is unusable with the current repo layout.

### 2.4 Tests
A duplicate test‑module name (`tests/unit/test_compiler.py` vs. `tests/cli/test_compiler.py`) produces a PyTest collection error, so compiler tests never run; the defect goes undetected in CI.

## 3. Implementation status
* Config loader: **✅ fully implemented & reliable**
* Recursive config loading / compile: **🟡 partially implemented, currently non‑functional**
* Related test coverage: **🟡 present but ineffective (collection clash)**

## 4. Next steps (recommended order)
1. Accept canonical path `<agent_dir>/config.yaml`; derive slug from YAML `slug` field, not filename.
2. Use `registry_manager.update_global_registry()` for writes so schema (`customModes`) is honoured.
3. Update single‑agent compile path to locate `<slug>/config.yaml` (optionally fall back to `<slug>.yaml`).
4. Emit explicit error if registry structure unexpected instead of swallowing `KeyError`.
5. Fix PyTest duplicate filenames; ensure compiler integration tests execute.
6. Add tests for nested sub‑dirs, duplicate slugs, malformed YAML, etc.
7. Include `rawr compile` in CI pipeline (after deleting registry) to assert end‑to‑end success.

## 5. Conclusion
Recursive agent‑config loading **exists but does not yet work** with the real `ai/agents` directory. Addressing the points above will bring the feature to a fully operational state and close the gap between tests and production behaviour.
