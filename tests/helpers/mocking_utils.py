import pathlib
from unittest.mock import mock_open, MagicMock

DEFAULT_ENCODING = 'utf-8'

def mock_file_read(mocker, file_path_str: str, content: str = "", read_error: Exception = None, permission_error: bool = False):
    """
    Mocks pathlib.Path.exists and builtins.open for reading a specific file.

    Args:
        mocker: The pytest-mock mocker fixture.
        file_path_str: The string representation of the file path to mock.
        content: The string content to return when the file is read. Defaults to empty string.
        # exists: (Removed) Whether the mocked file should appear to exist. Tests should mock Path.exists directly if needed.
        read_error: An exception instance to raise during open/read (e.g., json.JSONDecodeError).
                    Takes precedence over permission_error if both are set.
        permission_error: If True and read_error is None, raise PermissionError on open.
    """
    # Note: Mocking Path.exists is removed from this helper.
    # Tests requiring specific existence behavior should mock
    # pathlib.Path(file_path_str).exists() directly.
    file_path = pathlib.Path(file_path_str) # Still useful for error messages potentially
    # The line below was erroneously left from previous refactoring attempt and caused NameError
    # mock_exists.side_effect = lambda p: p == file_path if exists else False

    # Mock open based on error conditions or success
    if read_error:
        # Raise a specific error during read (simulates issues like decode errors)
        # Note: This mocks the open call itself raising the error.
        # If the error should happen *during* read(), mock_open().read.side_effect might be needed.
        # For simplicity here, we raise on open.
        mock_open_func = mocker.patch("builtins.open", side_effect=read_error)
    elif permission_error:
        # Raise PermissionError on open
        mock_open_func = mocker.patch("builtins.open", side_effect=PermissionError(f"Permission denied: {file_path_str}"))
    else:
        # Mock successful open and read
        mock_open_func = mocker.patch("builtins.open", mock_open(read_data=content))

    # Return the mock for the open call
    return mock_open_func

# Example Usage (in a test):
# def test_something(mocker):
#     mock_open_call = mock_file_read(mocker, "/fake/my_config.txt", content="data")
#     # ... call function under test ...
#     # ... assertions ...

# def test_file_not_found(mocker): # Test needs to mock Path.exists itself now
#     mocker.patch.object(pathlib.Path, 'exists', return_value=False)
#     # ... call function under test ...
#     # ... assert FileNotFoundError or appropriate handling ...

# def test_permission_denied(mocker): # Test might need to mock Path.exists = True
#     mocker.patch.object(pathlib.Path, 'exists', return_value=True)
#     mock_file_read(mocker, "/fake/protected.txt", permission_error=True)
#     # ... call function under test ...
#     # ... assert PermissionError or appropriate handling ...


def mock_file_write(mocker, file_path_str: str, write_error: Exception = None, permission_error: bool = False, serialization_error: Exception = None):
    """
    Mocks pathlib.Path.mkdir, builtins.open, and json.dump (if applicable) for writing a file.

    Args:
        mocker: The pytest-mock mocker fixture.
        file_path_str: The string representation of the file path to mock.
        write_error: An OS-level exception instance to raise during open (e.g., OSError).
                     Takes precedence over permission_error.
        permission_error: If True and write_error is None, raise PermissionError on open.
        serialization_error: An exception to raise during json.dump (e.g., TypeError).
    """
    file_path = pathlib.Path(file_path_str)

    # Mock directory creation
    mock_mkdir = mocker.patch.object(pathlib.Path, 'mkdir')

    # Mock open for writing
    mock_open_func = mock_open() # Default mock
    if write_error:
        mock_open_call = mocker.patch("builtins.open", side_effect=write_error)
    elif permission_error:
        mock_open_call = mocker.patch("builtins.open", side_effect=PermissionError(f"Permission denied: {file_path_str}"))
    else:
        # Mock successful open
        mock_open_call = mocker.patch("builtins.open", mock_open_func)

    # Mock json.dump (optional, based on serialization_error)
    mock_json_dump = None
    if serialization_error:
        mock_json_dump = mocker.patch("json.dump", side_effect=serialization_error)
    else:
        # Mock successful json.dump if no error specified
        mock_json_dump = mocker.patch("json.dump")

    # Return mocks for potential assertions
    return mock_mkdir, mock_open_call, mock_json_dump

# Example Usage (in a test):
# def test_write_success(mocker):
#     _, mock_open_call, mock_json_dump = mock_file_write(mocker, "/fake/output.json")
#     # ... call function under test ...
#     mock_open_call.assert_called_once_with(pathlib.Path("/fake/output.json"), 'w', encoding='utf-8')
#     mock_json_dump.assert_called_once()

# def test_write_permission_error(mocker):
#     mock_file_write(mocker, "/fake/protected.json", permission_error=True)
#     # ... call function under test ...
#     # ... assert PermissionError or appropriate handling ...

# def test_write_serialization_error(mocker):
#     mock_file_write(mocker, "/fake/bad_data.json", serialization_error=TypeError("Cannot serialize"))
#     # ... call function under test ...
#     # ... assert TypeError or appropriate handling ...
