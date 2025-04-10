# scripts/agent_config_manager/commands.py
import logging
from pathlib import Path

from .settings import load_configs, save_configs
from .markdown_utils import parse_markdown
from .models import AgentConfig

# Get a logger for this module
logger = logging.getLogger(__name__)

# --- Core Operations ---
def add_config(markdown_path_str: str, target_json_path: Path, markdown_base_dir: Path):
    """Adds a new agent configuration from a Markdown file."""
    logger.debug(f"Entering add_config with markdown_path_str='{markdown_path_str}', target_json_path='{target_json_path}', markdown_base_dir='{markdown_base_dir}'")
    # --- Path Validation ---
    markdown_path = Path(markdown_path_str).resolve()
    markdown_base_dir_resolved = markdown_base_dir.resolve()
    if not str(markdown_path).startswith(str(markdown_base_dir_resolved)):
        logger.warning(
            f"Markdown file path '{markdown_path}' is not inside the configured markdown base directory '{markdown_base_dir_resolved}'. Ensure this is intended."
        )
        # Consider raising an error if strict containment is required:
        # raise ValueError(f"Markdown file path '{markdown_path}' must be inside '{markdown_base_dir_resolved}'.")

    # --- Add Operation Specific Check ---
    # For 'add', the target JSON file should ideally exist, but load_configs handles creation if not.
    # Let's ensure the directory exists though.
    logger.debug(f"Ensuring target directory exists: {target_json_path.parent}")
    target_json_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Attempting to add configuration from: {markdown_path}")
    logger.debug(f"Parsing markdown file: {markdown_path}")
    new_config = parse_markdown(markdown_path)
    logger.debug(f"Parsed config: slug='{new_config.slug}', name='{new_config.name}'")
    logger.debug(f"Loading existing configs from: {target_json_path}")
    configs = load_configs(target_json_path)
    logger.debug(f"Loaded {len(configs)} existing configs.")

    if any(config.slug == new_config.slug for config in configs):
        logger.error(f"Agent with slug '{new_config.slug}' already exists in {target_json_path}.")
        raise ValueError(f"Error: Agent with slug '{new_config.slug}' already exists in {target_json_path}.")

    configs.append(new_config)
    logger.debug(f"Appending new config for slug '{new_config.slug}'. Total configs will be {len(configs) + 1}.")
    # Removed duplicate append
    logger.debug(f"Saving {len(configs)} configs to: {target_json_path}")
    save_configs(target_json_path, configs)
    logger.info(f"Successfully added agent '{new_config.slug}'.")
    logger.debug("Exiting add_config")


def update_config(markdown_path_str: str, target_json_path: Path, markdown_base_dir: Path, preserve_groups: bool):
    """Updates an existing agent configuration from a Markdown file."""
    logger.debug(f"Entering update_config with markdown_path_str='{markdown_path_str}', target_json_path='{target_json_path}', markdown_base_dir='{markdown_base_dir}'")
    logger.info(f"Attempting to update configuration from: {markdown_path_str}")
    # --- Path Validation ---
    markdown_path = Path(markdown_path_str).resolve()
    markdown_base_dir_resolved = markdown_base_dir.resolve()
    if not str(markdown_path).startswith(str(markdown_base_dir_resolved)):
        logger.warning(
            f"Markdown file path '{markdown_path}' is not inside the configured markdown base directory '{markdown_base_dir_resolved}'. Ensure this is intended."
        )
        # Consider raising an error if strict containment is required:
        # raise ValueError(f"Markdown file path '{markdown_path}' must be inside '{markdown_base_dir_resolved}'.")
    logger.debug(f"Parsing markdown file: {markdown_path}")
    updated_config = parse_markdown(markdown_path)
    logger.debug(f"Parsed config for update: slug='{updated_config.slug}', name='{updated_config.name}'")
    logger.debug(f"Loading existing configs from: {target_json_path}")
    configs = load_configs(target_json_path)
    logger.debug(f"Loaded {len(configs)} existing configs.")

    found = False
    for i, config in enumerate(configs):
        if config.slug == updated_config.slug:
            # --- Start: Added logic ---
            if preserve_groups:
                logger.debug(f"Preserving existing groups for slug '{config.slug}': {config.groups}")
                # Ensure the existing config actually has groups before copying
                if hasattr(config, 'groups') and config.groups is not None:
                     updated_config.groups = config.groups
                else:
                     # Handle case where existing config might somehow lack groups (though model default should prevent this)
                     logger.warning(f"Existing config for slug '{config.slug}' lacked groups attribute or was None. Cannot preserve.")
            # --- End: Added logic ---

            # Existing assignment (should be after the added logic)
            configs[i] = updated_config
            found = True
            logger.debug(f"Found existing config for slug '{updated_config.slug}' at index {i}. Replacing.") # Existing log
            break

    if not found:
        logger.error(f"Agent with slug '{updated_config.slug}' not found in {target_json_path} for update.")
        raise ValueError(f"Error: Agent with slug '{updated_config.slug}' not found in {target_json_path}.")

    logger.debug(f"Saving {len(configs)} configs (with update) to: {target_json_path}")
    save_configs(target_json_path, configs)
    logger.info(f"Successfully updated agent '{updated_config.slug}'.")
    logger.debug("Exiting update_config")


def delete_config(slug: str, target_json_path: Path):
    """Deletes an agent configuration by slug."""
    logger.debug(f"Entering delete_config with slug='{slug}', target_json_path='{target_json_path}'")
    logger.info(f"Attempting to delete configuration with slug: {slug}")
    logger.debug(f"Loading existing configs from: {target_json_path}")
    configs = load_configs(target_json_path)
    logger.debug(f"Loaded {len(configs)} existing configs.")
    initial_length = len(configs)
    logger.debug(f"Filtering configs to remove slug '{slug}'. Initial count: {initial_length}")
    configs = [config for config in configs if config.slug != slug]
    logger.debug(f"Filtered config count: {len(configs)}")

    if len(configs) == initial_length:
        logger.error(f"Agent with slug '{slug}' not found in {target_json_path} for deletion.")
        raise ValueError(f"Error: Agent with slug '{slug}' not found in {target_json_path}.")

    logger.debug(f"Saving {len(configs)} configs (after deletion) to: {target_json_path}")
    save_configs(target_json_path, configs)
    logger.info(f"Successfully deleted agent '{slug}'.")
    logger.debug("Exiting delete_config")