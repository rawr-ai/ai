# Detailed Refactoring Plan: `rawr` CLI Test Suite

This plan breaks down the refactoring strategy into actionable steps for the `implement` agent. Each step aims to improve the test suite's maintainability, robustness, and clarity.

**Assumptions:**
*   The project structure includes `tests/`, `tests/unit/`, `tests/integration/`, `tests/helpers/`, `tests/constants.py`, and `conftest.py` files (potentially at root and subdirectory levels).
*   `pytest` and `pytest-mock` (providing the `mocker` fixture) are used.

---

## Phase 1: Eliminate Direct `os.environ` Manipulation

**Goal:** Replace unsafe global state changes with controlled environment variable management using `pytest.monkeypatch`.

**Step 1.1: Identify `os.environ` Usage in Fixtures**
*   **Action:** Search all `conftest.py` files (root and subdirectories) for patterns like `os.environ[...] = ...`, `os.environ.update(...)`, `os.putenv(...)`, `del os.environ[...]`. Also check for direct reads like `os.environ.get(...)` or `os.getenv(...)` within fixtures where the intent might be better served by `monkeypatch`.
*   **Target Files:** `conftest.py` (all instances).
*   **Expected Outcome:** A list of fixtures modifying or directly reading `os.environ`.

**Step 1.2: Replace `os.environ` Modifications with `monkeypatch`**
*   **Action:** For each identified fixture:
    *   Add `monkeypatch` to the fixture's arguments.
    *   Replace direct assignments (`os.environ['KEY'] = 'val'`) with `monkeypatch.setenv('KEY', 'val')`.
    *   Replace deletions (`del os.environ['KEY']`) with `monkeypatch.delenv('KEY', raising=False)`.
    *   Replace updates (`os.environ.update({...})`) with multiple `monkeypatch.setenv` calls.
    *   Consider if direct reads (`os.getenv`) within fixtures should also be patched if they relate to configuration being set for the test scope.
*   **Target Files:** `conftest.py` (all instances identified in Step 1.1).
*   **Expected Outcome:** Fixtures no longer modify `os.environ` directly. Environment variable changes are scoped by `monkeypatch`.

---

## Phase 2: Refactor `tests/constants.py`

**Goal:** Separate configuration values from test data and eliminate patching of constants.

**Step 2.1: Analyze `tests/constants.py`**
*   **Action:** Review the contents of `tests/constants.py`. Categorize each constant as either:
    *   **Configuration-like:** Values that mimic application configuration or environment settings.
    *   **Test Data:** Sample inputs, expected outputs, identifiers, etc., used specifically for testing logic.
*   **Target Files:** `tests/constants.py`.
*   **Expected Outcome:** An understanding of the purpose of each constant.

**Step 2.2: Refactor Configuration-like Constants**
*   **Action:**
    *   Identify tests/fixtures that import and use these configuration-like constants.
    *   Remove the import from `tests/constants.py`.
    *   In the consuming test/fixture, use `monkeypatch.setenv` (if it represents an env var) or pass the value directly if it represents some other config. If the constant was being *patched* (`mocker.patch('tests.constants.CONFIG_VALUE', ...)`), remove the patch and instead configure the environment/component appropriately for the test using `monkeypatch` or direct setup.
    *   Remove the original constant definition from `tests/constants.py`.
*   **Target Files:** `tests/constants.py`, relevant test files (`test_*.py`), `conftest.py`.
*   **Expected Outcome:** Configuration-like values are no longer defined in `tests/constants.py` but are set appropriately within the scope of tests/fixtures that need them.

**Step 2.3: Relocate Test Data Constants**
*   **Action:**
    *   For constants categorized as test data:
        *   If used by only one or a few related test modules, move the constant definition directly into those test modules.
        *   If used more broadly or represents complex data structures, move the definition to a relevant module within `tests/helpers/` (e.g., `tests/helpers/sample_data.py` or `tests/helpers/data_factories.py`). Consider creating factory functions if data generation is complex.
    *   Update all imports to point to the new location.
    *   Remove the original constant definition from `tests/constants.py`.
*   **Target Files:** `tests/constants.py`, relevant test files (`test_*.py`), `tests/helpers/`.
*   **Expected Outcome:** `tests/constants.py` is significantly reduced or eliminated. Test data is located closer to its usage or within dedicated helper modules.

---

## Phase 3: Reduce Internal Patching in Unit Tests

**Goal:** Improve test robustness by shifting mocking away from internal implementation details towards component boundaries.

**Step 3.1: Identify Unit Tests with Excessive Internal Patching**
*   **Action:** Search within `tests/unit/` for test files with a high density of `mocker.patch` or `unittest.mock.patch` calls. Pay specific attention to patches targeting:
    *   Functions/classes deep within the application's internal modules.
    *   Constants previously located in `tests/constants.py`.
    *   Helper functions within the same module being tested.
*   **Target Files:** `tests/unit/**/*.py`.
*   **Expected Outcome:** A list of test modules/functions that heavily rely on patching internal details.

**Step 3.2: Refactor Tests to Mock at Boundaries**
*   **Action:** For each identified test/module:
    *   Analyze the purpose of the patches.
    *   Determine the actual public interface or boundary of the unit under test.
    *   Remove patches targeting internal implementation details.
    *   If necessary, add mocks for direct collaborators *at their API boundary*. For example, instead of mocking an internal utility function called by a method, mock the collaborator object that the method interacts with.
    *   Focus assertions on the observable behavior/state changes of the unit under test, not on whether internal functions were called (unless verifying essential interactions with a *direct* collaborator).
