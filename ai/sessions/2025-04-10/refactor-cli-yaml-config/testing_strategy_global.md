# Testing Strategy: Global Registry Update via YAML

**Date:** 2025-04-10
**Version:** 1.0

## 1. Introduction & Purpose

This document outlines the testing strategy for validating the refactored CLI functionality that updates the global `custom_modes.json` registry using `config.yaml` files. The primary goal is to ensure the new implementation is robust, reliable, and functionally equivalent to the previous method where applicable, specifically focusing on the global update pathway triggered via the `cli compile --global` command (or equivalent mechanism).

This strategy aligns with Tasks 3.3 and 4.2 outlined in the `implementation_plan_scoped.md`.

## 2. Scope

This strategy specifically covers the testing of components and workflows involved in processing `config.yaml` files to update the *global* `custom_modes.json` registry. It does *not* cover project-specific configuration updates or other CLI functionalities outside this scope.

## 3. Testing Levels & Approaches

A multi-layered testing approach will be employed:

### 3.1. Unit Testing

*   **Objective:** Verify the correctness of individual components in isolation.
*   **Targets:**
    *   `config_loader.py`: Test YAML parsing, schema validation (using Pydantic models defined in `config_yaml_schema_global.md`), handling of various valid and invalid input structures, and error reporting.
    *   `compiler.py` (Global Path Logic): Test the logic responsible for transforming the validated configuration data into the format required for `custom_modes.json`. Focus on correct data mapping, handling of different mode types, and generation of appropriate JSON structures.
    *   `registry_manager.py` (Global Path Logic): Test functions responsible for reading the existing global registry, merging/updating data based on compiled configuration, handling file I/O safely (including backup/rollback mechanisms defined in `rollback_strategy_global.md`), and writing the updated `custom_modes.json` file. Mock file system interactions and registry access where necessary.
*   **Tools:** `pytest` framework, potentially using `pytest-mock`.

### 3.2. Integration Testing

*   **Objective:** Verify the interaction and data flow between the core components involved in the global update process.
*   **Targets:** Test the end-to-end flow initiated by the `cli compile --global <path/to/config.yaml>` command (or its programmatic equivalent).
    *   Simulate command execution with various valid and invalid `config.yaml` inputs.
    *   Verify that the `config_loader`, `compiler`, and `registry_manager` interact correctly.
    *   Check for correct handling of file paths, registry location (`global_registry_access.md`), and error propagation.
    *   Verify that the final `custom_modes.json` file is updated as expected in a controlled test environment (e.g., using a temporary registry file).
*   **Tools:** `pytest` framework, potentially using test fixtures to set up controlled environments and sample input files.

### 3.3. Functional Equivalence Testing

*   **Objective:** Ensure the new YAML-based update mechanism produces the same `custom_modes.json` output as the legacy method for equivalent input configurations, where applicable. This focuses on ensuring backward compatibility and preventing regressions in existing functionality representation.
*   **Approach:**
    1.  Identify representative examples of configurations previously managed by the old system.
    2.  Create equivalent `config.yaml` files representing these configurations.
    3.  Generate `custom_modes.json` using the *old* method with the original input.
    4.  Generate `custom_modes.json` using the *new* `cli compile --global` command with the equivalent `config.yaml`.
    5.  Compare the resulting `custom_modes.json` files. Minor differences in formatting (e.g., key order, whitespace) may be acceptable if the semantic content is identical. Structural or data differences indicate failure.
*   **Tools:** `pytest`, custom comparison scripts/logic, potentially JSON diff tools.

## 4. Test Environment & Data

*   Tests will run in a controlled environment, separate from the production global registry.
*   A dedicated set of sample `config.yaml` files covering valid scenarios, edge cases, and invalid inputs will be created.
*   A baseline `custom_modes.json` file will be used for integration and functional equivalence tests.
*   Secrets or sensitive data required for registry access (if any, as defined in `global_registry_access.md`) will be mocked or handled securely in the test environment.

## 5. Success Criteria

*   All unit tests pass.
*   All integration tests pass, demonstrating correct end-to-end processing and registry updates in the test environment.
*   Functional equivalence tests pass, confirming the new method produces semantically identical output to the old method for equivalent inputs.
*   Test coverage metrics (e.g., line coverage) meet project standards (specific target TBD).

## 6. Test Execution & Reporting

*   Tests should be integrated into the CI/CD pipeline.
*   Test results will be reported automatically.
*   Failures should block deployment until resolved.