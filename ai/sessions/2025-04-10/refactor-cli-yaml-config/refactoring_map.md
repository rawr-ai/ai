# Refactoring Map: CLI YAML Transition (Global First)

**Date:** 2025-04-10
**Focus:** Strategic overview prioritizing the migration of **global** configuration management (`custom_modes.json`) to the new YAML system first.

---

## Now (Immediate Priority - Current Implementation Scope)

*   **Objective:** Replace Markdown parsing with `config.yaml` compilation **specifically for updating the global `custom_modes.json` registry.**
*   **Core Tasks:**
    *   Finalize YAML schema fields required for `custom_modes.json`.
    *   Implement YAML loading & validation for these fields (`config_loader.py`, Pydantic models).
    *   Implement metadata extraction from YAML for registry (`compiler.py` - scoped).
    *   Implement logic to safely read/update/write the global `custom_modes.json` (`registry_manager.py`).
    *   Integrate into `cli compile` command (global path only).
    *   Thoroughly test the global update pathway (unit, integration, functional equivalence).
    *   Define rollback procedures for the global path.
    *   Update documentation for the global YAML workflow.
    *   Migrate existing global modes from Markdown (or other source) to `config.yaml`.
    *   Validate migrated global configurations.
    *   Remove old Markdown parsing code related to global mode definitions.
*   **Key Outcome:** CLI can manage global modes via `config.yaml` compilation, updating `custom_modes.json` correctly.

---

## Next (Post-"Now" Stabilization & Minor Enhancements)

*   **Objective:** Stabilize the "Now" implementation and potentially add minor supporting features.
*   **Potential Tasks:**
    *   Address any bugs or performance issues identified in the "Now" phase.
    *   Refine error handling and user feedback for the `compile` command (global path).
    *   Potentially implement basic helper/linting commands for `config.yaml` structure (focused on global fields).
    *   Review and potentially refine the schema based on initial usage.
    *   Improve test coverage based on initial deployment experience.

---

## Later (Future Scope - Explicitly Deferred)

*   **Objective:** Extend CLI capabilities to handle project-level configurations and full instruction generation.
*   **Potential Tasks:**
    *   Implement project-level scope detection/handling (e.g., CLI flags, context awareness).
    *   Implement discovery and modification logic for project-level mode registries (e.g., `.roomodes`).
    *   Implement compiler logic to generate project-level instruction files (e.g., into `.roo/rules...` directories) based on `config.yaml`.
    *   Integrate project-level path into `cli compile` command.
    *   Develop comprehensive testing for project-level scope.
    *   Update documentation for project-level features.
    *   Migrate any existing project-specific configurations (if applicable).
    *   Revisit and implement/deprecate auxiliary commands (`add`, `update`, `delete`) considering both global and project scopes.
    *   Address any cross-cutting concerns between global and project configurations.

---