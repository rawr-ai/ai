# tests/cli/test_compile_integration.py
import pytest
import yaml
import json
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch

# Need to import the main 'cli' Typer application object
# Assuming it's defined in 'cli.main'
try:
    from cli.main import cli
except ImportError:
    # Provide a dummy object if import fails, so tests can be defined
    # but will fail clearly if the import path is wrong.
    print("Warning: Could not import 'cli' from 'cli.main'. Integration tests will fail.")
    cli = None

# Placeholder for valid agent config data
VALID_AGENT_CONFIG_DATA_1 = {
    "slug": "agent-one",
    "name": "Agent One",
    "description": "First valid test agent.",
    "roleDefinition": "Act as test agent 1.",
    "model": "test-model-1",
    "temperature": 0.7,
    "max_tokens": 100,
    "groups": ["test", "group1"],
    "version": "1.0.0",
}

VALID_AGENT_CONFIG_DATA_2 = {
    "slug": "agent-two",
    "name": "Agent Two",
    "description": "Second valid test agent.",
    "roleDefinition": "Act as test agent 2.",
    "model": "test-model-2",
    "temperature": 0.8,
    "max_tokens": 150,
    "groups": ["test", "group2"],
    "version": "1.1.0",
}

# Placeholder for invalid agent config data (e.g., missing 'name')
INVALID_AGENT_CONFIG_DATA = {
    "slug": "invalid-agent",
    # "name": "Invalid Agent", # Missing required field
    "description": "An invalid test agent.",
    "roleDefinition": "Act as an invalid test agent.",
    "model": "test-model-invalid",
    "temperature": 0.7,
    "max_tokens": 100,
    "groups": ["test", "invalid"],
    "version": "1.0.0",
}

# Config for fallback test
FALLBACK_AGENT_CONFIG_DATA = {
    "slug": "fallback-agent",
    "name": "Fallback Agent",
    "description": "Agent loaded via fallback path.",
    "roleDefinition": "Act as fallback agent.",
    "model": "test-model-fallback",
    "temperature": 0.6,
    "max_tokens": 120,
    "groups": ["test", "fallback"],
    "version": "1.0.1",
}


@pytest.fixture(scope="function")
def runner():
    """Provides a CliRunner instance for invoking CLI commands."""
    return CliRunner()

@pytest.fixture(scope="function")
def mock_agent_configs(tmp_path: Path):
    """Creates a temporary directory structure with mock agent configs."""
    agents_dir = tmp_path / "agents"
    registry_dir = tmp_path / ".rawr_registry"
    registry_file = registry_dir / "custom_modes.json"

    # Agent 1 (Valid, directory structure)
    agent1_dir = agents_dir / "agent-one"
    agent1_dir.mkdir(parents=True, exist_ok=True)
    with open(agent1_dir / "config.yaml", "w") as f:
        yaml.dump(VALID_AGENT_CONFIG_DATA_1, f)

    # Agent 2 (Valid, directory structure)
    agent2_dir = agents_dir / "agent-two"
    agent2_dir.mkdir(parents=True, exist_ok=True)
    with open(agent2_dir / "config.yaml", "w") as f:
        yaml.dump(VALID_AGENT_CONFIG_DATA_2, f)

    # Agent 3 (Invalid, directory structure)
    agent3_dir = agents_dir / "invalid-agent"
    agent3_dir.mkdir(parents=True, exist_ok=True)
    with open(agent3_dir / "config.yaml", "w") as f:
        yaml.dump(INVALID_AGENT_CONFIG_DATA, f)

    # Agent 4 (Valid, fallback path)
    with open(agents_dir / "fallback-agent.yaml", "w") as f:
        yaml.dump(FALLBACK_AGENT_CONFIG_DATA, f)

    # Ensure registry directory exists
    registry_dir.mkdir(parents=True, exist_ok=True)

    # Patch the config loader functions to point to the temp directories
    with patch('cli.config_loader.get_agent_config_dir', return_value=agents_dir), \
         patch('cli.config_loader.get_global_registry_path', return_value=registry_file):
        yield agents_dir, registry_file # Yield the paths for potential use in tests

# --- Integration Tests ---

def test_compile_all_agents_integration(runner: CliRunner, mock_agent_configs):
    """
    Integration test for `rawr compile` (compile all).
    Verifies successful compilation, partial success with invalid configs,
    and registry file creation/content.
    """
    agents_dir, registry_file = mock_agent_configs # Unpack paths from fixture

    # Invoke the compile command without arguments
    result = runner.invoke(cli, ["compile"], catch_exceptions=False)

    # Assertions
    assert "Processing 'agent-one/config.yaml'" in result.stdout
    assert "Processing 'agent-two/config.yaml'" in result.stdout
    assert "Processing 'invalid-agent/config.yaml'" in result.stdout
    assert "Processing 'fallback-agent.yaml'" not in result.stdout # Fallback shouldn't be picked up by compile all
    assert "Successfully processed agent: 'agent-one'" in result.stdout
    assert "Successfully processed agent: 'agent-two'" in result.stdout
    assert "Config validation failed" in result.stdout # Error for invalid-agent
    assert "❌ Error validating" in result.stdout
    assert "Skipping registry update" in result.stdout
    assert "Finished compiling agents." in result.stdout
    assert "Successfully compiled: 2" in result.stdout
    assert "Failed to compile: 1" in result.stdout
    assert "Registry written to:" in result.stdout
    assert str(registry_file) in result.stdout

    # Exit code 2 indicates partial success
    assert result.exit_code == 2, f"Expected exit code 2 (partial success), but got {result.exit_code}. Output:\n{result.stdout}"

    # Verify registry file content
    assert registry_file.exists()
    with open(registry_file, "r") as f:
        registry_data = json.load(f)

    assert "agents" in registry_data
    assert len(registry_data["agents"]) == 2
    assert "agent-one" in registry_data["agents"]
    assert registry_data["agents"]["agent-one"]["name"] == "Agent One"
    assert "agent-two" in registry_data["agents"]
    assert registry_data["agents"]["agent-two"]["name"] == "Agent Two"
    assert "invalid-agent" not in registry_data["agents"]
    assert "fallback-agent" not in registry_data["agents"]


