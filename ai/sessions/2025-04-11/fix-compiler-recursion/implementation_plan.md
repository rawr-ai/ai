# Implementation Plan: Fix `rawr` Compiler `agent_config_dir` Recursion

**Date:** 2025-04-14

## 1. Objective Summary

Modify the `rawr` compiler (`cli/compiler.py`) to recursively search for agent configuration files (identified as `<agent_slug>.yaml` in the relevant code section per the investigation report) within the directory specified by `agent_config_dir` in `rawr.config.yaml`.

## 2. Assumptions (Based *only* on the Investigation Report)

*   The target file for modification is `cli/compiler.py`.
*   The relevant logic is within the `_compile_all_agents` function (starting around line 158).
*   The current non-recursive directory iteration uses `agent_config_base_dir.iterdir()` (around line 191).
*   The code currently expects agent configuration files named `<agent_slug>.yaml` directly within the `agent_config_base_dir` (based on the check mentioned for line 192).

## 3. Implementation Steps

1.  **Locate File:** Open the file `cli/compiler.py`.
2.  **Locate Function:** Navigate to the `_compile_all_agents` function (report indicates it starts around line 158).
3.  **Identify Iteration:** Find the line performing directory iteration, reported as `agent_config_base_dir.iterdir()` (around line 191).
4.  **Modify Iteration for Recursion:**
    *   Replace the non-recursive `agent_config_base_dir.iterdir()` call with a recursive equivalent using `pathlib`. The recommended approach is to use `agent_config_base_dir.rglob('*.yaml')`. This method recursively finds all files ending in `.yaml` within the `agent_config_base_dir`.
    *   **Example Change (Conceptual):**
        *   **Current (around line 191):** `for item in agent_config_base_dir.iterdir():`
        *   **Proposed:** `for config_path in agent_config_base_dir.rglob('*.yaml'):`
5.  **Verify Subsequent Logic:**
    *   Review the logic immediately following the loop (reported as checking for `.yaml` files around line 192).
    *   Since `rglob('*.yaml')` already yields only `.yaml` files (`Path` objects), the explicit check `if item.is_file() and item.suffix == '.yaml':` (or similar, based on actual code) might become redundant or need adjustment.
    *   Ensure the logic correctly extracts the agent slug from the `config_path` (which will now be a full path including subdirectories) and proceeds with compilation as intended. The existing logic likely derives the slug from the filename, which should still be feasible.

## 4. Acceptance Criteria

*   The `rawr` compiler successfully discovers and processes `<agent_slug>.yaml` files located in immediate subdirectories of the configured `agent_config_dir`.
*   The `rawr` compiler successfully discovers and processes `<agent_slug>.yaml` files located in deeply nested subdirectories within the `agent_config_dir`.
*   The `rawr` compiler continues to correctly process `<agent_slug>.yaml` files located directly within the `agent_config_dir`.
*   The compiler correctly ignores non-YAML files or files not matching the expected naming pattern within the scanned directories.

## 5. Risks and Dependencies

*   **Dependency:** Assumes standard Python `pathlib` module is available and used.
*   **Risk (Minor):** Potential minor performance impact if `agent_config_dir` contains an exceptionally large number of nested files and directories.
*   **Risk:** The implementation must correctly handle the `Path` objects returned by `rglob` (which include the full path) in the subsequent processing logic (e.g., slug extraction).
*   **Consideration (Not explicitly in report):** Behavior with symbolic links within the `agent_config_dir` is not specified. `rglob` typically follows symlinks to directories on POSIX systems. The implementer should be aware of this default behavior.

## 6. Handoff Recommendation

Switch to the `implement` agent to execute this plan.