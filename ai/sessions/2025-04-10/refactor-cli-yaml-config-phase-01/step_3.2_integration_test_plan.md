# Integration Test Plan: `cli compile <agent-slug>` Command

**Date:** 2025-04-10
**Associated Task:** 3.2 (Implement `cli compile` command) - `ai/projects/cli-yaml-config/plans_strategies/implementation_plan_scoped.md`
**Scope:** Integration testing for the `cli compile <agent-slug>` command, focusing on its interaction with `config_loader`, `compiler`, and `registry_manager` to update the **global** `custom_modes.json` registry.

## 1. Objectives

*   Verify that the `cli compile` command correctly orchestrates the loading, validation, metadata extraction, and global registry update process based on an agent's `config.yaml`.
*   Ensure proper handling of various success and failure scenarios, including file system interactions and data validation.
*   Confirm that user feedback (stdout/stderr messages) is clear and accurate for different outcomes.
*   Validate that only the intended metadata (excluding `customInstructions`) is written to the global registry.

## 2. Test Environment & Tools

*   **Framework:** `pytest`
*   **CLI Testing:** `typer.testing.CliRunner`
*   **Mocking:** `unittest.mock` (specifically `patch`), `pytest` fixtures.
*   **File System:** `pytest`'s `tmp_path` fixture will be used to create isolated temporary directories for test artifacts (`config.yaml`, mocked `custom_modes.json`).
*   **Registry Path Mocking:** The `registry_manager.GLOBAL_REGISTRY_PATH` constant will be patched during tests to point to a temporary file within `tmp_path`.
*   **Configuration Path Assumption:** Tests will assume a standard agent configuration directory structure relative to a base path (e.g., `<base>/agents/<agent-slug>/config.yaml`). This base path might need mocking or setting within the test environment if `config_loader` relies on it implicitly.

## 3. Test Strategy

*   **Isolation:** Each test case will run in an isolated temporary directory provided by `tmp_path`.
*   **Mocking:** File system operations related to reading `config.yaml` and reading/writing `custom_modes.json` will be managed within the `tmp_path` fixture or explicitly mocked where necessary (e.g., simulating permission errors).
*   **Invocation:** The `CliRunner.invoke()` method will be used to run the `cli compile <agent-slug>` command.
*   **Assertions:** Assertions will check:
    *   CLI exit code (`result.exit_code`).
    *   CLI output (`result.stdout`, `result.stderr`).
    *   The state of the mocked `custom_modes.json` file after the command runs.
    *   Mock call counts and arguments (where necessary to verify interactions).

## 4. Test Cases

**Setup (Common for most tests):**

*   Use a `pytest` fixture to provide `CliRunner` and `tmp_path`.
*   Within the fixture or test setup, patch `registry_manager.GLOBAL_REGISTRY_PATH` to point to `tmp_path / "custom_modes.json"`.
*   Assume agent configs are expected under `tmp_path / "agents" / <agent-slug> / "config.yaml"`.

**Test Case 3.2.1: Successful Compilation (New Agent)**

*   **Description:** Verify successful compilation and addition of a new agent to an empty or non-existent registry.
*   **Preconditions:**
    *   Mocked `custom_modes.json` does not exist or is empty (`{"customModes": []}`).
    *   Create a valid `config.yaml` for `agent-a` under `tmp_path / "agents" / "agent-a" / "config.yaml"`. Include all required fields (`slug`, `name`, `roleDefinition`) and optional ones like `groups`, `apiConfiguration`. Include `customInstructions`.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-a"])`.
*   **Expected Outcome:**
    *   Exit code: 0.
    *   Stdout: Contains success message (e.g., "Successfully compiled and updated registry for agent 'agent-a'.").
    *   Mocked `custom_modes.json`: Exists and contains one entry under `customModes` for `agent-a`.
    *   The `agent-a` entry in JSON contains `slug`, `name`, `roleDefinition`, `groups`, `apiConfiguration` (if provided) but **NOT** `customInstructions`.

**Test Case 3.2.2: Successful Compilation (Update Existing Agent)**

*   **Description:** Verify successful compilation and update of an existing agent in the registry.
*   **Preconditions:**
    *   Create an initial mocked `custom_modes.json` containing an entry for `agent-a` (with some initial data).
    *   Create a valid `config.yaml` for `agent-a` under `tmp_path / "agents" / "agent-a" / "config.yaml"` with *updated* values for `name`, `roleDefinition`, etc. Include `customInstructions`.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-a"])`.
*   **Expected Outcome:**
    *   Exit code: 0.
    *   Stdout: Contains success message.
    *   Mocked `custom_modes.json`: Contains one entry for `agent-a` with the *updated* metadata.
    *   The `agent-a` entry **does not** contain `customInstructions`.

