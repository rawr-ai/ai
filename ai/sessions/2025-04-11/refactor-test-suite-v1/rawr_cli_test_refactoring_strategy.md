# Refactoring Strategy: `rawr` CLI Test Suite (Updated 2025-04-11)

## 1. Introduction

This document outlines a refactoring strategy for the `rawr` CLI test suite. The goal is to improve modularity, reduce brittleness, enhance maintainability, and establish clear testing conventions, based on analysis of the current test structure and identified patterns. This updated version incorporates findings from a review on 2025-04-11. The strategy focuses on actionable steps tailored for a small team.

## 2. Core Problems Addressed

Based on the analysis, this strategy directly targets:

*   **Global State Mutation:** Unsafe modification of `os.environ` within fixtures (likely in `conftest.py`).
*   **Excessive Internal Patching:** Over-reliance on mocking deep internal functions and constants (potentially involving `tests/constants.py`), leading to tight coupling and brittle tests, especially within the `unit/` directory.
*   **Fixture Management:** Potential for fixture duplication, overly complex fixtures, and suboptimal scoping in `conftest.py` files.
*   **Structure & Helpers:** Need for more specific, reusable test helpers within the existing `tests/helpers/` directory and clearer conventions across `unit/` and `integration/` tests.

## 3. Detailed Refactoring Plan

### 3.1. Eliminate `os.environ` Manipulation in Fixtures

*   **Problem:** Modifying `os.environ` directly in fixtures creates hidden dependencies and potential test side effects.
*   **Solution:**
    1.  **Identify:** Locate all fixtures (primarily in `conftest.py`) that modify `os.environ`.
    2.  **Replace:** Use `pytest`'s `monkeypatch` fixture to set/get environment variables *within the scope of the test or fixture that needs it*. This isolates the change.
        ```python
        # Example in a test function or fixture
        def test_something_with_env(monkeypatch):
            monkeypatch.setenv("MY_VAR", "test_value")
            # Code that relies on MY_VAR being set
            ...

        # Example patching os.getenv directly if preferred
        def test_something_else(mocker):
            mock_getenv = mocker.patch('os.getenv')
            mock_getenv.side_effect = lambda key, default=None: "mocked_value" if key == "TARGET_VAR" else os.environ.get(key, default)
            # Code that calls os.getenv("TARGET_VAR")
            ...
        ```
    3.  **Alternative (Consider):** If configuration is complex, introduce a dedicated configuration object/dataclass. Populate this object in fixtures and pass it explicitly. Start with `monkeypatch` for lower friction.
*   **Trade-offs:** `monkeypatch` is straightforward but still involves patching. Explicit config objects are cleaner but more invasive.

### 3.2. Reduce Internal Patching

*   **Problem:** Patching internal implementation details makes tests brittle; they break when implementation changes, even if the public behavior is correct. This is often seen when patching constants from shared files like `tests/constants.py`.
*   **Solution:**
    1.  **Shift Mocking Boundaries:** Mock collaborators at API boundaries, not deep internal functions. Test the behavior of the unit, not its specific internal calls unless absolutely necessary.
    2.  **Test Larger Units (Integration):** Minimize mocking in `integration/` tests. Allow components to interact naturally, focusing mocks on true external boundaries (filesystem, network APIs, external libraries).
    3.  **Refactor Constants (`tests/constants.py`):**
        *   If constants represent configuration, handle them via `monkeypatch` or config objects (see 3.1).
        *   If they are test data, move them closer to the tests that use them or into dedicated helper modules (e.g., `tests/helpers/data_factories.py`). Avoid patching constants directly.
    4.  **Dependency Injection:** Where appropriate, refactor application code to accept dependencies as arguments.
*   **Trade-offs:** Mocking at higher levels might require more complex mock setup but results in more robust tests. Dependency Injection requires application code changes but significantly improves testability.

### 3.3. Consolidate and Improve Fixtures

*   **Problem:** Potential for duplicated fixture logic, overly complex setup, and inefficient scoping within `conftest.py` files.
*   **Solution:**
    1.  **Audit Fixtures:** Review all fixtures in root and directory-level `conftest.py` files.
    2.  **Identify Duplication:** Look for fixtures performing similar setup.
    3.  **Consolidate:**
        *   Merge similar fixtures using parameterization (`@pytest.fixture(params=[...])`).
        *   Refactor complex fixtures into smaller, composable fixtures or utilize helper functions (see 3.4).
        *   Leverage existing factory patterns consistently.
    4.  **Review Scopes:** Ensure fixture scopes (`function`, `class`, `module`, `session`) are appropriate. Default to `function` unless a broader scope offers significant performance benefits and is safe (beware state leakage).
    5.  **Simplify:** Break down fixtures doing too many things.
