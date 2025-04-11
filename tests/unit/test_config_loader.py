import pytest
import yaml
from pydantic import ValidationError
from unittest.mock import mock_open, MagicMock
import os
from pathlib import Path

# Assuming the models are in cli.models and the loader in cli.config_loader
# Adjust the import path if necessary based on the project structure
from cli.models import GlobalAgentConfig, ApiConfig, GroupRestriction
from cli.config_loader import load_and_validate_config, ConfigLoadError, ConfigValidationError

# --- Test Data ---

MINIMAL_VALID_YAML = """
slug: test-agent
name: Test Agent
roleDefinition: This is a test agent.
groups:
  - group1
  - group2
"""

FULL_VALID_YAML = """
slug: full-agent
name: Full Agent
roleDefinition: A comprehensive test agent.
apiConfiguration:
  model: gpt-4
  # temperature: 0.7 # Removed - Not in ApiConfig model
  # max_tokens: 1000 # Removed - Not in ApiConfig model
  url: http://api.example.com
  # params: {"example": "value"} # Example optional params if needed
groups:
  - admin
  - ["dev", {"fileRegex": "\\\\.py$", "description": "Python files only"}]
  - ["qa", {"fileRegex": ".*", "description": "QA access"}] # Added required fileRegex
"""

GROUPS_WITH_RESTRICTIONS_YAML = """
slug: restricted-agent
name: Restricted Agent
roleDefinition: Agent with group restrictions.
groups:
  - users
  - ["editors", {"fileRegex": "\\\\.md$"}]
  - ["admins", {"fileRegex": ".*", "description": "Full access"}]
"""

INVALID_YAML_SYNTAX = """
slug: bad-syntax
name: Bad Syntax Agent
  roleDefinition: Indentation error here.
groups:
  - fail
"""

NOT_YAML_CONTENT = """
{ "json": "not yaml" }
"""

MISSING_REQUIRED_FIELD_YAML = """
name: Missing Slug Agent
roleDefinition: This agent is missing its slug.
groups:
  - missing
"""

INCORRECT_DATA_TYPE_YAML = """
slug: 12345
name: Wrong Type Agent
roleDefinition: Slug should be a string.
groups:
  - type-error
"""

INVALID_NESTED_MODEL_YAML = """
slug: nested-error-agent
name: Nested Error Agent
roleDefinition: API config is missing 'model'.
apiConfiguration:
  temperature: 0.5
groups:
  - nested
"""

INVALID_URL_YAML = """
slug: bad-url-agent
name: Bad URL Agent
roleDefinition: API URL is invalid.
apiConfiguration:
  model: gpt-3
  url: not-a-valid-url
groups:
  - url-error
"""

EXTRA_FIELD_YAML = """
slug: extra-field-agent
name: Extra Field Agent
roleDefinition: Contains an undefined field.
extraField: "someValue"
groups:
  - extra
"""

INVALID_GROUP_RESTRICTION_YAML = """
slug: bad-group-agent
name: Bad Group Agent
roleDefinition: Invalid key in group restriction.
groups:
  - ["group1", {"invalidKey": "value"}]
"""

# --- Test Suites ---

# Suite: Happy Path & Basic Validation

def test_load_minimal_valid_config(mocker):
    """LOADER_UT_001: Verify successful loading of minimal valid config."""
    mocker.patch("pathlib.Path.is_file", return_value=True) # Mock file existence check
    mocker.patch("pathlib.Path.open", mock_open(read_data=MINIMAL_VALID_YAML)) # Use mock_open
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(MINIMAL_VALID_YAML)) # Remove safe_load mock
    # mocker.patch("os.path.exists", return_value=True) # Replaced with pathlib mock
    config = load_and_validate_config(Path("mock_path/config.yaml")) # Pass a real Path object
    assert isinstance(config, GlobalAgentConfig)
    assert config.slug == "test-agent"
    assert config.name == "Test Agent"
    assert config.roleDefinition == "This is a test agent."
    assert config.groups == ["group1", "group2"]
    assert config.apiConfiguration is None

