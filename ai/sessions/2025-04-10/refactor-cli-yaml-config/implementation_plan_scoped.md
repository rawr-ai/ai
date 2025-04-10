# Implementation Plan: CLI Refactoring (YAML Transition) - SCOPED FOR "NOW"

**Date:** 2025-04-10
**Scope:** This plan focuses **exclusively** on the "Now" objective: Migrating the CLI's capability to manage the **global agent mode configuration** (`custom_modes.json`) using the new `config.yaml` system. Project-level configuration support is deferred ("Later").

## 1. Summary of Objective ("Now" Scope)

Refactor the internal `cli` tool to replace Markdown-based agent configuration parsing with a structured `config.yaml` system **for the purpose of updating the global `custom_modes.json` registry**. The CLI will act as a compiler, reading `config.yaml` files, extracting necessary metadata, and updating the `custom_modes.json` file, decoupling global mode definition from runtime instruction assembly. Generation of project-level instruction files (e.g., `.roo/rules/...`) is **out of scope** for this phase.

**References:** (Original references retained for context, but interpretation is filtered by the "Now" scope)
*   Original Plan: `ai/sessions/2025-04-10/refactor-cli-yaml-config/implementation_plan.md`
*   Analysis: `ai/sessions/2025-04-10/refactor-cli-yaml-config/implementation_plan_analysis.md` (Note: Analysis scope broader than "Now")
*   Findings: `ai/sessions/2025-04-10/refactor-cli-yaml-config/config_findings.md`
*   User Clarifications & Scope Constraint: (Provided in initiating prompt)

## 2. Pre-requisites & Assumptions

*   **P0.1: Finalize Canonical YAML Schema (for Global Scope):** Define and document the canonical `config.yaml` schema fields required **specifically for updating `custom_modes.json`** (e.g., `slug`, `name`, `roleDefinition`, `groups`, `apiConfiguration`). Fields related to project-level instructions can be defined but are not required for "Now" implementation. (Effort: Small - assuming external/iterative finalization as per clarification)
*   **A.1:** Required dependencies (PyYAML, Pydantic) are available or can be added via pip.
*   **A.2:** The location of the **global** Roo Code mode registry (`custom_modes.json`) is known and accessible by the CLI tool. Assumptions about path discovery must be documented.
*   **A.3:** The `cli` tool is written in Python.

## 3. Phased Implementation Plan ("Now" Scope)

### Phase 1: Setup & Core YAML Processing (Scoped)

*   **Goal:** Establish the foundation for YAML configuration handling focused on global mode metadata.
*   **Key Activities:**
    *   **1.1:** Define/Implement Pydantic models reflecting the **finalized schema fields relevant to `custom_modes.json`** (from P0.1) in `cli/models.py`.
    *   **1.2:** Implement `config_loader.py` to discover, load, parse, and validate `config.yaml` against the scoped Pydantic models.
    *   **1.3:** Add dependencies (PyYAML, Pydantic).
    *   **1.4:** Create unit tests for scoped models and loading/validation.
*   **Dependencies:** Completion/Clarity on P0.1 (Schema for global fields).
*   **Acceptance:** Models match required global fields; `config_loader` validates relevant parts of `config.yaml`. Unit tests pass.

### Phase 2: Compiler Implementation (Scoped for Metadata Extraction)

*   **Goal:** Implement logic to extract metadata required for the global registry update from the validated YAML.
*   **Key Activities:**
    *   **2.1:** Implement/Adjust `compiler.py`:
        *   Function `extract_registry_metadata` taking a validated Pydantic config object.
        *   Logic to extract relevant fields (`slug`, `name`, `roleDefinition`, `groups`, `apiConfiguration`, etc.) needed for `custom_modes.json`.
        *   **Defer:** Generation of project-level instruction files (e.g., `.roo/rules...`) is **NOT** part of "Now".
    *   **2.2:** **Defer:** Decision on auxiliary CLI commands (`add`, `update`, `delete`) can be deferred to "Later".
    *   **2.3:** Implement unit tests for metadata extraction logic.
*   **Dependencies:** Phase 1 completion.
*   **Acceptance:** `compiler.extract_registry_metadata` correctly extracts required fields for `custom_modes.json`. Unit tests pass.

### Phase 3: Global Registry Management & Command Integration (Core "Now" Phase)

