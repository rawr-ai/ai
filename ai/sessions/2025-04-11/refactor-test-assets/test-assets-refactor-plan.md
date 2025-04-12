Okay, I will create the detailed refactoring plan as requested.

```text
Refactoring Plan: Externalize Test Data Structures

**Objective:** To improve test readability and maintainability in `tests/unit/test_compiler.py` by externalizing inline `expected_output` dictionaries into separate JSON asset files.

**1. Analysis of Candidates:**

*   **`tests/conftest.py`, line 14 (`config_content`):** This variable's definition relies on dynamically generated paths (`tmp_path`, `agent_config_file_path`, `markdown_dir_path`) created within the `cli_config_yaml` fixture for each test run. Due to this dynamic nature, it cannot be directly externalized into a static asset file (like YAML or JSON). Therefore, this candidate will **not** be included in the externalization process outlined in this plan.
*   **`tests/unit/test_compiler.py`, line 15 (`expected_output` in `test_extract_full_data`):** This dictionary contains static data representing the expected output for the test. It is suitable for externalization into a JSON file.
*   **`tests/unit/test_compiler.py`, line 40 (`expected_output` in `test_extract_minimal_data`):** Similar to the above, this dictionary contains static data and is suitable for externalization into a JSON file.

**2. Proposed Asset Structure:**

Test assets will be stored in a dedicated directory structure mirroring the test source files:

```
tests/
├── assets/
│   └── unit/
│       └── test_compiler/
│           ├── expected_output_full.json
│           └── expected_output_minimal.json
├── conftest.py
└── unit/
    └── test_compiler.py
```

**3. Asset File Definitions:**

*   **File Path:** `tests/assets/unit/test_compiler/expected_output_full.json`
*   **Format:** JSON
*   **Content:**
    ```json
    {
      "slug": "test-agent",
      "name": "Test Agent",
      "roleDefinition": "This is a test role.",
      "groups": ["groupA", ["groupB", {"fileRegex": ".*\\.py", "description": "Python files"}]],
      "apiConfiguration": {"model": "gpt-4", "url": "http://example.com/api", "params": {"temp": 0.5}}
    }
    ```

*   **File Path:** `tests/assets/unit/test_compiler/expected_output_minimal.json`
*   **Format:** JSON
*   **Content:**
    ```json
    {
      "slug": "minimal-agent",
      "name": "Minimal Agent",
      "roleDefinition": "Minimal role.",
      "groups": ["core"],
      "apiConfiguration": null
    }
    ```

**4. Code Modification Plan (`tests/unit/test_compiler.py`):**

*   **Required Imports:** Add the following imports at the top of the file:
    ```python
    import json
    from pathlib import Path
    ```

*   **Modifications for `test_extract_full_data`:**
    *   Replace the inline definition of `expected_output`.
    *   Add code to load the data from the corresponding JSON asset file.

    ```python
    # Test Case ID: TC_EXTRACT_001 - Happy Path - Full Data Input
    def test_extract_full_data():
        """Verify correct metadata extraction with all fields populated."""
        input_config = GlobalAgentConfig(
            slug="test-agent",
            name="Test Agent",
            roleDefinition="This is a test role.",
            groups=["groupA", ("groupB", GroupRestriction(fileRegex=".*\\.py", description="Python files"))],
            apiConfiguration=ApiConfig(model="gpt-4", url="http://example.com/api", params={"temp": 0.5})
        )
        # --- Start Modification ---
        # Load expected output from asset file
        asset_path = Path(__file__).parent.parent / 'assets' / 'unit' / 'test_compiler' / 'expected_output_full.json'
        with open(asset_path, 'r') as f:
            expected_output = json.load(f)
        # --- End Modification ---

        actual_output = extract_registry_metadata(input_config)
        # Convert HttpUrl to string for comparison if present
        if actual_output.get("apiConfiguration") and isinstance(actual_output["apiConfiguration"].get("url"), object):
             actual_output["apiConfiguration"]["url"] = str(actual_output["apiConfiguration"]["url"])
        assert actual_output == expected_output
        assert set(actual_output.keys()) == set(expected_output.keys()) # Explicit key check
    ```

*   **Modifications for `test_extract_minimal_data`:**
    *   Replace the inline definition of `expected_output`.
    *   Add code to load the data from the corresponding JSON asset file.

    ```python
    # Test Case ID: TC_EXTRACT_002 - Happy Path - Minimal Data Input
    def test_extract_minimal_data():
        """Verify correct metadata extraction with only required fields and None for optional."""
        input_config = GlobalAgentConfig(
            slug="minimal-agent",
            name="Minimal Agent",
            roleDefinition="Minimal role.",
            groups=["core"],
            apiConfiguration=None
        )
        # --- Start Modification ---
        # Load expected output from asset file
        asset_path = Path(__file__).parent.parent / 'assets' / 'unit' / 'test_compiler' / 'expected_output_minimal.json'
        with open(asset_path, 'r') as f:
            expected_output = json.load(f)
        # --- End Modification ---

        actual_output = extract_registry_metadata(input_config)

        # Check if apiConfiguration is None or absent, depending on implementation choice
        if "apiConfiguration" in actual_output:
             assert actual_output["apiConfiguration"] is None
             assert actual_output == expected_output # Check full dict if key is present
        else:
            # If key is absent, remove it from expected for comparison
            # Ensure expected_output is mutable if deletion is needed, or handle comparison differently
            expected_output_copy = expected_output.copy()
            del expected_output_copy["apiConfiguration"]
            assert actual_output == expected_output_copy

        assert set(actual_output.keys()) <= {'slug', 'name', 'roleDefinition', 'groups', 'apiConfiguration'}
    ```

**5. Conclusion:**

This plan outlines the steps to externalize static `expected_output` data from `tests/unit/test_compiler.py` into JSON asset files located in `tests/assets/unit/test_compiler/`. The `config_content` variable in `tests/conftest.py` remains unchanged due to its dynamic nature. This refactoring aims to improve the readability and maintainability of the tests by separating test data from test logic.

**Note:** This plan describes the proposed changes. No files have been created or modified at this stage. Execution would require using file writing and modification tools based on this plan.
```