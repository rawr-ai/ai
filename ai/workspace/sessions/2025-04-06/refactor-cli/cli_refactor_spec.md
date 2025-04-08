# Specification: Refactoring `manage_agent_configs.py` CLI (`rawr`)

This document outlines the design for refactoring the `scripts/manage_agent_configs.py` CLI tool, introducing the `rawr` command and a dedicated configuration file.

## 1. CLI Command Structure (`rawr`)

The refactored CLI will be invoked using the root command `rawr`. The existing operations (`add`, `update`, `delete`) will become subcommands.

**Proposed Structure:**

*   **`rawr add <path_to_markdown>`**:
    *   **Action:** Adds a new agent configuration to the target JSON file.
    *   **Argument:** `<path_to_markdown>` - The relative path to the agent's definition Markdown file (e.g., `agents/code/agent_git.md`). The script will derive the agent slug and other necessary metadata from this file or its path.
*   **`rawr update <path_to_markdown>`**:
    *   **Action:** Updates an existing agent configuration in the target JSON file based on the provided Markdown file. It identifies the agent to update using the slug derived from the Markdown file.
    *   **Argument:** `<path_to_markdown>` - The relative path to the agent's definition Markdown file.
*   **`rawr delete <agent_slug>`**:
    *   **Action:** Deletes an agent configuration from the target JSON file.
    *   **Argument:** `<agent_slug>` - The unique identifier (slug) of the agent to be deleted (e.g., `code`).

**Justification:**

*   **Clarity & Convention:** Using subcommands (`add`, `update`, `delete`) under a single root command (`rawr`) is a standard and intuitive CLI pattern (cf. `git`, `docker`). It clearly separates distinct operations.
*   **Discoverability:** This structure makes commands easily discoverable via help flags (e.g., `rawr --help`, `rawr add --help`).
*   **Simplified Usage:** Removing the mandatory `--target-json` flag simplifies invocation. The script now relies on the configuration file for this path. Using the Markdown file path for `add` and `update` streamlines the process, as the script can extract necessary information directly. Using the `agent_slug` for `delete` provides a clear and unambiguous way to target an agent for removal.

## 2. Configuration File

A dedicated YAML configuration file will store necessary paths, centralizing configuration and removing the need for command-line arguments for these values.

*   **File Path:** `ai/cli_config.yaml`
    *   **Justification:** Placing the configuration within the `ai/` directory aligns with existing project structure (e.g., `ai/graph/mcp-config.yaml`) and keeps related configuration files grouped together.
*   **YAML Structure and Key Names:**

    ```yaml
    # Configuration for the 'rawr' CLI tool and potentially other AI-related scripts
    
    agent_config:
      # Path to the target JSON file where agent configurations are stored.
      # This path should be relative to the project root directory.
      # Example: "ai/graph/plays/custom_modes.json"
      target_json_path: "ai/graph/plays/custom_modes.json" 
    
      # Base directory containing the agent definition Markdown files.
      # This path should be relative to the project root directory.
      # Example: "agents/"
      markdown_base_dir: "agents/"
    
    # --- Future sections for other configurations can be added below ---
    ```

    *   **`agent_config`**: A top-level key to namespace configuration related to agent management.
    *   **`target_json_path`**: Stores the relative path to the JSON file containing the agent configurations array. The script will read this path from the config file.
    *   **`markdown_base_dir`**: Stores the relative path to the directory where agent Markdown definition files are located. This helps the script locate and process these files.

## 3. Future-Proofing Considerations

This design provides a foundation for future enhancements:

*   **Co-location of Assets:** The current structure uses a single `target_json_path` and a `markdown_base_dir`. A future iteration could modify the configuration and script logic to support co-locating an agent's Markdown definition and its individual JSON configuration snippet within a dedicated directory per agent (e.g., `agents/<agent_slug>/agent.md`, `agents/<agent_slug>/config.json`). The `markdown_base_dir` still serves as the root for discovering these agent directories. The script would then aggregate these individual JSON snippets into the final target JSON or manage them differently.
*   **Extended Configuration:** The YAML file can be easily extended with new sections and keys to support additional features or other related scripts without disrupting the existing `agent_config` section. For example, adding configuration for different environments (dev, prod) or other CLI tools.
*   **Validation & Metadata:** The script could be enhanced to perform more validation based on metadata potentially included in the Markdown frontmatter or derived from the file structure under `markdown_base_dir`.

This refactoring provides a more conventional, maintainable, and extensible approach to managing agent configurations via the CLI.