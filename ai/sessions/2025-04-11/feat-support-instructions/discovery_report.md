# Discovery Report: Adding `customInstructions` to Agent Configuration

## Objective

Analyze the Python agent configuration system to understand how to add a new optional `customInstructions` field (string) to the agent configuration defined in YAML files.

## Analysis

### 1. Configuration Model (`cli/models.py`)

-   The structure of individual agent configuration YAML files is defined and validated by Pydantic models in `cli/models.py`.
-   The primary model is `GlobalAgentConfig`.
-   Crucially, `GlobalAgentConfig` includes `class Config: extra = Extra.forbid` (line 38). This configuration prevents any fields present in the YAML file but not explicitly defined in the Pydantic model from being loaded, raising a validation error instead.

### 2. Configuration Loading (`cli/config_loader.py`)

-   The script `cli/config_loader.py` is responsible for determining the *paths* to configuration files and directories (e.g., `agent_config_dir`, `global_registry_path`).
-   It loads these path settings from `rawr.config.yaml`, `rawr.config.local.yaml`, and environment variables.
-   It does **not** handle the loading or validation of the individual agent configuration YAML files found within the `agent_config_dir`. The logic for reading these YAMLs and parsing them using `GlobalAgentConfig` resides elsewhere in the codebase (likely in the compiler or a related module).

### 3. Data Flow (Inferred)

1.  Path configuration is loaded by `cli/config_loader.py` to find the `agent_config_dir`.
2.  Another part of the system (e.g., `cli/compiler.py`) iterates through YAML files in `agent_config_dir`.
3.  Each YAML file's content is loaded and parsed/validated against the `cli.models.GlobalAgentConfig` Pydantic model.
4.  The resulting Python `GlobalAgentConfig` objects are used downstream.

### 4. Required Modifications

-   To add the `customInstructions` field, the `GlobalAgentConfig` class definition in `cli/models.py` **must** be modified.
-   A new field should be added, for example:
    ```python
    customInstructions: Optional[str] = Field(None, description="Optional custom instructions for the agent.")
    ```
-   No modifications are needed in `cli/config_loader.py` for this change.

### 5. Downstream Dependencies (`search_files` Results)

-   The search for imports of `cli.models` or `cli.config_loader` within `cli/*.py` yielded the following result:

    ```
    # cli/compiler.py
      2 | from typing import Dict, Any
      3 | from cli.models import GlobalAgentConfig
      4 |
    ```

-   This indicates that `cli/compiler.py` directly uses the `GlobalAgentConfig` model.
-   **Impact:** The compiler logic might need adjustments if it relies on a specific structure or iterates through all fields of the `GlobalAgentConfig` object. Further investigation of `cli/compiler.py` is recommended during the implementation phase to ensure compatibility with the added field.

## Conclusion

Adding the optional `customInstructions` field primarily requires modifying the `GlobalAgentConfig` Pydantic model in `cli/models.py`. The configuration loading script (`cli/config_loader.py`) is unaffected. The main downstream consumer identified is `cli/compiler.py`, which should be checked for compatibility during implementation.