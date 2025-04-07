# Agent Configuration Management Script Conventions

This document outlines the conventions for the script responsible for managing agent configurations based on Markdown definitions.

## 1. Language Choice

*   **Language:** Python
*   **Schema Validation:** Pydantic
*   **Justification:** Python is a suitable choice for scripting tasks within this project. Pydantic provides robust data validation, ensuring that the generated JSON configuration adheres to the expected schema derived from the Markdown files. While TypeScript/Zod is a viable alternative, Python aligns well with potential future scripting needs and common practices for configuration management tools.

## 2. Script Location

*   The script will be located at: `scripts/manage_agent_configs.py`

## 3. Markdown-to-JSON Mapping

The script will parse agent definition Markdown files (typically located under `agents/<agent_slug>/...`) and map their content to fields in the target JSON configuration file.

*   **Source Markdown Structure Assumption:** Agent definition Markdown files are expected to follow a structure similar to `agents/architect/agent_diagram.md`. Key sections are identified by specific headings.
*   **Target JSON Fields:** `slug`, `name`, `roleDefinition`, `customInstructions`.

### Mapping Details:

*   **`slug` (string):**
    *   **Source:** Derived from the **parent directory name** containing the primary agent definition Markdown file.
    *   **Example:** For a file at `agents/diagram/agent_diagram.md`, the slug would be `diagram`.
*   **`name` (string):**
    *   **Source:** Extracted from the **first H1 heading (`#`)** found in the Markdown file.
    *   **Example:** If the file starts with `# AI Diagram Agent`, the name will be `AI Diagram Agent`.
*   **`roleDefinition` (string):**
    *   **Source:** Content under the heading `# Core Identity &amp; Purpose` (or a similar primary role definition heading like `# Persona` or `# Role`). The script should look for the first occurrence of such a heading and capture all subsequent content until the next heading of the same or higher level (H1 or H2) or the end of the file. The captured content should include the heading itself.
    *   **Example:** All text following `# Core Identity &amp; Purpose` up to the next H1/H2.
*   **`customInstructions` (string):**
    *   **Source:** Content under a specific heading designated for custom instructions, such as `## Custom Instructions` or `## Mode-specific Instructions`. The script should capture all content following this heading until the next heading of the same or higher level (H2) or the end of the file. The captured content should include the heading itself. If multiple such sections exist, they might be concatenated or handled based on specific script logic (concatenation is the default assumption).
    *   **Note:** The exact heading marker for custom instructions needs to be standardized across agent definitions or made configurable in the script.

## 4. Target JSON Path

*   The script will manage entries within the following JSON file: `ai/graph/plays/custom_modes.json`
    *   This file is expected to be a JSON array where each object represents an agent configuration and contains the fields defined above (`slug`, `name`, `roleDefinition`, `customInstructions`).

## 5. Script Operations

The script should support the following operations via command-line arguments:

*   `add <path_to_markdown>`: Parses the Markdown file, extracts the data according to the mapping, and adds a new entry to the target JSON file. Fails if an entry with the same slug already exists.
*   `update <path_to_markdown>`: Parses the Markdown file, extracts the data, and updates the existing entry in the target JSON file matching the derived slug. Fails if no entry with the slug exists.
*   `delete <slug>`: Removes the entry corresponding to the given slug from the target JSON file. Fails if no entry with the slug exists.
*   `sync <directory_path>`: Scans the specified directory (e.g., `agents/`) recursively for agent definition files, then adds or updates corresponding entries in the JSON file. Optionally, could include a flag to remove JSON entries whose corresponding Markdown files no longer exist.