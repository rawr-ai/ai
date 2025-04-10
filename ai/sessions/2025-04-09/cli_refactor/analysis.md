# CLI Refactoring Proposal

## 1. Summary of Current Structure

Based on the scan results, the current CLI-related files are primarily located within the `scripts/` directory:

```
scripts/
├── manage_agent_configs.py  # Potential entry point
├── cli_config.yaml          # Configuration
└── agent_config_manager/    # Core logic module
    ├── __init__.py
    ├── cli.py               # CLI interface logic?
    ├── commands.py          # Command implementations
    ├── config.py            # Configuration handling logic
    ├── markdown_parser.py   # Specific parsing utility
    └── models.py            # Data models
```

The tests reside separately in the `tests/` directory.

## 2. Refactoring Goals

The primary goals for this refactoring are:
1.  Rename the root directory from `scripts/` to `cli/`.
2.  Establish a single, clear entry point script within `cli/`.
3.  Rename internal files descriptively.
4.  Improve the structure for better testability.

## 3. Proposed Target Structure

```
cli/
├── main.py                  # Single entry point
├── config.yaml              # Configuration file
└── agent_config/            # Renamed core logic module
    ├── __init__.py
    ├── commands.py          # Command implementations
    ├── settings.py          # Configuration handling logic
    ├── markdown_utils.py    # Markdown parsing utility
    └── models.py            # Data models
```

## 4. Entry Point (`cli/main.py`)

*   **Name:** `cli/main.py`
*   **Role:** This script will serve as the **single entry point** for the entire CLI application.
    *   It should initialize the CLI application (e.g., using a library like Typer, Click, or argparse).
    *   It will import and register the command functions defined in `cli/agent_config/commands.py`.
    *   It consolidates the entry point logic previously found in `scripts/manage_agent_configs.py` and potentially parts of `scripts/agent_config_manager/cli.py`.
    *   It handles argument parsing and delegates execution to the appropriate command function.

## 5. File Mapping and Renaming

The files currently within `scripts/agent_config_manager/` will be moved and potentially renamed within the new `cli/agent_config/` module:

| Current Path                                | Proposed New Path                   | Rationale                                                                 |
| :------------------------------------------ | :---------------------------------- | :------------------------------------------------------------------------ |
| `scripts/agent_config_manager/`             | `cli/agent_config/`                 | Core logic module, renamed for clarity within the `cli` context.        |
| `scripts/agent_config_manager/__init__.py`  | `cli/agent_config/__init__.py`      | Standard Python package initializer.                                      |
| `scripts/agent_config_manager/cli.py`       | (Logic merged into `cli/main.py`)   | Entry point and CLI framework setup belong in the main script.            |
| `scripts/agent_config_manager/commands.py`  | `cli/agent_config/commands.py`      | Name is descriptive; contains the actual command logic.                   |
| `scripts/agent_config_manager/config.py`    | `cli/agent_config/settings.py`      | `settings.py` is a common convention for configuration loading/handling.  |
| `scripts/agent_config_manager/markdown_parser.py` | `cli/agent_config/markdown_utils.py` | More general name (`_utils`) reflecting its utility function.             |
| `scripts/agent_config_manager/models.py`    | `cli/agent_config/models.py`        | Name is already descriptive and standard.                                 |

## 6. Configuration File (`cli/config.yaml`)

*   The configuration file `scripts/cli_config.yaml` should be moved to `cli/config.yaml`.
*   Placing it directly within the `cli` directory makes it easily discoverable alongside the entry point. The logic in `cli/agent_config/settings.py` will be responsible for loading this file.

## 7. Testing Considerations

*   This new structure promotes better separation of concerns:
    *   `cli/main.py` handles CLI argument parsing and framework setup.
    *   `cli/agent_config/commands.py` contains the core business logic of each command, making them easier to unit test independently of the CLI framework.
    *   Utilities (`settings.py`, `markdown_utils.py`, `models.py`) are clearly defined modules.
*   Tests in the `tests/` directory will need their import paths updated to reflect the new `cli.` structure (e.g., `from cli.agent_config.commands import some_command`).
*   Integration tests can target `cli/main.py` using tools like `CliRunner` (if using Click/Typer) or by invoking it as a subprocess.