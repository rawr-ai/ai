# Unit Test Plan: registry_manager.py (Task 3.1)

**Date:** 2025-04-10
**Associated Task:** Implement `registry_manager.py` (Task 3.1 from `implementation_plan_scoped.md`)
**Project Phase:** CLI YAML Config Refactoring Phase 1

## 1. Objective

Define unit tests for the `registry_manager.py` module. These tests will ensure the module correctly reads, updates, and safely writes the global `custom_modes.json` file according to the specified requirements, focusing on isolating the module's logic from the actual file system using mocking.

## 2. Scope

*   Unit testing of functions within `registry_manager.py`.
*   Focus on logic for reading, parsing, updating (add/modify), and writing the registry data structure.
*   Verification of requirements: safe writing, exclusion of `customInstructions`.
*   Testing of error handling scenarios related to file access (mocked).

**Out of Scope:**
*   Integration testing with `cli compile` command.
*   Testing the actual file system interactions (these will be mocked).
*   Testing the `compiler.extract_registry_metadata` function (assumed input).

## 3. Test Environment & Tools

*   **Framework:** `pytest`
*   **Mocking:** `pytest-mock` (specifically the `mocker` fixture)
*   **Language:** Python
*   **Key Mocks:**
    *   `pathlib.Path.exists`
    *   `pathlib.Path.read_text`
    *   `pathlib.Path.write_text`
    *   `json.load` / `json.loads`
    *   `json.dump` / `json.dumps`
    *   Potentially `tempfile.NamedTemporaryFile` or similar if used for safe writes.
    *   Built-in `open` function.

## 4. Test Strategy

*   **Isolation:** Each test will focus on a specific function or scenario within `registry_manager.py`.
*   **Mocking:** File system operations (`read`, `write`, `exists`) and JSON parsing/dumping will be heavily mocked to control inputs and outputs and prevent side effects on the actual global registry file. Mocked exceptions (e.g., `FileNotFoundError`, `PermissionError`) will be used to test error handling.
*   **Assertions:** Assertions will verify:
    *   The structure and content of the data returned by read operations.
    *   The arguments passed to mocked write operations (correct path, correct data structure, absence of `customInstructions`).
    *   Correct handling of edge cases (empty file, non-existent file).
    *   Correct exception handling.

## 5. Test Cases

Let's assume `registry_manager.py` has functions like `_read_registry()`, `_write_registry()`, and the main `update_global_registry(agent_metadata: dict)`. The global registry path will be a constant or configurable value within the module.

**Target Registry Path (to be mocked):** `/Users/mateicanavra/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json`

**Default Empty Structure:** `{"customModes": []}`

**Test Suite: Reading Registry (`_read_registry`)**

*   **TC-READ-01: Read Existing Valid JSON:**
    *   **Setup:** Mock `Path.exists` to return `True`. Mock `Path.read_text` to return valid JSON string (e.g., `{"customModes": [{"slug": "agent1", "name": "Agent One"}]}`). Mock `json.loads`.
    *   **Action:** Call `_read_registry()`.
    *   **Assert:** Returns the expected Python dictionary. `json.loads` called with correct string.
*   **TC-READ-02: Read Existing Empty JSON:**
    *   **Setup:** Mock `Path.exists` to return `True`. Mock `Path.read_text` to return `{"customModes": []}`. Mock `json.loads`.
    *   **Action:** Call `_read_registry()`.
    *   **Assert:** Returns `{"customModes": []}`.
*   **TC-READ-03: Read Existing Invalid JSON:**
    *   **Setup:** Mock `Path.exists` to return `True`. Mock `Path.read_text` to return invalid JSON string (`{`). Mock `json.loads` to raise `json.JSONDecodeError`.
    *   **Action:** Call `_read_registry()`.
    *   **Assert:** Raises an appropriate custom exception (e.g., `RegistryReadError`) or logs an error and returns the default empty structure (TBD based on implementation choice).
*   **TC-READ-04: File Not Found:**
    *   **Setup:** Mock `Path.exists` to return `False`. Mock `Path.read_text` to raise `FileNotFoundError`.
    *   **Action:** Call `_read_registry()`.
    *   **Assert:** Returns the default empty structure `{"customModes": []}`. `Path.read_text` is *not* called.
*   **TC-READ-05: Permission Denied:**
    *   **Setup:** Mock `Path.exists` to return `True`. Mock `Path.read_text` to raise `PermissionError`.
    *   **Action:** Call `_read_registry()`.
    *   **Assert:** Raises an appropriate custom exception (e.g., `RegistryReadError` or `RegistryPermissionError`).

**Test Suite: Updating Registry (`update_global_registry`)**

*(These tests implicitly test `_write_registry` via mocking)*

*   **TC-UPDATE-01: Add New Agent to Empty Registry:**
    *   **Setup:** Mock `_read_registry` to return `{"customModes": []}`. Mock `_write_registry`. Define `new_agent_metadata = {"slug": "new-agent", "name": "New Agent", "roleDefinition": "...", "customInstructions": "SHOULD BE IGNORED"}`.
    *   **Action:** Call `update_global_registry(new_agent_metadata)`.
    *   **Assert:** `_write_registry` called once. The dictionary passed to `_write_registry` contains `{"customModes": [{"slug": "new-agent", "name": "New Agent", "roleDefinition": "..."}]}` (NO `customInstructions`).
