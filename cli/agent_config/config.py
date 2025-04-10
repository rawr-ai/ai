# scripts/agent_config_manager/config.py
import json
import logging
from pathlib import Path
from typing import List

from pydantic import ValidationError
from .models import AgentConfig

# Get a logger for this module
logger = logging.getLogger(__name__)

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