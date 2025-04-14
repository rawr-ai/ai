import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Removed import: from cli.agent_config import commands # Updated path
# Removed import: from cli.agent_config.models import AgentConfig # Updated path

# --- Fixtures ---

@pytest.fixture
def mock_config_a():
    return AgentConfig(slug="agent-a", name="Agent A", roleDefinition="Role A")
#
@pytest.fixture
def mock_config_b():
    return AgentConfig(slug="agent-b", name="Agent B", roleDefinition="Role B", customInstructions="Custom B")
#
@pytest.fixture
def mock_configs_list(mock_config_a, mock_config_b):
    return [mock_config_a, mock_config_b]

@pytest.fixture
def mock_target_json_path(tmp_path):
    return tmp_path / "test_configs.json"

@pytest.fixture
def mock_markdown_base_dir(tmp_path):
    base = tmp_path / "markdown_files"
    base.mkdir()
    return base

@pytest.fixture
def mock_markdown_path_a(mock_markdown_base_dir, mock_config_a):
    # Create a dummy file structure matching how parse_markdown gets the slug
    agent_dir = mock_markdown_base_dir / mock_config_a.slug
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.touch() # Content doesn't matter as parse_markdown is mocked
    return str(p) # Function expects string path

@pytest.fixture
def mock_markdown_path_b(mock_markdown_base_dir, mock_config_b):
    agent_dir = mock_markdown_base_dir / mock_config_b.slug
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.touch()
    return str(p)

@pytest.fixture
def mock_markdown_path_new(mock_markdown_base_dir):
    agent_dir = mock_markdown_base_dir / "new-agent"
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.touch()
    return str(p)

# @pytest.fixture
# def mock_new_config():
#     return AgentConfig(slug="new-agent", name="New Agent", roleDefinition="New Role")


# --- Mocks Setup ---

@pytest.fixture(autouse=True)
def mock_dependencies():
    """Auto-applied fixture to mock dependencies for all tests in this module."""
    # Explicit paths used after removing tests/constants.py mock paths
    # Temporarily commented out due to removal of cli.agent_config
    # with patch('cli.agent_config.commands.load_configs') as mock_load, \
    #      patch('cli.agent_config.commands.save_configs') as mock_save, \
    #      patch('cli.agent_config.commands.parse_markdown') as mock_parse:
    # TODO: Reinstate or update patches when testing the new CompilerService
    if True: # Keep indentation correct for the yield below
        pass # Added to satisfy indentation after commenting out yield
        # Yield the mocks so tests can access them if needed, though often just
        # checking calls on them is sufficient.
        # yield mock_load, mock_save, mock_parse


# --- Tests for add_config ---

def test_add_config_success(
    mock_dependencies, mock_configs_list, mock_new_config,
    mock_markdown_path_new, mock_target_json_path, mock_markdown_base_dir
):
    mock_load, mock_save, mock_parse = mock_dependencies
    mock_load.return_value = mock_configs_list[:] # Return a copy
    mock_parse.return_value = mock_new_config

    commands.add_config(mock_markdown_path_new, mock_target_json_path, mock_markdown_base_dir)

    mock_parse.assert_called_once_with(Path(mock_markdown_path_new).resolve())
    mock_load.assert_called_once_with(mock_target_json_path)
    expected_save_list = mock_configs_list + [mock_new_config] # Original list + new
    # Check the second argument passed to save_configs
    mock_save.assert_called_once()
    call_args, _ = mock_save.call_args
    assert call_args[0] == mock_target_json_path
    # Compare lists element by element after sorting by slug for stability
    saved_list_sorted = sorted(call_args[1], key=lambda x: x.slug)
    expected_list_sorted = sorted(expected_save_list, key=lambda x: x.slug)
    assert saved_list_sorted == expected_list_sorted


