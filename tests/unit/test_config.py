import json
import pytest
from pathlib import Path
from pydantic import ValidationError
from scripts.agent_config_manager.config import load_configs, save_configs
from scripts.agent_config_manager.models import AgentConfig

# --- Fixtures ---

@pytest.fixture
def sample_configs():
    """Provides a list of sample AgentConfig objects."""
    return [
        AgentConfig(slug="agent-b", name="Agent B", roleDefinition="Role B"),
        AgentConfig(slug="agent-a", name="Agent A", roleDefinition="Role A", customInstructions="Custom A"),
    ]

@pytest.fixture
def valid_json_content(sample_configs):
    """Provides valid JSON content string corresponding to sample_configs."""
    # Mimic the structure expected by load_configs and produced by save_configs
    config_dicts = sorted(
        [config.dict(by_alias=True, exclude_none=True) for config in sample_configs],
        key=lambda x: x.get('slug', '')
    )
    return json.dumps({"customModes": config_dicts}, indent=2)

@pytest.fixture
def valid_json_file(tmp_path, valid_json_content):
    """Creates a temporary valid JSON file."""
    p = tmp_path / "valid_config.json"
    p.write_text(valid_json_content, encoding='utf-8')
    return p

@pytest.fixture
def invalid_structure_json_file(tmp_path):
    """Creates a temporary JSON file with invalid structure (missing 'customModes')."""
    p = tmp_path / "invalid_structure.json"
    p.write_text(json.dumps([{"slug": "test"}], indent=2), encoding='utf-8') # List instead of dict
    return p

@pytest.fixture
def invalid_data_json_file(tmp_path):
    """Creates a temporary JSON file with data violating AgentConfig schema."""
    p = tmp_path / "invalid_data.json"
    # Missing 'name' and 'roleDefinition'
    p.write_text(json.dumps({"customModes": [{"slug": "invalid"}]}, indent=2), encoding='utf-8')
    return p

@pytest.fixture
def invalid_json_syntax_file(tmp_path):
    """Creates a temporary file with invalid JSON syntax."""
    p = tmp_path / "invalid_syntax.json"
    p.write_text("{customModes: [}", encoding='utf-8') # Malformed JSON
    return p

@pytest.fixture
def non_list_custommodes_json_file(tmp_path):
    """Creates a temporary JSON file where 'customModes' is not a list."""
    p = tmp_path / "non_list_custommodes.json"
    p.write_text(json.dumps({"customModes": {"slug": "not-a-list"}}, indent=2), encoding='utf-8')
    return p


# --- Tests for load_configs ---

def test_load_configs_file_not_found(tmp_path):
    """Test load_configs when the JSON file does not exist."""
    non_existent_path = tmp_path / "non_existent.json"
    configs = load_configs(non_existent_path)
    assert configs == []

def test_load_configs_success(valid_json_file, sample_configs):
    """Test successful loading and parsing of valid configurations."""
    loaded_configs = load_configs(valid_json_file)
    # Sort both lists by slug for comparison as order isn't guaranteed by load
    loaded_configs.sort(key=lambda x: x.slug)
    sample_configs.sort(key=lambda x: x.slug)
    assert loaded_configs == sample_configs

def test_load_configs_invalid_structure(invalid_structure_json_file):
    """Test load_configs with JSON lacking the 'customModes' top-level key."""
    with pytest.raises(ValueError, match="structure is invalid"):
        load_configs(invalid_structure_json_file)

def test_load_configs_custommodes_not_list(non_list_custommodes_json_file):
    """Test load_configs when 'customModes' is not a list."""
    with pytest.raises(ValueError, match="'customModes' .* is not a list"):
        load_configs(non_list_custommodes_json_file)

def test_load_configs_invalid_data(invalid_data_json_file):
    """Test load_configs with data that fails AgentConfig validation."""
    with pytest.raises(ValueError, match="Data validation failed"):
        load_configs(invalid_data_json_file)

def test_load_configs_invalid_json_syntax(invalid_json_syntax_file):
    """Test load_configs with a file containing invalid JSON syntax."""
    with pytest.raises(ValueError, match="Invalid JSON format"):
        load_configs(invalid_json_syntax_file)

# --- Tests for save_configs ---

def test_save_configs_success(tmp_path, sample_configs, valid_json_content):
    """Test successful saving of configurations to a JSON file."""
    save_path = tmp_path / "output_config.json"
    save_configs(save_path, sample_configs)

    assert save_path.is_file()
    saved_content = save_path.read_text(encoding='utf-8')
    # Load the expected and actual content to compare data structures
    # This avoids issues with potential minor formatting differences if any
    expected_data = json.loads(valid_json_content)
    actual_data = json.loads(saved_content)

    # Compare the core data ('customModes' list)
    assert actual_data.get("customModes") == expected_data.get("customModes")
    # Check sorting within the saved file
    assert [item['slug'] for item in actual_data.get("customModes", [])] == ['agent-a', 'agent-b']


def test_save_configs_creates_directory(tmp_path, sample_configs):
    """Test that save_configs creates the parent directory if it doesn't exist."""
    save_dir = tmp_path / "new_dir"
    save_path = save_dir / "output_config.json"

    assert not save_dir.exists()
    save_configs(save_path, sample_configs)
    assert save_dir.exists()
    assert save_path.is_file()

def test_save_configs_empty_list(tmp_path):
    """Test saving an empty list of configurations."""
    save_path = tmp_path / "empty_config.json"
    save_configs(save_path, [])

    assert save_path.is_file()
    saved_content = save_path.read_text(encoding='utf-8')
    expected_data = {"customModes": []}
    actual_data = json.loads(saved_content)
    assert actual_data == expected_data