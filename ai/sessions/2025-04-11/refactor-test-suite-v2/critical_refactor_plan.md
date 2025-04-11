# Critical Test Suite Refactoring Plan

**Date:** 2025-04-11
**Target Branch:** `feat/cli-central-config`
**Based on:** `ai/sessions/2025-04-11/refactor-test-suite-v2/final_test_review_report.md` and Test Agent guidance.

## Objective

Address the two highest priority issues identified in the test suite review:
1.  Update/Rewrite skipped unit tests in `tests/unit/test_config_loader.py`.
2.  Refactor integration tests in `tests/integration/test_compile_command.py` to use `typer.testing.CliRunner`.

## Phase 1: Update/Rewrite Config Loader Unit Tests (`tests/unit/test_config_loader.py`)

**Goal:** Achieve comprehensive and isolated unit test coverage for the `cli.config_loader` module, incorporating Test Agent best practices.

**Steps:**

1.  **Remove Skip Marker:** Delete the `@pytest.mark.skip` decorator from the test file or individual tests within `tests/unit/test_config_loader.py`.
2.  **Review Current Implementation:** Thoroughly analyze the current code in `cli/config_loader.py` to understand its functionality, inputs, outputs, expected behavior, and potential error conditions.
3.  **Design Test Scenarios:** Based on the code review and Test Agent guidance, define comprehensive test cases covering:
    *   Loading valid configuration files (various structures, presence/absence of optional sections).
    *   Handling invalid configuration files (syntax errors, incorrect data types).
    *   Handling missing configuration files (`FileNotFoundError`).
    *   Handling missing required configuration elements (e.g., raise specific `ValueError` or custom `ConfigError`).
    *   Edge cases (e.g., empty files, files with only comments, unexpected file permissions if applicable).
    *   Error conditions during file reading or parsing.
    *   Verification of default value application.
4.  **Implement Tests with Strict Isolation:**
    *   Utilize the `tmp_path` fixture extensively to create temporary configuration files for each test scenario, ensuring complete file system isolation.
    *   Employ `monkeypatch` or `mocker.patch` judiciously to isolate tests from external dependencies (e.g., environment variables, OS-level interactions) if the loader uses them. Focus on patching direct dependencies of the loader module.
5.  **Implement Robust Assertions:**
    *   Use `pytest.raises` with specific exception types (`FileNotFoundError`, `ValueError`, custom `ConfigError`, etc.) and potentially `match` arguments to assert that expected exceptions are raised for error scenarios.
    *   For successful loads, perform detailed assertions on the structure and specific values within the returned configuration object/dictionary. Check data types.
    *   Explicitly verify that default values are correctly applied when optional sections or keys are missing in the test configuration files.
6.  **Refactor/Rewrite Tests:** Update any salvageable existing test logic to align with the current implementation and the isolation/assertion best practices outlined above. Prioritize rewriting tests completely if they are significantly outdated or poorly structured.
7.  **Run & Verify:** Execute the tests specifically for this module (`pytest tests/unit/test_config_loader.py -v`). Ensure all tests pass, fail appropriately for introduced errors, and provide clear, meaningful coverage of the defined scenarios.

## Phase 2: Refactor Compile Command Integration Tests (`tests/integration/test_compile_command.py`)

**Goal:** Ensure integration tests accurately simulate user interaction with the `compile` command via the CLI interface using `typer.testing.CliRunner`, incorporating Test Agent best practices.

**Steps:**

1.  **Import `CliRunner`:** Ensure `from typer.testing import CliRunner` is present in `tests/integration/test_compile_command.py`.
2.  **Instantiate `CliRunner`:** Create an instance of `CliRunner` within tests (e.g., `runner = CliRunner()`) or potentially via a shared fixture if multiple integration test files will use it.
3.  **Refactor Test Execution to Use `invoke`:** Modify existing tests that currently call the underlying compile function directly. Replace these calls with `runner.invoke()`:
    *   Pass the main Typer application object (likely `cli.main.app` or similar).
    *   Provide command-line arguments as a list of strings (e.g., `result = runner.invoke(app, ['compile', '--input', str(input_file_path), '--output', str(output_dir_path)])`).
4.  **Utilize Existing Fixtures for Environment Setup:**
    *   Leverage fixtures like `cli_config_yaml` and `create_markdown_file_factory` (potentially adapting them if needed) to set up the necessary environment (config files, input markdown files) within the test's `tmp_path`.
    *   Ensure `runner.invoke()` operates within the context of `tmp_path` where fixtures create files. If the command needs a specific CWD, consider how fixtures manage paths or potentially use `CliRunner(mix_stderr=False)` and pass environment variables if needed.
5.  **Implement Comprehensive `CliRunner` Assertions:**
    *   **Exit Code:** Assert strictly on `result.exit_code` (`assert result.exit_code == 0` for success, `assert result.exit_code != 0` for expected failures, potentially checking specific non-zero codes if defined).
    *   **Output Streams:** Assert on `result.stdout` and `result.stderr` for expected user messages, progress indicators, or error information. Use exact string matches, `in` checks, or regex matching (`assert re.search(...)`) as appropriate.
    *   **Side Effects:** Crucially, verify the expected side effects of the command. Check for the existence, content, and structure of output files created within `tmp_path`. Use file system checks (`os.path.exists`, reading file content) post-invocation.
6.  **Cover Diverse Command Scenarios:** Ensure tests cover a range of `compile` command use cases:
    *   Successful compilation with default options.
    *   Successful compilation utilizing various flags and options (`--output`, `--config`, specific format flags, etc.).
    *   Error scenarios triggered via the CLI (e.g., invalid input path provided as argument, missing required arguments, invalid config path specified via `--config`).
    *   Scenarios testing interaction between different flags.
    *   Basic tests with different valid input file contents leading to expected outputs.
7.  **Run & Verify:** Execute the integration tests (`pytest tests/integration/test_compile_command.py -v`). Ensure they pass, correctly capture CLI errors, and accurately validate the command's behavior and side effects through the `CliRunner` interface.

## Next Steps

Upon completion and approval of this plan, implementation can begin, starting with Phase 1. It is recommended to commit changes after each phase is successfully completed and verified locally. Ensure the Test Agent's guidance on isolation, coverage, `CliRunner` usage, fixtures, and assertions is strictly followed during implementation.