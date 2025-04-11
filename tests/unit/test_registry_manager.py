import json
import os
import pathlib
import tempfile
import shutil
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Module to test
from cli import registry_manager

# Define the mock path used in tests
MOCK_REGISTRY_PATH_STR = "/fake/path/to/custom_modes.json"
MOCK_REGISTRY_PATH = pathlib.Path(MOCK_REGISTRY_PATH_STR)

# Default empty structure expected
DEFAULT_EMPTY_REGISTRY = {"customModes": []}

# === Test Suite: read_global_registry ===

def test_read_registry_success_valid_json(mocker):
    """TC-READ-01: Read Existing Valid JSON"""
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    valid_json_str = '{"customModes": [{"slug": "agent1", "name": "Agent One"}]}'
    expected_data = {"customModes": [{"slug": "agent1", "name": "Agent One"}]}
    # Mock open directly as it's used in the function
    mocker.patch("builtins.open", mock_open(read_data=valid_json_str))
    # Mock json.load as it's called after open
    mock_json_load = mocker.patch("json.load", return_value=expected_data)

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    # open is called within the function, check its usage implicitly via json.load
    mock_json_load.assert_called_once()
    assert result == expected_data

def test_read_registry_success_empty_json(mocker):
    """TC-READ-02: Read Existing Empty JSON"""
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    empty_json_str = '{"customModes": []}'
    expected_data = DEFAULT_EMPTY_REGISTRY
    mocker.patch("builtins.open", mock_open(read_data=empty_json_str))
    mock_json_load = mocker.patch("json.load", return_value=expected_data)

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    mock_json_load.assert_called_once()
    assert result == expected_data

def test_read_registry_invalid_json_structure(mocker):
    """Test reading a file with invalid structure (not dict or missing key)"""
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    invalid_structure_str = '["list", "not", "dict"]' # Example of invalid structure
    mocker.patch("builtins.open", mock_open(read_data=invalid_structure_str))
    # json.load will succeed, but the structure check inside the function should fail
    mock_json_load = mocker.patch("json.load", return_value=["list", "not", "dict"])
    mock_log_error = mocker.patch("logging.error")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    mock_json_load.assert_called_once()
    mock_log_error.assert_called_once()
    assert "Invalid structure in registry file" in mock_log_error.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY

def test_read_registry_invalid_json_decode_error(mocker):
    """TC-READ-03: Read Existing Invalid JSON (Decode Error)"""
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    invalid_json_str = '{"customModes": [invalid json}'
    mocker.patch("builtins.open", mock_open(read_data=invalid_json_str))
    mock_json_load = mocker.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    mock_log_exception = mocker.patch("logging.exception")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    mock_json_load.assert_called_once()
    mock_log_exception.assert_called_once()
    assert "Error decoding JSON" in mock_log_exception.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY

def test_read_registry_file_not_found(mocker):
    """TC-READ-04: File Not Found"""
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=False)
    mock_open_func = mocker.patch("builtins.open") # Should not be called
    mock_log_warning = mocker.patch("logging.warning")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    mock_open_func.assert_not_called()
    mock_log_warning.assert_called_once()
    assert "Registry file not found" in mock_log_warning.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY

def test_read_registry_permission_error(mocker):
    """TC-READ-05: Permission Denied"""
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    # Mock open to raise PermissionError
    mocker.patch("builtins.open", side_effect=PermissionError("Permission denied"))
    mock_log_exception = mocker.patch("logging.exception")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    mock_log_exception.assert_called_once()
    assert "OS error reading registry file" in mock_log_exception.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY # Function handles OS errors by returning default

# === Test Suite: update_global_registry ===

def test_update_registry_add_new_to_empty():
    """TC-UPDATE-01: Add New Agent to Empty Registry"""
    current_data = {"customModes": []}
    new_agent_metadata = {
        "slug": "new-agent",
        "name": "New Agent",
        "roleDefinition": "Role for new agent",
        "customInstructions": "SHOULD BE IGNORED"
    }
    expected_stored_metadata = {
        "slug": "new-agent",
        "name": "New Agent",
        "roleDefinition": "Role for new agent"
        # customInstructions is excluded
    }
    expected_data = {"customModes": [expected_stored_metadata]}

    result = registry_manager.update_global_registry(current_data, new_agent_metadata)

    assert result == expected_data
    assert len(result["customModes"]) == 1
    assert "customInstructions" not in result["customModes"][0]

