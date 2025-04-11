# Unit Test Plan: Pydantic Models for Global Agent Config (Step 1.1)

**Date:** 2025-04-10
**Session Context:** `refactor-cli-yaml-config-phase-01`
**Target Models File:** `cli/models.py`
**Input Definition:** `ai/sessions/2025-04-10/refactor-cli-yaml-config-phase-01/step_01_definition.md`
**Testing Framework:** `pytest`

## 1. Objective

This plan outlines the unit tests required to validate the Pydantic models (`GroupRestriction`, `ApiConfig`, `GlobalAgentConfig`) defined for parsing and validating the global `config.yaml` structure. The goal is to ensure the models correctly enforce the schema, handle optional fields, validate data types, and reject invalid structures or extraneous fields as per the requirements.

## 2. Test Cases

### 2.1. `GroupRestriction` Model Tests

*   **Test Case GR-01:** Instantiate `GroupRestriction` with minimal valid data (only `fileRegex`).
    *   **Input:** `{"fileRegex": ".*\\.py"}`
    *   **Expected:** Successful instantiation, `description` is `None`.
*   **Test Case GR-02:** Instantiate `GroupRestriction` with all valid data.
    *   **Input:** `{"fileRegex": ".*\\.ts", "description": "TypeScript files"}`
    *   **Expected:** Successful instantiation with correct values.
*   **Test Case GR-03:** Instantiate `GroupRestriction` missing the required `fileRegex` field.
    *   **Input:** `{"description": "Missing regex"}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case GR-04:** Instantiate `GroupRestriction` with incorrect type for `fileRegex`.
    *   **Input:** `{"fileRegex": 123}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case GR-05:** Instantiate `GroupRestriction` with incorrect type for `description`.
    *   **Input:** `{"fileRegex": ".*", "description": ["list", "is", "wrong"]}`
    *   **Expected:** Pydantic `ValidationError`.

### 2.2. `ApiConfig` Model Tests

*   **Test Case AC-01:** Instantiate `ApiConfig` with minimal valid data (only `model`).
    *   **Input:** `{"model": "gpt-4"}`
    *   **Expected:** Successful instantiation, `url` and `params` are `None`.
*   **Test Case AC-02:** Instantiate `ApiConfig` with all valid data (including valid `HttpUrl`).
    *   **Input:** `{"model": "claude-3", "url": "https://api.example.com/v1", "params": {"temp": 0.5}}`
    *   **Expected:** Successful instantiation with correct values.
*   **Test Case AC-03:** Instantiate `ApiConfig` missing the required `model` field.
    *   **Input:** `{"url": "https://api.example.com/v1"}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case AC-04:** Instantiate `ApiConfig` with incorrect type for `model`.
    *   **Input:** `{"model": False}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case AC-05:** Instantiate `ApiConfig` with an invalid URL string for `url`.
    *   **Input:** `{"model": "gpt-3", "url": "not-a-valid-url"}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case AC-06:** Instantiate `ApiConfig` with incorrect type for `params`.
    *   **Input:** `{"model": "gemini", "params": ["param1", "param2"]}`
    *   **Expected:** Pydantic `ValidationError`.

### 2.3. `GlobalAgentConfig` Model Tests

*   **Test Case GAC-01:** Instantiate `GlobalAgentConfig` with minimal required fields and simple string groups.
    *   **Input:** `{"slug": "test-agent", "name": "Test Agent", "roleDefinition": "Role desc", "groups": ["read", "write"]}`
    *   **Expected:** Successful instantiation, `apiConfiguration` is `None`.
*   **Test Case GAC-02:** Instantiate `GlobalAgentConfig` with all fields, including `apiConfiguration`.
    *   **Input:** `{"slug": "api-agent", "name": "API Agent", "roleDefinition": "API role", "groups": ["api"], "apiConfiguration": {"model": "gpt-4o", "url": "https://api.openai.com"}}`
    *   **Expected:** Successful instantiation with nested `ApiConfig`.
*   **Test Case GAC-03:** Instantiate `GlobalAgentConfig` with `groups` containing a `Tuple[str, GroupRestriction]`.
    *   **Input:** `{"slug": "edit-agent", "name": "Edit Agent", "roleDefinition": "Edit role", "groups": [("edit", {"fileRegex": "\\.py$", "description": "Python files"})]}`
    *   **Expected:** Successful instantiation with nested `GroupRestriction`.
*   **Test Case GAC-04:** Instantiate `GlobalAgentConfig` with `groups` containing mixed types (`str` and `Tuple`).
    *   **Input:** `{"slug": "mixed-agent", "name": "Mixed Agent", "roleDefinition": "Mixed role", "groups": ["read", ("edit", {"fileRegex": "\\.md$"})]}`
    *   **Expected:** Successful instantiation.
*   **Test Case GAC-05:** Instantiate `GlobalAgentConfig` missing a required field (e.g., `name`).
    *   **Input:** `{"slug": "no-name", "roleDefinition": "...", "groups": ["read"]}`
    *   **Expected:** Pydantic `ValidationError`. (Repeat for `slug`, `roleDefinition`, `groups`).
*   **Test Case GAC-06:** Instantiate `GlobalAgentConfig` with incorrect type for a required field (e.g., `slug` as int).
    *   **Input:** `{"slug": 123, "name": "Wrong Type", "roleDefinition": "...", "groups": ["read"]}`
    *   **Expected:** Pydantic `ValidationError`. (Repeat for `name`, `roleDefinition`).
*   **Test Case GAC-07:** Instantiate `GlobalAgentConfig` with incorrect type/structure for `groups` (e.g., list of ints).
    *   **Input:** `{"slug": "bad-groups", "name": "Bad Groups", "roleDefinition": "...", "groups": [1, 2, 3]}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case GAC-08:** Instantiate `GlobalAgentConfig` with incorrect tuple structure in `groups`.
    *   **Input:** `{"slug": "bad-tuple", "name": "Bad Tuple", "roleDefinition": "...", "groups": [("edit", "just_a_string")]}`
    *   **Expected:** Pydantic `ValidationError`.
*   **Test Case GAC-09:** Instantiate `GlobalAgentConfig` with an extraneous field not defined in the model (e.g., `customInstructions`).
    *   **Input:** `{"slug": "extra-field", "name": "Extra", "roleDefinition": "...", "groups": ["read"], "customInstructions": "Do extra things"}`
    *   **Expected:** Pydantic `ValidationError` (assuming default Pydantic behavior or explicit `extra='forbid'`).

## 3. Test Environment & Execution

*   Tests will be implemented using `pytest`.
*   Pydantic `ValidationError` should be explicitly caught and asserted for negative test cases.
*   Tests should be self-contained and not rely on external file I/O for model validation itself.

## 4. Success Criteria

*   All defined unit test cases pass.
*   Tests demonstrate correct validation of required fields, optional fields, data types, nested structures, and rejection of invalid/extraneous data.