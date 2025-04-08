# Comparison: manage_agent_configs.py (Old vs. Current)

This document outlines the functional differences between the older version of the script (`ai/sessions/2025-04-08/old-test-suite-merge/manage_agent_configs.py`) and the current version (`scripts/manage_agent_configs.py`).

## Functional Differences:

1.  **Custom Instructions Headings:**
    *   **Old:** `CUSTOM_INSTRUCTIONS_HEADINGS = ["## Custom Instructions", "## Mode-specific Instructions"]`
    *   **Current:** `CUSTOM_INSTRUCTIONS_HEADINGS = ["## Custom Instructions", "## Mode-specific Instructions", "## Standard Operating Procedure (SOP) / Workflow"]`
    *   **Impact:** The current version recognizes and parses content under the `"## Standard Operating Procedure (SOP) / Workflow"` heading as part of `customInstructions`.

2.  **AgentConfig Model:**
    *   **Old:** Model includes `slug`, `name`, `roleDefinition`, `customInstructions`.
    *   **Current:** Adds an optional `groups: Optional[List[Any]] = Field(default=["read"])` field.
    *   **Impact:** The current version introduces a `groups` field (defaulting to `["read"]`) into the agent configuration structure and the output JSON.

3.  **CLI Configuration Loading & Path Resolution:**
    *   **Old:**
        *   Uses `-c`/`--config` argument for config file path.
        *   Resolves relative paths *within* the config file based on the *config file's directory*.
    *   **Current:**
        *   *Hardcodes* the config file path to `scripts/cli_config.yaml`.
        *   Resolves relative paths *within* the config file based on the *current working directory*.
    *   **Impact:** Significant change in how the config file is located and how paths inside it are interpreted.

4.  **CLI Arguments for Add/Update:**
    *   **Old:** Uses named argument `--md-path`.
    *   **Current:** Uses positional argument `path_to_markdown_file`.
    *   **Impact:** Command-line invocation syntax for `add` and `update` operations has changed.

## Summary:

The current version (`scripts/manage_agent_configs.py`) introduces changes to Markdown parsing (new heading), data structure (`groups` field), configuration file handling (hardcoded path, different relative path resolution), and command-line arguments (positional vs. named).