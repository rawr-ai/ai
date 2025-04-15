# Revised Implementation Plan: Fix `rawr` Compiler Recursive Path Handling

**Date:** 2025-04-15
**Based on Debug Report:** `ai/sessions/2025-04-11/fix-compiler-recursion/debug_report_failure_analysis.md`

## 1. Objective Summary

Revise the implementation in `cli/compiler.py` to correctly handle the full file paths returned by the recursive directory scan (`rglob`), ensuring that agent configuration files found in subdirectories are loaded using their actual paths, resolving the failure identified in the debug report.

## 2. Assumptions

*   The target file for modification is `cli/compiler.py`, and its content matches the version read during planning.
*   The core issue lies in `_compile_specific_agent` reconstructing the path instead of using the full path provided by the caller (`_compile_all_agents`).
*   The `rglob` implementation in `_compile_all_agents` correctly discovers files recursively.

## 3. Implementation Steps

1.  **Modify `_compile_specific_agent` Signature (Function Definition around line 74):**
    *   Change the function signature to accept the full `config_path: Path` instead of `agent_slug: str` and `agent_config_base_dir: Path`.
    *   Update the type hints and docstring (lines 74-97) to reflect this change. The function will now receive the direct path to the config file.
    *   **Example Signature Change:**
        *   **Current:** `def _compile_specific_agent(agent_slug: str, agent_config_base_dir: Path, current_registry_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:`
        *   **Proposed:** `def _compile_specific_agent(config_path: Path, current_registry_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:`

2.  **Update `_compile_specific_agent` Logic (Inside the function, lines 99-155):**
    *   **Extract Slug:** Add a line near the beginning to extract the `agent_slug` from the provided `config_path`: `agent_slug = config_path.stem`.
    *   **Remove Path Reconstruction:** Delete the line `agent_config_path = agent_config_base_dir / f"{agent_slug}.yaml"` (line 101).
    *   **Use Direct Path:** Replace all subsequent uses of the variable `agent_config_path` with the function parameter `config_path` (e.g., in `if not config_path.exists():`, `config_path.read_text()`, error messages, logging statements within this function - check lines approx. 106, 108, 111, 117, 118, 121).
    *   **Update Logging/Errors:** Ensure all logging messages and exception arguments within this function that previously used the `agent_slug` parameter now use the locally extracted `agent_slug` variable (check lines approx. 99, 115, 117, 119, 121, 122, 125, 126, 130, 131, 133, 134, 136, 143, 146, 147, 148, 150, 154).

3.  **Modify `_compile_all_agents` Call Site (Inside the loop, around lines 197-201):**
    *   Update the call to `_compile_specific_agent` to pass the `config_path` variable (which holds the full path from `rglob`) instead of `slug_to_compile` and `agent_config_base_dir`.
    *   **Example Call Change:**
        *   **Current:** `_compile_specific_agent(slug_to_compile, agent_config_base_dir, initial_registry_data)`
        *   **Proposed:** `_compile_specific_agent(config_path, initial_registry_data)`

4.  **Update `compile_agents` for Single Agent Case (Inside the `if agent_slug:` block, around lines 273-275):**
    *   **Construct Path:** Before calling `_compile_specific_agent`, construct the full path for the single agent: `single_agent_config_path = agent_config_dir / f"{agent_slug}.yaml"`.
    *   **Update Call:** Modify the call to `_compile_specific_agent` to pass the constructed `single_agent_config_path` instead of `agent_slug` and `agent_config_dir`.
    *   **Example Call Change:**
        *   **Current:** `_compile_specific_agent(agent_slug, agent_config_dir, initial_registry_data)`
        *   **Proposed:** `_compile_specific_agent(single_agent_config_path, initial_registry_data)`

## 4. Acceptance Criteria

*   The `rawr` compiler successfully discovers and processes `*.yaml` files located in immediate subdirectories of the configured `agent_config_dir`.
*   The `rawr` compiler successfully discovers and processes `*.yaml` files located in deeply nested subdirectories within the `agent_config_dir`.
*   The `rawr` compiler continues to correctly process `*.yaml` files located directly within the `agent_config_dir`.
*   Compiling a single agent using its slug still works correctly.
*   The compiler correctly ignores non-YAML files or files not matching the expected naming pattern within the scanned directories.

## 5. Risks and Dependencies

*   **Dependency:** Assumes standard Python `pathlib` module is available and used correctly.
*   **Risk (Low):** Potential for errors if any usage of `agent_config_path` or `agent_slug` within `_compile_specific_agent` is missed during the update. Careful review by the implementation agent is needed.
*   **Risk (Low):** The single agent compilation logic in `compile_agents` must correctly construct the path before calling the modified helper function.

## 6. Handoff Recommendation

Switch to the `implement` agent to execute this revised plan. Provide the path to this plan file and the target file `cli/compiler.py`.