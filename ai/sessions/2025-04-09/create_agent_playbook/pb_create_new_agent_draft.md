# Playbook: Create New Agent

## 1. Purpose/Objective

To define the standard, step-by-step process for designing, configuring, and registering a new agent (custom mode) within the Roo Code environment, ensuring consistency and adherence to established conventions.

## 2. Key Roles Involved

*   **Initiator:** Identifies the initial need or requirement for a new agent capability.
*   **Scout:** Receives the initial need, formalizes it, and creates a "seed prompt" outlining basic requirements.
*   **Head Trainer (HT):** Oversees the process, assigns tasks, and facilitates communication between roles. Receives seed prompts from the Scout and agent definitions from the Position Coach. Assigns design and configuration tasks.
*   **Position Coach (PC / Agent Designer):** Designs the agent's detailed blueprint based on requirements, including persona, scope, and the core system prompt. Creates the official Agent Definition Markdown file.
*   **Roster Manager (RM):** Manages the technical agent configuration. Receives the Agent Definition Markdown, uses the management script to update the central configuration file, and confirms completion.

## 3. Prerequisites

*   Familiarity with the core concepts of Roo Code agents/custom modes.
*   Understanding of the established agent configuration conventions (see Section 6).
*   Access to relevant project repositories and tools (specifically the Agent Configuration Management Script for the Roster Manager).

## 4. Workflow Steps

This workflow details the sequence from identifying a need to having a configured agent.

| Step | Action                                      | Actor(s)        | Input                                  | Output                                      |
| :--- | :------------------------------------------ | :-------------- | :------------------------------------- | :------------------------------------------ |
| 1    | Identify Need                               | Initiator       | Business/Operational Requirement       | Initial Request to Scout                    |
| 2    | Create Seed Prompt & Requirements           | Scout           | Initial Request                        | Seed Prompt & Requirements Document         |
| 3    | Submit & Assign Design Task                 | Scout -> HT -> PC | Seed Prompt & Requirements Document    | Agent Design Task assigned to PC            |
| 4    | Design Agent & Create Definition File       | PC              | Agent Design Task                      | Agent Definition Markdown (in slug-named dir) |
| 5    | Submit Definition & Assign Configuration Task | PC -> HT -> RM  | Agent Definition Markdown              | Configuration Task assigned to RM           |
| 6    | Execute Configuration via Script            | RM -> Script    | Path to Agent Definition Markdown      | Agent added/updated in Config File (JSON)   |
| 7    | Confirm Configuration Update                | Script -> RM -> HT | Script execution result (Success/Fail) | Confirmation of process completion to HT    |

*(Based on `analysis_summary.md` and `agent_creation_process.mermaid`)*

## 5. Inputs/Outputs Summary

*   **Primary Input:** An identified need for a new agent capability.
*   **Key Intermediate Artifacts:**
    *   Seed Prompt & Requirements Document (from Scout)
    *   Agent Definition Markdown File (from Position Coach)
*   **Primary Output:** A new or updated agent configuration registered in the central Agent Configuration File (JSON).

## 6. Key Conventions

Adherence to established conventions is crucial for consistency and tool compatibility.

*   **Agent Definition File (Markdown):**
    *   **Location:** `ai/agents/<team_or_function>/<agent_slug>/` (The directory name *is* the slug)
    *   **Naming:** Typically `agent_definition.md` or similar within a directory named after the slug (e.g., `ai/agents/diagram/agent_definition.md` yields slug `diagram`).
    *   **Structure:** Must follow the structure defined in `agent_config_conventions.md` for extracting `name`, `slug`, `roleDefinition`, and `customInstructions`.
*   **Agent Configuration File (JSON):**
    *   **Location:** Central file (e.g., `ai/graph/plays/custom_modes.json` - project-specific path) or project-specific (`.roomodes`).
    *   **Format:** JSON array `customModes` with objects containing `slug`, `name`, `roleDefinition`, `groups` (including potential file restrictions), and optional `customInstructions`, `apiConfiguration`.
*   **Referenced Documents:**
    *   `agent_config_conventions.md` (for detailed Markdown parsing and JSON structure rules)
    *   `official_roo-custom-modes.md` (for base JSON format and `groups` definitions)

## 7. Tools/Scripts Involved

*   **Agent Configuration Management Script:**
    *   **Location:** `scripts/agent_config_manager/`
    *   **Purpose:** Used by the Roster Manager to automate the translation of Markdown definitions into JSON configurations and update the central roster file.
    *   **Key Commands:**
        *   `add <markdown_path>`: Adds a new agent configuration from the Markdown file.
        *   `update <markdown_path>`: Updates an existing agent configuration based on the Markdown file.
        *   `delete <slug>`: Removes an agent configuration by its slug.
        *   `sync <directory_path>`: Scans a directory for Markdown definitions and updates the JSON file accordingly.

## 8. Verification/Completion Criteria

The agent creation process is considered complete when:

*   The Roster Manager confirms successful execution of the Agent Configuration Management Script (`add` or `update` command).
*   The new/updated agent appears in the list of available custom modes within the Roo Code environment.
*   (Post-Creation) The agent functions as intended according to its design (requires separate testing/validation).