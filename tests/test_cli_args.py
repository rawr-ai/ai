# tests/test_cli_args.py
import pytest
# import sys # No longer needed
from typer.testing import CliRunner # Added import
from cli.main import app # Added import

runner = CliRunner() # Instantiate runner

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_add_missing_arguments(mocker, cli_config_yaml): # Removed capsys
    """Tests that 'add' command exits with error if markdown path is missing."""
    # Mock config loading as it happens before argument parsing fails
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': 'dummy.json', 'markdown_base_dir': 'dummy_dir'})

    # Invoke CLI runner with missing argument
    result = runner.invoke(app, ["add"]) # Missing markdown_path

    # Assertions
    assert result.exit_code == 2 # Typer's exit code for missing arguments
    assert "Missing argument 'MARKDOWN_PATH'" in result.stdout # Typer's error message format
    mock_load_cli_config.assert_not_called() # Config load shouldn't happen if args fail early

def test_add_invalid_arguments(mocker, cli_config_yaml): # Removed tmp_path, capsys
    """Tests that 'add' command exits with error if the slug derived from the markdown path is invalid."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    invalid_md_path = markdown_dir / "invalid slug.md" # Keep path for argument

    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock parse_markdown to raise ValueError
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        side_effect=ValueError("Simulated Error: Invalid slug format: 'invalid slug'"))
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])

    # Invoke CLI runner
    result = runner.invoke(app, ["add", str(invalid_md_path)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code from ValueError
    # Check stdout for the error message
    assert "Error adding agent: Simulated Error: Invalid slug format: 'invalid slug'" in result.stdout
    mock_load_cli_config.assert_called_once()

def test_update_missing_arguments(mocker, cli_config_yaml): # Removed capsys
    """Tests that 'update' command exits with error if markdown path is missing."""
    # Mock config loading
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': 'dummy.json', 'markdown_base_dir': 'dummy_dir'})

    # Invoke CLI runner with missing argument
    result = runner.invoke(app, ["update"]) # Missing markdown_path

    # Assertions
    assert result.exit_code == 2 # Typer's exit code for missing arguments
    assert "Missing argument 'MARKDOWN_PATH'" in result.stdout # Typer's error message format
    mock_load_cli_config.assert_not_called()

def test_update_invalid_arguments(mocker, cli_config_yaml): # Removed tmp_path, capsys
    """Tests that 'update' command exits with error if the slug derived from the markdown path is invalid."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    invalid_md_path = markdown_dir / "invalid slug.md" # Keep path for argument

    # Mock functions
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    # Mock parse_markdown to raise ValueError
    mock_parse_markdown = mocker.patch("cli.agent_config.commands.parse_markdown",
                                        side_effect=ValueError("Simulated Error: Invalid slug format: 'invalid slug'"))
    mock_load_configs = mocker.patch("cli.agent_config.commands.load_configs", return_value=[])

    # Invoke CLI runner
    result = runner.invoke(app, ["update", str(invalid_md_path)])

    # Assertions
    assert result.exit_code == 1 # Failure exit code from ValueError
    # Check stdout for the error message
    assert "Error updating agent: Simulated Error: Invalid slug format: 'invalid slug'" in result.stdout
    mock_load_cli_config.assert_called_once()

def test_delete_missing_arguments(mocker, cli_config_yaml): # Removed capsys
    """Tests that 'delete' command exits with error if agent slug is missing."""
    # Mock config loading
    mock_load_cli_config = mocker.patch("cli.agent_config.settings.load_cli_config",
                                         return_value={'target_json_path': 'dummy.json', 'markdown_base_dir': 'dummy_dir'})

    # Invoke CLI runner with missing argument
    result = runner.invoke(app, ["delete"]) # Missing slug

    # Assertions
    assert result.exit_code == 2 # Typer's exit code for missing arguments
    assert "Missing argument 'SLUG'" in result.stdout # Typer's error message format
    mock_load_cli_config.assert_not_called()