def test_update_registry_add_new_to_existing():
    """TC-UPDATE-02: Add New Agent to Existing Registry"""
    current_data = {"customModes": [{"slug": "agent1", "name": "Agent One", "roleDefinition": "Role 1"}]}
    new_agent_metadata = {
        "slug": "new-agent",
        "name": "New Agent",
        "roleDefinition": "Role for new agent",
        "customInstructions": "SHOULD BE IGNORED"
    }
    expected_new_stored = {
        "slug": "new-agent",
        "name": "New Agent",
        "roleDefinition": "Role for new agent"
    }
    expected_data = {
        "customModes": [
            {"slug": "agent1", "name": "Agent One", "roleDefinition": "Role 1"},
            expected_new_stored
        ]
    }

    result = registry_manager.update_global_registry(current_data, new_agent_metadata)

    assert result == expected_data
    assert len(result["customModes"]) == 2
    assert "customInstructions" not in result["customModes"][1]

def test_update_registry_update_existing():
    """TC-UPDATE-03: Update Existing Agent"""
    current_data = {"customModes": [{"slug": "agent1", "name": "Agent One", "roleDefinition": "Old Role"}]}
    updated_agent_metadata = {
        "slug": "agent1",
        "name": "Agent One Updated",
        "roleDefinition": "New Role",
        "customInstructions": "SHOULD BE IGNORED"
    }
    expected_stored_metadata = {
        "slug": "agent1",
        "name": "Agent One Updated",
        "roleDefinition": "New Role"
    }
    expected_data = {"customModes": [expected_stored_metadata]}

    result = registry_manager.update_global_registry(current_data, updated_agent_metadata)

    assert result == expected_data
    assert len(result["customModes"]) == 1
    assert result["customModes"][0]["name"] == "Agent One Updated"
    assert result["customModes"][0]["roleDefinition"] == "New Role"
    assert "customInstructions" not in result["customModes"][0]

def test_update_registry_verify_custom_instructions_exclusion():
    """TC-UPDATE-04: Update Agent - Verify customInstructions Exclusion"""
    current_data = {"customModes": [{"slug": "agent1", "name": "Agent One"}]}
    agent_with_ci = {
        "slug": "agent1",
        "name": "Agent One",
        "roleDefinition": "Some role",
        "customInstructions": "This must not be written"
    }
    expected_stored_metadata = {
        "slug": "agent1",
        "name": "Agent One",
        "roleDefinition": "Some role"
    }
    expected_data = {"customModes": [expected_stored_metadata]}

    result = registry_manager.update_global_registry(current_data, agent_with_ci)

    assert result == expected_data
    assert "customInstructions" not in result["customModes"][0]

def test_update_registry_invalid_registry_data_input(mocker):
    """Test update with invalid initial registry data"""
    mock_log_error = mocker.patch("logging.error")
    invalid_data = ["not a dict"]
    agent_metadata = {"slug": "agent1", "name": "Agent One"}
    
    # Should initialize to default and add the agent
    expected_data = {"customModes": [{"slug": "agent1", "name": "Agent One"}]}

    result = registry_manager.update_global_registry(invalid_data, agent_metadata)

    mock_log_error.assert_called_once()
    assert "Invalid registry_data structure" in mock_log_error.call_args[0][0]
    assert result == expected_data

def test_update_registry_invalid_agent_metadata_input(mocker):
    """Test update with invalid agent metadata"""
    mock_log_error = mocker.patch("logging.error")
    current_data = {"customModes": []}
    invalid_agent_metadata = {"name": "No Slug"} # Missing slug
    
    # Should log error and return original data
    result = registry_manager.update_global_registry(current_data, invalid_agent_metadata)

    mock_log_error.assert_called_once()
    assert "Invalid agent_metadata passed" in mock_log_error.call_args[0][0]
    assert result == current_data # No change expected

# === Test Suite: write_global_registry ===
# NOTE: Tests related to the old safe-write mechanism (using tempfile and shutil.move)
# have been removed as the implementation now uses a direct write.
# New tests should be added to cover the current direct-write logic and error handling.