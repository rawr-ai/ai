# tests/test_delete_command.py
import pytest
import sys
import json
from pathlib import Path
from scripts.agent_config_manager.cli import main
from scripts.agent_config_manager.models import AgentConfig
# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_successful_delete(mocker, cli_config_yaml, tmp_path, caplog): # Changed capsys to caplog
    """Tests successfully deleting an existing agent."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock load_configs to return the agent to be deleted
    existing_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Test Instructions', capabilities=[])
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[existing_agent])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "delete", "test-agent"])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 0 # Success exit code
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
    assert "Successfully deleted agent 'test-agent'" in caplog.text

def test_delete_slug_missing(mocker, cli_config_yaml, tmp_path, capsys):
    """Tests error handling when trying to delete a non-existent agent slug."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock load_configs to return an empty list (agent not found)
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "delete", "non-existent-agent"])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr()
    # Check stderr for the specific error format
    assert "ERROR: ValueError: Error: Agent with slug 'non-existent-agent' not found" in captured.err
    mock_save_configs.assert_not_called()