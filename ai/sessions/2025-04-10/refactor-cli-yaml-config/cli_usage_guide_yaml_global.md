# CLI Usage Guide: Managing Global Modes with config.yaml

**Date:** 2025-04-10
**Version:** 1.0

## Overview

This guide explains how to use the `cli compile` command with a `config.yaml` file to add or update agent modes in the **global** Roo Code mode registry (`custom_modes.json`). This method provides a structured way to define mode metadata separate from custom instructions.

**Note:** This process *only* affects the global `custom_modes.json` registry. It does not generate project-level instruction files or manage project-specific modes (`.roomodes`).

## The `compile` Command for Global Modes

The primary command used is `cli compile`.

### Syntax

```bash
cli compile <agent-slug>
```

*   `<agent-slug>`: This is the unique identifier (the `slug` field) of the agent mode you want to add or update in the global registry.

### How it Works

1.  **Discovery:** The command expects to find a configuration file named `config.yaml` within a directory named after the `<agent-slug>` relative to your current working directory.
    *   Example: If you run `cli compile my-cool-agent`, the tool will look for `./my-cool-agent/config.yaml`.
2.  **Loading & Validation:** It loads the `config.yaml` file and validates its structure and content against the required schema for global mode updates. See the `config_yaml_schema_global.md` document for schema details.
3.  **Metadata Extraction:** If validation succeeds, the command extracts the necessary metadata fields (`slug`, `name`, `roleDefinition`, `groups`, and optionally `apiConfiguration`). Fields like `customInstructions` are ignored for global registry updates.
4.  **Registry Update:** The command accesses the global `custom_modes.json` file and adds or updates the entry for the specified `<agent-slug>` using the extracted metadata.
5.  **Feedback:** The command provides feedback on success or failure.

## Creating Your `config.yaml`

You need to create a `config.yaml` file that defines the metadata for your global agent mode.

### File Location

Place your `config.yaml` file inside a directory named exactly like the agent's `slug`.

*   Example Structure:
    ```
    your-workspace/
    └── my-cool-agent/
        └── config.yaml
    ```
*   Run the command from `your-workspace/`: `cli compile my-cool-agent`

### File Content & Schema

The `config.yaml` file must adhere to the schema defined in `config_yaml_schema_global.md`. Key required fields include:

*   `slug`: Unique identifier (must match the directory name and the command argument).
*   `name`: Human-readable name.
*   `roleDefinition`: The core prompt defining the agent.
*   `groups`: List of tool groups the agent can access.

Optional fields like `apiConfiguration` can also be included.

**Example `config.yaml`:**

```yaml
# ./my-cool-agent/config.yaml

slug: "my-cool-agent"
name: "My Cool Agent"
roleDefinition: |
  # Core Identity & Purpose
  *   **Your Role:** A helpful agent.
  *   **Your Expertise:** Being cool.
  *   **Your Primary Objective:** Assist with cool tasks.
groups:
  - "read"
  - "write"
apiConfiguration:
  model: "gpt-4-turbo-preview"

```

## Expected Feedback

*   **Success:** You should see a confirmation message indicating that the agent mode `<agent-slug>` was successfully compiled and the global registry was updated.
*   **Validation Errors:** If the `config.yaml` file is missing, malformed, or does not meet the schema requirements, the command will output specific error messages indicating the problem (e.g., "Missing required field: name", "Invalid type for field: groups").
*   **File Not Found:** If the directory or `config.yaml` file cannot be found based on the `<agent-slug>`, an error message will indicate this.

## Troubleshooting

*   **Schema Errors:** Carefully check your `config.yaml` against the `config_yaml_schema_global.md` document. Ensure all required fields are present and have the correct data types. Pay attention to indentation in YAML.
*   **File/Directory Not Found:** Verify that:
    *   You are running the `cli compile <agent-slug>` command from the parent directory containing the `<agent-slug>/` directory.
    *   The directory name exactly matches the `slug` in your `config.yaml` and the `<agent-slug>` argument in the command.
    *   The configuration file is named exactly `config.yaml` inside that directory.
*   **Registry Access Issues:** If the command reports errors accessing or writing to the global `custom_modes.json`, this might indicate a permissions issue or an unexpected problem with the Roo Code installation environment. Consult the `global_registry_access.md` document for details on expected access patterns.