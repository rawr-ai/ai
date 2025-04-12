# Agent Configuration Path Resolution

This document explains how the `rawr` CLI determines the path to an agent's `config.yaml` file when the `compile` command (or its alias `rawr [agent-slug]`) is invoked.

1.  **Command Invocation:** The process starts when the CLI command is run, e.g., `rawr compile <agent_slug>`. The `<agent_slug>` is passed to the command handler in `cli/main.py`.

2.  **Delegation to Compiler:** The command handler in `cli/main.py` delegates the core compilation logic to the `cli.compiler` module.

3.  **Path Determination in `cli.compiler`:**
    *   The compilation function within `cli.compiler` needs the path to the agent's configuration file.
    *   It retrieves the base directory for agent configurations by calling `config_loader.get_agent_config_dir()`. Let's call this `AGENT_CONFIG_DIR`.
    *   It then constructs the specific agent's config path, typically like this:
        ```python
        # Logic conceptually similar to this happens within cli.compiler
        agent_config_path = AGENT_CONFIG_DIR / agent_slug / "config.yaml"
        ```
    *   This combines three parts:
        *   `AGENT_CONFIG_DIR`: The base directory for all agent configurations, obtained from `config_loader`.
        *   `agent_slug`: The slug provided via the command line, used as the subdirectory name.
        *   `"config.yaml"`: The fixed filename within the agent's subdirectory.

4.  **Determining `AGENT_CONFIG_DIR` via `config_loader.py`:**
    *   The value of `AGENT_CONFIG_DIR` is determined by the `config_loader.py` module when the application starts.
    *   `config_loader.load_config()` determines the path using the following precedence:
        1.  **Environment Variable:** `RAWR_AGENT_CONFIG_DIR`. If set, its value is used (resolved to an absolute path).
        2.  **Local Config File:** The `agent_config_dir` key in `rawr.config.local.yaml` (relative to the project root). If found, this overrides the main config value.
        3.  **Main Config File:** The `agent_config_dir` key in `rawr.config.yaml` (relative to the project root). If found, this overrides the code default.
        4.  **Code Default:** If none of the above are set, the hardcoded default path `PROJECT_ROOT / "cli/agent_config"` is used (defined in `cli/config_loader.py`). **Note:** As of the last review, this default points to a directory structure (`cli/agent_config/`) that may have been removed or refactored elsewhere. The effective configuration likely relies on one of the higher-precedence methods (Env Var, `rawr.config.local.yaml`, or `rawr.config.yaml`) to specify the correct location for agent configurations.
    *   The final path is resolved to an absolute path and stored in the `settings` dictionary, accessible via `config_loader.get_agent_config_dir()`.

In essence, the CLI takes the `agent_slug`, finds the base agent configuration directory (`AGENT_CONFIG_DIR`) through a prioritized configuration loading mechanism managed by `config_loader.py`, and the `cli.compiler` module combines them to form the final path: `<AGENT_CONFIG_DIR>/<agent_slug>/config.yaml`.