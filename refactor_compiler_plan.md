# Modularising `cli/compiler.py`

`cli/compiler.py` is ~400–600 LOC and mixes many responsibilities.  This
document captures a safe, incremental roadmap to split it into focused
modules while preserving the public API (`compile_agents` and the Typer
command).

---

## 1  Current responsibilities

1. CLI / user interaction (Typer + pretty printing)
2. Config discovery (delegates partially to `config_loader`)
3. File I/O & YAML parsing
4. Validation (`pydantic` `GlobalAgentConfig`)
5. Metadata extraction (`extract_registry_metadata`)
6. Registry persistence (read / write global registry)
7. Orchestration / error aggregation (single vs. all agents)

---

## 2  Target package layout

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

Data‑flow is strictly one‑directional: `cli → core → (loader → validator →
metadata) + registry_bridge`.  This prevents circular imports.

---

## 3  Neutral data objects

```python
@dataclass
class CompileResult:
    slug: str
    success: bool
    error: Exception | None = None
    config_path: Path
```

`core.AgentCompiler` returns `list[CompileResult]`, replacing multiple loosely
coupled lists/counts.

---

## 4  Incremental git commits

1. **Safety net**  
   • Copy current `compiler.py` to `cli/compiler/legacy.py`.  
   • Re‑export `compile_agents` from the legacy file to keep behaviour green.

2. **Carve out `metadata.py`**  
   Move `extract_registry_metadata` unchanged; add unit tests.

3. **Introduce `loader.py` & `validator.py`**  
   – `loader.load_raw_config(path) -> dict`  
   – `validator.validate(data) -> GlobalAgentConfig`

4. **`registry_bridge.py`**  
   Thin wrappers for `registry_manager.read_global_registry` and
   `update_global_registry`.

5. **`core.py`**  
   Implement `AgentCompiler` with:
   ```python
   compile_agent(path: Path) -> CompileResult
   compile_all(base_dir: Path) -> list[CompileResult]
   ```

6. **`cli.py`**  
   Re‑build Typer UX that consumes `AgentCompiler` results and mimics current
   console output.

7. **Deprecate legacy**  
   Replace top‑level `cli/compiler.py` with thin façade importing from the new
   package and emitting a deprecation warning.  Remove `legacy.py` after a
   grace period.

---

## 5  Risk mitigation

* Keep `legacy.py` and feature‑flag the new flow via
  `ROO_NEW_COMPILER=1` until stable.
* Manual CLI runs on fixture directories before/after each commit.
* Copy logic verbatim first, avoid behaviour changes.

---

## 6  Clean‑up & future work

* Delete `legacy.py`, remove feature flag once stable.
* Extend `CompileResult` with timing metrics or structured error codes.
* Replace ad‑hoc `print`/`typer.echo` with `rich` once CLI stabilises.

---

Following this roadmap will shrink every individual file to <150 LOC, enable
focused unit testing, and set the stage for future enhancements such as
parallel compilation, dry‑run mode, or richer CLI output.
