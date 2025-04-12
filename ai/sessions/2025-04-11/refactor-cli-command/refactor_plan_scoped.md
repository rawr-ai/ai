# Refactoring Plan: Remove Non-Compile Commands from CLI

**Objective:** Modify the `rawr` CLI (specifically `cli/main.py` and `cli/constants.py`) to remove all code related to the `add`, `update`, and `delete` commands, leaving only the `compile` command functional. This plan is intended for execution by the `implement` agent.

**Target Files:**
*   `cli/main.py`
*   `cli/constants.py`

**Assumptions:**
*   The code is currently in the state described in the `code_investigation.md` report and user clarifications (commented-out sections exist).
*   No other parts of the codebase rely on the constants or code sections being removed.

**Refactoring Steps:**

1.  **Modify `cli/main.py`:**
    *   **Action:** Delete the commented-out helper function `get_config_paths`.
    *   **Location:** Lines 70 through 94 (inclusive).
    *   **Action:** Delete the commented-out `add_agent_config` command function block.
    *   **Location:** Lines 99 through 128 (inclusive).
    *   **Action:** Delete the commented-out `update_agent_config` command function block.
    *   **Location:** Lines 131 through 173 (inclusive).
    *   **Action:** Delete the commented-out `delete_agent_config` command function block.
    *   **Location:** Lines 176 through 205 (inclusive).
    *   **Action:** Delete the commented-out import block related to old command structure.
    *   **Location:** Lines 15 through 40 (inclusive).
    *   **Action:** Delete the unused import statement for `constants`.
    *   **Location:** Line 8 (`from . import constants`).

2.  **Modify `cli/constants.py`:**
    *   **Action:** Delete the constant definitions for `TARGET_JSON_PATH` and `MARKDOWN_BASE_DIR`.
    *   **Location:** Lines 5 and 6.
    *   **Action:** Delete the constant definitions for `CMD_ADD`, `CMD_UPDATE`, and `CMD_DELETE`.
    *   **Location:** Lines 16, 17, and 18.
    *   **Action:** Delete the constant definitions for `DEFAULT_TARGET_JSON` and `DEFAULT_MARKDOWN_DIR`.
    *   **Location:** Lines 41 and 42.

3.  **Final Check (Mental Verification):**
    *   Ensure the `@app.command("compile")` decorator (around Line 208 in the original `cli/main.py`) and the `compile_agent_config` function definition remain intact and unmodified by the previous steps.
    *   Ensure no other necessary imports or code logic in `cli/main.py` were accidentally removed.

**Acceptance Criteria:**
*   The file `cli/main.py` no longer contains the commented-out code blocks for `get_config_paths`, `add_agent_config`, `update_agent_config`, `delete_agent_config`, or the related old import block.
*   The file `cli/main.py` no longer contains the line `from . import constants`.
*   The file `cli/constants.py` no longer contains the definitions for `TARGET_JSON_PATH`, `MARKDOWN_BASE_DIR`, `CMD_ADD`, `CMD_UPDATE`, `CMD_DELETE`, `DEFAULT_TARGET_JSON`, `DEFAULT_MARKDOWN_DIR`.
*   The `compile` command definition and registration in `cli/main.py` are unchanged.

**Risks/Dependencies:**
*   Low risk, as changes involve removing commented-out code and clearly unused constants.
*   Assumes no external code directly imports or uses the removed constants from `cli/constants.py`.

**Handoff Recommendation:**
*   Execute this plan using the `implement` agent.
*   Suggest using `apply_diff` for targeted removals in both files.