# Mocking Usage Report

This report consolidates the usage of `mocker.patch` and the `tests.helpers.mocking_utils` module within the `tests/` directory.

## `mocker.patch` Occurrences

### tests/helpers/mocking_utils.py
- Line 32: `        mock_open_func = mocker.patch("builtins.open", side_effect=read_error)`
- Line 35: `        mock_open_func = mocker.patch("builtins.open", side_effect=PermissionError(f"Permission denied: {file_path_str}"))`
- Line 38: `        mock_open_func = mocker.patch("builtins.open", mock_open(read_data=content))`
- Line 50: `    # mocker.patch.object(pathlib.Path, 'exists', return_value=False)`
- Line 55: `    # mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
- Line 76: `    mock_mkdir = mocker.patch.object(pathlib.Path, 'mkdir')`
- Line 81: `        mock_open_call = mocker.patch("builtins.open", side_effect=write_error)`
- Line 83: `        mock_open_call = mocker.patch("builtins.open", side_effect=PermissionError(f"Permission denied: {file_path_str}"))`
- Line 86: `        mock_open_call = mocker.patch("builtins.open", mock_open_func)`
- Line 91: `        mock_json_dump = mocker.patch("json.dump", side_effect=serialization_error)`
- Line 94: `        mock_json_dump = mocker.patch("json.dump")`

### tests/integration/test_compile_command.py
- Line 87: `    mocker.patch('cli.main.AGENT_CONFIG_DIR', agents_base_dir)`
- Line 88: `    mocker.patch('cli.main.GLOBAL_REGISTRY_PATH', mock_registry_path)`
- Line 289: `    mock_read = mocker.patch('cli.registry_manager.read_global_registry', side_effect=OSError(MSG_ERR_PERMISSION_READ))`
- Line 315: `    mock_write = mocker.patch('cli.registry_manager.write_global_registry', side_effect=OSError(MSG_ERR_DISK_FULL_WRITE))`

### tests/unit/test_registry_manager.py
- Line 27: `    mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
- Line 31: `    mock_json_load = mocker.patch("json.load", return_value=expected_data)`
- Line 47: `    mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
- Line 50: `    mock_json_load = mocker.patch("json.load", return_value=expected_data)`
- Line 62: `    mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
- Line 66: `    mock_json_load = mocker.patch("json.load", return_value=["list", "not", "dict"])`
- Line 67: `    mock_log_error = mocker.patch("logging.error")`
- Line 81: `    mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
- Line 84: `    mock_json_load = mocker.patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0))`
- Line 85: `    mock_log_exception = mocker.patch("logging.exception")`
- Line 98: `    mock_exists = mocker.patch.object(pathlib.Path, 'exists', return_value=False)`
- Line 100: `    mock_open_func = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR) # Content doesn't matter here`
- Line 101: `    mock_log_warning = mocker.patch("logging.warning")`
- Line 114: `    mocker.patch.object(pathlib.Path, 'exists', return_value=True)`
- Line 116: `    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, permission_error=True)`
- Line 117: `    mock_log_exception = mocker.patch("logging.exception")`
- Line 225: `    mock_log_error = mocker.patch("logging.error")`
- Line 240: `    mock_log_error = mocker.patch("logging.error")`
- Line 281: `    mock_log_exception = mocker.patch("logging.exception")`
- Line 302: `    mock_log_exception = mocker.patch("logging.exception")`
- Line 323: `    mock_log_exception = mocker.patch("logging.exception")`

## `mocking_utils` Usage (Import or Direct Call)

### tests/unit/test_registry_manager.py
- Line 11: `from tests.helpers import mocking_utils # Use absolute import from project root`
- Line 29: `    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=valid_json_str)`
- Line 49: `    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=empty_json_str)`
- Line 64: `    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=invalid_structure_str)`
- Line 83: `    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, content=invalid_json_str)`
- Line 100: `    mock_open_func = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR) # Content doesn't matter here`
- Line 116: `    _ = mocking_utils.mock_file_read(mocker, MOCK_REGISTRY_PATH_STR, permission_error=True)`
- Line 256: `    mock_mkdir, mock_open_call, mock_json_dump = mocking_utils.mock_file_write(mocker, MOCK_REGISTRY_PATH_STR)`
- Line 278: `    mock_mkdir, mock_open_error, mock_json_dump = mocking_utils.mock_file_write(`
- Line 299: `    mock_mkdir, mock_open_error, mock_json_dump = mocking_utils.mock_file_write(`
- Line 319: `    mock_mkdir, mock_open_call, mock_json_dump = mocking_utils.mock_file_write(`