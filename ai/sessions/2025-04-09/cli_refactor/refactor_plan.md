# CLI Refactoring Implementation Plan

## 1. Objective Summary

Refactor the project's command-line interface (CLI) tooling based on the proposals outlined in `ai/sessions/2025-04-09/cli_refactor/analysis.md`. The core goals are to:
1.  Rename the primary CLI directory from `scripts` to `cli`.
2.  Establish `cli/main.py` as the single entry point.
3.  Rename internal files and modules for clarity (`agent_config_manager` -> `agent_config`, `config.py` -> `settings.py`, etc.).
4.  Update all internal code references and import statements to reflect the new structure.
5.  Update associated unit and integration tests (`tests/`) to align with the refactored code paths and structure.
6.  Ensure the refactored structure improves maintainability and testability.

This plan is intended for execution by the `code` agent on the `refactor/cli-structure` branch.

## 2. Assumptions

*   The `analysis.md` document accurately reflects the current state and the agreed-upon target structure.
*   All refactoring work will be performed on the `refactor/cli-structure` Git branch.
*   The existing test suite in the `tests/` directory provides adequate coverage of the current CLI functionality.
*   A CLI framework like Typer, Click, or argparse will be used for `cli/main.py` as suggested in the analysis.

## 3. Detailed Refactoring Steps

**Step 1: Rename Top-Level Directory**
*   **Action:** Rename the `scripts/` directory to `cli/`.
*   **Git:** Use `git mv scripts cli` to ensure history is tracked.

**Step 2: Move/Rename Core Logic Module**
*   **Action:** Rename the internal module directory `cli/agent_config_manager/` to `cli/agent_config/`.
*   **Git:** Use `git mv cli/agent_config_manager cli/agent_config`.

**Step 3: Move Configuration File**
*   **Action:** Move the configuration file `cli/cli_config.yaml` to `cli/config.yaml`.
*   **Git:** Use `git mv cli/cli_config.yaml cli/config.yaml`.

**Step 4: Create New Entry Point (`cli/main.py`)**
*   **Action 4.1:** Create the new file `cli/main.py`.
*   **Action 4.2:** Implement the core CLI application setup in `cli/main.py` (e.g., using Typer or Click).
    *   This involves initializing the framework.
    *   Importing command functions from `cli/agent_config/commands.py`.
    *   Registering these functions with the CLI framework.
*   **Action 4.3:** Migrate and merge the entry point logic from the *original* `scripts/manage_agent_configs.py` and `scripts/agent_config_manager/cli.py` into `cli/main.py`. Ensure all argument parsing and command delegation logic is captured.
*   **Action 4.4:** Delete the now redundant files:
    *   Delete `cli/manage_agent_configs.py` (the original entry point, moved in Step 1).
    *   Delete `cli/agent_config/cli.py` (the old CLI logic file, moved in Step 2).
*   **Git:** Add `cli/main.py` and commit the deletions.

**Step 5: Rename Internal Files within `cli/agent_config/`**
*   **Action 5.1:** Rename `cli/agent_config/config.py` to `cli/agent_config/settings.py`.
    *   **Git:** `git mv cli/agent_config/config.py cli/agent_config/settings.py`
*   **Action 5.2:** Rename `cli/agent_config/markdown_parser.py` to `cli/agent_config/markdown_utils.py`.
    *   **Git:** `git mv cli/agent_config/markdown_parser.py cli/agent_config/markdown_utils.py`
*   **Note:** Files `__init__.py`, `commands.py`, and `models.py` within `cli/agent_config/` retain their names but are now in the new location.

**Step 6: Update Internal Imports and Code References**
*   **Action 6.1:** Perform a project-wide search within the `cli/` directory for outdated import statements and references.
    *   Search for `from scripts...` and replace with `from cli...`.
    *   Search for `from agent_config_manager...` and replace with `from cli.agent_config...`.
    *   Search for imports of `config` from the old module and update to `settings` (e.g., `from cli.agent_config.settings import ...`).
    *   Search for imports of `markdown_parser` and update to `markdown_utils`.
*   **Action 6.2:** Specifically modify `cli/agent_config/settings.py` (formerly `config.py`) to load its configuration from the new path `cli/config.yaml`. Update any hardcoded paths or relative path logic.
*   **Action 6.3:** Review `cli/main.py` and `cli/agent_config/commands.py` to ensure all internal function calls and class instantiations use the correct new module paths.

**Step 7: Update Tests (`tests/`)**
*   **Action 7.1:** Identify all test files within the `tests/` directory (including subdirectories like `tests/unit/`, `tests/integration/` if they exist) that import code from the original `scripts/` directory.
*   **Action 7.2:** Update import paths in these test files to reflect the new structure.
    *   Example: `from scripts.agent_config_manager.commands import X` becomes `from cli.agent_config.commands import X`.
    *   Example: `from scripts.agent_config_manager.models import Y` becomes `from cli.agent_config.models import Y`.
*   **Action 7.3:** Review and update test setup, fixtures, and assertions.
    *   Integration tests might need to be modified to invoke the CLI via `cli/main.py` (e.g., using `subprocess` or a framework runner like `CliRunner`).
    *   Unit tests might need adjustments if function signatures or dependencies within `cli/agent_config/` modules have changed slightly during refactoring. Ensure mocks and patches target the new paths.

## 4. Risks and Mitigation

*   **Risk:** Broken internal code references or imports after renaming/moving files.
    *   **Mitigation:** Perform thorough search-and-replace for old paths (`scripts.`, `agent_config_manager.`). Run static analysis tools (e.g., `mypy`, `flake8`) after changes. Execute the full test suite frequently during the process.
*   **Risk:** Test failures due to incorrect import paths or changes in how the CLI is invoked.
    *   **Mitigation:** Systematically update test imports alongside code changes. Carefully review integration test setup to target `cli/main.py`. Run tests after each major step (e.g., after renaming, after updating imports).
*   **Risk:** Logic errors introduced when merging functionality into `cli/main.py`.
    *   **Mitigation:** Carefully review the logic of the original `scripts/manage_agent_configs.py` and `scripts/agent_config_manager/cli.py` before merging. Test the `cli/main.py` entry point thoroughly with various arguments (including `--help`).
*   **Risk:** Configuration loading fails due to path changes.
    *   **Mitigation:** Explicitly test the configuration loading mechanism in `cli/agent_config/settings.py` and ensure it correctly finds `cli/config.yaml`.

## 5. Validation Steps

1.  **Static Analysis:** Run linters and type checkers (e.g., `flake8 cli/`, `mypy cli/`) to catch syntax errors, style issues, and type inconsistencies. Address any reported errors.
2.  **Unit Tests:** Execute the unit test suite (e.g., `pytest tests/unit/`). All tests should pass.
3.  **Integration Tests:** Execute the integration test suite (e.g., `pytest tests/integration/` or relevant path). All tests should pass.
4.  **Manual CLI Checks:** Run basic commands through the new entry point to verify core functionality:
    *   `python cli/main.py --help` (Verify help output reflects available commands)
    *   Execute 1-2 representative commands with typical arguments (e.g., `python cli/main.py agent list`, `python cli/main.py agent create ...`) and check for expected output or side effects.

## 6. Handoff Recommendation

This plan is now ready for execution.

```xml
<switch_mode>
<mode_slug>code</mode_slug>
<reason>To execute the detailed CLI refactoring plan located at ai/sessions/2025-04-09/cli_refactor/refactor_plan.md.</reason>
</switch_mode>