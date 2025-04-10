# tests/test_config_handling.py
import pytest
import sys
import json
import yaml
from pathlib import Path
from typer.testing import CliRunner # Added import
from cli.main import app # Added import
from cli.agent_config.models import AgentConfig # Path already updated
# Import helper from conftest if needed (needed for some tests below)

runner = CliRunner() # Instantiate runner

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_missing_cli_config_yaml(mocker): # Removed tmp_path, capsys
    """Tests error handling when the specified CLI config YAML file does not exist."""
    # Mock load_cli_config to raise FileNotFoundError
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         side_effect=FileNotFoundError("Simulated Error: CLI config file not found"))
    # No need for dummy_md_path or sys.argv patching

    # Invoke CLI runner (any command will trigger config load)
    result = runner.invoke(app, ["add", "dummy.md"])

    # Assertions
    assert result.exit_code == 1
    # Check stdout for the error message from main.py's exception handler
    assert "Error: Failed to load CLI configuration." in result.stdout
    assert "Simulated Error: CLI config file not found" in result.stdout
    mock_load_cli_config.assert_called_once()

def test_malformed_cli_config_yaml(mocker): # Removed tmp_path, capsys
    """Tests error handling when the CLI config YAML file has invalid YAML syntax."""
    # Mock load_cli_config to raise ValueError (simulating YAMLError)
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         side_effect=ValueError("Simulated Error: Invalid YAML format"))
    # No need for paths or sys.argv patching

    # Invoke CLI runner
    result = runner.invoke(app, ["add", "dummy.md"])

    # Assertions
    assert result.exit_code == 1
    assert "Error: Failed to load CLI configuration." in result.stdout
    assert "Simulated Error: Invalid YAML format" in result.stdout
    mock_load_cli_config.assert_called_once()

def test_invalid_cli_config_yaml_missing_keys(mocker): # Removed tmp_path, capsys
    """Tests error handling when the CLI config YAML is valid YAML but missing required keys."""
    # Mock load_cli_config to return incomplete data
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'markdown_base_dir': 'dummy_dir'}) # Missing 'target_json_path'
    # No need for paths or sys.argv patching

    # Invoke CLI runner
    result = runner.invoke(app, ["add", "dummy.md"])

    # Assertions
    assert result.exit_code == 1
    # Error should be caught in get_config_paths when accessing missing key
    assert "Error: Failed to load CLI configuration." in result.stdout
    # The underlying error might be KeyError or similar
    assert "KeyError" in result.stdout or "'target_json_path'" in result.stdout # Check for key error indication
    mock_load_cli_config.assert_called_once()

def test_non_existent_target_json(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests that the script handles a non-existent target JSON file gracefully (e.g., creates it on add)."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Ensure the target file does NOT exist initially
    if agent_config_file.exists():
        agent_config_file.unlink()

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock load_configs to return [], simulating the file not existing
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        return_value=AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions=''))
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    # No longer need md_file creation moved up
    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(md_file)])

    # Assertions
    assert result.exit_code == 0 # Should succeed by creating the file
    assert f"Successfully added agent configuration from: {md_file}" in result.stdout
    mock_load_cli_config.assert_called_once()
    # Check that save_configs was called
    mock_save_configs.assert_called_once()
    # Check the arguments passed to save_configs
    args, kwargs = mock_save_configs.call_args
    saved_path = args[0] # First arg is path
    saved_data = args[1] # Second arg is the list of configs
    assert isinstance(saved_data, list) # Check the second argument
    assert len(saved_data) == 1
    assert saved_data[0].slug == 'test-agent'
    assert saved_path == agent_config_file # Check the first argument

def test_empty_target_json(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests that the script handles an empty target JSON file correctly."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Create an empty target JSON file
    agent_config_file.touch() # Creates an empty file

    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock load_configs to return an empty list
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])
    mock_parsed_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Mock Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown", return_value=mock_parsed_agent)
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(md_file)])

    # Assertions
    assert result.exit_code == 0 # Should succeed
    assert f"Successfully added agent configuration from: {md_file}" in result.stdout
    mock_load_cli_config.assert_called_once()
    mock_save_configs.assert_called_once()
    args, kwargs = mock_save_configs.call_args
    # Check that the saved data is the new agent structure (list of configs)
    saved_path = args[0] # First arg is path
    saved_data = args[1] # Second arg is the list of configs
    assert isinstance(saved_data, list) # Check the second argument
    assert len(saved_data) == 1
    assert saved_data[0].slug == 'test-agent'
    assert saved_data[0].name == 'Test Agent'
    assert saved_data[0].roleDefinition == 'Test Role'
    assert saved_path == agent_config_file

def test_malformed_target_json_invalid_json(mocker, cli_config_yaml, create_markdown_file_factory): # Removed tmp_path, capsys
    """Tests error handling when the target JSON file contains invalid JSON."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Create a malformed target JSON file
    with open(agent_config_file, 'w') as f:
        f.write("invalid json: : :")

    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock load_configs to raise JSONDecodeError
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs",
                                      side_effect=json.JSONDecodeError("Simulated Error: Expecting value", "invalid json", 0))
    # Mock parse_markdown (might not be reached)
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        return_value=AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions=''))
    mock_save_configs = mocker.patch("cli.agent_config.commands.save_configs")

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(md_file)])

    # Assertions
    assert result.exit_code == 1 # Should fail
    # Check stdout for the error message
    assert "Error adding agent: Invalid JSON format" in result.stdout
    assert "Simulated Error: Expecting value" in result.stdout
    mock_load_cli_config.assert_called_once()
    mock_save_configs.assert_not_called() # Should not attempt to write