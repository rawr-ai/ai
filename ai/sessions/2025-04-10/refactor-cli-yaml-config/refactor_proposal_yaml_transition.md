**High-Level Refactoring Proposal: CLI Transition to YAML Configuration**

**Date:** 2025-04-10

**1. Introduction & Objective**

This document outlines a high-level refactoring strategy for the internal `cli` tool. The primary objective is to transition from the current approach of parsing agent definitions (including role, behavior, and instructions) directly from Markdown files to a centralized, structured YAML configuration system.

This transition is driven by the need to:
*   Simplify and standardize agent configuration management.
*   Eliminate the complex and brittle logic required to extract structured data from Markdown.
*   Decouple the CLI from managing specific fields (like `customInstructions`) that are better handled by the target runtime environment (Roo Code).
*   Improve maintainability and extensibility of the CLI tool.

This proposal is based on the analysis documented in `ai/sessions/2025-04-10/roo-config-upgrade/report.md` and `ai/sessions/2025-04-10/roo-config-upgrade/modes_vs_instructions_summary.md`, and considers the draft YAML structure outlined in `ai/projects/cli-yaml-config/agent_config_draft.yaml` and `ai/projects/cli-yaml-config/yaml_config_ideas.md`.

**2. Proposed High-Level Strategy**

The core strategy is to establish a single YAML file per agent as the definitive source of truth for its configuration. The `cli` tool will be refactored to act as a **compiler**, reading this YAML configuration and generating the necessary output formats required by downstream consumers, primarily Roo Code's file-based instruction system.

Key tenets of this strategy:
*   **YAML as the Source:** All agent configuration (role, behavior, context, tools, workflows, etc.) will reside in a dedicated `config.yaml` file within the agent's directory.
*   **CLI as Compiler:** The CLI's primary role shifts from parsing Markdown to reading, validating, and compiling the YAML into target formats.
*   **Decoupling:** The CLI will cease extracting and managing fields like `customInstructions` for Roo Code outputs, respecting the findings in the analysis reports. Instruction assembly becomes the responsibility of the Roo Code runtime.
*   **Deprecation:** Existing Markdown parsing logic for agent configuration will be deprecated and removed.

**3. Key Components & Considerations**

**3.1. YAML as Source of Truth**

*   **Location:** A standard `config.yaml` file will be expected within each agent's directory (e.g., `ai/agents/[agent-name]/config.yaml`).
*   **Schema & Validation:** The CLI must implement robust parsing and validation against the defined YAML schema (based on `agent_config_draft.yaml`). Libraries like `PyYAML` and `Pydantic` (or similar) should be used for loading and validation.
*   **Content:** This YAML file will contain all configurable aspects of the agent, including role definitions, behavior rules (SOPs, boundaries), context references, tool configurations, workflow definitions, and team relationships, as outlined in the draft schema.

**3.2. Compilation Targets**

The refactored CLI (`cli compile ...`) will generate the following primary outputs from the source `config.yaml`:

1.  **Roo Code File-Based Instructions:**
    *   Generate the necessary file structure and content for Roo Code's preferred instruction mechanism (v3.11.9+).
    *   This involves creating a `.roo/rules-{modeSlug}/` directory within the agent's directory (or a user-configurable output location).
    *   Relevant sections from the YAML (e.g., `role.raw`, `behavior.raw`, `behavior.sops`, `behavior.boundaries`) will be compiled into appropriately named files (e.g., `01_role.md`, `02_behavior.md`) within this directory. The exact mapping needs definition during implementation.
    *   **Crucially:** The CLI will **not** attempt to populate the `customInstructions` field in any generated JSON output for Roo Code.
2.  **Generated Markdown Prompt File (Optional but Recommended):**
    *   Compile a comprehensive `prompt.md` file (or similar) that aggregates the core identity, role, expertise, mandate, behavior rules, etc., from the YAML into a human-readable format suitable for direct use as a system prompt or for review. This replaces the need to manually maintain the agent definition in the main Markdown file.
3.  **Updated `custom_modes.json` / `.roomodes`:**
    *   The CLI will still need to update the central Roo Code mode registry (`custom_modes.json` or `.roomodes`).
    *   It will populate fields like `slug`, `name`, `roleDefinition` (potentially sourced from a dedicated field in YAML or the generated `prompt.md`), `tools` (native groups), etc., based on the `config.yaml`.
    *   It will **explicitly exclude** the `customInstructions` field.

**3.3. Revised CLI Workflow**

The proposed workflow for the `compile` command:

