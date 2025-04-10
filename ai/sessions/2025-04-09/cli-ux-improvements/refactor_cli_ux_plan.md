# Refactoring Plan: CLI UX Improvements - Constants & Entry Point

## 1. Objective Summary

This plan outlines the steps required to refactor the CLI application by:
1.  Introducing centralized constants files (`cli/constants.py`, `tests/constants.py`) to replace magic strings, improving maintainability and reducing errors.
2.  Implementing a standard Python package entry point (`rawr`) using `pyproject.toml` and `setuptools`, allowing the CLI to be invoked consistently after installation.

This plan synthesizes findings from the analysis report (`sessions/2025-04-09/cli-ux-improvements/analysis_report_step2b.md`) and the `rawr` implementation recommendation (`sessions/2025-04-09/cli-ux-improvements/rawr_implementation_recommendation.md`).

## 2. Assumptions

*   The project uses `setuptools` or is amenable to using it as the build backend.
*   The primary CLI application logic resides in `cli/main.py` with the `typer` app object named `app`.
*   The project structure includes `cli/` and `tests/` directories at the root.
*   The target branch for these changes is `refactor/cli-ux-improvements`.

## 3. Detailed Steps

### Step 3.1: Setup `pyproject.toml` for `rawr` Alias

*   **Action:** Create or update the `pyproject.toml` file in the project root (`/Users/mateicanavra/Documents/.nosync/DEV/ai`).
*   **Details:**
    *   Ensure the file exists. If not, create it.
    *   Add or ensure the following content is present, adjusting metadata (`name`, `version`, `description`, `requires-python`) as appropriate for the project:
        ```toml
        [build-system]
        requires = ["setuptools>=61.0"] # Specify setuptools build backend
        build-backend = "setuptools.build_meta"

        [project]
        name = "ai-cli-tool" # TODO: Confirm/Update package name
        version = "0.1.0"    # TODO: Confirm/Update initial version
        description = "CLI tool for managing AI agent configurations." # TODO: Confirm/Update description
        requires-python = ">=3.8" # TODO: Confirm/Update Python version
        # Add other metadata like authors, license, readme, etc. if desired

        [project.scripts]
        # Defines the 'rawr' command pointing to the 'app' object in 'cli.main'
        rawr = "cli.main:app"
        ```
*   **Rationale:** Implements the recommended approach for creating a standard CLI entry point (PEP 621).
*   **Files Involved:** `pyproject.toml`

### Step 3.2: Create `cli/constants.py`

*   **Action:** Create a new file `cli/constants.py`.
*   **Details:** Add initial structure with comments for categories based on the analysis and strategy:
    ```python
    # cli/constants.py
    """Centralized constants for the CLI application."""

    # --- Configuration Keys ---
    # (e.g., keys used in config.yaml)

    # --- JSON/Data Structure Keys ---
    # (e.g., keys within agents.json, Pydantic models)

    # --- Command Names ---
    # (e.g., 'add', 'update', 'delete')

    # --- Environment Variables ---
    # (e.g., 'AGENT_CLI_CONFIG_PATH')

    # --- Markdown Parsing Headings ---
    # (e.g., '# Role', '## Custom Instructions')

    # --- Default Paths/Files ---
    # (e.g., default config path, default output dirs)

    ```
*   **Rationale:** Establishes the primary location for application-level constants.
*   **Files Involved:** `cli/constants.py`

### Step 3.3: Create `tests/constants.py`

*   **Action:** Create a new file `tests/constants.py`.
*   **Details:** Add initial structure with comments for categories relevant to tests:
    ```python
    # tests/constants.py
    """Centralized constants for tests."""

    # --- Test Configuration/Defaults ---
    # (e.g., default filenames/paths used within test fixtures)

    # --- Mock Paths ---
    # (e.g., strings used for patching like 'cli.main.load_cli_config')

    # --- Shared Test Data (Use Sparingly) ---
    # (e.g., common slugs or names if heavily reused across test files)

    ```
*   **Rationale:** Establishes a dedicated location for test-specific constants, avoiding clutter in `cli/constants.py`.
*   **Files Involved:** `tests/constants.py`

