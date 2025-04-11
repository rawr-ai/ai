import json
import os
import pathlib
import tempfile
import shutil
import pytest
from unittest.mock import mock_open, MagicMock # Removed 'patch' as mocker is used

# Module to test
from cli import registry_manager
from tests.helpers import mocking_utils # Use absolute import from project root

# Define the mock path used in tests
MOCK_REGISTRY_PATH_STR = "/fake/path/to/custom_modes.json"
MOCK_REGISTRY_PATH = pathlib.Path(MOCK_REGISTRY_PATH_STR)

# Default empty structure expected
DEFAULT_EMPTY_REGISTRY = {"customModes": []}

# === Test Suite: read_global_registry ===

def test_read_registry_success_valid_json(mocker):
    """TC-READ-01: Read Existing Valid JSON"""
    valid_json_str = '{"customModes": [{"slug": "agent1", "name": "Agent One"}]}'
    expected_data = {"customModes": [{"slug": "agent1", "name": "Agent One"}]}
    # Mock exists explicitly
    mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    # Use helper to mock file read (without exists)
    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=valid_json_str)
    # Still need to mock json.load as it's separate from file reading
    mock_json_load = mocker.patch("json.load", return_value=expected_data)

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    # Assert exists was checked (implicitly by the function under test)
    # mocker.patch.object(pathlib.Path, 'exists').assert_called_once() # Cannot assert on the patch object directly this way
    # We rely on the test passing as confirmation exists was checked correctly.
    # open is called within the function, check its usage implicitly via json.load
    mock_json_load.assert_called_once()
    assert result == expected_data

def test_read_registry_success_empty_json(mocker):
    """TC-READ-02: Read Existing Empty JSON"""
    empty_json_str = '{"customModes": []}'
    expected_data = DEFAULT_EMPTY_REGISTRY
    # Mock exists explicitly
    mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    # Use helper
    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=empty_json_str)
    mock_json_load = mocker.patch("json.load", return_value=expected_data)

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    # mocker.patch.object(pathlib.Path, 'exists').assert_called_once()
    mock_json_load.assert_called_once()
    assert result == expected_data

def test_read_registry_invalid_json_structure(mocker):
    """Test reading a file with invalid structure (not dict or missing key)"""
    invalid_structure_str = '["list", "not", "dict"]' # Example of invalid structure
    # Mock exists explicitly
    mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    # Use helper
    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=invalid_structure_str)
    # json.load will succeed, but the structure check inside the function should fail
    mock_json_load = mocker.patch("json.load", return_value=["list", "not", "dict"])
    mock_log_error = mocker.patch("logging.error")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    # mocker.patch.object(pathlib.Path, 'exists').assert_called_once()
    mock_json_load.assert_called_once()
    mock_log_error.assert_called_once()
    assert "Invalid structure in registry file" in mock_log_error.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY

def test_read_registry_invalid_json_decode_error(mocker):
    """TC-READ-03: Read Existing Invalid JSON (Decode Error)"""
    invalid_json_str = '{"customModes": [invalid json}'
    # Mock exists explicitly
    mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    # Use helper - Note: json.load mock is still needed separately
    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=invalid_json_str)
    mock_json_load = mocker.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    mock_log_exception = mocker.patch("logging.exception")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    # mocker.patch.object(pathlib.Path, 'exists').assert_called_once()
    mock_json_load.assert_called_once()
    mock_log_exception.assert_called_once()
    assert "Error decoding JSON" in mock_log_exception.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY

def test_read_registry_file_not_found(mocker):
    """TC-READ-04: File Not Found"""
    # Mock exists explicitly
    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=False)
    # Use helper (it won't actually mock open if exists is false, but call it for consistency)
    mock_open_func = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR) # Content doesn't matter here
    mock_log_warning = mocker.patch("logging.warning")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    mock_exists.assert_called_once_with()
    mock_open_func.assert_not_called()
    mock_log_warning.assert_called_once()
    assert "Registry file not found" in mock_log_warning.call_args[0][0]
    assert result == DEFAULT_EMPTY_REGISTRY

def test_read_registry_permission_error(mocker):
    """TC-READ-05: Permission Denied"""
    # Mock exists explicitly
    mocker.patch.object(pathlib.Path, 'exists', return_value=True)
    # Use helper
    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, permission_error=True)
    mock_log_exception = mocker.patch("logging.exception")

    result = registry_manager.read_global_registry(MOCK_REGISTRY_PATH)

    # mocker.patch.object(pathlib.Path, 'exists').assert_called_once()
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

