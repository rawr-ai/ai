# Migration Plan: Global Modes to YAML Configuration

**Version:** 1.0
**Date:** 2025-04-10
**Status:** Draft

## 1. Introduction

This document outlines the plan for migrating existing global modes (currently managed implicitly or via the central `custom_modes.json` registry) to the new `config.yaml`-based configuration system. The goal is to transition all global modes to be defined and managed via individual YAML files, which are then compiled into the `custom_modes.json` registry using the `cli compile --global` command.

This migration corresponds to Phase 5 of the `implementation_plan_scoped.md`.

## 2. Scope

This migration plan applies to all modes considered "global" within the system. This includes modes currently present in the central `custom_modes.json` registry that are not associated with a specific project or user workspace.

## 3. Prerequisites

Before initiating the migration, the following components and documentation must be in place and validated:

*   **`config_yaml_schema_global.md`:** The canonical schema for `config.yaml` files defining global modes must be finalized and documented.
*   **`config_loader.py`:** The module responsible for parsing and validating `config.yaml` files (including Pydantic models based on the schema) must be implemented and unit-tested.
*   **`registry_manager.py`:** The module responsible for reading from and writing to the global `custom_modes.json` registry must be implemented, tested, and its access patterns documented in `global_registry_access.md`.
*   **`compiler` module:** The logic responsible for transforming validated YAML data into the `custom_modes.json` format must be implemented and tested.
*   **`cli compile --global` command:** The CLI command pathway for processing global `config.yaml` files must be implemented.
*   **`rollback_strategy_global.md`:** A clear rollback plan must be documented.
*   **`testing_strategy_global.md`:** A testing strategy for the global update pathway must be defined.

## 4. Migration Script (`migrate_global_modes.py`)

A dedicated migration script (tentatively named `migrate_global_modes.py`) will be developed (as per Task 5.1) to automate the conversion process.

*   **Purpose:** To read existing global mode definitions from the current `custom_modes.json` file and generate corresponding `config.yaml` files adhering to the `config_yaml_schema_global.md`.
*   **Input:**
    *   `--input-json`: Path to the current global `custom_modes.json` file. (Default path should be configurable or derived from `global_registry_access.md`).
    *   `--output-dir`: Path to the directory where the generated `config.yaml` files will be saved.
*   **Output:** A set of `config.yaml` files, potentially one per global mode, placed in the specified output directory. The naming convention for these files should be determined (e.g., `<mode_slug>_config.yaml`).
*   **Logic:**
    *   Read and parse the input `custom_modes.json`.
    *   Iterate through each mode defined in the JSON.
    *   Map the existing JSON fields (e.g., `name`, `slug`, `description`, `system_prompt`, `tools`, etc.) to the corresponding fields defined in the `config_yaml_schema_global.md`.
    *   Handle potential data inconsistencies, missing fields, or necessary transformations during mapping. Log warnings or errors as appropriate.
    *   Generate a `config.yaml` file for each mode using the mapped data.
*   **Usage:**
    ```bash
    python cli/migration/migrate_global_modes.py --input-json <path_to_custom_modes.json> --output-dir <path_to_output_directory>
    ```

## 5. Validation Steps (Task 5.2)

Before applying the migration to the live system, the generated `config.yaml` files must be thoroughly validated:

1.  **Schema Validation:** Programmatically validate each generated `config.yaml` file against the Pydantic models defined in `config_loader.py` (which reflect `config_yaml_schema_global.md`). Any validation errors must be investigated and corrected, potentially requiring adjustments to the migration script logic.
2.  **Content Validation:** Perform a manual or semi-automated review comparing the content of the generated YAML files against the original entries in `custom_modes.json`. Verify that names, slugs, descriptions, prompts, and tool configurations have been transferred accurately.
3.  **Dry Run Compilation:** Execute the `cli compile --global --dry-run` command (assuming implementation) pointing it to the directory containing the generated `config.yaml` files. This simulates the update process without modifying the actual `custom_modes.json`. Check the command output for any errors or warnings reported by the compiler or registry manager.

## 6. Execution Steps

1.  **Backup:** Create a secure backup of the current global `custom_modes.json` file, following the procedure outlined in `rollback_strategy_global.md`.
2.  **Run Migration Script:** Execute the `migrate_global_modes.py` script, providing the path to the current `custom_modes.json` and the desired output directory for the new `config.yaml` files.
    ```bash
    python cli/migration/migrate_global_modes.py --input-json <path_to_live_custom_modes.json> --output-dir <path_to_generated_configs>
    ```
3.  **Perform Validation:** Execute all validation steps outlined in Section 5 on the generated `config.yaml` files. Address any issues found by correcting the script and regenerating/revalidating as needed.
4.  **Execute Live Compilation:** Once validation is successful, execute the `cli compile --global` command, pointing it to the directory containing the validated `config.yaml` files. This will update the live `custom_modes.json` registry.
    ```bash
    # Example assuming generated configs are in 'configs/global/' relative to workspace
    cli compile --global --config-dir configs/global/
    ```
    *(Note: The exact command syntax and options for specifying the source directory need to be confirmed based on the final CLI implementation and documented in `cli_usage_guide_yaml_global.md`)*

## 7. Verification (Task 5.4)

After the live compilation, verify the success of the migration:

1.  **Registry Comparison:** Compare the newly updated `custom_modes.json` file with the backup created in Step 6.1. Use a diff tool to ensure that the changes reflect the expected transformations based on the migrated modes and that no unintended data loss or corruption occurred.
2.  **Functional Testing:** Perform basic functional tests using the CLI. Attempt to list, view, and potentially use (if applicable) the migrated global modes to ensure they are correctly registered and accessible. Refer to `testing_strategy_global.md` for relevant test cases.

## 8. Rollback

If any step during the Execution (Section 6) or Verification (Section 7) fails critically, initiate the rollback procedure documented in `rollback_strategy_global.md`. This typically involves restoring the `custom_modes.json` file from the backup created in Step 6.1. Investigate the cause of the failure before re-attempting the migration.