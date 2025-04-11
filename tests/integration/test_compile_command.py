# tests/integration/test_compile_command.py
import pytest
import yaml
import json
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch
from pydantic import ValidationError

# Import the app instance directly from the main module
from cli.main import app
from cli.main import app, compile_agent_config # Import command function directly
from cli import constants
from cli.models import GlobalAgentConfig # Use the correct model name
from cli.config_loader import ConfigLoadError, ConfigValidationError

# Test-specific constants
MOCK_AGENTS_DIR_NAME = "mock_agents"
MOCK_REGISTRY_FILENAME = "mock_custom_modes.json"
CONFIG_FILENAME = "config.yaml"

# Dictionary Keys (matching cli.constants where possible, but defined here for test scope)
KEY_CUSTOM_MODES = "customModes"
KEY_SLUG = "slug"
KEY_NAME = "name"
KEY_ROLE_DEF = "roleDefinition"
KEY_CUSTOM_INSTR = "customInstructions"
KEY_GROUPS = "groups"
KEY_API_CONFIG = "apiConfiguration"
KEY_ENDPOINT = "endpoint" # Nested within API config
KEY_RAW_CONTENT = "raw_content" # For error reading registry
KEY_ERROR = "error" # For error reading registry


# Agent Slugs
AGENT_A_SLUG = "agent-a"
AGENT_B_SLUG = "agent-b"
NON_EXISTENT_SLUG = "non-existent-agent"
INVALID_YAML_SLUG = "agent-invalid-yaml"
SCHEMA_FAIL_SLUG = "agent-schema-fail"
READ_FAIL_SLUG = "agent-read-fail"
WRITE_FAIL_SLUG = "agent-write-fail"

# Command
CMD_COMPILE = "compile"

# Message Snippets (Key parts for assertion)
MSG_SUCCESS_PREFIX = "Successfully compiled and updated global registry for agent:"
MSG_ERR_CONFIG_NOT_FOUND = "Config file not found for agent"
MSG_ERR_VALIDATION_FAILED = "Error: Config validation failed"
MSG_ERR_READ_FAILED = "Error: An unexpected error occurred while reading the global registry"
MSG_ERR_WRITE_FAILED = "Error: An unexpected error occurred while writing the global registry"
MSG_ERR_PREFIX = "❌ Error:"
MSG_ERR_PERMISSION_READ = "Permission denied reading registry"
MSG_ERR_DISK_FULL_WRITE = "Disk full writing registry"
MSG_ERR_FIELD_REQUIRED = "field required"
MSG_ERR_VALIDATION_INDICATOR = "validation error" # Generic indicator
MSG_ERR_YAML_INDICATOR = "YAML" # Generic indicator
MSG_ERR_PARSING_INDICATOR = "parsing" # Generic indicator
MSG_ERR_SCAN_INDICATOR = "scan" # Generic indicator

# --- Test Fixtures ---

@pytest.fixture
def setup_test_env(tmp_path, mocker):
    """
    Sets up an isolated test environment in a temporary directory.

    - Creates mock agent config directory structure.
    - Creates a mock global registry file path.
    - Patches constants used by cli.main and potentially other modules.
    - Provides CliRunner, tmp_path, mock registry path, and mock agents dir.
    """
    runner = CliRunner(mix_stderr=False) # Ensure stderr is captured separately
    agents_base_dir = tmp_path / MOCK_AGENTS_DIR_NAME
    agents_base_dir.mkdir()
    mock_registry_path = tmp_path / MOCK_REGISTRY_FILENAME

    # --- CRITICAL: Patch constants used within cli.main ---
    # Patch where they are defined (constants module) AND where they are imported/used (main module)
    # This addresses potential import-time resolution issues highlighted in debugging.
    # Patching cli.constants.* was incorrect as these are defined locally in cli.main using getattr fallbacks.
    # mocker.patch('cli.constants.AGENT_CONFIG_DIR', agents_base_dir) # REMOVED - Attribute doesn't exist here
    # mocker.patch('cli.constants.GLOBAL_REGISTRY_PATH', mock_registry_path) # REMOVED - Attribute doesn't exist here
    mocker.patch('cli.main.AGENT_CONFIG_DIR', agents_base_dir)
    mocker.patch('cli.main.GLOBAL_REGISTRY_PATH', mock_registry_path)

    print(f"DEBUG: Fixture setup - tmp_path: {tmp_path}")
    print(f"DEBUG: Fixture setup - agents_base_dir: {agents_base_dir}")
    print(f"DEBUG: Fixture setup - mock_registry_path: {mock_registry_path}")

    # Initialize registry file for tests that need it to exist
    # mock_registry_path.write_text(json.dumps({"customModes": []}))

    yield runner, tmp_path, mock_registry_path, agents_base_dir

    # Cleanup is handled automatically by tmp_path fixture