### Step 3.4: Populate `cli/constants.py`

*   **Action:** Add constants to `cli/constants.py` based on the "High" and "Medium" priority items from the analysis report (`analysis_report_step2b.md`, Section 3).
*   **Details:** Focus on the following categories, using `UPPER_SNAKE_CASE`:
    *   **Config Keys:** `TARGET_JSON_PATH = "target_json_path"`, `MARKDOWN_BASE_DIR = "markdown_base_dir"`
    *   **JSON/Data Structure Keys:** `CUSTOM_MODES = "customModes"`, `SLUG = "slug"`, `NAME = "name"`, `ROLE_DEFINITION = "roleDefinition"`, `CUSTOM_INSTRUCTIONS = "customInstructions"` (Add others as identified in models/parsing logic).
    *   **Command Names:** `CMD_ADD = "add"`, `CMD_UPDATE = "update"`, `CMD_DELETE = "delete"`
    *   **Environment Variables:** `ENV_CONFIG_PATH = "AGENT_CLI_CONFIG_PATH"`
    *   **Markdown Parsing Headings:** `MD_HEADING_CORE_ID = "# Core Identity & Purpose"`, `MD_HEADING_ROLE = "# Role"`, `MD_HEADING_PERSONA = "# Persona"`, `MD_HEADING_CUSTOM_INSTRUCTIONS = "## Custom Instructions"` (Add all headings defined in `markdown_utils.py`).
    *   **Default Paths/Files:** `DEFAULT_CONFIG_PATH = "cli/config.yaml"`, `DEFAULT_TARGET_JSON = "configs/agents.json"`, `DEFAULT_MARKDOWN_DIR = "docs/agents/"`
*   **Rationale:** Centralizes critical and common strings used in the application logic.
*   **Files Involved:** `cli/constants.py`

### Step 3.5: Populate `tests/constants.py`

*   **Action:** Add constants to `tests/constants.py` based on test setup and analysis report (`analysis_report_step2b.md`, Sections 2 & 3).
*   **Details:** Focus on the following categories:
    *   **Test Configuration/Defaults:** `TEST_CONFIG_FILENAME = "config.yaml"`, `TEST_AGENTS_FILENAME = "agent_configs.json"`, `TEST_MARKDOWN_DIRNAME = "markdown_files"`
    *   **Mock Paths:** `MOCK_LOAD_CLI_CONFIG = "cli.main.load_cli_config"`, `MOCK_PARSE_MARKDOWN = "cli.agent_config.commands.parse_markdown"`, `MOCK_SAVE_AGENT_CONFIG = "cli.agent_config.commands.save_agent_config"` (Add others identified in test files).
    *   **Note:** Default JSON structures for tests (like the initial agent config) should preferably be loaded from dedicated fixture files (e.g., `tests/fixtures/default_agents.json`) within test setup (e.g., `conftest.py`) rather than defined as string constants here.
*   **Rationale:** Centralizes strings specific to the test environment and mocking setup.
*   **Files Involved:** `tests/constants.py`

### Step 3.6: Refactor `cli/**/*.py`

*   **Action:** Systematically replace identified magic strings in all `*.py` files within the `cli/` directory with imports from `cli.constants`.
*   **Details:**
    *   Ensure a systematic scan of *all* `.py` files within the `cli/` directory.
    *   Add `import cli.constants as const` (or similar) at the top of relevant files.
    *   Search for strings matching the constants defined in Step 3.4 (e.g., `"target_json_path"`, `"customModes"`, `"add"`, `"AGENT_CLI_CONFIG_PATH"`, `"# Role"`, `"configs/agents.json"`).
    *   Replace the literal strings with their corresponding constant (e.g., `const.TARGET_JSON_PATH`, `const.CUSTOM_MODES`, `const.CMD_ADD`, `const.ENV_CONFIG_PATH`, `const.MD_HEADING_ROLE`, `const.DEFAULT_TARGET_JSON`).
    *   Pay close attention to context (e.g., dictionary keys vs. command names).