def test_add_config_duplicate_slug(
    mock_dependencies, mock_configs_list, mock_config_a, # mock_config_a has slug 'agent-a'
    mock_markdown_path_a, mock_target_json_path, mock_markdown_base_dir
):
    mock_load, _, mock_parse = mock_dependencies
    mock_load.return_value = mock_configs_list[:]
    # Make parse_markdown return a config with an existing slug
    mock_parse.return_value = mock_config_a

    with pytest.raises(ValueError, match=f"Agent with slug '{mock_config_a.slug}' already exists"):
        commands.add_config(mock_markdown_path_a, mock_target_json_path, mock_markdown_base_dir)

    mock_parse.assert_called_once()
    mock_load.assert_called_once()


# --- Tests for update_config ---

def test_update_config_success(
    mock_dependencies, mock_configs_list, mock_config_a,
    mock_markdown_path_a, mock_target_json_path, mock_markdown_base_dir
):
    mock_load, mock_save, mock_parse = mock_dependencies
    mock_load.return_value = mock_configs_list[:] # Return a copy
    # Simulate parsing the markdown for agent-a, perhaps with updated content
    updated_config_a = AgentConfig(slug="agent-a", name="Agent A Updated", roleDefinition="Role A Updated")
    mock_parse.return_value = updated_config_a

    commands.update_config(mock_markdown_path_a, mock_target_json_path, mock_markdown_base_dir, preserve_groups=True)

    mock_parse.assert_called_once_with(Path(mock_markdown_path_a).resolve())
    mock_load.assert_called_once_with(mock_target_json_path)
    # Expected list should have agent-a replaced
    original_config_b = next(c for c in mock_configs_list if c.slug == "agent-b")
    expected_save_list = [updated_config_a, original_config_b]

    mock_save.assert_called_once()
    call_args, _ = mock_save.call_args
    assert call_args[0] == mock_target_json_path
    saved_list_sorted = sorted(call_args[1], key=lambda x: x.slug)
    expected_list_sorted = sorted(expected_save_list, key=lambda x: x.slug)
    assert saved_list_sorted == expected_list_sorted


def test_update_config_slug_not_found(
    mock_dependencies, mock_configs_list, mock_new_config, # Use a non-existent slug
    mock_markdown_path_new, mock_target_json_path, mock_markdown_base_dir
):
    mock_load, _, mock_parse = mock_dependencies
    mock_load.return_value = mock_configs_list[:]
    mock_parse.return_value = mock_new_config # Config with slug 'new-agent'

    with pytest.raises(ValueError, match=f"Agent with slug '{mock_new_config.slug}' not found"):
        commands.update_config(mock_markdown_path_new, mock_target_json_path, mock_markdown_base_dir, preserve_groups=True)

    mock_parse.assert_called_once()
    mock_load.assert_called_once()


# --- Tests for delete_config ---

def test_delete_config_success(
    mock_dependencies, mock_configs_list, mock_config_a, mock_config_b,
    mock_target_json_path
):
    mock_load, mock_save, _ = mock_dependencies
    mock_load.return_value = mock_configs_list[:] # Return a copy
    slug_to_delete = mock_config_a.slug

    commands.delete_config(slug_to_delete, mock_target_json_path)

    mock_load.assert_called_once_with(mock_target_json_path)
    # Expected list should only contain agent-b
    expected_save_list = [mock_config_b]

    mock_save.assert_called_once()
    call_args, _ = mock_save.call_args
    assert call_args[0] == mock_target_json_path
    # Compare lists (order should be preserved if only one element)
    assert call_args[1] == expected_save_list


def test_delete_config_slug_not_found(
    mock_dependencies, mock_configs_list, mock_target_json_path
):
    mock_load, mock_save, _ = mock_dependencies
    mock_load.return_value = mock_configs_list[:]
    slug_to_delete = "non-existent-slug"

    with pytest.raises(ValueError, match=f"Agent with slug '{slug_to_delete}' not found"):
        commands.delete_config(slug_to_delete, mock_target_json_path)

    mock_load.assert_called_once_with(mock_target_json_path)
    mock_save.assert_not_called() # Save should not be called if slug not found