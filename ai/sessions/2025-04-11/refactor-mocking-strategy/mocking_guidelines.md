# Project Mocking Guidelines

## 1. Introduction

This document outlines the official strategy and guidelines for using mocks in tests within this project. The goal is to ensure consistency, maintainability, and readability across the test suite.

## 2. Chosen Strategy: Refined Hybrid Approach

We adopt a **Refined Hybrid Mocking Strategy**. This approach balances the use of centralized **Mocking Helpers** for common or complex scenarios with the explicitness of **Inline `mocker.patch`** for simple, unique cases.

This strategy aims to:
*   **Promote DRY (Don't Repeat Yourself):** By using helpers for recurring mocking patterns.
*   **Maintain Explicitness:** By using inline patches for straightforward cases where the mock is simple and local to the test.
*   **Improve Readability:** By abstracting complex setup logic into helpers and keeping simple mocks direct.
*   **Ensure Maintainability:** By centralizing common logic while allowing flexibility.

## 3. Core Guidelines

### 3.1. When to Use Mocking Helpers (e.g., `tests/helpers/mocking_utils.py`)

Mocking helpers are **strongly preferred** or **required** for specific categories of interactions to ensure consistency and abstract complexity.

**Use Helpers For:**

*   **File System Interactions:** ALL mocking related to file operations (`builtins.open`, `pathlib.Path`, `os`, `shutil`, etc.). Use the utilities provided in `tests/helpers/mocking_utils.py`.
    *   *Example (Conceptual):*
        ```python
        # Instead of multiple inline mocker.patch calls for open, read, exists...
        def test_config_loading(mock_fs):
            # Use a helper that sets up the mock file system state
            mock_fs.expect_read('config.json', returns='{"key": "value"}')
            
            result = load_config('config.json')
            
            assert result == {"key": "value"}
        ```
*   **(Future) External API/Service Interactions:** When interactions with external services are added, dedicated helpers *must* be created and used.
*   **Complex Scenarios:** Any mocking scenario requiring more than 2-3 related `mocker.patch` calls should generally be considered for a helper.

### 3.2. When to Use Inline `mocker.patch`

Inline `mocker.patch` or `mocker.patch.object` is acceptable **only** for the following simple and specific scenarios:

*   **Simple Return Value / Attribute Patching:** Mocking a single function/method call to return a specific value, or patching a simple object attribute.
    *   *Example:*
        ```python
        def test_widget_processing_success(mocker):
            mock_status = mocker.patch('mymodule.widget.get_status', return_value='READY')
            widget = MyWidget()
            
            result = widget.process()
            
            assert result is True
            mock_status.assert_called_once()
        ```
*   **Simple Side Effects:** Mocking a function/method to raise a specific, simple exception.
    *   *Example:*
        ```python
        def test_widget_processing_error(mocker):
            mock_status = mocker.patch('mymodule.widget.get_status', side_effect=ConnectionError("Failed to connect"))
            widget = MyWidget()

            with pytest.raises(ConnectionError):
                widget.process()
            
            mock_status.assert_called_once()
        ```
*   **Patching Configuration / Constants:** Mocking module-level variables or constants specific to a test setup.
    *   *Example:*
        ```python
        def test_feature_flag_disabled(mocker):
            mocker.patch('mymodule.config.FEATURE_ENABLED', False)
            
            # ... test logic for when feature is disabled ...
        ```
*   **Patching Logging Functions:** Mocking logging calls (`logging.info`, `logger.error`, etc.) to assert that specific messages were logged.
    *   *Example:*
        ```python
        def test_error_logging(mocker):
            mock_log_error = mocker.patch('mymodule.logger.error')
            
            process_with_potential_error(should_fail=True)
            
            mock_log_error.assert_called_once_with("Processing failed due to error X")
        ```
*   **Truly Unique, Simple Scenarios:** Cases involving only 1-2 simple patches that clearly don't fit into existing helper categories and are unlikely to be repeated.

**Avoid Inline `mocker.patch` For:** Scenarios covered by Section 3.1 (File System, External APIs, complex setups).

### 3.3. Creating New Helpers

If you find yourself repeating the same inline `mocker.patch` logic (even moderately complex, involving 2+ patches) across multiple tests, consider creating a new, reusable helper function within `tests/helpers/`.
*   Ensure new helpers are well-tested themselves.
*   Document the helper's purpose and usage clearly.
*   Follow the existing patterns in `mocking_utils.py` where applicable.

## 4. Rationale

This refined hybrid approach was chosen because it:
*   Leverages the existing helper structure (`mocking_utils.py`).
*   Provides a pragmatic balance between DRY and explicitness.
*   Minimizes the risk of excessive code duplication found in a purely inline approach.
*   Avoids the high upfront cost, potential rigidity, and abstraction risks associated with a fully mandated, comprehensive helper library for all mocking.

Adhering to these guidelines will help maintain a clean, understandable, and robust test suite.