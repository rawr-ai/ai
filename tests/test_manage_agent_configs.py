import pytest
from pathlib import Path
from scripts.manage_agent_configs import main  # Assuming your script's main function is named 'main'
import sys
import yaml
import json

@pytest.fixture
def cli_config_yaml(tmp_path):
    config_content = {
        'agent_config_file': str(tmp_path / 'agent_configs.json'),
        'markdown_base_dir': str(tmp_path / 'markdown_files')
    }
    cli_config_path = tmp_path / 'cli_config.yaml'
    with open(cli_config_path, 'w') as f:
        yaml.dump(config_content, f)
    return cli_config_path, tmp_path / 'agent_configs.json', tmp_path / 'markdown_files'

def create_markdown_file(markdown_dir, slug, content=""):
    agent_dir = markdown_dir / slug
    agent_dir.mkdir(exist_ok=True)
    md_file = agent_dir / f"{slug}.md"
    with open(md_file, 'w') as f:
        f.write(content)
    return md_file

def test_add_missing_arguments(mocker, cli_config_yaml):
    cli_config_path, _, _ = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Error: the following arguments are required for subcommand add: path_to_markdown_file" in sys.stderr.getvalue()

def test_add_invalid_arguments(mocker, cli_config_yaml, tmp_path):
    cli_config_path, _, _ = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", "invalid-slug", "agent", "--description", "Test Agent", "--markdown_file", "docs/agent_template.md"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Invalid slug format" in sys.stderr.getvalue()

def test_update_missing_arguments(mocker, cli_config_yaml):
    cli_config_path, _, _ = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Error: the following arguments are required for subcommand update: path_to_markdown_file" in sys.stderr.getvalue()

def test_update_invalid_arguments(mocker, cli_config_yaml):
    cli_config_path, _, _ = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", "invalid-slug", "--description", "Updated Description"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Invalid slug format" in sys.stderr.getvalue()

def test_delete_missing_arguments(mocker, cli_config_yaml):
    cli_config_path, _, _ = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "delete"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Error: the following arguments are required for subcommand delete: agent_slug" in sys.stderr.getvalue()

def test_verbose_flag(mocker, cli_config_yaml, tmp_path, capsys):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value="# Test Agent\n# Core Identity & Purpose\nTest Role")
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    mocker.patch("json.load", return_value={'customModes': []})
    mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent", "--verbose"])
    main()
    sys_exit_mock.assert_called_once_with(0)
    captured = capsys.readouterr()
    assert "DEBUG: Verbose logging enabled." in captured.out
    assert "DEBUG: Loading configuration from:" in captured.out
    assert "DEBUG: Target JSON path loaded:" in captured.out
    assert "DEBUG: Markdown base directory loaded:" in captured.out
    assert "INFO: Parsing Markdown file:" in captured.out
    assert "INFO: Successfully added agent 'test-agent'." in captured.out

def test_missing_cli_config_yaml(mocker, tmp_path):
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(tmp_path / 'non_existent_config.yaml'), "add", "test-agent", "agent", "--description", "Test Agent", "--markdown_file", "docs/agent_template.md"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Configuration file not found" in sys.stderr.getvalue()

def test_malformed_cli_config_yaml(mocker, tmp_path):
    cli_config_path = tmp_path / 'cli_config.yaml'
    with open(cli_config_path, 'w') as f:
        f.write("invalid yaml: : :")
    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", "test-agent", "agent", "--description", "Test Agent", "--markdown_file", "docs/agent_template.md"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Error parsing configuration file" in sys.stderr.getvalue()

def test_malformed_cli_config_yaml_missing_agent_config_file(mocker, tmp_path):
    cli_config_path = tmp_path / 'cli_config.yaml'
    config_content = {'markdown_base_dir': str(tmp_path / 'markdown_files')} # Missing 'agent_config_file'
    with open(cli_config_path, 'w') as f:
        yaml.dump(config_content, f)

    sys_exit_mock = mocker.patch("sys.exit")
    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", "test-agent", "agent", "--description", "Test Agent", "--markdown_file", "docs/agent_template.md"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Invalid configuration format in" in sys.stderr.getvalue()
    assert "Missing required keys." in sys.stderr.getvalue()

def test_successful_add(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value="# Test Agent\n# Core Identity & Purpose\nTest Role")
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    mocker.patch("json.load", return_value={'customModes': []})
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(0)
    json_dump_mock.assert_called_once()
    # Optionally, assert the content of the dumped JSON

def test_successful_update(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        '# Test Agent\n# Core Identity & Purpose\nTest Role', # For markdown parsing
        json.dumps({'customModes': [{'slug': 'test-agent', 'name': 'Test Agent', 'roleDefinition': 'Initial Role'}]}), # Initial JSON load
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nUpdated Test Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(md_file)])
    main()
    sys_exit_mock.assert_called_once_with(0)
    json_dump_mock.assert_called_once()
    # Optionally, assert the content of the dumped JSON for update

def test_successful_delete(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value=json.dumps({'customModes': [{'slug': 'test-agent', 'name': 'Test Agent', 'roleDefinition': 'Test Role'}]})) # Initial JSON load
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "delete", "test-agent"])
    main()
    sys_exit_mock.assert_called_once_with(0)
    json_dump_mock.assert_called_once()
    # Optionally, assert the content of the dumped JSON for delete