*   **Target Files:** Test files identified in Step 3.1.
*   **Expected Outcome:** Tests verify the unit's behavior by interacting with its public interface and mocking only direct external dependencies or collaborators, making them less brittle to implementation changes.

---

## Phase 4: Consolidate and Optimize Fixtures

**Goal:** Improve fixture reusability, clarity, and performance.

**Step 4.1: Audit Fixtures**
*   **Action:** Review all fixtures defined in the root `conftest.py` and any subdirectory `conftest.py` files. Look for:
    *   Similar setup logic repeated across multiple fixtures.
    *   Fixtures doing too many unrelated things.
    *   Fixtures with potentially incorrect or inefficient scopes (e.g., `session` scope for mutable objects without proper cleanup).
*   **Target Files:** `conftest.py` (all instances).
*   **Expected Outcome:** Identification of fixtures needing consolidation, simplification, or scope adjustment.

**Step 4.2: Consolidate and Simplify Fixtures**
*   **Action:**
    *   Merge similar fixtures using techniques like `@pytest.fixture(params=[...])` or by creating a base fixture that others depend on.
    *   Extract complex setup logic into helper functions (potentially in `tests/helpers/`) called by the fixture.
    *   Break down large fixtures into smaller, more focused, composable fixtures.
*   **Target Files:** `conftest.py` (all instances).
*   **Expected Outcome:** Reduced fixture duplication, improved readability, and clearer setup logic.

**Step 4.3: Optimize Fixture Scopes**
*   **Action:** Review the scope (`function`, `class`, `module`, `session`) of each fixture.
    *   Ensure the scope is appropriate for the fixture's purpose and cost.
    *   Default to `function` unless a broader scope provides significant, necessary performance gains *and* the fixture yields immutable data or manages its state carefully to avoid test interference.
    *   Change scopes where necessary (e.g., from `session` to `function` if state leakage is a risk).
*   **Target Files:** `conftest.py` (all instances).
*   **Expected Outcome:** Fixture scopes are used efficiently and safely, balancing performance with test isolation.

---

## Phase 5: Enhance and Utilize Test Helpers

**Goal:** Centralize reusable test logic for setup, data generation, and common actions.

**Step 5.1: Identify Opportunities for Helpers**
*   **Action:** While performing other refactoring steps (especially Phases 3 and 4), look for repeated patterns of:
    *   Complex test data creation.
    *   Filesystem setup/teardown.
    *   Common mocking scenarios (e.g., mocking an API client).
    *   Running CLI commands and asserting results.
*   **Target Files:** `test_*.py`, `conftest.py`.
*   **Expected Outcome:** Identification of logic suitable for extraction into `tests/helpers/`.

**Step 5.2: Create/Refine Helper Modules**
*   **Action:** Based on identified opportunities:
    *   Create new modules in `tests/helpers/` if needed (e.g., `data_factories.py`, `fs_utils.py`, `mocking_utils.py`, `cli_runner.py`).
    *   Add well-defined functions or classes to these modules to encapsulate the reusable logic. Ensure helpers are focused and have clear interfaces.
*   **Target Files:** `tests/helpers/`.
*   **Expected Outcome:** A structured `tests/helpers/` directory with reusable utilities.

**Step 5.3: Update Tests/Fixtures to Use Helpers**
*   **Action:** Refactor the tests and fixtures identified in Step 5.1 to import and use the newly created or refined helper functions/classes. Remove the duplicated logic from the original locations.
*   **Target Files:** `test_*.py`, `conftest.py`.
*   **Expected Outcome:** Tests and fixtures are cleaner, more readable, and leverage centralized helper utilities.

---

## Phase 6: Review and Refine Integration Tests

**Goal:** Ensure integration tests provide high-level validation with minimal, targeted mocking.

**Step 6.1: Review Integration Tests**
*   **Action:** Examine the tests within the `tests/integration/` directory. Assess:
    *   What components are being tested together?
    *   What is being mocked? Is the mocking necessary, or does it prevent true integration testing?
    *   Are the tests verifying behavior from an end-user or external system perspective?
*   **Target Files:** `tests/integration/**/*.py`.
*   **Expected Outcome:** Understanding of the current state and effectiveness of integration tests.

**Step 6.2: Reduce Unnecessary Mocking**
*   **Action:**
    *   Identify mocks that target internal components rather than true external boundaries (e.g., external APIs, filesystem operations that *should* be tested, databases).
    *   Remove unnecessary mocks, allowing components to interact as they would in production.
    *   Retain mocks only for genuinely external systems or components explicitly excluded from the integration scope.
*   **Target Files:** `tests/integration/**/*.py`.
*   **Expected Outcome:** Integration tests provide more realistic end-to-end validation with fewer, more targeted mocks.

---

## Phase 7: Adhere to Conventions (Ongoing)

**Goal:** Maintain consistency across the test suite.

**Step 7.1: Apply Conventions During Refactoring**
*   **Action:** Throughout all preceding phases, ensure that any new or modified code adheres to the established conventions for:
    *   Fixture naming and scoping (Strategy Section 4.1).
    *   Mocking strategies (Strategy Section 4.2).
    *   Test structure and naming (Strategy Section 4.3).
*   **Target Files:** All modified files (`test_*.py`, `conftest.py`, `tests/helpers/**/*.py`).
*   **Expected Outcome:** The refactored codebase consistently follows the agreed-upon testing conventions.

---

**Next Steps:**
This plan should be executed sequentially by the `implement` agent. After each phase or significant step, running the test suite (`pytest`) is crucial to ensure no regressions have been introduced.