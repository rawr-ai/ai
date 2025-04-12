# Refactoring Plan: `cli` Directory Maintainability

**Date:** 2025-04-12
**Branch:** `refactor/cli-maintainability`
**Context:** Step 4 of Playbook `pb_refactor_codebase.md`. This plan details the implementation steps for the high-priority refactoring candidates identified in `analysis.md` and incorporates decisions from `investigation_report.md`.
**Analysis Report:** `ai/sessions/2025-04-11/modularize-cli/analysis.md`
**Investigation Report:** `ai/sessions/2025-04-11/modularize-cli/investigation_report.md`

## 1. Refactoring Goal

Based on the technical analysis and subsequent investigation, the primary goal is:

1.  **Separate Concerns in `cli/main.py`:** Extract the compilation orchestration logic from the `compile_agent_config` command function to improve modularity, testability, and adherence to the Single Responsibility Principle (SRP).

*(Note: The original goal to rename `cli/agent_config/models.py` is obsolete due to the decision to remove the entire `cli/agent_config/` directory.)*

## 2. Scope of Changes

### Goal 1: Separate Concerns in `cli/main.py`

*   **Files/Directories to Remove:**
    *   `cli/agent_config/` (and all its contents)
*   **Files to Modify:**
    *   `cli/main.py`: Remove orchestration logic from `compile_agent_config`. Update it to instantiate and call the new orchestrator/service, handle its exceptions, and manage CLI interactions (Typer arguments, user feedback). Remove any imports from the now-deleted `cli/agent_config/`.
    *   Any other file importing from or referencing `cli/agent_config/`. These references must be removed or refactored.
*   **Files to Create:**
    *   `cli/compiler.py` (or similar, e.g., `compilation_service.py`): This new module will contain the extracted orchestration logic (e.g., in a `CompilerService` class or dedicated functions). It will handle reading the registry, deciding the compilation flow (single vs. all), calling helper functions (`_compile_single_agent`, `_compile_all_agents` - which might also move here or be called from here), and interacting with `registry_manager` to write the final registry.
*   **Potential Modifications:**
    *   `cli/registry_manager.py`: May require adjustments if the interaction pattern changes slightly with the new orchestrator.
    *   Test files related to `cli/main.py` and potentially `cli/agent_config/`.

## 3. Proposed Sequence & Techniques

The refactoring will proceed in the following order:

1.  **Step 1: Remove `cli/agent_config/` Directory and Orphaned References**
    *   **Technique:** Directory Removal, Code Search & Removal.
    *   **Action:** Delete the `cli/agent_config/` directory entirely.
    *   **Action:** Use search tools (`search_files`) to identify all files importing from or referencing `cli.agent_config` or its former contents (e.g., `AgentConfig`, `schema`, `models`).
    *   **Action:** Remove or refactor the code using these orphaned references. Ensure the application still builds and core functionalities reliant on other parts of `cli` are not broken by missing imports.
    *   **Action:** Run tests to catch immediate `ImportError` issues.

2.  **Step 2: Extract Compilation Orchestration Logic**
    *   **Technique:** Extract Class/Module, Move Method/Function.
    *   **Action:** Create the new file `cli/compiler.py`.
    *   **Action:** Define a new class (e.g., `CompilerService`) or functions within `cli/compiler.py`.
    *   **Action:** Following the TDD cycle (`pb_tdd_cycle.md`), write initial tests for the intended orchestration logic in the new module.
    *   **Action:** Carefully move the core orchestration logic (reading registry, deciding flow, calling compile helpers, writing registry via `registry_manager`) from `cli/main.py::compile_agent_config` to the new `CompilerService` in `cli/compiler.py`. Helper functions like `_compile_single_agent` and `_compile_all_agents` might also be moved or refactored as part of this.
    *   **Action:** Update `cli/main.py::compile_agent_config` to:
        *   Instantiate `CompilerService`.
        *   Call the appropriate method on the service.
        *   Handle exceptions raised by the service and provide user feedback via `typer.echo`.
        *   Focus solely on CLI argument parsing and presentation logic.
    *   **Action:** Adapt existing tests for `cli/main.py` and ensure all tests (old and new) pass.

## 4. Potential Risks & Mitigation

*   **Step 1 Risk:** Incomplete removal of orphaned references leading to `ImportError` or runtime failures in less-tested code paths.
    *   **Mitigation:** Use `search_files` tool extensively across the codebase for `cli.agent_config`. Run all existing tests after removal. Perform manual testing of relevant CLI commands, especially those indirectly related to compilation that might have had subtle dependencies.
*   **Step 2 Risk:** Incorrect extraction or modification of logic leading to behavioral changes or bugs in the compilation process.
    *   **Mitigation:** Strictly adhere to the TDD cycle (`pb_tdd_cycle.md`). Write comprehensive unit tests for the new `CompilerService` *before and during* the extraction. Keep changes small and incremental. Rely heavily on the existing test suite to catch regressions. Perform thorough manual testing of the `compile` command with various scenarios (single agent, all agents, errors).
*   **General Risk:** Merge conflicts if other changes are made concurrently on the `refactor/cli-maintainability` branch.
    *   **Mitigation:** Commit changes frequently after each logical sub-step (e.g., after removal, after extracting a specific part of the logic). Coordinate with other developers if applicable.

## 5. Validation Criteria

Success will be validated by:

1.  **Directory Removal:** Confirmation that the `cli/agent_config/` directory no longer exists.
2.  **Test Suite:** All existing and newly added unit/integration tests must pass after each refactoring step. No tests should fail due to `ImportError` related to `cli.agent_config`.
3.  **TDD Cycle:** Adherence to the Test-Driven Development cycle as outlined in `pb_tdd_cycle.md` for Step 2 (Extraction).
4.  **Functionality:** The `ai-agent compile` command must function identically to the pre-refactoring version from a user's perspective for all core scenarios. Other CLI commands should remain unaffected.
5.  **Code Review:** The refactored code should be reviewed for clarity, adherence to SRP, improved modularity, successful separation of concerns, and complete removal of dependencies on `cli/agent_config/`.
6.  **Static Analysis:** Code linters and static analysis tools should pass without new errors related to the changes.

## 6. Handoff Recommendation

Upon completion and approval of this plan, the next step is to execute the refactoring tasks.

**Recommendation:** Switch to the `implement` mode to carry out the refactoring steps defined in this plan, following the specified sequence and validation criteria.

```sh
# Suggested command for next step
# switch_mode(mode_slug='implement', reason='Execute the updated refactoring plan for cli maintainability.')