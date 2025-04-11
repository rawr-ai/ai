# tests/unit/test_config_loader.py
import pytest
import yaml
import os
from pathlib import Path
import sys
import importlib # Needed for reloading the module under test
import builtins # Needed for mocking builtins.open

# Module to test
from cli import config_loader

# --- Test Constants ---
DEFAULT_AGENT_DIR_NAME = "cli/agent_config"
DEFAULT_REGISTRY_NAME = ".rawr_registry/custom_modes.json"

MAIN_CONFIG_FILENAME = "rawr.config.yaml"
LOCAL_CONFIG_FILENAME = "rawr.config.local.yaml"

# --- Helper Functions ---

def create_config_file(path: Path, content: dict):
    """Creates a YAML config file at the specified path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(content, f)

# --- Test Suite ---

# Fixture to ensure module is reloaded for tests that modify its state/dependencies
@pytest.fixture(autouse=True)
def reload_config_loader():
    """Ensures config_loader is reloaded before each test."""
    # Store original state if necessary, e.g., original sys.path or env vars
    original_env = os.environ.copy()
    original_settings = config_loader.settings.copy() if hasattr(config_loader, 'settings') else None

    importlib.reload(config_loader)
    yield
    # Restore original state after test
    os.environ.clear()
    os.environ.update(original_env)
    if original_settings is not None:
         config_loader.settings = original_settings # Restore if needed, though reload might suffice
    importlib.reload(config_loader) # Reload again to clean up module state

def test_load_config_defaults(monkeypatch):
    """
    LOADER_UT_NEW_001: Verify default paths are returned when no config files or env vars exist.
    """
    # Ensure config files don't exist (tmp_path is clean by default)
    # Ensure env vars are not set
    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Mock paths to ensure they don't exist during the test run
    monkeypatch.setattr(config_loader.Path, 'exists', lambda self: False)
    monkeypatch.setattr(config_loader.Path, 'is_file', lambda self: False)


    # We need to reload the module AFTER patching env vars and mocks. The fixture handles this.
    config = config_loader.load_config()
    project_root = config_loader.PROJECT_ROOT # Get the actual project root used

    expected_agent_dir = (project_root / DEFAULT_AGENT_DIR_NAME).resolve()
    expected_registry_path = (project_root / DEFAULT_REGISTRY_NAME).resolve()

    assert isinstance(config, dict)
    assert 'agent_config_dir' in config
    assert 'global_registry_path' in config
    assert config['agent_config_dir'] == expected_agent_dir
    assert config['global_registry_path'] == expected_registry_path
    assert config['agent_config_dir'].is_absolute()
    assert config['global_registry_path'].is_absolute()

def test_load_config_main_config_relative(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_002: Verify loading relative paths from the main config file.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME # Does not exist
    agent_dir_rel = "config/agents_main"
    registry_rel = "config/registry_main.json"

    create_config_file(main_config_path, {
        'agent_config_dir': agent_dir_rel,
        'global_registry_path': registry_rel
    })

    # Mock the paths used by the loader to point to our temp files
    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    # Mock PROJECT_ROOT so relative paths are resolved against tmp_path
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path)

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload to use mocked paths/root (handled by fixture)
    config = config_loader.load_config()

    assert config['agent_config_dir'] == (tmp_path / agent_dir_rel).resolve()
    assert config['global_registry_path'] == (tmp_path / registry_rel).resolve()

def test_load_config_main_config_absolute(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_003: Verify loading absolute paths from the main config file.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME # Does not exist
    # Use paths within tmp_path but make them absolute for the test
    agent_dir_abs = (tmp_path / "abs_agents").resolve()
    registry_abs = (tmp_path / "abs_registry.json").resolve()

    create_config_file(main_config_path, {
        'agent_config_dir': str(agent_dir_abs), # Store as string in YAML
        'global_registry_path': str(registry_abs)
    })

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    # Mocking PROJECT_ROOT shouldn't affect absolute paths loading from YAML
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path / "fake_root")

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload handled by fixture
    config = config_loader.load_config()

    assert config['agent_config_dir'] == agent_dir_abs
    assert config['global_registry_path'] == registry_abs


def test_load_config_local_overrides_main(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_004: Verify local config overrides main config.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    agent_dir_local = "config/agents_local"
    registry_local = "config/registry_local.json"

    create_config_file(main_config_path, {
        'agent_config_dir': agent_dir_main,
        'global_registry_path': registry_main
    })
    create_config_file(local_config_path, {
        'agent_config_dir': agent_dir_local,
        'global_registry_path': registry_local
    })

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path)

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload handled by fixture
    config = config_loader.load_config()

    assert config['agent_config_dir'] == (tmp_path / agent_dir_local).resolve()
    assert config['global_registry_path'] == (tmp_path / registry_local).resolve()

def test_load_config_local_partial_override(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_005: Verify local config partially overrides main config.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    # Local only overrides agent_config_dir
    agent_dir_local = "config/agents_local"

    create_config_file(main_config_path, {
        'agent_config_dir': agent_dir_main,
        'global_registry_path': registry_main
    })
    create_config_file(local_config_path, {
        'agent_config_dir': agent_dir_local
        # 'global_registry_path' is missing here
    })

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path)

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload handled by fixture
    config = config_loader.load_config()

    # agent_config_dir should come from local
    assert config['agent_config_dir'] == (tmp_path / agent_dir_local).resolve()
    # global_registry_path should come from main (since local didn't override)
    assert config['global_registry_path'] == (tmp_path / registry_main).resolve()


def test_load_config_env_overrides_all_relative(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_006: Verify env vars override local and main (relative env path).
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    agent_dir_local = "config/agents_local"
    registry_local = "config/registry_local.json"
    agent_dir_env = "env_agents" # Relative to CWD
    registry_env = "env_registry.json"

    create_config_file(main_config_path, {'agent_config_dir': agent_dir_main, 'global_registry_path': registry_main})
    create_config_file(local_config_path, {'agent_config_dir': agent_dir_local, 'global_registry_path': registry_local})

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path / "fake_root") # Should be ignored for env vars

    monkeypatch.setenv("RAWR_AGENT_CONFIG_DIR", agent_dir_env)
    monkeypatch.setenv("RAWR_GLOBAL_REGISTRY_PATH", registry_env)

    # Change CWD to tmp_path for resolving relative env vars
    monkeypatch.chdir(tmp_path)

    # Reload handled by fixture
    config = config_loader.load_config()

    # Env vars are resolved relative to CWD at time of load_config call
    assert config['agent_config_dir'] == (tmp_path / agent_dir_env).resolve()
    assert config['global_registry_path'] == (tmp_path / registry_env).resolve()

def test_load_config_env_overrides_all_absolute(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_007: Verify env vars override local and main (absolute env path).
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    agent_dir_local = "config/agents_local"
    registry_local = "config/registry_local.json"
    # Absolute paths for env vars
    agent_dir_env_abs = (tmp_path / "env_agents_abs").resolve()
    registry_env_abs = (tmp_path / "env_registry_abs.json").resolve()

    create_config_file(main_config_path, {'agent_config_dir': agent_dir_main, 'global_registry_path': registry_main})
    create_config_file(local_config_path, {'agent_config_dir': agent_dir_local, 'global_registry_path': registry_local})

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path / "fake_root") # Ignored

    monkeypatch.setenv("RAWR_AGENT_CONFIG_DIR", str(agent_dir_env_abs))
    monkeypatch.setenv("RAWR_GLOBAL_REGISTRY_PATH", str(registry_env_abs))

    # Reload handled by fixture
    config = config_loader.load_config()

    assert config['agent_config_dir'] == agent_dir_env_abs
    assert config['global_registry_path'] == registry_env_abs

def test_load_config_env_partial_override(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_008: Verify env var partially overrides local/main.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    agent_dir_local = "config/agents_local"
    # registry_local is missing
    # Env var only overrides agent_config_dir
    agent_dir_env = "env_agents" # Relative

    create_config_file(main_config_path, {'agent_config_dir': agent_dir_main, 'global_registry_path': registry_main})
    create_config_file(local_config_path, {'agent_config_dir': agent_dir_local})

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path) # For resolving YAML paths

    monkeypatch.setenv("RAWR_AGENT_CONFIG_DIR", agent_dir_env)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False) # Ensure this one isn't set

    monkeypatch.chdir(tmp_path) # For relative env var resolution

    # Reload handled by fixture
    config = config_loader.load_config()

    # agent_config_dir should come from env
    assert config['agent_config_dir'] == (tmp_path / agent_dir_env).resolve()
    # global_registry_path should come from local (which got it from main)
    assert config['global_registry_path'] == (tmp_path / registry_main).resolve()


def test_load_config_file_not_found_graceful(monkeypatch, tmp_path, capsys):
    """
    LOADER_UT_NEW_009: Verify graceful handling when config files don't exist (uses defaults).
    """
    main_config_path = tmp_path / "nonexistent" / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / "nonexistent" / LOCAL_CONFIG_FILENAME

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    # Use real PROJECT_ROOT for defaults comparison
    project_root = config_loader.PROJECT_ROOT
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', project_root)


    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload handled by fixture
    config = config_loader.load_config()
    captured = capsys.readouterr() # Capture warnings

    # Should fall back to code defaults
    expected_agent_dir = (project_root / DEFAULT_AGENT_DIR_NAME).resolve()
    expected_registry_path = (project_root / DEFAULT_REGISTRY_NAME).resolve()
    assert config['agent_config_dir'] == expected_agent_dir
    assert config['global_registry_path'] == expected_registry_path

    # Check that no errors were printed (it should handle missing files silently)
    assert "Warning: Could not read" not in captured.err
    assert "Warning: Error parsing" not in captured.err


def test_load_config_yaml_error_graceful(monkeypatch, tmp_path, capsys):
    """
    LOADER_UT_NEW_010: Verify graceful handling of YAML syntax errors (uses previous/default values).
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME # Will have bad syntax

    # Valid main config
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    create_config_file(main_config_path, {
        'agent_config_dir': agent_dir_main,
        'global_registry_path': registry_main
    })

    # Invalid local config
    local_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_config_path, 'w') as f:
        f.write("agent_config_dir: bad_dir\n  bad_indent: true") # Invalid YAML

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path)

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload handled by fixture
    config = config_loader.load_config()
    captured = capsys.readouterr()

    # Should use values from main config because local failed to parse
    assert config['agent_config_dir'] == (tmp_path / agent_dir_main).resolve()
    assert config['global_registry_path'] == (tmp_path / registry_main).resolve()

    # Check that a warning was printed to stderr
    assert f"Warning: Error parsing {local_config_path}" in captured.err

