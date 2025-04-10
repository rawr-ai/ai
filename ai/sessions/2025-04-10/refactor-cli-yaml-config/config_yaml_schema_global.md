# YAML Schema: config.yaml for Global Mode Registry Updates

**Date:** 2025-04-10
**Version:** 1.0
**Scope:** This document defines the required YAML structure and fields for a `config.yaml` file when used by the `cli compile` command **specifically** to add or update an agent mode entry in the **global** `custom_modes.json` registry.

## Purpose

This schema serves as the definitive reference for the structure, fields, data types, and validation rules applicable to `config.yaml` files intended for managing global agent modes. It ensures consistency for developers implementing the parser/validator and for users creating agent configurations for the global registry.

**Note:** This schema *only* covers the fields necessary for updating the global `custom_modes.json`. Fields related to project-level instruction generation (e.g., detailed behavior, context, workflows, team) or the `customInstructions` field itself are **not** included here as they are not written to the global registry in this workflow.

## Schema Definition

A `config.yaml` file for global registry updates represents a single agent mode and must contain the following top-level keys:

```yaml
# --- Required Fields ---

# Unique identifier for the agent mode. Must be URL-safe.
# Type: String
# Required: Yes
slug: "your-agent-slug"

# Human-readable display name for the agent mode.
# Type: String
# Required: Yes
name: "Your Agent Name"

# The core prompt defining the agent's persona, role, and primary objective.
# This corresponds to the 'roleDefinition' field in custom_modes.json.
# Type: String (Multiline allowed)
# Required: Yes
roleDefinition: |
  # Core Identity & Purpose
  *   **Your Role:** ...
  *   **Your Expertise:** ...
  *   **Your Primary Objective:** ...

# List of tool groups the agent has access to. Corresponds to 'groups' in custom_modes.json.
# See Roo Code documentation for available tool groups.
# Type: List of Strings
# Required: Yes
groups:
  - "read"
  - "write"
  - "execute"
  # - "edit" # Example: Add edit group
  # - ["edit", { "fileRegex": "\\.py$", "description": "Python files only" }] # Example: Edit group with file restriction

# --- Optional Fields ---

# API configuration details if the mode uses a specific API endpoint.
# Corresponds to 'apiConfiguration' in custom_modes.json.
# Type: Object
# Required: No
apiConfiguration:
  # The model identifier (e.g., "gpt-4", "claude-3-opus-20240229")
  # Type: String
  # Required: Yes (if apiConfiguration is present)
  model: "gpt-4-turbo-preview"

  # The base URL for the API endpoint.
  # Type: String (URL)
  # Required: No
  # url: "https://api.example.com/v1" # Example

  # Additional parameters specific to the API provider (e.g., temperature, top_p).
  # Structure depends on the provider.
  # Type: Object
  # Required: No
  # params:
  #   temperature: 0.7 # Example
```

## Validation Rules

*   All `Required: Yes` fields must be present.
*   `slug` must be a non-empty string, typically following kebab-case convention.
*   `name` must be a non-empty string.
*   `roleDefinition` must be a non-empty string.
*   `groups` must be a list, and each item must be either a string (group name) or a list containing the group name string and an object with `fileRegex` and optionally `description` for file restrictions (currently only applicable to the "edit" group).
*   If `apiConfiguration` is present, `model` within it is required and must be a non-empty string. `url` if present must be a valid URL string.

## Excluded Fields (for Global Scope)

The following fields, while potentially part of a broader agent configuration vision or present in the old `custom_modes.json` structure, are **explicitly excluded** when compiling for the global registry:

*   `customInstructions`: This field is managed separately (e.g., via UI or project-level files) and is not stored in the global `custom_modes.json` via this YAML workflow.
*   Any fields related to `behavior`, `context`, `workflows`, `team`, etc., as defined in broader draft schemas. These are relevant for project-level instruction generation, which is outside the scope of global registry updates.