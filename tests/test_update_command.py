# tests/test_update_command.py
import pytest
import sys
import json
from pathlib import Path
from scripts.agent_config_manager.cli import main
from scripts.agent_config_manager.models import AgentConfig
# Removed incorrect import: from .conftest import create_markdown_file

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_successful_update(mocker, cli_config_yaml, tmp_path, caplog, create_markdown_file_factory): # Changed capsys to caplog
    """Tests successfully updating an existing agent."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock parse_markdown to return the updated agent details
    mock_updated_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Updated Test Role', instructions='Updated Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown", return_value=mock_updated_agent)
    # Mock load_configs to return the initial agent details
    initial_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Initial Role', instructions='Initial Instructions', capabilities=[])
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[initial_agent])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # Create the markdown file that will be used for the update
    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nUpdated Test Role")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 0 # Success exit code
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
    assert "Successfully updated agent 'test-agent'" in caplog.text

def test_update_slug_missing(mocker, cli_config_yaml, tmp_path, capsys, create_markdown_file_factory):
    """Tests error handling when trying to update a non-existent agent slug."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock parse_markdown to return the details of the agent to be updated
    mock_parsed_agent = AgentConfig(slug='non-existent-agent', name='Non Existent Agent', roleDefinition='Test Role', instructions='Non Existent Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown", return_value=mock_parsed_agent)
    # Mock load_configs to return an empty list (agent not found)
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # Create markdown for an agent that doesn't exist in the JSON
    md_file = create_markdown_file_factory(markdown_dir, 'non-existent-agent', "# Non Existent Agent\n# Core Identity & Purpose\nTest Role")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr()
    # Check stderr for the specific error format
    assert "ERROR: ValueError: Error: Agent with slug 'non-existent-agent' not found" in captured.err
    mock_save_configs.assert_not_called()

def test_update_invalid_markdown_file_non_existent(mocker, cli_config_yaml, tmp_path, capsys):
    """Tests error handling when the specified markdown file for 'update' does not exist."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    non_existent_md_path = markdown_dir / 'non_existent_agent.md' # Define path earlier

    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock parse_markdown to raise FileNotFoundError
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown",
                                        side_effect=FileNotFoundError(f"Markdown file not found at path: {non_existent_md_path}"))
    # Mock load_configs as it might be called before parse_markdown
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # non_existent_md_path defined earlier

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(non_existent_md_path)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr()
    # Error message comes from the raised FileNotFoundError in the mocked parse_markdown
    # Check stderr for the specific error format
    assert f"ERROR: FileNotFoundError: Markdown file not found at path: {non_existent_md_path}" in captured.err
    mock_save_configs.assert_not_called()

def test_update_invalid_markdown_content_malformed(mocker, cli_config_yaml, tmp_path, capsys, create_markdown_file_factory):
    """Tests error handling when the markdown file content for 'update' is malformed."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Simulate parse_markdown raising an error
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown",
                                        side_effect=ValueError("Could not find role definition heading"))
    # Load should still happen before parse, return the agent that exists
    existing_agent = AgentConfig(slug='malformed-agent', name='Malformed Agent', roleDefinition='Existing Role', instructions='Existing Instructions', capabilities=[])
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[existing_agent])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # Use a unique slug matching the one mocked in JSON
    md_file = create_markdown_file_factory(markdown_dir, 'malformed-agent', "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr()
    # Check stderr for the specific error format
    assert "ERROR: ValueError: Could not find role definition heading" in captured.err
    mock_save_configs.assert_not_called()