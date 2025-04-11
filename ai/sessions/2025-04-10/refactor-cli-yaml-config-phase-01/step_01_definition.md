# Definition: First Actionable Step - CLI YAML Refactoring (Phase 1 - Global Scope)

**Session:** CLI YAML Config Refactoring Phase 1 (`ai/sessions/2025-04-10/refactor-cli-yaml-config-phase-01/`)
**Date:** 2025-04-10
**Source Plan:** `ai/projects/cli-yaml-config/plans_strategies/implementation_plan_scoped.md`

## Identified First Actionable Implementation Step

Based on analysis of `implementation_plan_scoped.md`, `project_index.md`, and `implementation_entry_point.md`, the first actionable *implementation* step is:

**Task 1.1: Define/Implement Pydantic models reflecting the finalized schema fields relevant to `custom_modes.json` (from P0.1) in `cli/models.py`.**

**Rationale:**
*   Pre-requisite P0.1 (Finalize Schema) is identified as a planning/documentation step, likely completed as indicated by the existence of `config_yaml_schema_global.md` and statements in `implementation_entry_point.md`.
*   Task 1.1 is the first task listed under Phase 1 implementation in the scoped plan and involves concrete code creation.

## Detailed Requirements for Step 1.1

*   **Objective:** Create Python Pydantic models that accurately represent the structure and data types of the YAML configuration fields required *only* for updating the global `custom_modes.json` registry.
*   **Target File:** `cli/models.py`
*   **Primary Input:** The finalized YAML schema definition for the global scope. This definition should be consulted from the relevant supporting document (likely `ai/projects/cli-yaml-config/config_yaml_schema_global.md`).
*   **Key Implementation Details:**
    *   Utilize the `pydantic` Python library.
    *   Define Pydantic `BaseModel` classes.
    *   Models must strictly reflect *only* the fields necessary for the global scope as defined in the schema document (e.g., `slug`, `name`, `roleDefinition`, `groups`, `apiConfiguration`, etc. - verify exact fields). Fields related to project-level instructions (`customInstructions`, etc.) must be excluded or handled appropriately if present in the schema but not needed for this step.
    *   Apply appropriate Python type hints (e.g., `str`, `Optional[str]`, `List[str]`, `Dict[str, Any]`).
    *   Leverage Pydantic validation features where applicable (e.g., required fields, constraints).
*   **Expected Output:** A well-structured Python file (`cli/models.py`) containing the defined Pydantic models ready for use in YAML loading and validation (Task 1.2).
*   **Acceptance Criteria (Reference: Plan Task 1.1 & 34):**
    *   The implemented Pydantic models accurately match the required global fields defined in the finalized schema.
    *   The code is placed correctly in `cli/models.py`.
    *   (Implicit: Code should be clean, readable, and follow standard Python conventions).

## Next Step Recommendation (Post Task 1.1 Completion)

Proceed to **Task 1.2: Implement `config_loader.py`** to discover, load, parse, and validate `config.yaml` against these newly defined Pydantic models.