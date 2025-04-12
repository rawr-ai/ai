# Test Strategy: `cli` Directory Refactoring

**Date:** 2025-04-12
**Branch:** `refactor/cli-maintainability`
**Based On:** `ai/sessions/2025-04-11/modularize-cli/refactor_plan.md`

## 1. Introduction & Goal

This document outlines the test strategy for the refactoring effort detailed in the `refactor_plan.md`. The primary goals of the refactoring are:

1.  Safely remove the deprecated `cli/agent_config/` directory and all references to it.
2.  Extract compilation orchestration logic from `cli/main.py` into a new `cli/compiler.py` module to improve modularity and testability.

This strategy focuses *exclusively* on validating the steps outlined in the refactoring plan.

## 2. Scope

This strategy covers the testing activities required to validate the two main refactoring steps:

*   **Step 1:** Removal of `cli/agent_config/` and orphaned references.
*   **Step 2:** Extraction of compilation orchestration logic to `cli/compiler.py`.

This document defines the *strategy* and *types* of tests required. It does **not** include the implementation details of the tests themselves. Test implementation will follow this strategy.

## 3. Test Strategy for Step 1: Removal of `cli/agent_config/`

**Objective:** Verify the complete removal of the `cli/agent_config/` directory and ensure no orphaned references remain in the codebase, preventing `ImportError` or related runtime issues.

**Approach:**

1.  **Static Verification (Post-Removal):**
    *   **Code Search:** After deleting the directory, perform a comprehensive search across the entire codebase (using tools like `search_files`) for any remaining imports or references to `cli.agent_config`, `AgentConfig`, or other symbols previously defined within that directory. All identified references must be removed or refactored.
    *   **Build/Import Check:** Ensure the application builds successfully and basic imports work without errors.
2.  **Automated Testing (Post-Removal):**
    *   **Execute Existing Test Suite:** Run the *entire* existing test suite. The primary goal here is to catch any immediate `ImportError` exceptions or failures caused by the removal of code that existing tests might implicitly depend on. Pay close attention to failures in tests related to `cli/main.py` or other CLI components.
3.  **Manual Verification (Mitigation):**
    *   As per the refactoring plan's risk mitigation, manually execute relevant CLI commands, particularly those *not* directly related to `compile` but potentially having subtle dependencies, to ensure they haven't been broken by the removal.

**Success Criteria:**

*   `cli/agent_config/` directory is confirmed deleted.
*   Code search confirms no remaining references.
*   The application builds successfully.
*   The existing test suite passes without `ImportError` related to `cli.agent_config`.
*   Manual checks of relevant CLI commands show no regressions.

## 4. Test Strategy for Step 2: Extraction to `cli/compiler.py`

**Objective:** Verify that the compilation orchestration logic is correctly extracted to `cli/compiler.py` (e.g., `CompilerService`) and that the `ai-agent compile` command retains its original functionality from a user perspective, while `cli/main.py` is simplified.

**Approach:** Test-Driven Development (TDD) as outlined in `pb_tdd_cycle.md`.

1.  **Testing the New Module (`cli/compiler.py` - e.g., `CompilerService`):**
    *   **Unit Tests (Primary Focus):** Write comprehensive unit tests for the new `CompilerService` class or functions *before and during* the extraction.
        *   **Input:** Test with various inputs (e.g., different registry states, specific agent names, flags for compiling all).
        *   **Logic:** Verify the core orchestration logic (correct flow for single vs. all agents, correct calls to helper functions - potentially mocked).
        *   **Interaction:** Mock dependencies like `registry_manager` to verify the service calls them correctly (e.g., `read_registry`, `write_registry`) with the expected data.
        *   **Output/State:** Verify the expected state changes or outputs (e.g., data passed to `registry_manager.write_registry`).
        *   **Error Handling:** Test scenarios where compilation might fail (e.g., invalid agent name, issues reading/writing registry) and ensure appropriate exceptions are raised.
    *   **Integration Tests (Potential/Secondary):** Depending on the final implementation and its interaction with the file system (registry files), limited integration tests might be considered *if* unit tests with mocks are deemed insufficient to cover critical file interactions. However, the primary focus should remain on unit tests.
2.  **Testing the Modified Module (`cli/main.py`):**
    *   **Unit Tests:** Adapt existing unit tests for `cli/main.py::compile_agent_config`.
        *   **Mocking:** Mock the new `CompilerService`.
        *   **Verification:** Verify that `compile_agent_config` correctly instantiates the `CompilerService`, calls the appropriate method based on CLI arguments, and handles exceptions raised by the mocked service by providing correct user feedback (e.g., `typer.echo` calls).
        *   **Focus:** Ensure these tests now focus *only* on the CLI interaction aspects (argument parsing, service instantiation, exception handling, user feedback) and *not* the orchestration logic itself.
3.  **End-to-End / Functional Validation:**
    *   **CLI Command Testing:** After the extraction and unit/integration tests pass, perform manual or automated functional tests by running the `ai-agent compile` command with various arguments (single agent, all agents, non-existent agent, etc.). Verify the output and side effects (e.g., updated registry file) match the pre-refactoring behavior exactly.
    *   **Regression Testing:** Run the *full* application test suite to ensure no other CLI commands or parts of the application were negatively affected.

**Success Criteria:**

*   Comprehensive unit tests exist for `cli/compiler.py` covering logic, interactions, and error handling.
*   Adapted unit tests for `cli/main.py` verify correct interaction with the (mocked) `CompilerService` and CLI feedback.
*   All unit and integration tests pass.
*   Functional tests confirm the `ai-agent compile` command behaves identically to the user.
*   The full test suite passes, indicating no regressions.

## 5. General Considerations

*   **Full Test Suite Execution:** The complete test suite should be run frequently during the refactoring process, especially after completing each major step (Step 1 and Step 2).
*   **Static Analysis:** Ensure code linters and static analysis tools pass without new errors after the changes.
*   **Code Review:** The test strategy assumes successful code review as a validation step, ensuring the implementation aligns with the plan and testing goals.

## 6. Environment

*   Tests should be executed in a consistent and reproducible environment that mirrors the development/CI environment. Specific environment setup (e.g., virtual environments, dependencies) should be handled during test *implementation*.

## 7. Cleanup

*   While this strategy document does not define specific cleanup steps (as these depend on test implementation details like temporary file creation), it mandates that **all test implementations derived from this strategy MUST include explicit cleanup steps** for any resources created during testing (e.g., temporary files, mock registry entries). Cleanup must be performed reliably after test execution, whether tests pass or fail.