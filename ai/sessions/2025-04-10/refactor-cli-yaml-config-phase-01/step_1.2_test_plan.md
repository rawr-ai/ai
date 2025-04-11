# Unit Test Plan: config_loader.py

**Date:** 2025-04-10
**Version:** 1.0
**Associated Task:** 1.2 (Implement `config_loader.py`) from `implementation_plan_scoped.md`
**Associated Models:** `cli/models.py` (`GlobalAgentConfig`, `ApiConfig`, `GroupRestriction`)
**Testing Strategy:** `testing_strategy_global.md` (Section 3.1)

## 1. Objective

To define unit tests for the `config_loader.py` module. These tests aim to verify the module's ability to correctly load, parse, and validate `config.yaml` files against the defined Pydantic schema (`GlobalAgentConfig`), and to handle various error conditions gracefully.

## 2. Scope

*   Testing the core function(s) within `config_loader.py` responsible for reading a YAML file from a given path, parsing its content, and validating it against the `GlobalAgentConfig` Pydantic model.
*   Testing focuses on validation logic, error handling for parsing and schema mismatches, and successful object creation.
*   **Out of Scope for Unit Tests (May be covered in Integration Tests):**
    *   File discovery logic (Unit tests will assume a file path is provided or mock file system interactions).
    *   Interactions with other modules like `compiler.py` or `registry_manager.py`.

## 3. Test Environment & Tools

*   **Framework:** `pytest`
*   **Mocking:** `pytest-mock` (for mocking file system operations like `open`, `os.path.exists`, etc.)
*   **Dependencies:** `PyYAML`, `Pydantic`

## 4. Test Cases

The following test cases will be implemented. Mocking will be used to simulate file content and file system states.

---

**Suite: Happy Path & Basic Validation**

*   **Test Case ID:** `LOADER_UT_001`
    *   **Description:** Verify successful loading, parsing, and validation of a minimal valid `config.yaml`.
    *   **Input:** Mock `config.yaml` content with required fields only (`slug`, `name`, `roleDefinition`, `groups` as simple list).
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Returns a valid `GlobalAgentConfig` Pydantic object matching the input YAML content. No exceptions raised.

*   **Test Case ID:** `LOADER_UT_002`
    *   **Description:** Verify successful loading with all optional fields (`apiConfiguration`) present and valid.
    *   **Input:** Mock `config.yaml` content including a valid `apiConfiguration` section.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Returns a valid `GlobalAgentConfig` object with the `apiConfiguration` attribute correctly populated.

*   **Test Case ID:** `LOADER_UT_003`
    *   **Description:** Verify successful loading with `groups` containing tuples with restrictions.
    *   **Input:** Mock `config.yaml` content where `groups` includes `["group1", ["group2", {"fileRegex": "\\.py$", "description": "Python files"}]]`.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Returns a valid `GlobalAgentConfig` object with `groups` correctly parsed into strings and tuples containing `GroupRestriction` objects.

---

**Suite: YAML Parsing Errors**

*   **Test Case ID:** `LOADER_UT_101`
    *   **Description:** Verify handling of invalid YAML syntax (e.g., incorrect indentation).
    *   **Input:** Mock `config.yaml` content with syntax errors.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises a `yaml.YAMLError` (or a custom exception wrapping it).

*   **Test Case ID:** `LOADER_UT_102`
    *   **Description:** Verify handling of non-YAML file content.
    *   **Input:** Mock file content that is not valid YAML (e.g., plain text, JSON).
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises a `yaml.YAMLError` (or a custom exception wrapping it).

---

**Suite: Pydantic Schema Validation Errors**

*   **Test Case ID:** `LOADER_UT_201`
    *   **Description:** Verify handling of missing required fields (e.g., missing `slug`).
    *   **Input:** Mock `config.yaml` content lacking the `slug` field.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises `pydantic.ValidationError`.

*   **Test Case ID:** `LOADER_UT_202`
    *   **Description:** Verify handling of incorrect data types (e.g., `slug` provided as a number).
    *   **Input:** Mock `config.yaml` content with `slug: 123`.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises `pydantic.ValidationError`.

*   **Test Case ID:** `LOADER_UT_203`
    *   **Description:** Verify handling of invalid nested model data (e.g., `apiConfiguration.model` missing).
    *   **Input:** Mock `config.yaml` content with `apiConfiguration` present but missing the required `model` field.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises `pydantic.ValidationError`.

*   **Test Case ID:** `LOADER_UT_204`
    *   **Description:** Verify handling of invalid URL format in `apiConfiguration.url`.
    *   **Input:** Mock `config.yaml` content with `apiConfiguration.url: "not-a-valid-url"`.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises `pydantic.ValidationError`.

*   **Test Case ID:** `LOADER_UT_205`
    *   **Description:** Verify handling of extra fields when `Extra.forbid` is set.
    *   **Input:** Mock `config.yaml` content with an additional, undefined field (e.g., `extraField: "someValue"`).
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises `pydantic.ValidationError`.

*   **Test Case ID:** `LOADER_UT_206`
    *   **Description:** Verify handling of invalid structure within the `groups` list (e.g., tuple with incorrect restriction format).
    *   **Input:** Mock `config.yaml` content with `groups: [["group1", {"invalidKey": "value"}]]`.
    *   **Steps:** Call `load_agent_config('mock_path/config.yaml')`.
    *   **Expected Result:** Raises `pydantic.ValidationError`.

---

**Suite: File Handling Errors**

*   **Test Case ID:** `LOADER_UT_301`
    *   **Description:** Verify handling when the specified `config.yaml` file does not exist.
    *   **Input:** Mock `os.path.exists` to return `False` for the given path.
    *   **Steps:** Call `load_agent_config('non_existent_path/config.yaml')`.
    *   **Expected Result:** Raises `FileNotFoundError` (or a custom exception wrapping it).

*   **Test Case ID:** `LOADER_UT_302`
    *   **Description:** Verify handling when there are permission errors reading the file.
    *   **Input:** Mock the `open()` built-in function to raise a `PermissionError` when called for the specified path.
    *   **Steps:** Call `load_agent_config('permission_denied_path/config.yaml')`.
    *   **Expected Result:** Raises `PermissionError` (or a custom exception wrapping it).

---

## 5. Test Data Requirements

*   Sample `config.yaml` files (or string representations for mocking) covering:
    *   Minimal valid configuration.
    *   Fully populated valid configuration.
    *   Configurations with various valid `groups` structures.
    *   Files with YAML syntax errors.
    *   Files with various Pydantic schema violations (missing fields, wrong types, extra fields, invalid nested data).

## 6. Assumptions & Dependencies

*   The `config_loader.py` module will have a primary function (e.g., `load_agent_config`) that accepts a file path as input.
*   The Pydantic models in `cli/models.py` are stable and correctly represent the target schema for this phase.
*   Standard Python exceptions (`FileNotFoundError`, `PermissionError`) and exceptions from `PyYAML` (`yaml.YAMLError`) and `Pydantic` (`pydantic.ValidationError`) will be used for error signaling, unless custom exceptions are introduced.