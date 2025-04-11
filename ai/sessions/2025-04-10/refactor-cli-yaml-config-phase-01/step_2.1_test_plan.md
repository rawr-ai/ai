# Unit Test Plan: `extract_registry_metadata` Function

**Objective:** Define unit tests for the `extract_registry_metadata` function, anticipated to reside in `cli/compiler.py`. This function's purpose is to extract metadata from a validated `GlobalAgentConfig` Pydantic object, specifically for updating the global `custom_modes.json` registry.

**Target Function Signature (Assumed):**
```python
# In cli/compiler.py
from cli.models import GlobalAgentConfig
from typing import Dict, Any

def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
    """
    Extracts metadata suitable for the custom_modes.json registry
    from a validated GlobalAgentConfig object.
    Excludes fields not relevant to the registry (e.g., customInstructions).
    """
    # Implementation to be added
    pass
```

**Scope:** This plan covers unit testing of the metadata extraction logic within the `extract_registry_metadata` function. It does *not* cover the upstream processes of configuration file loading, parsing, or validation, nor the downstream process of writing to the `custom_modes.json` file.

**Required Metadata Fields for `custom_modes.json`:**
Based on `implementation_plan_scoped.md` and `cli/models.py`:
*   `slug`
*   `name`
*   `roleDefinition`
*   `groups`
*   `apiConfiguration` (if present in the input `GlobalAgentConfig`)

**Explicitly Excluded Fields:**
*   `customInstructions` (Note: This field is not present in the `GlobalAgentConfig` model itself, ensuring its exclusion is implicit by only selecting required fields).

**Test Cases:**

1.  **Test Case ID: TC_EXTRACT_001**
    *   **Scenario:** Happy Path - Full Data Input
    *   **Description:** Verify correct metadata extraction when the input `GlobalAgentConfig` object contains values for all required fields and the optional `apiConfiguration` field.
    *   **Input:** A `GlobalAgentConfig` instance populated with:
        *   `slug`: "test-agent"
        *   `name`: "Test Agent"
        *   `roleDefinition`: "This is a test role."
        *   `groups`: ["groupA", ("groupB", {"fileRegex": ".*\\.py", "description": "Python files"})]
        *   `apiConfiguration`: {"model": "gpt-4", "url": "http://example.com/api", "params": {"temp": 0.5}}
    *   **Expected Output:** A dictionary containing keys `slug`, `name`, `roleDefinition`, `groups`, and `apiConfiguration` with values identical to the input object's corresponding fields. The structure of nested objects (`groups` tuples, `apiConfiguration`) should be preserved as required by the registry format.
    *   **Verification:** Assert that the returned dictionary contains exactly the expected keys and that their values match the input data precisely.

2.  **Test Case ID: TC_EXTRACT_002**
    *   **Scenario:** Happy Path - Minimal Data Input
    *   **Description:** Verify correct metadata extraction when the input `GlobalAgentConfig` contains only the required fields, and optional fields like `apiConfiguration` are `None`.
    *   **Input:** A `GlobalAgentConfig` instance populated with:
        *   `slug`: "minimal-agent"
        *   `name`: "Minimal Agent"
        *   `roleDefinition`: "Minimal role."
        *   `groups`: ["core"]
        *   `apiConfiguration`: `None`
    *   **Expected Output:** A dictionary containing keys `slug`, `name`, `roleDefinition`, and `groups`. The `apiConfiguration` key should either be absent or have a value of `None` (consistency to be decided during implementation, but test should check for one of these).
    *   **Verification:** Assert that the returned dictionary contains the required keys with correct values and handles the absent optional field as expected.

3.  **Test Case ID: TC_EXTRACT_003**
    *   **Scenario:** Groups Variation - Simple String List
    *   **Description:** Verify correct handling and extraction when the `groups` field is a simple list of strings.
    *   **Input:** `GlobalAgentConfig` with `groups=["groupX", "groupY"]` (other required fields populated minimally).
    *   **Expected Output:** The returned dictionary includes the key `groups` with the value `["groupX", "groupY"]`.
    *   **Verification:** Assert the `groups` value in the output dictionary is a list identical to the input.

4.  **Test Case ID: TC_EXTRACT_004**
    *   **Scenario:** Groups Variation - Mixed String and Tuple List
    *   **Description:** Verify correct handling and extraction when the `groups` field contains a mix of simple strings and tuples (string, `GroupRestriction`).
    *   **Input:** `GlobalAgentConfig` with `groups=["groupA", ("groupB", {"fileRegex": ".*\\.md"})]` (other required fields populated minimally).
    *   **Expected Output:** The returned dictionary includes the key `groups` with a value representing the mixed list structure accurately, suitable for `custom_modes.json` (e.g., `["groupA", ["groupB", {"fileRegex": ".*\\.md", "description": None}]]`). *Note: The exact serialization format for the tuple within the JSON needs confirmation, but the test should verify the chosen format.*
    *   **Verification:** Assert the `groups` value in the output dictionary correctly reflects the mixed structure and content of the input.

5.  **Test Case ID: TC_EXTRACT_005**
    *   **Scenario:** Groups Variation - Empty List
    *   **Description:** Verify correct handling when the input `groups` list is empty.
    *   **Input:** `GlobalAgentConfig` with `groups=[]` (other required fields populated minimally).
    *   **Expected Output:** The returned dictionary includes the key `groups` with the value `[]`.
    *   **Verification:** Assert the `groups` value in the output dictionary is an empty list.

6.  **Test Case ID: TC_EXTRACT_006**
    *   **Scenario:** Field Exclusion Verification
    *   **Description:** Explicitly verify that the output dictionary contains *only* the keys corresponding to the fields required for `custom_modes.json` (`slug`, `name`, `roleDefinition`, `groups`, `apiConfiguration`) and no others.
    *   **Input:** A `GlobalAgentConfig` instance (e.g., the one from TC_EXTRACT_001).
    *   **Expected Output:** The set of keys in the returned dictionary is exactly `{ 'slug', 'name', 'roleDefinition', 'groups', 'apiConfiguration' }`.
    *   **Verification:** Assert that `set(output_dict.keys())` is equal to the expected set of keys.

**Test Implementation Notes:**

*   **Framework:** `pytest` is recommended.
*   **Dependencies:** Tests will require importing `GlobalAgentConfig`, `ApiConfig`, and `GroupRestriction` from `cli.models`.
*   **Test Data:** Each test case will construct the specified `GlobalAgentConfig` instance in memory.
*   **Assertions:** Use standard `pytest` assertions (`assert`) to compare the dictionary returned by `extract_registry_metadata` against the expected dictionary structure and values for each test case. Focus on both key presence/absence and value correctness.