*   **Trade-offs:** Broader fixture scopes improve speed but increase the risk of test interdependence if not managed carefully.

### 3.4. Enhance and Utilize Dedicated Test Helpers (`tests/helpers/`)

*   **Problem:** Test logic (setup, data generation, complex mocking) scattered within tests or fixtures, reducing readability and reusability. The `tests/helpers/` directory exists but can be leveraged more effectively.
*   **Solution:**
    1.  **Refine Structure:** Organize modules within `tests/helpers/` for specific concerns:
        *   `fs_utils.py`: Functions for setting up complex directory structures, creating files. E.g., `setup_project_structure(tmp_path, spec: dict)`.
        *   `mocking_utils.py`: Helpers for common mocking scenarios. E.g., `mock_api_client(mocker, base_url, responses: dict)`.
        *   `data_factories.py`: Functions/classes to generate test data. E.g., `create_sample_config(**overrides)`.
        *   `cli_runner.py`: Centralize CLI invocation logic if using `CliRunner`. E.g., `run_cli_command(args: list, expect_exit_code: int = 0) -> Result`.
    2.  **Refactor Usage:** Update tests and fixtures to import and use these helpers.
*   **Trade-offs:** Introduces a small amount of indirection but significantly improves readability and reusability.

## 4. Proposed Conventions

### 4.1. Fixture Usage and Naming

*   **Naming:** Use descriptive names, potentially indicating scope (e.g., `temp_project_dir_function`, `mock_user_config_module`). Be consistent.
*   **Scope:** Default to `function`. Use broader scopes consciously for performance, ensuring isolation.
*   **Location:** Root `conftest.py` for widely shared. Directory `conftest.py` for directory-specific. Test file for single-use.
*   **Dependencies:** Keep fixture dependencies clear and shallow.

### 4.2. Mocking Strategies

*   **When:** Mock external systems, libraries with side effects, or direct collaborators when isolating a unit. Avoid mocking internal implementation details.
*   **What:** Mock at the boundary between your code and the dependency (`mocker.patch`, `unittest.mock.patch`).
*   **How:** Use `autospec=True`. Prefer mocking objects/classes over functions if simpler. Keep mock setups focused. Verify interactions (`assert_called_once_with`) when necessary, but prefer state-based assertions.

### 4.3. Test Structure and Naming

*   **Structure:** Maintain `unit/` and `integration/` separation. The existing `helpers/` directory should house reusable utilities. Group related tests within files (e.g., `test_subcommand.py`). Use classes (`class TestSubcommand:`) for grouping tests sharing setup.
*   **Naming:** `test_scenario_or_unit[_when_condition][_expected_outcome]`. Examples: `test_add_command_adds_item_to_list`, `test_config_loader_when_file_missing_raises_error`.

## 5. Initial Refactoring Targets

Based on the analysis highlighting `os.environ` issues and heavy patching:

1.  **`conftest.py` (Root & potentially subdirs):** Audit and refactor fixtures manipulating `os.environ`. Consolidate complex/duplicated fixtures.
2.  **Tests with Heavy Patching (likely `unit/`):** Identify test modules with high density of `mocker.patch` calls, especially those patching deep internals or constants from `tests/constants.py`. Apply revised mocking strategy.
3.  **Integration Tests (`integration/`):** Review to ensure they provide genuine end-to-end value. Reduce mocking, focusing only on true external boundaries.
4.  **`tests/constants.py`:** Analyze constants. Refactor config-like constants. Move test data constants closer to usage or into `tests/helpers/data_factories.py`.
5.  **Helper Usage:** Ensure the `tests/helpers/` directory is effectively utilized and potentially expanded with more specific utilities as refactoring progresses.

*(Note: Consider reviewing `tests/refactoring_validation_process.md` and `tests/test_manage_agent_configs_plan.md` alongside the refactoring effort for potential integration or alignment.)*

## 6. Conclusion

This refactoring strategy provides a roadmap to address the identified issues in the `rawr` CLI test suite. By focusing on isolating state changes, improving mocking boundaries, consolidating fixtures, enhancing helpers, and establishing clear conventions, the test suite will become more robust, maintainable, and easier for the team to work with. It is recommended to tackle these changes incrementally, starting with the highest-impact areas like `os.environ` manipulation and heavily patched test modules.