def test_load_config_permission_error_graceful(monkeypatch, tmp_path, capsys):
    """
    LOADER_UT_NEW_011: Verify graceful handling of file permission errors.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME # Unreadable

    # Valid main config
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    create_config_file(main_config_path, {
        'agent_config_dir': agent_dir_main,
        'global_registry_path': registry_main
    })

    # Create local config but make it unreadable
    create_config_file(local_config_path, {'agent_config_dir': 'local_unreadable'})
    # Attempt to make unreadable, might fail on some systems/runners
    try:
        local_config_path.chmod(0o000)
    except PermissionError:
        pytest.skip("Could not set file permissions to 000 for permission test.")


    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path)

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Mock open to raise PermissionError for the specific file
    original_open = builtins.open
    def mock_open_wrapper(file, *args, **kwargs):
        try:
            resolved_file = Path(file).resolve()
        except Exception:
             return original_open(file, *args, **kwargs)

        if resolved_file == local_config_path.resolve():
            raise PermissionError(f"[Errno 13] Permission denied: '{local_config_path}'")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', mock_open_wrapper)

    # Reload handled by fixture, will now use the mocked open
    config = config_loader.load_config()
    captured = capsys.readouterr()

    # Should use values from main config because local was unreadable
    assert config['agent_config_dir'] == (tmp_path / agent_dir_main).resolve()
    assert config['global_registry_path'] == (tmp_path / registry_main).resolve()

    # Check that a warning was printed to stderr
    assert f"Warning: Could not read {local_config_path}" in captured.err
    assert "Permission denied" in captured.err

    # Restore permissions if possible (pytest tmp_path cleanup should handle this anyway)
    try:
        local_config_path.chmod(0o644)
    except PermissionError:
        pass


def test_load_config_yaml_not_dict_warning(monkeypatch, tmp_path, capsys):
    """
    LOADER_UT_NEW_012: Verify warning when YAML file is not a dictionary.
    """
    main_config_path = tmp_path / MAIN_CONFIG_FILENAME
    local_config_path = tmp_path / LOCAL_CONFIG_FILENAME # Will contain a list

    # Valid main config
    agent_dir_main = "config/agents_main"
    registry_main = "config/registry_main.json"
    create_config_file(main_config_path, {
        'agent_config_dir': agent_dir_main,
        'global_registry_path': registry_main
    })

    # Invalid local config (list instead of dict)
    local_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_config_path, 'w') as f:
        yaml.dump(['item1', 'item2'], f)

    monkeypatch.setattr(config_loader, 'DEFAULT_CONFIG_PATH', main_config_path)
    monkeypatch.setattr(config_loader, 'LOCAL_CONFIG_PATH', local_config_path)
    monkeypatch.setattr(config_loader, 'PROJECT_ROOT', tmp_path)

    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    # Reload handled by fixture
    config = config_loader.load_config()
    captured = capsys.readouterr()

    # Should use values from main config because local was not a dict
    assert config['agent_config_dir'] == (tmp_path / agent_dir_main).resolve()
    assert config['global_registry_path'] == (tmp_path / registry_main).resolve()

    # Check that a warning was printed to stderr
    assert f"Warning: Config file {local_config_path} is not a valid dictionary. Ignoring." in captured.err


# --- Tests for Accessor Functions ---

def test_get_agent_config_dir(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_101: Verify get_agent_config_dir returns correct path from loaded settings.
    """
    env_path = tmp_path / "env_dir_accessor"
    monkeypatch.setenv("RAWR_AGENT_CONFIG_DIR", str(env_path))
    monkeypatch.delenv("RAWR_GLOBAL_REGISTRY_PATH", raising=False)

    importlib.reload(config_loader) # Reload to pick up patched env vars
    # Reload handled by fixture, loads settings with env var
    # Access directly via getter after reload
    retrieved_path = config_loader.get_agent_config_dir()

    assert retrieved_path == env_path.resolve()
    assert retrieved_path.is_absolute()

