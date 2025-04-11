# tests/constants.py
"""Centralized constants for tests."""

# --- Test Configuration/Defaults ---
TEST_CONFIG_FILENAME = "config.yaml"
TEST_AGENTS_FILENAME = "agent_configs.json"
TEST_MARKDOWN_DIRNAME = "markdown_files"

# Mock paths removed as per refactoring strategy (encourage higher-level mocking)
# --- Shared Test Data (Use Sparingly) ---
# (e.g., common slugs or names if heavily reused across test files)
# Example: DEFAULT_TEST_SLUG = "test-agent"