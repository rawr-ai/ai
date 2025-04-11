# Task Definition: Implement Pydantic Models for Global Agent Config (Step 1.1)

**Date:** 2025-04-10
**Session Context:** `refactor-cli-yaml-config-phase-01`
**Source Plan:** `ai/projects/cli-yaml-config/plans_strategies/implementation_plan_scoped.md` (Task 1.1)
**Input Schema:** `ai/projects/cli-yaml-config/config/config_yaml_schema_global.md`

## Objective

Implement the necessary Pydantic models in the target file `cli/models.py` to represent, load, and validate the structure of a `config.yaml` file, strictly adhering to the fields defined in the global schema (`config_yaml_schema_global.md`). These models are intended *only* for processing configurations related to updating the global `custom_modes.json` registry.

## Target File

*   `cli/models.py`

## Requirements

1.  **Import necessary types:** Ensure `pydantic` (v2 preferred if available) and relevant types from `typing` (e.g., `List`, `Optional`, `Union`, `Dict`, `Any`, `Tuple`, `Literal`) are imported. Use `HttpUrl` from Pydantic for URL validation if applicable.
2.  **Define `GroupRestriction` Model:**
    *   Create a Pydantic model named `GroupRestriction`.
    *   Fields:
        *   `fileRegex`: `str` (Required)
        *   `description`: `Optional[str]` (Optional)
3.  **Define `ApiConfig` Model:**
    *   Create a Pydantic model named `ApiConfig`.
    *   Fields:
        *   `model`: `str` (Required)
        *   `url`: `Optional[pydantic.HttpUrl]` (Optional)
        *   `params`: `Optional[Dict[str, Any]]` (Optional)
4.  **Define `GlobalAgentConfig` Model:**
    *   Create the main Pydantic model named `GlobalAgentConfig`.
    *   Fields:
        *   `slug`: `str` (Required)
        *   `name`: `str` (Required)
        *   `roleDefinition`: `str` (Required)
        *   `groups`: `List[Union[str, Tuple[str, GroupRestriction]]]` (Required). This structure reflects the schema allowing either a simple group name string or a tuple containing the group name and its restriction object. Validate that the tuple form is primarily used as shown for 'edit' in the schema example, but allow the general structure.
        *   `apiConfiguration`: `Optional[ApiConfig]` (Optional)
5.  **Validation:** Ensure Pydantic's built-in validation enforces required fields and types as specified in the schema document.
6.  **Scope Limitation:** **Do not** include fields in these models that are explicitly excluded in the schema for the global scope, such as `customInstructions`, `behavior`, `context`, `workflows`, `team`, etc. The models must *only* represent the structure needed for updating `custom_modes.json`.

## Acceptance Criteria

*   The file `cli/models.py` contains the Pydantic models (`GroupRestriction`, `ApiConfig`, `GlobalAgentConfig`) as defined above.
*   The models accurately reflect the structure and types specified in `ai/projects/cli-yaml-config/config/config_yaml_schema_global.md`.
*   The models only include fields relevant to the global `custom_modes.json` update path.
*   The code is well-formatted and includes necessary imports.

## Next Step

The `code` agent will use this definition to implement the Pydantic models in `cli/models.py`.