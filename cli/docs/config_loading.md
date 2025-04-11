Based on the provided code, here's how the `compile` command in `cli/main.py` determines the path to an agent's `config.yaml` using the `agent_slug`:

1.  **Command Invocation:** The process starts when the CLI command is run, e.g., `python cli/main.py compile <agent_slug>`. The `<agent_slug>` is passed as an argument to the `compile_agent_config` function in `cli/main.py`.

2.  **Path Construction in `main.py`:**
    *   Inside `compile_agent_config`, line 216 constructs the path:
        ```python
        agent_config_path = AGENT_CONFIG_DIR / agent_slug / "config.yaml"
        ```
    *   This combines three parts:
        *   `AGENT_CONFIG_DIR`: The base directory for all agent configurations.
        *   `agent_slug`: The slug provided via the command line, used as the subdirectory name.
        *   `"config.yaml"`: The fixed filename within the agent's subdirectory.

3.  **Determining `AGENT_CONFIG_DIR`:**
    *   The value of `AGENT_CONFIG_DIR` is obtained on line 45 of `main.py`:
        ```python
        AGENT_CONFIG_DIR = config_loader.get_agent_config_dir()
        ```
    *   This delegates the path lookup to the `config_loader.py` module.

4.  **Configuration Loading in `config_loader.py`:**
    *   `get_agent_config_dir()` (lines 78-80) retrieves the path from the `settings` dictionary (key: `'agent_config_dir'`).
    *   The `settings` dictionary is populated by `load_config()` (line 75) when the module loads.
    *   `load_config()` (lines 18-72) determines the `agent_config_dir` path using the following precedence:
        1.  **Environment Variable:** `RAWR_AGENT_CONFIG_DIR` (Lines 58-61).
        2.  **Local Config File:** `agent_config_dir` key in `rawr.config.local.yaml` (relative to project root) (Lines 54-55, 31-49).
        3.  **Main Config File:** `agent_config_dir` key in `rawr.config.yaml` (relative to project root) (Lines 51-52, 31-49).
        4.  **Code Default:** `PROJECT_ROOT / "cli/agent_config"` (Line 15).
    *   The final path is resolved to an absolute path (line 69).

In essence, the command takes the `agent_slug`, finds the base agent configuration directory (`AGENT_CONFIG_DIR`) through a prioritized configuration loading mechanism, and then combines them to form the final path: `<AGENT_CONFIG_DIR>/<agent_slug>/config.yaml`.