*   **Rationale:** Applies the constants to the application code, achieving the core refactoring goal.
*   **Files Involved:** All `*.py` files within the `cli/` directory (e.g., `main.py`, `agent_config/commands.py`, `agent_config/settings.py`, `agent_config/markdown_utils.py`, `agent_config/models.py`, etc.).

### Step 3.7: Refactor `tests/**/*.py`

*   **Action:** Systematically replace identified magic strings in all `*.py` files within the `tests/` directory (including `conftest.py`) with imports from `cli.constants` and `tests.constants`.
*   **Details:**
    *   Ensure a systematic scan of *all* `.py` files within the `tests/` directory.
    *   Add `import cli.constants as cli_const` and `import tests.constants as test_const` (or similar) at the top of relevant files.
    *   Replace application-level strings (command names, JSON keys, env var name) with imports from `cli_const`.
    *   Replace test-specific strings (test config filenames, mock paths) with imports from `test_const`.
    *   Update `tests/conftest.py` to use constants for filenames, directory names, the environment variable name, and to load default JSON content from a fixture file (see Step 3.5 note) instead of using hardcoded strings or constants.
*   **Rationale:** Applies the constants to the test code, ensuring tests remain aligned with the application and improving test maintainability.
*   **Files Involved:** All `*.py` files within the `tests/` directory (e.g., `conftest.py`, `test_*.py` files).

### Step 3.8: Review and Update Tests

*   **Action:** Review all tests after refactoring to ensure they still pass and accurately reflect the changes.
*   **Details:**
    *   Run the full test suite (`pytest`).
    *   Pay special attention to tests involving configuration loading, command invocation (using `CliRunner`), and mocking.
    *   Adjust assertions or test setup if the refactoring exposed issues or changed behavior slightly (e.g., if default paths used in tests were implicitly tied to production defaults).
*   **Rationale:** Confirms that the refactoring did not introduce regressions.
*   **Files Involved:** `tests/**/*.py`

## 4. Acceptance Criteria / Validation Steps

The refactoring is considered successful when:

1.  **`pyproject.toml` Exists:** The `pyproject.toml` file is present in the root directory with the correct `[build-system]` and `[project.scripts]` sections.
2.  **Constants Files Exist:** `cli/constants.py` and `tests/constants.py` exist and are populated according to the plan.
3.  **Magic Strings Replaced:** A search for the high/medium priority literal strings (identified in the analysis) within `cli/**/*.py` and `tests/**/*.py` yields no results (or only acceptable instances, e.g., in comments or unrelated contexts).
4.  **Tests Pass:** The full test suite passes when run via `pytest` from the project root.
5.  **Local Installation Works:** The package can be installed in editable mode without errors: `pip install -e .` (from the project root).
6.  **`rawr` Command Works:** After installation, invoking the `rawr` command (e.g., `rawr --help`, `rawr add --help`) executes the CLI application successfully.

## 5. Risks and Dependencies

*   **Risk:** Missing some magic strings during the replacement phase, leading to inconsistencies or errors. Mitigation: Systematic search and review, potentially using automated tools or careful code review.
*   **Risk:** Incorrectly mapping a string to a constant, leading to runtime errors. Mitigation: Careful review during replacement, thorough testing.
*   **Risk:** Conflicts if `pyproject.toml` already exists with different build system settings. Mitigation: Carefully merge required sections.
*   **Dependency:** Requires `setuptools` to be available in the environment for building/installing.
*   **Dependency:** Assumes the `typer` application object is correctly named `app` in `cli.main`.

## 6. Next Steps (Handoff Recommendation)

This plan is ready for execution. It involves file creation and modification across the `cli/` and `tests/` directories, as well as the project root.

*   **Recommendation:** Use `switch_mode` to transition to the `implement` or `code` mode for executing the steps outlined in this plan.
    ```xml
    <switch_mode>
    <mode_slug>implement</mode_slug>
    <reason>Ready to execute the updated refactoring plan: create constants files, update pyproject.toml, and replace magic strings across all relevant files.</reason>
    </switch_mode>