# Investigation Report: `rawr` Compiler `agent_config_dir` Recursion Bug

**Date:** 2025-04-14

**Objective:** Investigate and verify the reported bug where the `rawr` compiler does not recursively search for agent configurations within the directory specified by `agent_config_dir` in `rawr.config.yaml`.

**Provided Information:**

*   `rawr.config.yaml` location: `rawr.config.yaml` (project root)
*   Compiler source code location: `cli/compiler.py`
*   Reported issue: Compiler only finds configurations directly within `agent_config_dir`, not in subdirectories.
*   Example `agent_config_dir` from `rawr.config.yaml`: `ai/agents/edit`

**Analysis Steps & Findings:**

1.  **Configuration File Analysis (`rawr.config.yaml`):**
    *   Confirmed the setting `agent_config_dir: ai/agents/edit` (line 6).

2.  **Compiler Code Analysis (`cli/compiler.py`):**
    *   The `agent_config_dir` path is loaded via `config_loader.get_agent_config_dir()` (line 31) and passed to the relevant functions.
    *   The primary logic for finding multiple agent configurations resides in the `_compile_all_agents` function (starts line 158).
    *   **Key Finding:** This function iterates through the specified `agent_config_base_dir` (which corresponds to `agent_config_dir`) using `agent_config_base_dir.iterdir()` (line 191).
    *   The `pathlib.Path.iterdir()` method **only yields items directly within the directory**, it does not recurse into subdirectories.
    *   The code then checks for files ending in `.yaml` (line 192) within this non-recursive iteration, expecting files named like `<agent_slug>.yaml`.

**Bug Verification:**

*   The direct use of `Path.iterdir()` in `cli/compiler.py` (line 191) confirms that the directory scanning mechanism is **inherently non-recursive**.
*   The current implementation correctly matches the user's report: it will only find `.yaml` files located directly inside the `ai/agents/edit` directory and will not discover configurations placed in subdirectories like `ai/agents/edit/my_agent/config.yaml`.

**Conclusion:**

The reported bug is verified. The `rawr` compiler currently lacks recursive directory scanning capabilities when processing the `agent_config_dir` due to the use of `Path.iterdir()`. The implementation expects agent configuration files (`<slug>.yaml`) to exist directly within the specified directory, not within nested subdirectories.