def test_load_full_valid_config(mocker):
    """LOADER_UT_002: Verify successful loading with all optional fields."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=FULL_VALID_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(FULL_VALID_YAML))
    config = load_and_validate_config(Path("mock_path/config.yaml"))
    assert isinstance(config, GlobalAgentConfig)
    assert config.slug == "full-agent"
    assert config.apiConfiguration is not None
    assert isinstance(config.apiConfiguration, ApiConfig)
    assert config.apiConfiguration.model == "gpt-4"
    # assert config.apiConfiguration.temperature == 0.7 # Field removed from model/YAML
    # assert config.apiConfiguration.max_tokens == 1000 # Field removed from model/YAML
    assert str(config.apiConfiguration.url) == "http://api.example.com/" # Pydantic adds trailing slash
    assert len(config.groups) == 3
    assert config.groups[0] == "admin"
    assert isinstance(config.groups[1], tuple)
    assert config.groups[1][0] == "dev"
    assert isinstance(config.groups[1][1], GroupRestriction)
    assert config.groups[1][1].fileRegex == "\\.py$" # YAML loads \\ as \
    assert config.groups[1][1].description == "Python files only"
    assert isinstance(config.groups[2], tuple)
    assert config.groups[2][0] == "qa"
    assert isinstance(config.groups[2][1], GroupRestriction)
    assert config.groups[2][1].fileRegex == ".*" # Check for the added regex
    assert config.groups[2][1].description == "QA access"


def test_load_groups_with_restrictions(mocker):
    """LOADER_UT_003: Verify successful loading with groups containing restrictions."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=GROUPS_WITH_RESTRICTIONS_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(GROUPS_WITH_RESTRICTIONS_YAML))
    # mocker.patch("os.path.exists", return_value=True) # Replaced with pathlib mock
    config = load_and_validate_config(Path("mock_path/config.yaml")) # Pass a real Path object
    assert isinstance(config, GlobalAgentConfig)
    assert config.slug == "restricted-agent"
    assert len(config.groups) == 3
    assert config.groups[0] == "users"
    assert isinstance(config.groups[1], tuple)
    assert config.groups[1][0] == "editors"
    assert isinstance(config.groups[1][1], GroupRestriction)
    assert config.groups[1][1].fileRegex == "\\.md$" # YAML loads \\ as \
    assert config.groups[1][1].description is None
    assert isinstance(config.groups[2], tuple)
    assert config.groups[2][0] == "admins"
    assert isinstance(config.groups[2][1], GroupRestriction)
    assert config.groups[2][1].fileRegex == ".*"
    assert config.groups[2][1].description == "Full access"

# Suite: YAML Parsing Errors

def test_load_invalid_yaml_syntax(mocker):
    """LOADER_UT_101: Verify handling of invalid YAML syntax."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    # Use mock_open for the file read
    mocker.patch("pathlib.Path.open", mock_open(read_data=INVALID_YAML_SYNTAX))
    # mocker.patch("yaml.safe_load", side_effect=yaml.YAMLError("Syntax Error")) # Remove safe_load mock
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigLoadError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

def test_load_non_yaml_content(mocker):
    """LOADER_UT_102: Verify handling of non-YAML file content."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=NOT_YAML_CONTENT))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(NOT_YAML_CONTENT)) # Remove safe_load mock
    # mocker.patch("os.path.exists", return_value=True)
    # Expect ConfigValidationError because Pydantic validation will fail
    with pytest.raises(ConfigValidationError):
         load_and_validate_config(Path("mock_path/config.yaml"))

# Suite: Pydantic Schema Validation Errors

def test_load_missing_required_field(mocker):
    """LOADER_UT_201: Verify handling of missing required fields."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=MISSING_REQUIRED_FIELD_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(MISSING_REQUIRED_FIELD_YAML))
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigValidationError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

def test_load_incorrect_data_type(mocker):
    """LOADER_UT_202: Verify handling of incorrect data types."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=INCORRECT_DATA_TYPE_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(INCORRECT_DATA_TYPE_YAML))
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigValidationError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

def test_load_invalid_nested_model(mocker):
    """LOADER_UT_203: Verify handling of invalid nested model data."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=INVALID_NESTED_MODEL_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(INVALID_NESTED_MODEL_YAML))
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigValidationError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

def test_load_invalid_url(mocker):
    """LOADER_UT_204: Verify handling of invalid URL format."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=INVALID_URL_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(INVALID_URL_YAML))
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigValidationError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

def test_load_extra_field(mocker):
    """LOADER_UT_205: Verify handling of extra fields when Extra.forbid is set."""
    # This assumes GlobalAgentConfig uses Extra.forbid (or equivalent in Pydantic v2+)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=EXTRA_FIELD_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(EXTRA_FIELD_YAML))
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigValidationError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

def test_load_invalid_group_restriction(mocker):
    """LOADER_UT_206: Verify handling of invalid structure within groups."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open", mock_open(read_data=INVALID_GROUP_RESTRICTION_YAML))
    # mocker.patch("yaml.safe_load", return_value=yaml.safe_load(INVALID_GROUP_RESTRICTION_YAML))
    # mocker.patch("os.path.exists", return_value=True)
    with pytest.raises(ConfigValidationError): # Expect custom exception
        load_and_validate_config(Path("mock_path/config.yaml"))

# Suite: File Handling Errors

def test_load_file_not_found(mocker):
    """LOADER_UT_301: Verify handling when the config file does not exist."""
    # Mock the is_file check directly on the Path class
    mocker.patch("pathlib.Path.is_file", return_value=False)
    with pytest.raises(FileNotFoundError):
        # Pass a real Path object, the mock will intercept the is_file call
        load_and_validate_config(Path("non_existent_path/config.yaml"))

def test_load_permission_error(mocker):
    """LOADER_UT_302: Verify handling when there are permission errors reading the file."""
    # Mock is_file to return True for this path
    mocker.patch("pathlib.Path.is_file", return_value=True)
    # Mock the open method on the Path class to raise PermissionError
    mocker.patch("pathlib.Path.open", side_effect=PermissionError("Permission denied"))

    with pytest.raises(PermissionError):
        # Pass a real Path object, the mock will intercept the open call
        load_and_validate_config(Path("permission_denied_path/config.yaml"))