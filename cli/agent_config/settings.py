# cli/agent_config/settings.py
import json
import logging
from pathlib import Path
import os # Added import
from typing import List, Dict, Any
import yaml

from pydantic import ValidationError
from .models import AgentConfig

# Get a logger for this module
logger = logging.getLogger(__name__)

# Define the default path to the CLI configuration file relative to the project root
DEFAULT_CLI_CONFIG_PATH = Path("cli/config.yaml").resolve()
# Allow overriding via environment variable for testing
CLI_CONFIG_ENV_VAR = "AGENT_CLI_CONFIG_PATH"

def load_cli_config() -> Dict[str, Any]:
    """
    Loads the CLI's operational configuration.
    Uses AGENT_CLI_CONFIG_PATH environment variable if set, otherwise defaults to cli/config.yaml.
    """
    config_path_str = os.environ.get(CLI_CONFIG_ENV_VAR)
    if config_path_str:
        config_path = Path(config_path_str).resolve()
        logger.info(f"Using CLI config path from environment variable {CLI_CONFIG_ENV_VAR}: {config_path}")
    else:
        config_path = DEFAULT_CLI_CONFIG_PATH
        logger.info(f"Using default CLI config path: {config_path}")

    logger.debug(f"Entering load_cli_config, attempting to load from: {config_path}")
    if not config_path.is_file():
        logger.error(f"CLI configuration file not found at {config_path}.")
        raise FileNotFoundError(f"CLI configuration file not found: {config_path}")
    try:
        logger.info(f"Loading CLI configuration from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        if not isinstance(config_data, dict):
            logger.error(f"Invalid format: CLI config file {config_path} did not parse as a dictionary.")
            raise TypeError(f"CLI configuration ({config_path}) is not a valid dictionary.")
        logger.info("Successfully loaded CLI configuration.")
        logger.debug(f"CLI Config content: {config_data}")
        logger.debug("Exiting load_cli_config (success)")
        return config_data
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {config_path}: {e}")
        raise ValueError(f"Invalid YAML format in {config_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading CLI config from {config_path}: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load CLI configuration from {config_path}: {e}")


def load_configs(json_path: Path) -> List[AgentConfig]:
    """Loads agent configurations from the JSON file."""
    logger.debug(f"Entering load_configs with json_path='{json_path}'")
    if not json_path.is_file():
        logger.warning(f"Target JSON file not found at {json_path}. Returning empty list.")
        logger.debug("Exiting load_configs (file not found)")
        return []
    try:
        logger.info(f"Loading configurations from: {json_path}")
        logger.debug(f"Opening file for reading: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded raw JSON data.")
        # Expect a dictionary with a 'customModes' key containing the list
        if not isinstance(data, dict) or "customModes" not in data:
            logger.error(f"Invalid format: Target JSON file {json_path} does not contain a top-level 'customModes' key.")
            raise TypeError(f"Target JSON ({json_path}) structure is invalid. Expected {{'customModes': [...]}}.")
        if not isinstance(data["customModes"], list):
             logger.error(f"Invalid format: 'customModes' key in {json_path} does not contain a list.")
             raise TypeError(f"'customModes' in {json_path} is not a list.")
        logger.debug(f"Attempting to parse {len(data['customModes'])} items into AgentConfig models.")
        configs = [AgentConfig.parse_obj(item) for item in data["customModes"]]
        logger.info(f"Successfully loaded and validated {len(configs)} configurations.")
        logger.debug("Exiting load_configs (success)")
        return configs
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error in {json_path}: {e}")
        raise ValueError(f"Invalid JSON format in {json_path}: {e}")
    except ValidationError as e:
        logger.error(f"Data validation error parsing {json_path}: {e}")
        raise ValueError(f"Data validation failed for {json_path}: {e}")
    except TypeError as e: # Catch potential issues if data is not list of dicts before parse_obj
         logger.error(f"Type error during config loading from {json_path}: {e}")
         raise ValueError(f"Incorrect data structure in {json_path}: {e}")


def save_configs(json_path: Path, configs: List[AgentConfig]):
    """Saves agent configurations to the JSON file."""
    logger.debug(f"Entering save_configs with json_path='{json_path}' and {len(configs)} configs")
    try:
        logger.info(f"Saving {len(configs)} configurations to: {json_path}")
        # Ensure parent directory exists
        logger.debug(f"Ensuring parent directory exists: {json_path.parent}")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        # Convert Pydantic models to dicts for JSON serialization, respecting aliases
        logger.debug("Converting AgentConfig models to dictionaries for JSON serialization.")
        config_dicts = sorted( # Sort by slug for consistency
            [config.dict(by_alias=True, exclude_none=True) for config in configs],
            key=lambda x: x.get('slug', '')
        )
        logger.debug(f"Prepared {len(config_dicts)} dictionaries for saving.")
        logger.debug(f"Opening file for writing: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            # Wrap the list in the expected top-level structure
            logger.debug("Wrapping config list in {'customModes': ...} structure.")
            output_data = {"customModes": config_dicts}
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved configurations to {json_path}")
        logger.debug("Exiting save_configs (success)")
    except IOError as e:
        logger.error(f"IOError writing to JSON file {json_path}: {e}")
        raise IOError(f"Error writing to JSON file {json_path}: {e}")
    except Exception as e:
        # Log the full traceback for unexpected errors during save
        logger.exception(f"An unexpected error occurred during saving to {json_path}")
        raise RuntimeError(f"An unexpected error occurred during saving: {e}")