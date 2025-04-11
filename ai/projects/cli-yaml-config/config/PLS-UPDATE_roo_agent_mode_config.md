# Roocode Custom Mode/Agent Configuration Guide

This document summarizes how to configure custom modes (agents) in Roocode, based on information scraped from the official documentation URLs:
- `https://docs.roocode.com/community`
- `https://docs.roocode.com/features/custom-modes/`
- `https://docs.roocode.com/features/tools/tool-use-overview`

## Configuration Format & Location

*   **Format:** Custom modes are defined using **JSON**.
*   **Structure:** Configuration files contain a top-level `customModes` array. Each object within this array defines a single custom mode.
*   **Locations:**
    *   **Global Modes:** Defined in `custom_modes.json`. These modes are available across all workspaces. (The exact file path for global settings was not specified in the scraped text but is likely in a user-level configuration directory).
    *   **Project-Specific Modes:** Defined in a `.roomodes` file located in the **project's root directory**.
*   **Precedence:** Project-specific (`.roomodes`) settings override Global (`custom_modes.json`) settings, which in turn override Roocode's default mode settings.

## Mode Definition JSON Structure

Each object within the `customModes` array should have the following properties:

```json
{
  "slug": "example-mode", // Required: Unique ID (lowercase, numbers, hyphens)
  "name": "Example Mode", // Required: Display Name for UI
  "roleDefinition": "You are Roo, an expert in...", // Required: Defines expertise/personality (start of system prompt)
  "groups": [ // Required: Array of allowed tool groups
    "read", // Allows read_file, search_files, list_files, list_code_definition_names
    "command", // Allows execute_command
    "browser", // Allows browser_action
    "mcp", // Allows use_mcp_tool, access_mcp_resource
    // "edit" group can have restrictions:
    ["edit", {
      "fileRegex": "\\\\.(js|ts)$", // Regex pattern (double-escaped backslashes)
      "description": "JavaScript/TypeScript files only" // Optional description
    }]
    // Note: "workflow" tools (ask_follow_up_question, attempt_completion, switch_mode, new_task) are generally always available. Their availability is observed/inferred and not explicitly listed in the Custom Modes documentation.
  ],
  "customInstructions": "Follow these specific guidelines...", // Optional: Added to end of system prompt
  "apiConfiguration": { // Optional: Customize AI model/parameters
    "model": "gpt-4",
    "temperature": 0.2
  },
}
```

### Key Properties Explained:

*   **`slug` (Required):** A short, unique, machine-readable identifier.
*   **`name` (Required):** The user-friendly name displayed in the Roocode interface.
*   **`roleDefinition` (Required):** Crucial for defining the agent's persona and core function. Placed at the *beginning* of the system prompt.
*   **`groups` (Required):** An array listing the tool categories the mode can access. See the Tool Use Overview documentation for details on which tools belong to which group (`read`, `edit`, `browser`, `command`, `mcp`).
*   **`fileRegex` (within `edit` group):** Uses standard regular expressions to filter which files the mode can modify. **Important:** Backslashes in the regex pattern must be double-escaped within the JSON string (e.g., `\.` becomes `\\\\.`).
*   **`customInstructions` (Optional):** Provides specific rules or guidelines for the mode's behavior. Appended to the *end* of the system prompt. Can be supplemented by placing instructions in a `.roorules-{mode-slug}` file in the project root (these are appended after the JSON instructions). Using a `.roorules` file is beneficial for managing longer instructions, enabling version control, and allowing non-technical users to edit instructions easily.
*   **`apiConfiguration` (Optional):** Allows specifying different LLM models or parameters (like temperature) for specific modes.

## Regex Usage for `fileRegex`

When defining `fileRegex` patterns, remember:

*   **JSON escaping:** Backslashes must be double-escaped (e.g., `\.` becomes `\\\\.`).
*   **Common patterns:**
    *   `\\\\.(js|ts)$`: Matches JavaScript and TypeScript files.
    *   `\\\\.md$`: Matches Markdown files.
    *   `\\\\.json$`: Matches JSON files.
*   **Roo assistance:** Ask Roo to generate the `fileRegex` pattern for you!

## Examples

The official documentation provides several key JSON examples directly, including:

*   Basic Documentation Writer
*   Test Engineer
*   Project-Specific Mode Override

*(Refer to the official documentation for the full JSON of these examples).*

## Creation Methods

1.  **Ask Roo:** Prompt Roocode directly (e.g., "Create a mode called 'My Mode' that can only read files").
2.  **Prompts Tab UI:** Use the graphical interface in the Roocode Prompts tab. Note that `fileRegex` restrictions currently require manual JSON editing and cannot be set via the Prompts Tab UI.
3.  **Manual JSON Editing:** Directly edit the `custom_modes.json` (global) or `.roomodes` (project) files.

This guide provides a comprehensive overview based on the available documentation content.