# Project Index: CLI Refactoring (YAML Transition - "Now" Scope)

**Date:** 2025-04-10

## 1. "Now" Scope Objective

Refactor the internal `cli` tool to replace Markdown-based agent configuration parsing with a structured `config.yaml` system **exclusively for the purpose of updating the global `custom_modes.json` registry**. The CLI will act as a compiler, reading `config.yaml` files, extracting necessary metadata, and updating the `custom_modes.json` file. Generation of project-level instruction files (e.g., `.roo/rules/...`) and handling of project-level scope (`.roomodes`) are **out of scope** for this "Now" phase.

## 2. Key Current Documents

*   **`implementation_plan_scoped.md`**: The definitive, phased plan detailing tasks required *only* for the "Now" scope (global registry update).
*   **`refactoring_map.md`**: Strategic overview outlining the "Now", "Next", and "Later" phases, confirming the immediate focus on the global path.
*   **`roo_config_findings.md`**: Summary of the current Roo Code configuration system based on documentation, providing context for registry locations and structure.

## 3. Conflict Analysis & Document Status

*   **Older Documents (`proposal_analysis.md`, `refactor_proposal_yaml_transition.md`):** These documents reflect the initial, broader vision for the YAML transition, including project-level scope and `.roo/rules...` generation. While the core concept of using YAML is retained, the scope described is **outdated** for the current "Now" implementation phase, as significant parts are deferred to "Later".
*   **`target_architecture.md`**:
    *   Provides a relevant conceptual overview of potential CLI components (`config_loader`, `compiler`, `registry_manager`) that will be implemented in a *scoped-down* manner for the "Now" phase.
    *   However, the detailed YAML schema, the description of `.roo/rules...` file generation, and the associated data flow diagram are **outdated** for the "Now" scope. They represent the target for the *full* refactoring ("Later" phase) and do not accurately reflect the limited functionality being built immediately. This document should be referenced with the understanding that only a subset of its described functionality applies to "Now".

## 4. Recommended Best Practices for "Now" Phase Execution

*   **Strict Scoping:** Adhere strictly to the tasks defined in `implementation_plan_scoped.md`. Avoid implementing features planned for "Later".
*   **Global Path Focus:** Concentrate all implementation, testing, and validation efforts solely on the pathway for updating the **global** `custom_modes.json` via `config.yaml`.
*   **Scoped Schema:** Define and validate YAML using Pydantic models that include *only* the fields essential for the global `custom_modes.json` update during this phase.
*   **Registry Safety:** Implement robust, safe read/update/write logic specifically for the global `custom_modes.json`, including backup/restore considerations.
*   **No `customInstructions`:** Ensure the `cli compile` process explicitly excludes the `customInstructions` field when updating the global registry.
*   **Migration Validation:** Thoroughly validate any migration scripts and the resulting `config.yaml` files for existing global modes.
*   **Rollback Plan:** Define and document a clear rollback strategy specifically for potential failures during the global registry update process.
*   **Path Verification:** Confirm and correctly use the path to the global `custom_modes.json` file.

## 5. Supporting Documents & Diagrams

*   **`config_yaml_schema_global.md`**: Defines the YAML schema for global mode configuration updates.
*   **`global_registry_access.md`**: Details the access patterns and safety measures for the global `custom_modes.json` registry.
*   **`rollback_strategy_global.md`**: Outlines the plan for reverting changes to the global registry if issues arise.
*   **`testing_strategy_global.md`**: Describes the testing approach for validating the global registry update functionality.
*   **`migration_plan_global.md`**: Plan for migrating existing global modes to the new `config.yaml` format.
*   **`cli_usage_guide_yaml_global.md`**: Guide on how to use the updated CLI for managing global modes via YAML.
*   **`diagram_refactoring_plan_global.md`**: Visual representation of the refactoring plan for the global scope.
*   **`diagram_target_architecture_global.md`**: Diagram illustrating the target architecture for the global update mechanism.
*   **`diagram_config_structure_definitive.md`**: Definitive diagram showing the structure of the `config.yaml` file for global modes.