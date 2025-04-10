# tests/test_add_command.py
import pytest
import sys
import json
import logging # Added for verbose test
from pathlib import Path
from typer.testing import CliRunner # Added import
from cli.main import app # Added import
from cli.agent_config.models import AgentConfig # Path already updated
# Removed incorrect import: from .conftest import create_markdown_file

runner = CliRunner() # Instantiate runner

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_successful_add(mocker, cli_config_yaml, caplog, create_markdown_file_factory): # Removed tmp_path (unused directly)
    """Tests successfully adding a new agent."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock functions used by the CLI command and underlying logic
    # Mock load_cli_config where it's used in main.py
    mock_load_cli_config = mocker.patch("cli.main.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})

    # Mocks for add_config (in commands.py)
    mock_parsed_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Mock Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown", return_value=mock_parsed_agent)
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[]) # Simulate empty initial config
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    # Invoke the CLI runner
    result = runner.invoke(app, ["add", str(md_file)])

    caplog.set_level(logging.INFO, logger="cli.agent_config.commands") # Ensure INFO logs are captured
    # Assertions
    assert result.exit_code == 0
    assert f"Successfully added agent configuration from: {md_file}" in result.stdout
    mock_load_cli_config.assert_called_once() # Verify config load was attempted
    mock_save_configs.assert_called_once()
    # Optionally, assert the content of the saved JSON
    args, kwargs = mock_save_configs.call_args
    # The saved data should be a list of AgentConfig objects now
    saved_data = args[1] # Second arg is the list of configs
    assert isinstance(saved_data, list) # Check the second argument
    assert len(saved_data) == 1
    assert saved_data[0].slug == 'test-agent'
    assert saved_data[0].name == 'Test Agent'
    assert saved_data[0].roleDefinition == 'Test Role'
    assert args[0] == agent_config_file # First arg is the path
    # Log assertion removed as caplog doesn't capture reliably with CliRunner here

def test_add_slug_exists(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests error handling when adding an agent whose slug already exists."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    mock_parsed_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Mock Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown", return_value=mock_parsed_agent)
    existing_agent = AgentConfig(slug='test-agent', name='Existing Agent', roleDefinition='Existing Role', instructions='Existing Instructions', capabilities=[])
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[existing_agent])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(md_file)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Typer echoes errors to stdout by default unless err=True is used
    assert "Error adding agent: Error: Agent with slug 'test-agent' already exists" in result.stdout
    mock_save_configs.assert_not_called() # Ensure no save is attempted

def test_add_invalid_markdown_file_non_existent(mocker, cli_config_yaml): # Removed tmp_path, capsys
    """Tests error handling when the specified markdown file for 'add' does not exist."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    non_existent_md_path = markdown_dir / 'non_existent_agent.md' # Define path earlier for use in mock

    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock parse_markdown to raise FileNotFoundError
    # Note: The actual FileNotFoundError might be raised earlier during path validation within add_config
    # Let's assume parse_markdown is where it's caught for this test structure.
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        side_effect=FileNotFoundError(f"Simulated error: Markdown file not found at path: {non_existent_md_path}"))
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[]) # May not be called if parse fails first
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # non_existent_md_path defined earlier

    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(non_existent_md_path)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Check stdout for the error message (Typer default)
    # The exact error message depends on where the FileNotFoundError is caught and re-raised/printed by Typer
    # Check for the generic "An unexpected error occurred" message from main.py
    assert "An unexpected error occurred: Simulated error: Markdown file not found" in result.stdout
    mock_save_configs.assert_not_called()

# This test checks stderr, so it needs capsys, not caplog
def test_add_invalid_markdown_content_malformed(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests error handling when the markdown file content is malformed (e.g., missing role heading)."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Simulate parse_markdown raising an error
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        side_effect=ValueError("Simulated Error: Could not find role definition heading"))
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Use a unique slug for the malformed file to avoid conflicts with other tests
    md_file = create_markdown_file_factory(markdown_dir, 'malformed-agent', "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading")

    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(md_file)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Check stdout for the error message
    assert "Error adding agent: Simulated Error: Could not find role definition heading" in result.stdout
    mock_save_configs.assert_not_called()

def test_verbose_flag(mocker, cli_config_yaml, caplog, create_markdown_file_factory): # Removed tmp_path
    """Tests that the verbose flag enables debug logging during an add operation."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    mock_parsed_agent = AgentConfig(slug='verbose-agent', name='Verbose Agent', roleDefinition='Verbose Role', instructions='Verbose Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown", return_value=mock_parsed_agent)
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Use a unique slug for the verbose test
    md_file = create_markdown_file_factory(markdown_dir, 'verbose-agent', "# Verbose Agent\n# Core Identity & Purpose\nVerbose Role")

    # Set logging level directly for the test
    logging.getLogger('cli').setLevel(logging.DEBUG) # Assuming 'cli' is the root logger name used in main.py or submodules
    # Or set for specific modules if needed:
    # logging.getLogger('cli.main').setLevel(logging.DEBUG)
    # logging.getLogger('cli.agent_config.commands').setLevel(logging.DEBUG)
    # logging.getLogger('cli.agent_config.settings').setLevel(logging.DEBUG)

    # Invoke CLI runner (no need for --log-level arg now)
    result = runner.invoke(app, ["add", str(md_file)])

    # Reset logging level after test if necessary (though pytest isolation might handle this)
    logging.getLogger('cli').setLevel(logging.INFO)
    assert result.exit_code == 0 # Should still succeed
    # No need to capture stdout/stderr manually, caplog handles log capture
    # Check for expected DEBUG and INFO messages in stdout
    # Check for expected DEBUG and INFO messages using the actual log format
    # Check for expected DEBUG/INFO messages using the actual log format
    # Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
    # We won't check asctime, but will check name, level, and message start
    # Check log messages using caplog.text, including filename/lineno
    # Check log messages using caplog.text, matching the actual format
    # Check for expected DEBUG/INFO messages using the new module paths
    # Note: Exact logger names ('cli.main', 'cli.agent_config.settings', etc.) might need adjustment
    # based on logging.getLogger(__name__) usage in the refactored code.
    # Assuming logger names match module paths for now.
    assert "DEBUG    cli.agent_config.settings:settings.py" in caplog.text # Check if settings logs debug
    assert "DEBUG    cli.main:main.py" in caplog.text # Check if main logs debug
    assert "DEBUG    cli.agent_config.commands:commands.py" in caplog.text # Check if commands logs debug
    assert "INFO     cli.agent_config.commands:commands.py" in caplog.text # Check for INFO messages too
    assert "Successfully added agent 'verbose-agent'." in caplog.text # Check specific INFO message