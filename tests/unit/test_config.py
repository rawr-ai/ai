import json
import pytest
from pathlib import Path
from pydantic import ValidationError
# Removed import: from cli.agent_config.settings import load_configs, save_configs # Updated path
# Removed import: from cli.agent_config.models import AgentConfig # Updated path

# --- Fixtures ---

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

# --- Tests for save_configs ---