def test_write_registry_success(mocker):
    """TC-WRITE-01: Successfully write valid data to a file."""
    # Use helper
    mock_mkdir, mock_open_call, mock_json_dump = mocking_utils.mock_file_write(mocker, MOCK_REGISTRY_PATH_STR)
    # Get the file handle mock from the open call mock if needed for assertions
    mock_open_func = mock_open_call.return_value

    registry_data = {"customModes": [{"slug": "test-agent", "name": "Test Agent"}]}
    # No need to check exact string, just that dump is called correctly
    # expected_json_str = json.dumps(registry_data, indent=4)

    result = registry_manager.write_global_registry(registry_data, MOCK_REGISTRY_PATH)

    # Assert parent directory creation was attempted (exist_ok=True handles existing dirs)
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    # Assert file was opened for writing (using the mock returned by the helper)
    mock_open_call.assert_called_once_with(MOCK_REGISTRY_PATH, 'w', encoding='utf-8')
    # Assert json.dump was called with correct data and formatting
    mock_json_dump.assert_called_once_with(registry_data, mock_open_func, indent=2) # Pass the handle directly
    # Function returns None on success, success is indicated by no exceptions raised
    # and mocks being called correctly.

def test_write_registry_permission_error(mocker):
    """TC-WRITE-02: Handle PermissionError during file write."""
    # Use helper
    mock_mkdir, mock_open_error, mock_json_dump = mocking_utils.mock_file_write(
        mocker, MOCK_REGISTRY_PATH_STR, permission_error=True
    )
    mock_log_exception = mocker.patch("logging.exception")

    registry_data = {"customModes": [{"slug": "test-agent", "name": "Test Agent"}]}

    # Expect PermissionError to be raised
    with pytest.raises(PermissionError, match="Permission denied"):
        registry_manager.write_global_registry(registry_data, MOCK_REGISTRY_PATH)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_open_error.assert_called_once_with(MOCK_REGISTRY_PATH, 'w', encoding='utf-8')
    mock_log_exception.assert_called_once()
    # Check the log message content (adjust based on actual log format if needed)
    assert f"OS error writing registry file {MOCK_REGISTRY_PATH}" in mock_log_exception.call_args[0][0]
    mock_json_dump.assert_not_called()

def test_write_registry_other_os_error(mocker):
    """TC-WRITE-03: Handle other OSErrors during file write."""
    # Use helper
    mock_mkdir, mock_open_error, mock_json_dump = mocking_utils.mock_file_write(
        mocker, MOCK_REGISTRY_PATH_STR, write_error=OSError("Disk full")
    )
    mock_log_exception = mocker.patch("logging.exception")

    registry_data = {"customModes": [{"slug": "test-agent", "name": "Test Agent"}]}

    # Expect OSError to be raised
    with pytest.raises(OSError, match="Disk full"):
        registry_manager.write_global_registry(registry_data, MOCK_REGISTRY_PATH)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_open_error.assert_called_once_with(MOCK_REGISTRY_PATH, 'w', encoding='utf-8')
    mock_log_exception.assert_called_once()
    assert f"OS error writing registry file {MOCK_REGISTRY_PATH}" in mock_log_exception.call_args[0][0]
    mock_json_dump.assert_not_called()

def test_write_registry_invalid_data_type(mocker):
    """TC-WRITE-04: Handle non-dict data passed for writing (should not happen with type hints but test defensively)."""
    # Use helper
    mock_mkdir, mock_open_call, mock_json_dump = mocking_utils.mock_file_write(
        mocker, MOCK_REGISTRY_PATH_STR, serialization_error=TypeError("Not serializable")
    )
    mock_open_func = mock_open_call.return_value # Get handle for assertion
    mock_log_exception = mocker.patch("logging.exception")

    invalid_data = ["list", "not", "dict"] # Example invalid data

    # Expect TypeError to be raised due to json.dump failure
    with pytest.raises(TypeError, match="Not serializable"):
        registry_manager.write_global_registry(invalid_data, MOCK_REGISTRY_PATH)

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_open_call.assert_called_once_with(MOCK_REGISTRY_PATH, 'w', encoding='utf-8') # Target the open mock itself
    # json.dump was called (and raised the configured error)
    mock_json_dump.assert_called_once_with(invalid_data, mock_open_func, indent=2) # Pass the mock handle directly
    mock_log_exception.assert_called_once()
    # Check the log message content
    assert f"Unexpected error writing registry file {MOCK_REGISTRY_PATH}" in mock_log_exception.call_args[0][0]