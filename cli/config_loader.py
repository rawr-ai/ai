# cli/config_loader.py

import yaml
from pathlib import Path
from typing import Any, Dict

import pydantic

# Assuming models are defined in cli.models as reviewed
from cli.models import GlobalAgentConfig

# Define custom exceptions for better error context
class ConfigLoadError(Exception):
    """Custom exception for errors during YAML loading or parsing."""
    pass

class ConfigValidationError(Exception):
    """Custom exception for errors during Pydantic validation."""
    pass

def load_and_validate_config(file_path: Path) -> GlobalAgentConfig:
    """
    Loads a YAML configuration file from the given path, parses it,
    and validates it against the GlobalAgentConfig Pydantic model.

    Args:
        file_path: The Path object pointing to the configuration file.

    Returns:
        A validated GlobalAgentConfig instance.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        PermissionError: If there are permissions issues reading the file.
        ConfigLoadError: If the file content is not valid YAML.
        ConfigValidationError: If the YAML content does not match the
                               GlobalAgentConfig schema.
        OSError: For other file system related errors during reading.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        with file_path.open('r', encoding='utf-8') as f:
            raw_config_data = f.read()
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading file: {file_path}") from e
    except OSError as e:
        # Catch other potential OS errors during file read
        raise OSError(f"Error reading file: {file_path}") from e

    try:
        config_data: Dict[str, Any] = yaml.safe_load(raw_config_data)
        if config_data is None:
             # Handle empty YAML file case
             raise ConfigLoadError(f"YAML file is empty or contains only comments: {file_path}")
    except yaml.YAMLError as e:
        raise ConfigLoadError(f"Error parsing YAML file: {file_path}\nDetails: {e}") from e

    try:
        validated_config = GlobalAgentConfig.parse_obj(config_data)
        return validated_config
    except pydantic.ValidationError as e:
        raise ConfigValidationError(f"Configuration validation failed for file: {file_path}\nDetails:\n{e}") from e