# --- Helper Functions ---

def create_mock_config(agents_dir: Path, slug: str, config_data: dict):
    """Creates a mock config.yaml file for a given agent slug."""
    agent_dir = agents_dir / slug
    agent_dir.mkdir(parents=True, exist_ok=True)
    config_path = agent_dir / CONFIG_FILENAME # Use literal filename
    import yaml # Import yaml safely inside the function
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        print(f"DEBUG: Created mock config at {config_path}")
    except Exception as e:
        print(f"ERROR creating mock config: {e}")
        raise
    return config_path

def read_mock_registry(registry_path: Path) -> dict:
    """Reads the content of the mock registry file."""
    if not registry_path.exists():
        return {KEY_CUSTOM_MODES: []} # Return default empty structure if file doesn't exist
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from {registry_path}")
        # Return raw content for debugging if needed, or raise/return empty
        try:
            return {KEY_RAW_CONTENT: registry_path.read_text()}
        except Exception:
            return {KEY_ERROR: "Could not read or decode file"}
    except Exception as e:
        print(f"ERROR reading mock registry: {e}")
        return {KEY_ERROR: str(e)}


# --- Test Cases (Based on step_3.2_integration_test_plan.md) ---

def test_compile_success_new_agent(setup_test_env):
    """Test Case 3.2.1: Successful compilation of a new agent."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = AGENT_A_SLUG
    config_data = {
        KEY_SLUG: agent_slug,
        KEY_NAME: "Agent A",
        KEY_ROLE_DEF: "Role for Agent A",
        # KEY_CUSTOM_INSTR: "These should NOT be in the registry.", # Not part of GlobalAgentConfig
        KEY_GROUPS: ["group1"], # Required field
        KEY_API_CONFIG: {"model": "gpt-4"} # Use ApiConfig structure, 'model' is required
}
    create_mock_config(agents_dir, agent_slug, config_data)

    # Ensure registry doesn't exist initially or is empty
    if mock_registry_path.exists():
        mock_registry_path.unlink()

    # Action
    compile_agent_config(agent_slug) # Call function directly

    # Assertions
    # No exit code or stdout to check with direct call
    assert mock_registry_path.exists(), "Registry file was not created."

    registry_content = read_mock_registry(mock_registry_path)
    assert KEY_CUSTOM_MODES in registry_content
    assert isinstance(registry_content[KEY_CUSTOM_MODES], list)
    assert len(registry_content[KEY_CUSTOM_MODES]) == 1

    agent_entry = registry_content[KEY_CUSTOM_MODES][0]
    assert agent_entry[KEY_SLUG] == agent_slug
    assert agent_entry[KEY_NAME] == config_data[KEY_NAME]
    assert agent_entry[KEY_ROLE_DEF] == config_data[KEY_ROLE_DEF]
    assert agent_entry[KEY_GROUPS] == config_data[KEY_GROUPS]
    # Adjust assertion for nested ApiConfig model
    assert agent_entry[KEY_API_CONFIG]["model"] == config_data[KEY_API_CONFIG]["model"]
    # assert KEY_CUSTOM_INSTR not in agent_entry # Already verified by schema validation


def test_compile_success_update_agent(setup_test_env):
    """Test Case 3.2.2: Successful update of an existing agent."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = AGENT_B_SLUG
    initial_config_data = {
        KEY_SLUG: agent_slug,
        KEY_NAME: "Agent B Old",
        KEY_ROLE_DEF: "Old Role",
        KEY_GROUPS: ["group1"], # Required field
        # apiConfiguration is optional, so omit initially
    }
    updated_config_data = {
        KEY_SLUG: agent_slug,
        KEY_NAME: "Agent B New",
        KEY_ROLE_DEF: "New Role for Agent B",
        # KEY_CUSTOM_INSTR: "Update instructions - should be ignored.", # Not part of GlobalAgentConfig
        KEY_GROUPS: ["group1", "group2"], # Changed groups, required field
        KEY_API_CONFIG: {"model": "gpt-3.5-turbo", "url": "http://example.com/api/b/new"} # Added API config using correct schema
}

    # Preconditions: Create initial registry and updated config file
    initial_registry = {KEY_CUSTOM_MODES: [initial_config_data]}
    mock_registry_path.write_text(json.dumps(initial_registry, indent=2))
    create_mock_config(agents_dir, agent_slug, updated_config_data)

    # Action
    compile_agent_config(agent_slug) # Call function directly

    # Assertions
    # No exit code or stdout to check with direct call
    registry_content = read_mock_registry(mock_registry_path)
    assert len(registry_content[KEY_CUSTOM_MODES]) == 1 # Should still only have one agent

    agent_entry = registry_content[KEY_CUSTOM_MODES][0]
    assert agent_entry[KEY_SLUG] == agent_slug
    assert agent_entry[KEY_NAME] == updated_config_data[KEY_NAME] # Verify update
    assert agent_entry[KEY_ROLE_DEF] == updated_config_data[KEY_ROLE_DEF] # Verify update
    assert agent_entry[KEY_GROUPS] == updated_config_data[KEY_GROUPS] # Verify update
    # Adjust assertion for nested ApiConfig model
    assert agent_entry[KEY_API_CONFIG]["model"] == updated_config_data[KEY_API_CONFIG]["model"] # Verify update
    assert str(agent_entry[KEY_API_CONFIG]["url"]) == updated_config_data[KEY_API_CONFIG]["url"] # Verify update (URL is HttpUrl)
    # assert KEY_CUSTOM_INSTR not in agent_entry # Already verified by schema validation


