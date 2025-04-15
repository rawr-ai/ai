# Debug Report: Failure Analysis for Compiler Recursion Fix

**Date:** 2025-04-15

**Objective:** Analyze why the previous attempt to implement recursive directory scanning in `cli/compiler.py` failed, despite using `rglob`.

**Analysis:**

1.  **Implementation Plan vs. Code:**
    *   The implementation plan correctly identified the need to replace `iterdir()` with `rglob('*.yaml')` for recursive scanning.
    *   The modified code in `cli/compiler.py` (line 192) correctly implements `agent_config_base_dir.rglob('*.yaml')`.
    *   The plan also highlighted the need to verify subsequent logic, particularly how the agent slug and file path were handled.

2.  **Identified Issue:**
    *   The loop in `_compile_all_agents` iterates through `config_path` objects returned by `rglob`. These are *full paths* to the discovered YAML files (e.g., `ai/agents/edit/subdir/my-agent.yaml`).
    *   The agent slug is correctly extracted from the filename using `config_path.stem` (line 193).
    *   However, the extracted `slug_to_compile` and the *original* `agent_config_base_dir` are passed to the `_compile_specific_agent` function (lines 197-201).
    *   Inside `_compile_specific_agent`, the code attempts to load the configuration file by *reconstructing* the path using `agent_config_base_dir / f"{agent_slug}.yaml"` (line 101).
    *   This reconstruction assumes the configuration file is directly within the `agent_config_base_dir`. It ignores the actual subdirectory where `rglob` found the file.

3.  **Root Cause of Failure:**
    *   When `rglob` finds a configuration file in a subdirectory (e.g., `ai/agents/edit/subdir/my-agent.yaml`), `_compile_specific_agent` incorrectly tries to load it from the base directory (e.g., `ai/agents/edit/my-agent.yaml`).
    *   This results in a `FileNotFoundError` within `_compile_specific_agent` (line 107), which is caught and handled as an `AgentLoadError` or `AgentProcessingError` in the calling loop, causing the compilation for that agent to fail.

**Conclusion:**

The previous fix failed because while it correctly implemented recursive file *discovery* using `rglob`, it did not update the file *loading* logic within `_compile_specific_agent` to use the actual full path provided by `rglob`. The loading logic still assumes a flat directory structure.

**Recommendation for Next Steps:**

Modify `_compile_specific_agent` to accept the full `config_path` as an argument instead of the `agent_slug` and `agent_config_base_dir`, and use that path directly for loading the file. Alternatively, modify the call site in `_compile_all_agents` to pass the correct path derived from `config_path` if `_compile_specific_agent`'s signature cannot be changed easily.