def test_add_slug_exists(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        '# Test Agent\n# Core Identity & Purpose\nTest Role', # For markdown parsing
        json.dumps({'customModes': [{'slug': 'test-agent', 'name': 'Test Agent', 'roleDefinition': 'Existing Role'}]}), # Initial JSON load with existing slug
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "Error: Agent with slug 'test-agent' already exists" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called() # Ensure no save is attempted

def test_add_invalid_markdown_file_non_existent(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", side_effect=[
        False, # For markdown_path.is_file() check - non-existent
        True,  # For cli_config.yaml existence
    ])
    mock_read_text = mocker.patch("pathlib.Path.read_text")
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load", return_value={'customModes': []})
    json_dump_mock = mocker.patch("json.dump")

    non_existent_md_path = markdown_dir / 'non_existent_agent' / 'non_existent_agent.md'

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(non_existent_md_path), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "FileNotFoundError: Markdown file not found" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_add_invalid_markdown_content_malformed(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value="# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading") # Malformed content
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load", return_value={'customModes': []})
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'malformed_agent', "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "ValueError: Could not find any role definition heading" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_update_slug_missing(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        '# Non Existent Agent\n# Core Identity & Purpose\nTest Role', # For markdown parsing - but slug will be non-existent-agent
        json.dumps({'customModes': []}), # Initial JSON load - no agents
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'non-existent-agent', "# Non Existent Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(md_file)])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "ValueError: Error: Agent with slug 'non-existent-agent' not found" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_update_invalid_markdown_file_non_existent(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", side_effect=[
        False, # For markdown_path.is_file() check - non-existent
        True,  # For cli_config.yaml existence
        True, # For target json existence
    ])
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value=json.dumps({'customModes': [{'slug': 'test-agent', 'name': 'Test Agent', 'roleDefinition': 'Existing Role'}]}))
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    non_existent_md_path = markdown_dir / 'non_existent_agent' / 'non_existent_agent.md'

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(non_existent_md_path)])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "FileNotFoundError: Markdown file not found" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_update_invalid_markdown_content_malformed(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading", # Malformed markdown
        json.dumps({'customModes': [{'slug': 'test-agent', 'name': 'Test Agent', 'roleDefinition': 'Existing Role'}]}), # Initial JSON load
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'malformed_agent', "# Test Agent\nInvalid Markdown Content - Missing Role Definition Heading")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "update", str(md_file)])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "ValueError: Could not find any role definition heading" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_delete_slug_missing(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value=json.dumps({'customModes': []})) # Initial JSON load - no agents
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "delete", "non-existent-agent"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "ValueError: Error: Agent with slug 'non-existent-agent' not found" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_non_existent_target_json(mocker, cli_config_yaml, tmp_path):
    cli_config_path, _, markdown_dir = cli_config_yaml
    agent_config_file = tmp_path / 'non_existent_agent_configs.json' # Point config to non-existent file
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", side_effect=[
        True, # For markdown file check
        False, # For target_json_path.is_file() initially - non-existent
        True, # For cli_config.yaml existence
    ])
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value="# Test Agent\n# Core Identity & Purpose\nTest Role")
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Not needed as file doesn't exist initially
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(0)
    json_dump_mock.assert_called_once()
    # Optionally, assert the content of the dumped JSON - should be created

def test_empty_target_json(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    with open(agent_config_file, 'w') as f: # Create empty target JSON
        f.write("")
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        '# Test Agent\n# Core Identity & Purpose\nTest Role', # For markdown parsing
        "", # Empty JSON content initially
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(0)
    json_dump_mock.assert_called_once()
    # Optionally, assert the content of dumped JSON - should be updated

def test_malformed_target_json_invalid_json(mocker, cli_config_yaml, tmp_path):
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    with open(agent_config_file, 'w') as f: # Create malformed target JSON
        f.write("invalid json: : :")
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        '# Test Agent\n# Core Identity & Purpose\nTest Role', # For markdown parsing
        "invalid json: : :", # Malformed JSON content
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    json_load_mock = mocker.patch("json.load") # Already mocked with side_effect above
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(1)
    assert "ValueError: Invalid JSON format in" in sys.stderr.getvalue()
    assert "JSONDecodeError" in sys.stderr.getvalue()
    json_dump_mock.assert_not_called()

def test_success_exit_code(mocker, cli_config_yaml, tmp_path): # Example happy path - add
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", return_value="# Test Agent\n# Core Identity & Purpose\nTest Role")
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    mocker.patch("json.load", return_value={'customModes': []})
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(0)

def test_failure_exit_code(mocker, cli_config_yaml, tmp_path): # Example error case - add slug exists
    cli_config_path, agent_config_file, markdown_dir = cli_config_yaml
    sys_exit_mock = mocker.patch("sys.exit")
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_read_text = mocker.patch("pathlib.Path.read_text", side_effect=[
        '# Test Agent\n# Core Identity & Purpose\nTest Role',
        json.dumps({'customModes': [{'slug': 'test-agent', 'name': 'Test Agent', 'roleDefinition': 'Existing Role'}]}), # Config with existing slug
    ])
    mock_write_text = mocker.patch("pathlib.Path.write_text")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={'agent_config_file': str(agent_config_file), 'markdown_base_dir': str(markdown_dir)})
    mocker.patch("json.load")
    json_dump_mock = mocker.patch("json.dump")

    md_file = create_markdown_file(markdown_dir, 'test-agent', "# Test Agent\n# Core Identity & Purpose\nTest Role")

    sys_argv_mock = mocker.patch("sys.argv", ["scripts/manage_agent_configs.py", "--config", str(cli_config_path), "add", str(md_file), "agent", "--description", "Test Agent"])
    main()
    sys_exit_mock.assert_called_once_with(1)