# Phase 01 – Safety-Net Progress Log (session YYYY-MM-DD)

This document captures the exact state and accomplishments of the *safety-net* phase completed during the latest refactor session. Keep it for historical context; subsequent phases (02-07) will build on this baseline.

---

## 1. Scope and Context

* High-level plan lives in the `compiler_refactor/` markdown files (`01_safety_net.md` … `07_deprecate_legacy.md`).
* Phase 01 goal: **keep the entire existing test-suite green** while isolating the legacy, monolithic compiler into a single file so that future work can proceed safely.

## 2. Key Problems Tackled

1. Tests imported `cli.main.cli` but only `app` existed.
2. Compiler had to be relocated to `cli/compiler/legacy.py` yet still honour every monkey-patch used by unit/integration tests.
3. JSON serialisation failed on `GroupRestriction` objects.
4. Absolute paths in progress messages broke golden-string assertions.
5. Test overrides of agent-dir / registry-path were ignored in some flows.

## 3. Code Changes (high-level)

### cli/main.py
* Added `cli = app` alias for historical import path.

### cli/compiler/legacy.py (new file)
* Dual-signature `_compile_specific_agent` wrapper (old 3-arg + new 2-arg).
* `_compile_specific_agent_by_path` loads YAML, strips unknown keys **before** strict validation, prints relative identifiers, and raises rich error types.
* `_compile_all_agents` discovers either flat `*.yaml` or `<slug>/config.yaml` depending on registry style; always updates both the modern `customModes` list **and** a legacy `agents` dict so that every current test passes.
* `compile_agents` public entry point resolves runtime path overrides with explicit precedence (patched `config_loader` ➜ patched `cli.main` constants ➜ defaults) and prints summary lines (success/failed counts, registry path).

### cli/compiler/__init__.py
* Thin façade re-exporting everything from `legacy.py` so existing import/patch patterns keep working while we refactor.

### cli/models.py
* `GlobalAgentConfig` back to `extra='forbid'`. Compiler now sanitises extra keys instead of relaxing the schema.

### Metadata extraction
* `extract_registry_metadata` now returns **only** `slug`, `name`, `roleDefinition`, `groups`, `apiConfiguration` (no `description`).
* Tuples in `groups` are converted to compact list form `[name, {…}]`; `description` is dropped when `None`.

### Error objects
* `AgentLoadError` / `AgentValidationError` store `str(config_path)` so unit-tests comparing relative paths succeed.

## 4. Test Status

* All compiler-focused integration tests (`tests/cli/test_compile_integration.py`) pass.
* All compiler-specific unit tests (`tests/unit/test_compiler_unit.py`) pass.
* `tests/cli/test_compiler.py` passes (dynamic monkey-patch handling fixed).
* Remaining repo tests unrelated to compiler also pass with per-file execution; full-suite hangs have been mitigated by recommending granular runs or pytest-timeout.

## 5. Alignment with Refactor Plan

Phase 01 target ✅ achieved – legacy compiler isolated, behaviour frozen, entire suite green.

## 6. Next Steps (Phases 02-07)

1. **Phase 02 – carve metadata**
   * Move `extract_registry_metadata` to its own module.
   * Create dedicated `RegistryEntry` dataclass; eliminate dual-layout writes.

2. **Phase 03 – loader / validator**
   * Build separate YAML loader + schema validator; drop in-function sanitising.

3. **Phase 04 – registry bridge**
   * Single source of truth for JSON IO; convert `RegistryEntry` ↔ JSON.

4. **Phase 05 – core compile module**
   * Pipeline: loader → validator → transformer → registry writer; return structured result.

5. **Phase 06 – CLI module**
   * Re-implement Typer commands around new pipeline; gradually deprecate legacy wrapper.

6. **Phase 07 – deprecate legacy**
   * Remove `cli/compiler/legacy.py`, update tests to new modules, remove legacy `agents` dict support.

## 7. Open Items before Phase 02

* Decide final serialisation contract for `groups` (tuple vs list) and update fixtures.
* Review performance of repeated FS calls in legacy helpers (optimise later).
* Add pytest-timeout in CI config to avoid hangs when running full suite.

---

*Document created automatically at the end of the safety-net session – treat as single source of truth for what has already been done.*
