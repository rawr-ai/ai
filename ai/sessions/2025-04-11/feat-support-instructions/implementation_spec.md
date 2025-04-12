# Implementation Specification: Adding `customInstructions`

## 1. Overview

This specification details the required changes to add an optional `customInstructions` field to the agent configuration system, based on the findings in `discovery_report.md`.

## 2. File Modifications

### 2.1. `cli/models.py`

-   **Action:** Add a new field to the `GlobalAgentConfig` Pydantic model.
-   **Details:** Insert the following field definition within the `GlobalAgentConfig` class:

    ```python
    from typing import Optional
    from pydantic import Field

    # ... other fields ...

    customInstructions: Optional[str] = Field(None, description="Optional user-defined instructions for the agent.")

    # ... rest of the class ...
    ```
-   **Rationale:** This defines the new optional field, allowing it to be parsed from YAML configuration files and validated by Pydantic. The `Optional[str]` type ensures it's not required, and `Field(None, ...)` sets the default to `None` if not provided in the YAML.

### 2.2. `cli/config_loader.py`

-   **Action:** No changes required.
-   **Rationale:** As confirmed in the discovery report, this script handles configuration *paths* and does not load or validate the agent configuration YAML content itself.

### 2.3. `cli/compiler.py`

-   **Action:** Verify usage of `GlobalAgentConfig` and adapt if necessary.
-   **Details:** The discovery report identified that `cli/compiler.py` imports and uses `GlobalAgentConfig`. During the implementation phase, the developer must:
    -   Examine how `GlobalAgentConfig` objects are used within `cli/compiler.py`.
    -   Ensure that any logic iterating over fields or assuming a specific structure of the `GlobalAgentConfig` object gracefully handles the new, optional `customInstructions` field (which might be `None`).
    -   Determine if and how the `customInstructions` value should be utilized within the compiler logic. If it needs to be passed further, implement the necessary plumbing.
-   **Rationale:** Adding a new field to a model can impact downstream consumers. Verification is needed to prevent runtime errors and ensure the new field is correctly integrated if used by the compiler.

## 3. Summary for Implementer

1.  Add the `customInstructions: Optional[str] = Field(...)` line to `GlobalAgentConfig` in `cli/models.py`.
2.  No changes are needed in `cli/config_loader.py`.
3.  Carefully review `cli/compiler.py` to ensure it handles the potentially `None` value of `customInstructions` and integrates it as needed.