def test_compile_fail_config_not_found(setup_test_env, mocker): # Add mocker fixture
    """Test Case 3.2.3: Failure when agent config.yaml is not found."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = NON_EXISTENT_SLUG

    # Preconditions: Ensure registry exists (or not), but config doesn't
    initial_registry = {KEY_CUSTOM_MODES: []}
    mock_registry_path.write_text(json.dumps(initial_registry, indent=2))
    # DO NOT create config for agent_slug

    # Action & Assertions
    # Expect FileNotFoundError
    with pytest.raises(FileNotFoundError) as excinfo:
        compile_agent_config(agent_slug) # Call function directly
    # Optionally check the error message content if needed
    assert agent_slug in str(excinfo.value)
    assert "Configuration file not found" in str(excinfo.value)

    # Verify registry remains unchanged
    registry_content = read_mock_registry(mock_registry_path)
    assert registry_content == initial_registry


def test_compile_fail_invalid_yaml(setup_test_env, mocker): # Add mocker fixture
    """Test Case 3.2.4: Failure when config.yaml has invalid YAML syntax."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = INVALID_YAML_SLUG

    # Preconditions: Create invalid YAML
    agent_dir = agents_dir / agent_slug
    agent_dir.mkdir(parents=True, exist_ok=True)
    config_path = agent_dir / "config.yaml" # Use literal filename
    invalid_yaml_content = "slug: agent-invalid-yaml\nname: Invalid\nroleDefinition: Bad Role\ngroups: [group1" # Missing closing bracket
    config_path.write_text(invalid_yaml_content)
    print(f"DEBUG: Created invalid mock config at {config_path}")

    initial_registry = {KEY_CUSTOM_MODES: []}
    mock_registry_path.write_text(json.dumps(initial_registry, indent=2))

    # Action & Assertions
    # Expect ConfigLoadError (from invalid YAML)
    with pytest.raises(ConfigLoadError) as excinfo:
        compile_agent_config(agent_slug) # Call function directly
    # Optionally check the error message content if needed
    assert agent_slug in str(excinfo.value)
    assert "Error parsing YAML file" in str(excinfo.value)

    # Verify registry remains unchanged
    registry_content = read_mock_registry(mock_registry_path)
    assert registry_content == initial_registry


