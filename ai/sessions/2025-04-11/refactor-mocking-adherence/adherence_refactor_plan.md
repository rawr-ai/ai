# Mocking Adherence Refactoring Plan

## Introduction

This plan outlines the necessary refactoring steps to ensure tests comply with the project's mocking guidelines (`ai/sessions/2025-04-11/refactor-mocking-strategy/mocking_guidelines.md`). The analysis is based on the guidelines and the usage report (`ai/sessions/2025-04-11/refactor-mocking-strategy/mocking_usage_report.md`).

## Files Requiring Refactoring

### 1. `tests/unit/test_registry_manager.py`

**Violations:** This file contains multiple instances where `mocker.patch` is used directly to mock file system components (`pathlib.Path.exists`) or file-related operations (`json.load`) instead of relying exclusively on the helpers provided in `tests/helpers/mocking_utils.py`, as required by the guidelines. These patches are often redundant alongside existing helper calls.

**Refactoring Steps:**

The primary action for this file is to **remove** the direct `mocker.patch` calls related to `pathlib.Path.exists` and `json.load` within tests that already utilize `mocking_utils.mock_file_read`. The helper functions are designed to handle the necessary underlying mocks for file existence and content loading.

*   **Line 27:** `mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
    *   **Violation:** Direct patching of `pathlib.Path.exists`.
    *   **Action:** Remove this line. The subsequent `mocking_utils.mock_file_read` call (Line 29) handles the necessary mocking.
*   **Line 31:** `mock_json_load = mocker.patch("json.load", return_value=expected_data)`
    *   **Violation:** Direct patching of `json.load`.
    *   **Action:** Remove this line. The `mocking_utils.mock_file_read` call (Line 29) simulates reading the specified `content`, making this patch redundant.
*   **Line 47:** `mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
    *   **Violation:** Direct patching of `pathlib.Path.exists`.
    *   **Action:** Remove this line. The subsequent `mocking_utils.mock_file_read` call (Line 49) handles the necessary mocking.
*   **Line 50:** `mock_json_load = mocker.patch("json.load", return_value=expected_data)`
    *   **Violation:** Direct patching of `json.load`.
    *   **Action:** Remove this line. The `mocking_utils.mock_file_read` call (Line 49) simulates reading the specified `content`.
*   **Line 62:** `mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
    *   **Violation:** Direct patching of `pathlib.Path.exists`.
    *   **Action:** Remove this line. The subsequent `mocking_utils.mock_file_read` call (Line 64) handles the necessary mocking.
*   **Line 66:** `mock_json_load = mocker.patch("json.load", return_value=["list", "not", "dict"])`
    *   **Violation:** Direct patching of `json.load`.
    *   **Action:** Remove this line. The `mocking_utils.mock_file_read` call (Line 64) simulates reading the specified `content`.
*   **Line 81:** `mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
    *   **Violation:** Direct patching of `pathlib.Path.exists`.
    *   **Action:** Remove this line. The subsequent `mocking_utils.mock_file_read` call (Line 83) handles the necessary mocking.
*   **Line 84:** `mock_json_load = mocker.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0))`
    *   **Violation:** Direct patching of `json.load` side effect.
    *   **Action:** Remove this line. The `mocking_utils.mock_file_read` call (Line 83) simulates reading invalid JSON content, which should cause the actual `json.load` within the code under test to raise the `JSONDecodeError`.
*   **Line 98:** `mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=False)`
    *   **Violation:** Direct patching of `pathlib.Path.exists`.
    *   **Action:** Remove this line. The `mocking_utils.mock_file_read` helper (used on Line 100, though perhaps intended differently here) should ideally be configurable or a different helper used to simulate a non-existent file scenario if needed for `read_global_registry`. *Correction:* The guideline implies helpers *must* be used for file system interactions. If `mock_file_read` doesn't cover non-existence cleanly, the helper itself might need adjustment, but the direct patch is still a violation. For now, the action is removal, assuming the test logic or helper usage needs review.
*   **Line 114:** `mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
    *   **Violation:** Direct patching of `pathlib.Path.exists`.
    *   **Action:** Remove this line. The subsequent `mocking_utils.mock_file_read` call (Line 116) with `permission_error=True` handles the relevant file interaction mocking.

**Note:** Patches for `logging` functions (e.g., Lines 67, 85, 101, 117, 225, 240, 281, 302, 323) are **compliant** with the guidelines and should **not** be removed.

## Files Not Requiring Refactoring (Based on Report)

*   `tests/helpers/mocking_utils.py`: Contains the implementation of helpers; internal use of `mocker.patch` is expected.
*   `tests/integration/test_compile_command.py`: Uses `mocker.patch` for compliant purposes (config variables, simple side effects).

## Next Steps

1.  Apply the specified removal actions to `tests/unit/test_registry_manager.py`.
2.  Run the test suite (`pytest tests/unit/test_registry_manager.py`) to ensure tests still pass after removing the redundant patches. Adjust helper usage or test logic if removal reveals issues masked by the direct patches.