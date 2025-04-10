# tests/constants.py
"""Centralized constants for tests."""

# --- Test Configuration/Defaults ---
TEST_CONFIG_FILENAME = "config.yaml"
TEST_AGENTS_FILENAME = "agent_configs.json"
TEST_MARKDOWN_DIRNAME = "markdown_files"

# --- Mock Paths ---
# Used for patching in tests
MOCK_LOAD_CLI_CONFIG = "cli.main.load_cli_config"
MOCK_GET_CONFIG_PATHS = "cli.main.get_config_paths" # Added based on main.py usage
MOCK_PARSE_MARKDOWN = "cli.agent_config.commands.parse_markdown"
MOCK_SAVE_AGENT_CONFIG = "cli.agent_config.commands.save_agent_config"
MOCK_SETTINGS_LOAD_CLI_CONFIG = "cli.agent_config.settings.load_cli_config" # Used in settings tests
MOCK_SETTINGS_GET_CLI_CONFIG_PATH = "cli.agent_config.settings.get_cli_config_path" # Used in settings tests
MOCK_COMMANDS_ADD_CONFIG = "cli.agent_config.commands.add_config" # Used in main tests
MOCK_COMMANDS_UPDATE_CONFIG = "cli.agent_config.commands.update_config" # Used in main tests
MOCK_COMMANDS_DELETE_CONFIG = "cli.agent_config.commands.delete_config" # Used in main tests

# --- Shared Test Data (Use Sparingly) ---
# (e.g., common slugs or names if heavily reused across test files)
# Example: DEFAULT_TEST_SLUG = "test-agent"