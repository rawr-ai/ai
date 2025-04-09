# Findings Report: CLI `--preserve-groups` Feature

This document summarizes the analysis of the `scripts/agent_config_manager` CLI tool to determine the requirements for adding a `--preserve-groups` flag to the `update` command.

## 1. Current Update Flow

The `update` command is initiated from `cli.py`.
*   It uses `argparse` to parse command-line arguments, including the path to the Markdown file defining the agent configuration.
*   It then calls the `commands.update_config` function, passing the necessary arguments.

## 2. `commands.update_config` Logic

*   The function reads and parses the specified Markdown file into a new `AgentConfig` object (`updated_config`) using `markdown_parser.parse_markdown`.
*   It loads the existing configurations from the target JSON file using `config.load_configs`.
*   It iterates through the loaded configurations to find the one with a matching `slug`.
*   **Crucially, upon finding a match, it replaces the entire existing `AgentConfig` object in the list with the newly parsed `updated_config` object.**
*   Finally, it saves the modified list of configurations back to the JSON file using `config.save_configs`.

This complete replacement of the object is the reason why existing fields like `groups` are currently overwritten by the values (or defaults) present in the `updated_config` derived from the Markdown file.

## 3. `groups` Field Handling

*   **Model (`models.py`):** The `AgentConfig` Pydantic model defines the `groups` field, likely with a default value (e.g., `["read"]` as seen in the provided file content).
*   **Loading (`config.py`):** `load_configs` uses the `AgentConfig` model to parse the data loaded from JSON. If the `groups` key is missing for an entry in the JSON, Pydantic assigns the default value from the model. If the key is present, its value is loaded.
*   **Saving (`config.py`):** `save_configs` serializes the list of `AgentConfig` objects back into JSON format. It writes the current value of the `groups` attribute for each object into the output file.

## 4. Required Modification Points

To implement the `--preserve-groups` functionality, changes are needed in:

*   **`cli.py`:** To add the new command-line flag `--preserve-groups` to the `update` subcommand's argument parser.
*   **`commands.py`:** To modify the `update_config` function to:
    *   Accept the value of the new flag as an argument.
    *   Implement conditional logic to copy the `groups` value from the existing configuration to the new configuration *before* the replacement occurs, but only if the flag is set.

## 5. Proposed High-Level Approach

1.  **Add Flag:** Define a `--preserve-groups` argument in `cli.py` for the `update` parser, using `action='store_true'`.
2.  **Pass Flag:** Modify the call to `commands.update_config` in `cli.py` to pass the value of this new flag.
3.  **Conditional Copy:** In `commands.update_config`, after finding the existing configuration object (`config`) and before replacing it with the new one (`updated_config`), check if the `preserve_groups` flag is true. If yes, execute `updated_config.groups = config.groups`.
4.  **Proceed:** Continue with the existing logic to replace the object in the list (`configs[i] = updated_config`) and save the list.