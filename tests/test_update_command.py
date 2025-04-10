# tests/test_update_command.py
import pytest
import sys
import json
from pathlib import Path
from typer.testing import CliRunner # Added import
from cli.main import app # Added import
from cli.agent_config.models import AgentConfig # Path already updated
# Removed incorrect import: from .conftest import create_markdown_file

runner = CliRunner() # Instantiate runner

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_successful_update(mocker, cli_config_yaml, caplog, create_markdown_file_factory): # Removed tmp_path
    """Tests successfully updating an existing agent."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock parse_markdown to return the updated agent details
    mock_updated_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Updated Test Role', instructions='Updated Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown", return_value=mock_updated_agent)
    # Mock load_configs to return the initial agent details
    initial_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Initial Role', instructions='Initial Instructions', capabilities=[])
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[initial_agent])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Create the markdown file that will be used for the update
    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nUpdated Test Role")

    # Invoke CLI runner
    result = runner.invoke(app, ["update", str(md_file)])

    # Assertions
    assert result.exit_code == 0
    assert f"Successfully updated agent configuration from: {md_file}" in result.stdout
    mock_load_cli_config.assert_called_once()
    mock_save_configs.assert_called_once()
    # Assert the content of the saved JSON reflects the update
    args, kwargs = mock_save_configs.call_args
    # The saved data should be a list containing the updated AgentConfig object
    saved_path = args[0] # First arg is path
    saved_data = args[1] # Second arg is the list of configs
    assert isinstance(saved_data, list) # Check the second argument
    assert isinstance(saved_data, list)
    assert len(saved_data) == 1
    assert saved_data[0].slug == 'test-agent'
    assert saved_data[0].name == 'Test Agent'
    assert saved_data[0].roleDefinition == 'Updated Test Role'
    assert args[0] == agent_config_file # First arg is the path
    # Check log messages using caplog
    assert "Successfully updated agent 'test-agent'." in caplog.text # Note the period

def test_update_slug_missing(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests error handling when trying to update a non-existent agent slug."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock parse_markdown
    mock_parsed_agent = AgentConfig(slug='non-existent-agent', name='Non Existent Agent', roleDefinition='Test Role', instructions='Non Existent Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown", return_value=mock_parsed_agent)
    # Mock load_configs to return an empty list
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Create markdown for an agent that doesn't exist in the JSON
    md_file = create_markdown_file_factory(markdown_dir, 'non-existent-agent', "# Non Existent Agent\n# Core Identity & Purpose\nTest Role")

    # Invoke CLI runner
    result = runner.invoke(app, ["update", str(md_file)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Check stdout for the error message
    assert "Error updating agent: Error: Agent with slug 'non-existent-agent' not found" in result.stdout
    mock_save_configs.assert_not_called()

def test_update_invalid_markdown_file_non_existent(mocker, cli_config_yaml): # Removed tmp_path, capsys
    """Tests error handling when the specified markdown file for 'update' does not exist."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    non_existent_md_path = markdown_dir / 'non_existent_agent.md' # Define path earlier

    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock parse_markdown to raise FileNotFoundError
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        side_effect=FileNotFoundError(f"Simulated Error: Markdown file not found at path: {non_existent_md_path}"))
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # non_existent_md_path defined earlier

    # Invoke CLI runner
    result = runner.invoke(app, ["update", str(non_existent_md_path)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Check stdout for the error message
    assert "Error updating agent: Simulated Error: Markdown file not found" in result.stdout
    mock_save_configs.assert_not_called()

def test_update_invalid_markdown_content_malformed(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests error handling when the markdown file content for 'update' is malformed."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Simulate parse_markdown raising an error
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        side_effect=ValueError("Simulated Error: Could not find role definition heading"))
    # Load should still happen before parse
    existing_agent = AgentConfig(slug='malformed-agent', name='Malformed Agent', roleDefinition='Existing Role', instructions='Existing Instructions', capabilities=[])
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[existing_agent])
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # Use a unique slug matching the one mocked in JSON
    md_file = create_markdown_file_factory(markdown_dir, 'malformed-agent', "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading")

    # Invoke CLI runner
    result = runner.invoke(app, ["update", str(md_file)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code
    # Check stdout for the error message
    assert "Error updating agent: Simulated Error: Could not find role definition heading" in result.stdout
    mock_save_configs.assert_not_called()