*   **TC-UPDATE-02: Add New Agent to Existing Registry:**
    *   **Setup:** Mock `_read_registry` to return `{"customModes": [{"slug": "agent1", "name": "Agent One"}]}`. Mock `_write_registry`. Define `new_agent_metadata = {"slug": "new-agent", "name": "New Agent", "roleDefinition": "..."}`.
    *   **Action:** Call `update_global_registry(new_agent_metadata)`.
    *   **Assert:** `_write_registry` called once. The dictionary passed contains both `agent1` and `new-agent` under `customModes`, correctly structured, without `customInstructions` for the new agent.
*   **TC-UPDATE-03: Update Existing Agent:**
    *   **Setup:** Mock `_read_registry` to return `{"customModes": [{"slug": "agent1", "name": "Agent One", "roleDefinition": "Old Role"}]}`. Mock `_write_registry`. Define `updated_agent_metadata = {"slug": "agent1", "name": "Agent One Updated", "roleDefinition": "New Role", "customInstructions": "SHOULD BE IGNORED"}`.
    *   **Action:** Call `update_global_registry(updated_agent_metadata)`.
    *   **Assert:** `_write_registry` called once. The dictionary passed contains `{"customModes": [{"slug": "agent1", "name": "Agent One Updated", "roleDefinition": "New Role"}]}` (updated fields, NO `customInstructions`).
*   **TC-UPDATE-04: Update Agent - Verify `customInstructions` Exclusion:**
    *   **Setup:** Mock `_read_registry` to return `{"customModes": [{"slug": "agent1", "name": "Agent One"}]}`. Mock `_write_registry`. Define `agent_with_ci = {"slug": "agent1", "name": "Agent One", "customInstructions": "This must not be written"}`.
    *   **Action:** Call `update_global_registry(agent_with_ci)`.
    *   **Assert:** `_write_registry` called once. The dictionary passed to `_write_registry` for `agent1` does **not** contain the `customInstructions` key.
*   **TC-UPDATE-05: Handle Read Error During Update:**
    *   **Setup:** Mock `_read_registry` to raise `RegistryReadError`. Mock `_write_registry`. Define `agent_metadata = {"slug": "agent1", "name": "Agent One"}`.
    *   **Action:** Call `update_global_registry(agent_metadata)`.
    *   **Assert:** Raises `RegistryReadError` (or appropriate exception). `_write_registry` is *not* called.
*   **TC-UPDATE-06: Handle Write Error During Update:**
    *   **Setup:** Mock `_read_registry` to return `{"customModes": []}`. Mock `_write_registry` to raise `RegistryWriteError` (or `PermissionError`, etc.). Define `agent_metadata = {"slug": "agent1", "name": "Agent One"}`.
    *   **Action:** Call `update_global_registry(agent_metadata)`.
    *   **Assert:** Raises `RegistryWriteError` (or appropriate exception).

**Test Suite: Writing Registry (`_write_registry`)**

*(Focus on safe write mechanism if implemented, e.g., temp file usage)*

*   **TC-WRITE-01: Successful Write:**
    *   **Setup:** Mock `Path.write_text` (or `open` and `json.dump`). Define `data_to_write = {"customModes": [{"slug": "agent1", "name": "Agent One"}]}`.
    *   **Action:** Call `_write_registry(data_to_write)`.
    *   **Assert:** `Path.write_text` (or equivalent) called with the correct target path and correctly formatted JSON string representation of `data_to_write`.
*   **TC-WRITE-02: Safe Write (Temp File):** (If applicable)
    *   **Setup:** Mock `tempfile.NamedTemporaryFile`, mock `os.replace` (or `shutil.move`), mock `Path.write_text`. Define `data_to_write`.
    *   **Action:** Call `_write_registry(data_to_write)`.
    *   **Assert:** `NamedTemporaryFile` is used. `write_text` called on the temp file path. `os.replace` called with temp file path and final target path. Original `write_text` on final path might not be called directly.
*   **TC-WRITE-03: Permission Denied on Write:**
    *   **Setup:** Mock `Path.write_text` (or `open`) to raise `PermissionError`. Define `data_to_write`.
    *   **Action:** Call `_write_registry(data_to_write)`.
    *   **Assert:** Raises `RegistryWriteError` or `RegistryPermissionError`.
*   **TC-WRITE-04: Disk Full Error on Write:** (Harder to mock precisely, might simulate via generic `OSError`)
    *   **Setup:** Mock `Path.write_text` (or `open`) to raise `OSError("No space left on device")`. Define `data_to_write`.
    *   **Action:** Call `_write_registry(data_to_write)`.
    *   **Assert:** Raises `RegistryWriteError` or `OSError`.

## 6. Prerequisites

*   Python environment with `pytest` and `pytest-mock` installed.
*   The `registry_manager.py` module implemented (even if basic structure).

## 7. Success Criteria

*   All defined unit tests pass.
*   Test coverage meets project standards (if defined).
*   Tests effectively mock file system interactions.
*   Tests cover requirements including `customInstructions` exclusion and error handling.

## 8. Cleanup

*   No explicit cleanup steps are required for these unit tests as all file system interactions are mocked. The tests do not create actual files or directories.