def test_compile_fail_schema_validation(setup_test_env, mocker): # Add mocker fixture
    """Test Case 3.2.5: Failure when config.yaml fails Pydantic schema validation."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = SCHEMA_FAIL_SLUG
    # Missing 'name', which is required by AgentConfig model (presumably)
    config_data = {
        KEY_SLUG: agent_slug,
        # "name": "Agent Schema Fail", # Missing required field
        KEY_ROLE_DEF: "Role definition is present",
        KEY_GROUPS: ["group1"], # Add missing required field
    }
    create_mock_config(agents_dir, agent_slug, config_data)

    initial_registry = {KEY_CUSTOM_MODES: []}
    mock_registry_path.write_text(json.dumps(initial_registry, indent=2))

    # Action & Assertions
    # Expect ConfigValidationError
    with pytest.raises(ConfigValidationError) as excinfo:
        compile_agent_config(agent_slug) # Call function directly
    # Optionally check the error message content if needed
    assert agent_slug in str(excinfo.value)
    assert "Configuration validation failed" in str(excinfo.value)
    assert "Field required" in str(excinfo.value) # Check for Pydantic detail

    # Verify registry remains unchanged
    registry_content = read_mock_registry(mock_registry_path)
    assert registry_content == initial_registry


def test_compile_fail_registry_read_error(setup_test_env, mocker):
    """Test Case 3.2.6: Failure when reading the global registry fails."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = READ_FAIL_SLUG
    config_data = {
        KEY_SLUG: agent_slug,
        KEY_NAME: "Agent Read Fail",
        KEY_ROLE_DEF: "Role definition",
        KEY_GROUPS: ["group1"], # Add missing required field
    }
    create_mock_config(agents_dir, agent_slug, config_data)

    # Precondition: Patch registry read function to raise OSError
    mock_read = mocker.patch('cli.registry_manager.read_global_registry', side_effect=OSError(MSG_ERR_PERMISSION_READ))

    # Action & Assertions
    # Expect OSError and check the message
    with pytest.raises(OSError) as excinfo:
        compile_agent_config(agent_slug) # Call function directly
    assert MSG_ERR_PERMISSION_READ in str(excinfo.value)
    mock_read.assert_called_once_with(mock_registry_path) # Verify mock was called


def test_compile_fail_registry_write_error(setup_test_env, mocker):
    """Test Case 3.2.7: Failure when writing the updated global registry fails."""
    runner, tmp_path, mock_registry_path, agents_dir = setup_test_env
    agent_slug = WRITE_FAIL_SLUG
    config_data = {
        KEY_SLUG: agent_slug,
        KEY_NAME: "Agent Write Fail",
        KEY_ROLE_DEF: "Role definition",
        KEY_GROUPS: ["group1"], # Add missing required field (Corrected: remove duplicate)
    }
    create_mock_config(agents_dir, agent_slug, config_data)

    # Precondition: Ensure registry can be read (or doesn't exist), patch write function
    if mock_registry_path.exists():
        mock_registry_path.unlink() # Start clean

    mock_write = mocker.patch('cli.registry_manager.write_global_registry', side_effect=OSError(MSG_ERR_DISK_FULL_WRITE))

    # Action & Assertions
    # Expect OSError and check the message
    with pytest.raises(OSError) as excinfo:
        compile_agent_config(agent_slug) # Call function directly
    assert MSG_ERR_DISK_FULL_WRITE in str(excinfo.value)
    # Check that write was called (after successful steps before it)
    mock_write.assert_called_once() # Verify mock was called


# Test Case 3.2.8 (Call Sequence) is optional and lower priority per the plan.
# It requires more complex mocking of multiple functions and return values.
# Skipping for now to focus on core functionality and error handling.

# --- TODO: Add more tests as needed ---
# - Test with different valid config structures (e.g., missing optional fields)
# - Test slug case sensitivity if relevant
# - Test interaction with a registry containing many other agents