def test_get_global_registry_path(monkeypatch, tmp_path):
    """
    LOADER_UT_NEW_102: Verify get_global_registry_path returns correct path from loaded settings.
    """
    env_path = tmp_path / "env_registry_accessor.json"
    monkeypatch.setenv("RAWR_GLOBAL_REGISTRY_PATH", str(env_path))
    monkeypatch.delenv("RAWR_AGENT_CONFIG_DIR", raising=False)

    importlib.reload(config_loader) # Reload to pick up patched env vars
    # Reload handled by fixture
    # Access directly via getter after reload
    retrieved_path = config_loader.get_global_registry_path()

    assert retrieved_path == env_path.resolve()
    assert retrieved_path.is_absolute()

def test_getters_fallback_to_defaults(monkeypatch):
    """
    LOADER_UT_NEW_103: Verify getters fall back to defaults if settings are somehow empty/invalid.
    """
    # Simulate settings being empty or corrupted *after* initial load
    # The fixture reloads, so we need to patch 'settings' *after* the reload within the test
    importlib.reload(config_loader) # Initial load via fixture
    monkeypatch.setattr(config_loader, 'settings', {}) # Corrupt settings

    # We don't need to reload again, just call getters on the corrupted state
    project_root = config_loader.PROJECT_ROOT
    expected_agent_dir = (project_root / DEFAULT_AGENT_DIR_NAME).resolve()
    expected_registry_path = (project_root / DEFAULT_REGISTRY_NAME).resolve()

    assert config_loader.get_agent_config_dir() == expected_agent_dir
    assert config_loader.get_global_registry_path() == expected_registry_path