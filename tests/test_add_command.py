# tests/test_add_command.py
import pytest
import sys
import json
from pathlib import Path
from scripts.agent_config_manager.cli import main
from scripts.agent_config_manager.models import AgentConfig
# Removed incorrect import: from .conftest import create_markdown_file

# Note: cli_config_yaml fixture is automatically available from conftest.py
# Note: mocker, tmp_path, and capsys fixtures are built-in

def test_successful_add(mocker, cli_config_yaml, tmp_path, caplog, create_markdown_file_factory): # Changed capsys to caplog
    """Tests successfully adding a new agent."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions used by cli.main and commands.add_config
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data")) # Mock open within cli scope
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    mock_parsed_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Mock Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown", return_value=mock_parsed_agent)
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[]) # Simulate empty initial config
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 0 # Success exit code
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
    # Check log messages using caplog
    assert "Successfully added agent 'test-agent'" in caplog.text

def test_add_slug_exists(mocker, cli_config_yaml, tmp_path, capsys, create_markdown_file_factory):
    """Tests error handling when adding an agent whose slug already exists."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    mock_parsed_agent = AgentConfig(slug='test-agent', name='Test Agent', roleDefinition='Test Role', instructions='Mock Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown", return_value=mock_parsed_agent)
    # Simulate loading existing config data with the conflicting slug
    existing_agent = AgentConfig(slug='test-agent', name='Existing Agent', roleDefinition='Existing Role', instructions='Existing Instructions', capabilities=[])
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[existing_agent])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    md_file = create_markdown_file_factory(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr()
    # Check stderr for the specific error format
    assert "ERROR: ValueError: Error: Agent with slug 'test-agent' already exists" in captured.err
    mock_save_configs.assert_not_called() # Ensure no save is attempted

def test_add_invalid_markdown_file_non_existent(mocker, cli_config_yaml, tmp_path, capsys):
    """Tests error handling when the specified markdown file for 'add' does not exist."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    non_existent_md_path = markdown_dir / 'non_existent_agent.md' # Define path earlier for use in mock

    # Mock high-level functions
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Mock parse_markdown to raise FileNotFoundError, simulating the file check failure within the command
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown",
                                        side_effect=FileNotFoundError(f"Markdown file not found at path: {non_existent_md_path}"))
    # load_configs might still be called before parse_markdown, depending on implementation
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[])
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # non_existent_md_path defined earlier

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(non_existent_md_path)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr()
    # Error message comes from the raised FileNotFoundError in the mocked parse_markdown
    # Check stderr for the specific error format
    assert f"ERROR: FileNotFoundError: Markdown file not found at path: {non_existent_md_path}" in captured.err
    mock_save_configs.assert_not_called()

# This test checks stderr, so it needs capsys, not caplog
def test_add_invalid_markdown_content_malformed(mocker, cli_config_yaml, tmp_path, capsys, create_markdown_file_factory):
    """Tests error handling when the markdown file content is malformed (e.g., missing role heading)."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    # Simulate parse_markdown raising an error due to malformed content
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown",
                                        side_effect=ValueError("Could not find role definition heading"))
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[]) # Load should still happen before parse
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # Use a unique slug for the malformed file to avoid conflicts with other tests
    md_file = create_markdown_file_factory(markdown_dir, 'malformed-agent', "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading")

    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 1 # Failure exit code
    captured = capsys.readouterr() # Re-add capsys capture
    # Check stderr for the specific error format
    assert "ERROR: ValueError: Could not find role definition heading" in captured.err
    mock_save_configs.assert_not_called()

def test_verbose_flag(mocker, cli_config_yaml, tmp_path, caplog, create_markdown_file_factory): # Changed capsys to caplog
    """Tests that the verbose flag enables debug logging during an add operation."""
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    # Mock high-level functions
    mocker.patch("scripts.agent_config_manager.cli.Path.is_file", return_value=True)
    mocker.patch("scripts.agent_config_manager.cli.open", mocker.mock_open(read_data="mock data"))
    mocker.patch("scripts.agent_config_manager.cli.yaml.safe_load",
                 return_value={'target_json_path': agent_config_file, 'markdown_base_dir': markdown_dir})
    mock_parsed_agent = AgentConfig(slug='verbose-agent', name='Verbose Agent', roleDefinition='Verbose Role', instructions='Verbose Instructions', capabilities=[])
    mock_parse_markdown = mocker.patch("scripts.agent_config_manager.commands.parse_markdown", return_value=mock_parsed_agent)
    mock_load_configs = mocker.patch("scripts.agent_config_manager.commands.load_configs", return_value=[]) # Simulate empty initial config
    mock_save_configs = mocker.patch("scripts.agent_config_manager.commands.save_configs")

    # Use a unique slug for the verbose test
    md_file = create_markdown_file_factory(markdown_dir, 'verbose-agent', "# Verbose Agent\n# Core Identity & Purpose\nVerbose Role")

    # Add --verbose flag
    # Move --log-level before the subparser command 'add'
    mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "--log-level", "DEBUG", "add", str(md_file)])
    with pytest.raises(SystemExit) as e:
         main()
    assert e.value.code == 0 # Should still succeed
    # No need to capture stdout/stderr manually, caplog handles log capture
    # Check for expected DEBUG and INFO messages in stdout
    # Check for expected DEBUG and INFO messages using the actual log format
    # Check for expected DEBUG/INFO messages using the actual log format
    # Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
    # We won't check asctime, but will check name, level, and message start
    # Check log messages using caplog.text, including filename/lineno
    # Check log messages using caplog.text, matching the actual format
    assert "DEBUG    scripts.agent_config_manager.cli:cli.py:61 Debug logging enabled." in caplog.text
    assert "DEBUG    scripts.agent_config_manager.cli:cli.py:69 Loading configuration from:" in caplog.text
    assert "DEBUG    scripts.agent_config_manager.cli:cli.py:77 Target JSON path loaded:" in caplog.text
    assert "DEBUG    scripts.agent_config_manager.cli:cli.py:78 Markdown base directory loaded:" in caplog.text
    assert "DEBUG    scripts.agent_config_manager.commands:commands.py:15 Entering add_config with" in caplog.text
    assert "DEBUG    scripts.agent_config_manager.commands:commands.py:32 Parsing markdown file:" in caplog.text
    assert "DEBUG    scripts.agent_config_manager.commands:commands.py:35 Loading existing configs from:" in caplog.text
    assert "DEBUG    scripts.agent_config_manager.commands:commands.py:46 Saving 1 configs to:" in caplog.text
    # assert "INFO - Parsing Markdown file:" in captured.out
    assert "INFO     scripts.agent_config_manager.commands:commands.py:48 Successfully added agent 'verbose-agent'." in caplog.text