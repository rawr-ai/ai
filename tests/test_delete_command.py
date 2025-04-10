# tests/test_delete_command.py
import pytest
import sys
import json
from pathlib import Path
from typer.testing import CliRunner # Added import
from cli.main import app # Added import
from cli.agent_config.models import AgentConfig # Path already updated

runner = CliRunner() # Instantiate runner
# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_successful_delete(mocker, cli_config_yaml, caplog): # Removed tmp_path
    """Tests successfully deleting an existing agent."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Simulate successful CLI config load
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock load_configs to return the agent to be deleted
    existing_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Test Instructions', capabilities=[])
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[existing_agent])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Invoke CLI runner
    result = runner.invoke(app, ["delete", "test-agent"])

    # Assertions
    assert result.exit_code == 0
    assert "Successfully deleted agent configuration with slug: test-agent" in result.stdout
    mock_load_cli_config.assert_called_once()
    mock_save_configs.assert_called_once()
    # Assert the content of the saved JSON reflects the deletion
    args, kwargs = mock_save_configs.call_args
    # The saved data should be an empty list of AgentConfig objects now
    saved_path = args[0] # First arg is path
    saved_data = args[1] # Second arg is the list of configs
    assert isinstance(saved_data, list) # Check the second argument
    assert isinstance(saved_data, list)
    assert len(saved_data) == 0
    assert args[0] == agent_config_file # First arg is the path
    # Check log messages using caplog
    assert "Successfully deleted agent 'test-agent'." in caplog.text # Note the period

def test_delete_slug_missing(mocker, cli_config_yaml): # Removed tmp_path, capsys
    """Tests error handling when trying to delete a non-existent agent slug."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock load_configs to return an empty list
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Invoke CLI runner
    result = runner.invoke(app, ["delete", "non-existent-agent"])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Check stdout for the error message
    assert "Error deleting agent: Error: Agent with slug 'non-existent-agent' not found" in result.stdout
    mock_save_configs.assert_not_called()