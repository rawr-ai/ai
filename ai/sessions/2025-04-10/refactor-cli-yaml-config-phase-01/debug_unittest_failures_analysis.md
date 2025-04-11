# Unit Test Failure Analysis (Remediation Step F1.1)

**Date:** 2025-04-10
**Branch:** `refactor/cli-yaml-global`

This document details the root cause analysis for unit test failures identified in `tests/unit/test_compiler.py` and `tests/unit/test_registry_manager.py` on the `refactor/cli-yaml-global` branch.

## 1. `tests/unit/test_compiler.py` Failures (2 Failures)

*   **Affected Function:** `cli.compiler.extract_registry_metadata`
*   **Failing Tests (Likely):** `test_extract_full_data` (TC_EXTRACT_001), `test_extract_groups_mixed_list` (TC_EXTRACT_004)
*   **Root Cause:** **Incorrect Test Assertions**
    *   **Analysis:** The `extract_registry_metadata` function uses Pydantic's `model_dump(mode='json', ...)` method for serialization. This method correctly converts Python data types, including tuples within lists, into their JSON-compatible representations (lists become JSON arrays, tuples within lists also become elements in JSON arrays).
    *   The failing tests, however, assert that the `groups` field in the returned dictionary should contain Python *tuples* (e.g., `("groupB", {"fileRegex": ...})`). This expectation is incorrect for JSON-serialized output.
    *   **Example Discrepancy (from `test_extract_full_data`):**
        *   **Expected `groups` in test:** `["groupA", ("groupB", {"fileRegex": ".*\\.py", "description": "Python files"})]` (Contains a tuple)
        *   **Actual `groups` from function:** `["groupA", ["groupB", {"fileRegex": ".*\\.py", "description": "Python files"}]]` (Tuple converted to list)
*   **Conclusion:** The implementation in `cli/compiler.py` appears correct for JSON serialization. The tests need to be updated to assert the expected *list* structure instead of tuples within the `groups` field.

## 2. `tests/unit/test_registry_manager.py` Failures (4 Failures)

*   **Affected Function:** `cli.registry_manager.write_global_registry`
*   **Failing Tests (Likely):** `test_write_registry_success`, `test_write_registry_permission_error_on_move`, `test_write_registry_permission_error_on_temp_write`, `test_write_registry_os_error_disk_full`
*   **Root Cause:** **Outdated Test Logic**
    *   **Analysis:** The `write_global_registry` function was refactored. The previous implementation used a safe-write pattern involving `tempfile.NamedTemporaryFile` and `shutil.move` for atomicity. The current implementation performs a direct write to the target file path using `open()` and `json.dump()`.
    *   The existing tests for this function are still based on the *old* implementation. They heavily mock `tempfile.NamedTemporaryFile` and `shutil.move` and assert behavior related to this temporary file workflow.
    *   Since the implementation no longer uses these components, the mocks are ineffective, and the tests fail because they are testing logic that doesn't exist anymore.
*   **Conclusion:** The tests for `write_global_registry` are outdated due to the refactoring. They need to be rewritten to reflect the current direct-write implementation, likely by mocking `open()` and `json.dump()` on the target path and testing the relevant error handling scenarios for direct file I/O.

## Summary

The unit test failures stem from two distinct issues:

1.  **Incorrect Assertions (`test_compiler.py`):** Tests expect Python tuples in JSON-serialized output.
2.  **Outdated Test Logic (`test_registry_manager.py`):** Tests mock a previous implementation's safe-write mechanism (temp files) which is no longer used.

Both test files require updates to align with the current implementation on the `refactor/cli-yaml-global` branch. The underlying implementation code in `cli/compiler.py` and `cli/registry_manager.py` does not appear to be the direct cause of these specific test failures, although the registry manager's direct write is less safe than the previous atomic write.