*   **Goal:** Integrate components into the `compile` command to update the **global** `custom_modes.json`.
*   **Key Activities:**
    *   **3.1:** Implement `registry_manager.py`:
        *   Function to read the **global** `custom_modes.json`.
        *   Function `update_global_registry` taking agent metadata (from Phase 2) to add/update the agent's entry, ensuring `customInstructions` is **excluded**.
        *   Logic to write the updated `custom_modes.json` back safely.
    *   **3.2:** Refactor/Implement `cli compile <agent-slug>` command:
        *   Integrate calls to `config_loader.load_agent_config`.
        *   Integrate calls to `compiler.extract_registry_metadata`.
        *   Integrate calls to `registry_manager.update_global_registry`.
        *   **No** project-scope flags needed for "Now".
        *   Provide clear user feedback.
    *   **3.3:** Implement integration tests for the `compile` command focusing **only** on the global update path.
*   **Dependencies:** Phase 1 & 2 completion. Confirmed path to global `custom_modes.json`.
*   **Acceptance:** `cli compile` successfully loads config, extracts metadata, and updates the **global** `custom_modes.json` correctly (metadata present, `customInstructions` absent). Integration tests for global path pass.

### Phase 4: Integration Testing, Rollback Planning, Documentation & Deprecation (Scoped)

*   **Goal:** Ensure robustness of the global update path, plan rollback, document, and remove old code.
*   **Key Activities:**
    *   **4.1:** Define Rollback Strategy for global path failures.
    *   **4.2:** Enhance Testing Strategy & Execute Thorough Testing **for the global path**. Functional equivalence checks compare old global mode management vs. new YAML-driven global management.
    *   **4.3:** Update CLI documentation for the YAML workflow focused on global modes.
    *   **4.4:** **After successful testing (4.2)**, remove old Markdown parsing code related to global mode definition.
    *   **4.5:** **Defer:** Implementation of auxiliary command decision (Task 2.2).
*   **Dependencies:** Phase 3 completion.
*   **Acceptance:** Rollback plan documented; Global path passes all tests; Docs updated; Old Markdown parsing code (for global modes) removed.

### Phase 5: Configuration Migration (Scoped for Global Modes)

*   **Goal:** Migrate existing agent configurations currently defined in the **global** `custom_modes.json` to the new `config.yaml` format.
*   **Key Activities:**
    *   **5.1 (Planning & Scripting):** Develop/test migration script focusing on extracting data relevant to `custom_modes.json` from old sources (likely Markdown) and generating corresponding `config.yaml` files.
    *   **5.2 (Validation Definition):** Define validation steps for migrated **global** configurations (schema checks, metadata comparison).
    *   **5.3 (Execution & Validation):** Run migration script for global modes. Execute validation steps.
    *   **5.4 (Final Verification):** Run `cli compile` on all migrated global agents. Verify successful compilation and correct `custom_modes.json` updates.
*   **Dependencies:** Completion of Phase 4.
*   **Acceptance:** All agents previously in global `custom_modes.json` have a validated `config.yaml`; `cli compile` runs successfully for all migrated global agents.

## 4. Rollback Plan Summary (Scoped)

*   Detailed rollback strategy (Task 4.1) will focus on reverting changes affecting the global `custom_modes.json` update pathway. Mechanisms include Git reverts, registry restoration from backup, etc.

## 5. Acceptance Criteria (Overall "Now" Scope)

*   `cli` tool successfully compiles `config.yaml` files **solely** to update the **global** `custom_modes.json` registry.
*   `cli compile` correctly updates `custom_modes.json` with metadata, excluding `customInstructions`.
*   Generation of project-level instruction files is **not** implemented.
*   Logic for parsing Markdown for global mode definitions is removed.
*   Refactored CLI passes all tests for the global update path.
*   Documentation reflects the YAML workflow for global modes.
*   Existing global agent configurations are migrated to `config.yaml` and validated.
*   Rollback plan for global path exists.

## 6. Risks & Dependencies Summary (Scoped)

*   **Key Dependencies:** Finalized schema for global fields (P0.1); Known path to `custom_modes.json` (A.2).
*   **Key Risks:** Schema definition for global fields; Migration accuracy for global modes; Registry corruption (`custom_modes.json`); Rollback complexity for global path. Mitigations focus on these scoped areas.

## 7. Next Steps / Handoff Recommendation

Proceed with executing this **scoped** plan, starting with Pre-requisite P0.1 (ensuring clarity on schema fields needed for `custom_modes.json`).