def test_compile_single_agent_integration(runner: CliRunner, mock_agent_configs):
    """
    Integration test for `rawr compile <slug>` (compile single valid agent).
    """
    agents_dir, registry_file = mock_agent_configs
    target_slug = "agent-one"

    # Invoke the compile command with a specific valid slug
    result = runner.invoke(cli, ["compile", target_slug], catch_exceptions=False)

    # Assertions
    assert f"Processing '{target_slug}/config.yaml'" in result.stdout
    assert f"Successfully processed agent: '{target_slug}'" in result.stdout
    assert "Finished compiling agents." in result.stdout
    assert "Successfully compiled: 1" in result.stdout
    assert "Failed to compile: 0" in result.stdout
    assert "Registry written to:" in result.stdout
    assert str(registry_file) in result.stdout

    # Exit code 0 indicates success
    assert result.exit_code == 0, f"Expected exit code 0, but got {result.exit_code}. Output:\n{result.stdout}"

    # Verify registry file content
    assert registry_file.exists()
    with open(registry_file, "r") as f:
        registry_data = json.load(f)

    assert "agents" in registry_data
    assert len(registry_data["agents"]) == 1
    assert target_slug in registry_data["agents"]
    assert registry_data["agents"][target_slug]["name"] == "Agent One"


def test_compile_single_agent_not_found_integration(runner: CliRunner, mock_agent_configs):
    """
    Integration test for `rawr compile <slug>` when the slug does not exist.
    """
    agents_dir, registry_file = mock_agent_configs
    target_slug = "nonexistent-agent"

    # Invoke the compile command with a non-existent slug
    result = runner.invoke(cli, ["compile", target_slug], catch_exceptions=False)

    # Assertions
    assert f"Agent config file not found for slug '{target_slug}'" in result.stdout
    assert "❌ Compilation failed" in result.stdout
    assert "Registry not written" in result.stdout

    # Exit code 1 indicates failure
    assert result.exit_code == 1, f"Expected exit code 1, but got {result.exit_code}. Output:\n{result.stdout}"

    # Verify registry file was NOT created or modified (if it existed before)
    # For simplicity, we check it doesn't exist, assuming it wasn't there initially.
    # A more robust check might involve reading initial state if needed.
    assert not registry_file.exists()


def test_compile_single_agent_fallback_path_integration(runner: CliRunner, mock_agent_configs):
    """
    Integration test for `rawr compile <slug>` using the fallback path (<slug>.yaml).
    """
    agents_dir, registry_file = mock_agent_configs
    target_slug = "fallback-agent"

    # Invoke the compile command targeting the agent defined by fallback path
    result = runner.invoke(cli, ["compile", target_slug], catch_exceptions=False)

    # Assertions
    assert f"Using fallback config path: {agents_dir / (target_slug + '.yaml')}" in result.stdout
    assert f"Processing '{target_slug}.yaml'" in result.stdout # Adjusted expectation
    assert f"Successfully processed agent: '{target_slug}'" in result.stdout
    assert "Finished compiling agents." in result.stdout
    assert "Successfully compiled: 1" in result.stdout
    assert "Failed to compile: 0" in result.stdout
    assert "Registry written to:" in result.stdout
    assert str(registry_file) in result.stdout

    # Exit code 0 indicates success
    assert result.exit_code == 0, f"Expected exit code 0, but got {result.exit_code}. Output:\n{result.stdout}"

    # Verify registry file content
    assert registry_file.exists()
    with open(registry_file, "r") as f:
        registry_data = json.load(f)

    assert "agents" in registry_data
    assert len(registry_data["agents"]) == 1
    assert target_slug in registry_data["agents"]
    assert registry_data["agents"][target_slug]["name"] == "Fallback Agent"

def test_compile_single_agent_invalid_integration(runner: CliRunner, mock_agent_configs):
    """
    Integration test for `rawr compile <slug>` when the target config is invalid.
    """
    agents_dir, registry_file = mock_agent_configs
    target_slug = "invalid-agent"

    # Invoke the compile command with the invalid slug
    result = runner.invoke(cli, ["compile", target_slug], catch_exceptions=False)

    # Assertions
    assert f"Processing '{target_slug}/config.yaml'" in result.stdout
    assert "Config validation failed" in result.stdout
    assert "❌ Error validating" in result.stdout
    assert "❌ Compilation failed" in result.stdout
    assert "Registry not written" in result.stdout

    # Exit code 1 indicates failure
    assert result.exit_code == 1, f"Expected exit code 1, but got {result.exit_code}. Output:\n{result.stdout}"

    # Verify registry file was NOT created or modified
    assert not registry_file.exists()