```mermaid
flowchart TD
  A[User invokes CLI command<br>(e.g., "cli compile [agent-name]" or "cli compile --all")]
  B[CLI finds agent config.yaml<br>(e.g., ai/agents/[agent-name]/config.yaml)]
  C[CLI reads & validates YAML against schema]
  D["Compile YAML into internal representation"]
  E["Generate .roo/rules-{modeSlug}/ directory & instruction files"]
  F["Generate prompt.md (optional)"]
  G["Update custom_modes.json / .roomodes<br>(Core fields ONLY, NO customInstructions)"]
  H["Output: Success message / Path to outputs"]

  A --> B
  B --> C
  C --> D
  D --> E
  D --> F
  E --> G
  F --> G
  G --> H

  subgraph Validation & Compilation
    direction LR
    C -- Valid --> D
    C -- Invalid --> H(Output: Validation Error)
  end

  subgraph Output Generation
    direction TB
    E
    F
    G
  end
```

**3.4. Code Changes**

Significant refactoring will be required in the `cli` codebase:

*   **`cli/agent_config/`:**
    *   Remove modules/functions related to parsing Markdown for configuration (`markdown_utils.py` likely needs heavy modification or replacement).
    *   Introduce new modules/functions for reading, validating, and processing the `config.yaml` file.
    *   Implement the logic to compile YAML sections into the target output formats (.roo/rules files, prompt.md).
*   **`cli/main.py` (and command handlers):**
    *   Update command definitions (deprecate parts of `add`/`update` related to Markdown parsing, introduce `compile`).
    *   Modify the logic for interacting with `custom_modes.json` to exclude `customInstructions`.
*   **Dependencies:** Add dependencies for YAML parsing and validation (e.g., `PyYAML`, `Pydantic`).

**3.5. Deprecations**

The following aspects of the current system will be deprecated and removed:

*   Extraction of `role`, `behavior`, `customInstructions`, `mode-specific instructions`, etc., directly from agent Markdown files (`ai/agents/[agent-name]/agent.md`).
*   The logic within the CLI that populates the `customInstructions` field in `custom_modes.json`.
*   The reliance on specific Markdown headings (e.g., "## Custom Instructions") for configuration. The primary agent Markdown file becomes primarily documentation or potentially the *target* for the generated `prompt.md`.

**3.6. Directory Structure**

*   **`ai/agents/[agent-name]/`:**
    *   `config.yaml`: **New** - The single source of truth for configuration.
    *   `agent.md`: **Retained/Modified** - Becomes primarily documentation or the target for the generated `prompt.md`. No longer parsed for config.
    *   `.roo/rules-{modeSlug}/`: **New (Generated)** - Contains compiled instruction files for Roo Code.
    *   `prompt.md`: **New (Generated, Optional)** - Compiled, human-readable prompt.
*   **`cli/`:** Code changes as described above.
*   **Central Roo Code Config:** (`custom_modes.json` / `.roomodes`) - Still updated by the CLI, but with modified content (no `customInstructions`).

**3.7. Integration Points & Existing Commands**

*   **`add`/`update`/`delete` Commands:** These commands need re-evaluation.
    *   `add`: Could potentially scaffold a basic `config.yaml` and `agent.md`. It would no longer parse the initial Markdown for config.
    *   `update`: Its primary function might shift to triggering the `compile` process after manual edits to `config.yaml`, or it could be deprecated in favor of `compile`. Direct parsing/updating from Markdown is removed.
    *   `delete`: Should remove the agent's directory (`ai/agents/[agent-name]/`) and its entry from `custom_modes.json`.
*   **Compilation Trigger:** The `compile` command becomes central. It could be run manually after editing `config.yaml` or potentially integrated into pre-commit hooks or CI/CD pipelines.

**4. Conclusion & Next Steps**

This refactoring represents a significant shift towards a more robust and maintainable configuration system for the `cli` tool. By centralizing configuration in YAML and treating the CLI as a compiler, we align better with modern development practices and decouple the tool from the complexities of runtime instruction assembly handled by Roo Code.

**Next Steps (High-Level):**

1.  **Detailed Design:** Refine the YAML schema and the mapping logic for compilation targets.
2.  **Implementation:**
    *   Implement YAML parsing and validation.
    *   Implement the compilation logic for `.roo/rules/` and `prompt.md`.
    *   Refactor CLI commands (`compile`, `add`, `update`, `delete`).
    *   Remove deprecated Markdown parsing logic.
3.  **Testing:** Develop unit and integration tests for the new YAML processing and compilation logic.
4.  **Documentation:** Update developer documentation for the `cli` tool, explaining the new YAML-based workflow.
5.  **Migration:** Plan and execute the migration of existing agent configurations from Markdown to the new `config.yaml` format.