**Test Case 3.2.3: Failure - Agent Config Not Found**

*   **Description:** Verify correct error handling when the `config.yaml` for the specified agent slug does not exist.
*   **Preconditions:**
    *   Mocked `custom_modes.json` exists (can be empty or have other agents).
    *   Ensure no `config.yaml` exists for `non-existent-agent`.
*   **Action:** Run `runner.invoke(app, ["compile", "non-existent-agent"])`.
*   **Expected Outcome:**
    *   Exit code: Non-zero (e.g., 1).
    *   Stderr: Contains error message indicating configuration file not found for `non-existent-agent`.
    *   Mocked `custom_modes.json`: Remains unchanged from its initial state.

**Test Case 3.2.4: Failure - Invalid YAML Syntax**

*   **Description:** Verify correct error handling when `config.yaml` contains invalid YAML syntax.
*   **Preconditions:**
    *   Mocked `custom_modes.json` exists.
    *   Create an invalid `config.yaml` (e.g., unbalanced brackets, incorrect indentation) for `agent-b` under `tmp_path / "agents" / "agent-b" / "config.yaml"`.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-b"])`.
*   **Expected Outcome:**
    *   Exit code: Non-zero.
    *   Stderr: Contains error message indicating a YAML parsing error in the specific file.
    *   Mocked `custom_modes.json`: Remains unchanged.

**Test Case 3.2.5: Failure - Schema Validation Error**

*   **Description:** Verify correct error handling when `config.yaml` is valid YAML but fails Pydantic schema validation.
*   **Preconditions:**
    *   Mocked `custom_modes.json` exists.
    *   Create a `config.yaml` for `agent-c` that is valid YAML but missing a required field (e.g., `name`) or has incorrect data types.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-c"])`.
*   **Expected Outcome:**
    *   Exit code: Non-zero.
    *   Stderr: Contains error message indicating a validation error, ideally mentioning the specific field(s) and error type (e.g., "field required", "value is not a valid integer").
    *   Mocked `custom_modes.json`: Remains unchanged.

**Test Case 3.2.6: Failure - Registry Read Error**

*   **Description:** Verify error handling when reading the global registry fails.
*   **Preconditions:**
    *   Patch `registry_manager.read_global_registry` to raise an `OSError` (e.g., simulating permission denied).
    *   Create a valid `config.yaml` for `agent-d`.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-d"])`.
*   **Expected Outcome:**
    *   Exit code: Non-zero.
    *   Stderr: Contains error message indicating failure to read the registry file.

**Test Case 3.2.7: Failure - Registry Write Error**

*   **Description:** Verify error handling when writing the updated global registry fails.
*   **Preconditions:**
    *   Ensure `registry_manager.read_global_registry` works (or returns a default).
    *   Patch `registry_manager.write_global_registry` to raise an `OSError` (e.g., simulating disk full or permission denied).
    *   Create a valid `config.yaml` for `agent-e`.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-e"])`.
*   **Expected Outcome:**
    *   Exit code: Non-zero.
    *   Stderr: Contains error message indicating failure to write the updated registry file.

**Test Case 3.2.8: Verify Call Sequence (Optional - Lower Priority)**

*   **Description:** Use mocks to verify the internal sequence of calls: loader -> compiler -> registry manager update -> registry manager write.
*   **Preconditions:**
    *   Patch `config_loader.load_and_validate_config`, `compiler.extract_registry_metadata`, `registry_manager.update_global_registry`, `registry_manager.write_global_registry`.
    *   Configure mocks to return appropriate values to allow the sequence to proceed.
    *   Create a valid `config.yaml` for `agent-f`.
*   **Action:** Run `runner.invoke(app, ["compile", "agent-f"])`.
*   **Expected Outcome:**
    *   Exit code: 0.
    *   Assert that `load_and_validate_config` was called once with the correct path.
    *   Assert that `extract_registry_metadata` was called once with the object returned by the loader mock.
    *   Assert that `update_global_registry` was called once with the data returned by the compiler mock.
    *   Assert that `write_global_registry` was called once with the data returned by the update mock.

## 5. Prerequisites

*   Implementation of Task 3.1 (`registry_manager.py`).
*   Implementation of Task 3.2 (`cli compile` command structure in `cli/main.py`).
*   Availability of `pytest`, `typer`, and `unittest.mock`.

## 6. Cleanup

*   `pytest`'s `tmp_path` fixture automatically handles the cleanup of temporary directories and files created during the tests.
*   Ensure mocks are properly unpatched after each test (handled by `pytest` fixtures or context managers like `patch`).