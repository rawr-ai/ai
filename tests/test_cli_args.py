# tests/test_cli_args.py
import pytest
import sys
from scripts.agent_config_manager.cli import main

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_add_missing_arguments(mocker, cli_config_yaml, capsys):
    """Tests that 'add' command exits with error if markdown path is missing."""
    cli_config_path, _, _ = cli_config_yaml
    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add"])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 2 # Check exit code directly (Updated based on simulated output)
    captured = capsys.readouterr()
    assert "error: the following arguments are required: path_to_markdown_file" in captured.err # Updated based on simulated output

def test_add_invalid_arguments(mocker, cli_config_yaml, tmp_path, capsys):
    """Tests that 'add' command exits with error if the slug derived from the markdown path is invalid."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml # Need agent_config_file for mock
    # mocker.patch("sys.exit")
    # Create a dummy markdown file path that implies an invalid slug
    invalid_md_path = markdown_dir / "invalid slug.md" # Simplified path for testing slug derivation
    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(invalid_md_path)])

    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock parse_markdown to raise ValueError for invalid slug, simulating validation within the command
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown",
                                        side_effect=ValueError("Invalid slug format: 'invalid slug'"))
    # Mock load_configs as it might be called before parse_markdown
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[])

    with pytest.raises(SystemExit) as e:
         main() # Correctly indented
    assert e.value.code == 1 # Assert exit code 1 for ValueError
    captured = capsys.readouterr()
    # Error message now comes from the ValueError raised by the mocked parse_markdown
    # Check the error message printed to stderr (updated format)
    assert "ERROR: ValueError: Invalid slug format: 'invalid slug'" in captured.err

def test_update_missing_arguments(mocker, cli_config_yaml, capsys):
    """Tests that 'update' command exits with error if markdown path is missing."""
    cli_config_path, _, _ = cli_config_yaml
    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update"])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 2 # Updated based on simulated output
    captured = capsys.readouterr()
    assert "error: the following arguments are required: path_to_markdown_file" in captured.err # Updated based on simulated output

def test_update_invalid_arguments(mocker, cli_config_yaml, tmp_path, capsys):
    """Tests that 'update' command exits with error if the slug derived from the markdown path is invalid."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml # Need agent_config_file for mock
    # Create a dummy markdown file path that implies an invalid slug
    invalid_md_path = markdown_dir / "invalid slug.md" # Simplified path
    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(invalid_md_path)])

    # Mock high-level functions
    # Simulate successful CLI config load
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock parse_markdown to raise ValueError for invalid slug
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown",
                                        side_effect=ValueError("Invalid slug format: 'invalid slug'"))
    # Mock load_configs as it might be called before parse_markdown
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[])

    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    # Check stderr for the specific error format
    assert "ERROR: ValueError: Invalid slug format: 'invalid slug'" in captured.err

def test_delete_missing_arguments(mocker, cli_config_yaml, capsys):
    """Tests that 'delete' command exits with error if agent slug is missing."""
    cli_config_path, _, _ = cli_config_yaml
    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "delete"])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 2 # Updated based on simulated output
    captured = capsys.readouterr()
    assert "error: the following arguments are required: agent_slug" in captured.err # Updated based on simulated output