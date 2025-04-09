# Analysis Summary: Agent Creation Process

This document summarizes the findings from analyzing various project files to understand the current process for creating a new agent (custom mode) within the Roo Code environment.

## 1. Overview of the Process

Creating a new agent involves a multi-step process spanning conceptual design, detailed prompt engineering, and technical configuration management:

1.  **Need Identification &amp; Seed Prompt (Scout):** The process typically starts when a need for a new agent capability is identified (often by leadership like GM, HC, or Scout). The Scout role is responsible for creating an initial "seed prompt" outlining the basic requirements.
2.  **Agent Design &amp; Prompt Engineering (Position Coach):** The seed prompt and requirements are passed (usually via the Head Trainer) to the Position Coach (Agent Designer). This role designs the agent's detailed blueprint, including its persona, expertise, scope, responsibilities, and core system prompt. This design is captured in a structured Markdown file.
3.  **Configuration &amp; Registration (Roster Manager):** The finalized Markdown design artifact is handed off (potentially via the Head Trainer or an automated workflow) to the Roster Manager. The Roster Manager uses a dedicated script (`scripts/agent_config_manager/`) to parse the Markdown file, translate the design into the required JSON format, and add or update the agent's configuration in the central JSON roster file.

## 2. Key Roles Involved

Based on the organizational chart (`agent_org_chart.md`, `agent_orchestration_system.md`) and roster details (`franchise_roster.md`):

*   **Scout:** Identifies agent needs and creates initial seed prompts.
*   **Position Coach (Agent Designer):** The core designer. Translates requirements into a detailed agent definition (Markdown artifact), including the system prompt. Reports to the Head Trainer.
*   **Head Trainer:** Oversees agent creation and development. Coordinates between Scout, Position Coach, and Roster Manager. Receives design specifications from the Position Coach.
*   **Roster Manager:** Manages the technical agent inventory. Translates Markdown designs into JSON configurations, uses the management script to update the central roster file, and maintains agent records. Reports to the Director of Agent Operations.
*   **General Manager (GM):** Oversees the strategic aspects of agent development and roster management.

## 3. Key Artifacts &amp; Conventions

*   **Agent Definition File (Markdown):**
    *   **Location:** Typically stored under `ai/agents/<team_or_function>/` (e.g., `ai/agents/training/`).
    *   **Naming:** Convention appears to be `agent_<slug>.md` (e.g., `agent_position_coach.md`).
    *   **Structure (`agent_config_conventions.md`, example `agent_position_coach.md`):**
        *   **`name`:** Extracted from the first H1 heading (`#`).
        *   **`slug`:** Derived from the parent directory name (e.g., `training`).
        *   **`roleDefinition`:** Content under a primary role heading like `# Core Identity &amp; Purpose` or `# Persona`.
        *   **`customInstructions`:** Content under headings like `## Custom Instructions` or `## Mode-specific Instructions`.
*   **Agent Configuration File (JSON):**
    *   **Location:** Specified as `ai/graph/plays/custom_modes.json` in `agent_config_conventions.md`. This likely corresponds to the global `custom_modes.json` mentioned in the official Roo Code docs. Project-specific modes can also exist in `.roomodes`.
    *   **Format (`official_roo-custom-modes.md`, `agent_config_conventions.md`):** A JSON file containing a `customModes` array. Each object represents an agent and includes:
        *   `slug` (string, required)
        *   `name` (string, required)
        *   `roleDefinition` (string, required)
        *   `groups` (array, required): Defines allowed tool groups (`read`, `edit`, `browser`, `command`, `mcp`). Can include file restrictions for the `edit` group (e.g., `["edit", { "fileRegex": "\\\\.md$", "description": "Markdown only" }]`).
        *   `customInstructions` (string, optional)
        *   `apiConfiguration` (object, optional): For model customization.

## 4. Tools Involved

*   **Agent Configuration Management Script:**
    *   **Location:** `scripts/agent_config_manager/` (contains `commands.py`, `markdown_parser.py`, etc.).
    *   **Function:** A Python script (likely invoked via a CLI wrapper) used by the Roster Manager.
    *   **Commands (`commands.py`, `agent_config_conventions.md`):**
        *   `add <markdown_path>`: Parses Markdown, adds new entry to JSON.
        *   `update <markdown_path>`: Parses Markdown, updates existing entry in JSON (can preserve existing `groups`).
        *   `delete <slug>`: Removes entry from JSON by slug.
        *   `sync <directory_path>`: (Mentioned in conventions, likely in CLI) Scans directory, adds/updates JSON entries.

## 5. Other Relevant Context

*   **Agent Mandates (`agent_mandates.md`):** Agents are designed with specific high-level purposes (e.g., Analyze, Implement, Test, Document), providing a taxonomy for their function.
*   **Playbooks (`ai/playbooks/`):** Define structured workflows for sequences of agent actions, documented in Markdown files (e.g., `pb_iterative_execution_verification.md`). They typically outline purpose, roles, and steps.