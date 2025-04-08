# scripts/manage_agent_configs.py
import argparse
import json
import logging
import os
import re
import sys
import yaml
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from pydantic import BaseModel, ValidationError, Field

# --- Configuration ---
# TARGET_JSON_PATH and MARKDOWN_BASE_DIR are now loaded from cli_config.yaml
ROLE_DEFINITION_HEADINGS = ["# Core Identity & Purpose", "# Persona", "# Role"]
CUSTOM_INSTRUCTIONS_HEADINGS = ["## Custom Instructions", "## Mode-specific Instructions"]
HEADING_PATTERN = re.compile(r"^\s*(#+)\s+(.*)", re.MULTILINE)

# --- Pydantic Model ---
class AgentConfig(BaseModel):
    slug: str
    name: str
    roleDefinition: str = Field(..., alias="roleDefinition")
    customInstructions: Optional[str] = Field(None, alias="customInstructions")

    class Config:
        allow_population_by_field_name = True # Allows using field names ('roleDefinition') instead of aliases during initialization if needed.

# --- Helper Functions ---

def _find_section(content: str, start_headings: List[str], start_offset: int = 0) -> Optional[Tuple[str, int, int]]:
    """
    Finds the first occurrence of any start_heading from the offset
    and returns the full section content including the heading, its start index, and its end index.
    The section ends before the next heading of the same or lower level, or EOF.
    """
    best_match_start_index = -1
    found_heading = None

    # Find the earliest occurrence of any of the start headings
    for heading in start_headings:
        try:
            current_start_index = content.index(heading, start_offset)
            if best_match_start_index == -1 or current_start_index < best_match_start_index:
                best_match_start_index = current_start_index
                found_heading = heading
        except ValueError:
            continue # Heading not found

    if best_match_start_index == -1:
        return None # No start heading found

    # Determine the level of the found heading
    heading_match = HEADING_PATTERN.match(content[best_match_start_index:])
    if not heading_match:
         # This should ideally not happen if the heading was found by index, but safeguard anyway
        logging.warning(f"Could not parse heading level for found heading: '{found_heading}'")
        start_level = heading.count('#') # Fallback to counting '#'
    else:
        start_level = len(heading_match.group(1))

    # Find the end of the section
    end_index = len(content)
    content_start_after_heading = best_match_start_index + len(found_heading)

    # Look for the next heading of the same or lower level
    for match in HEADING_PATTERN.finditer(content, content_start_after_heading):
        next_level = len(match.group(1))
        if next_level <= start_level:
            end_index = match.start()
            break # Found the boundary

    section_content = content[best_match_start_index:end_index].strip()
    return section_content, best_match_start_index, end_index


def parse_markdown(markdown_path: Path) -> AgentConfig:
    """Parses an agent Markdown file and returns an AgentConfig object."""
    if not markdown_path.is_file():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    logging.info(f"Parsing Markdown file: {markdown_path}")
    content = markdown_path.read_text(encoding="utf-8")

    # Extract slug from parent directory
    slug = markdown_path.parent.name
    if not slug:
        raise ValueError(f"Could not determine slug from path: {markdown_path}")
    logging.debug(f"Extracted slug: {slug}")

    # Extract name from first H1 (more robust regex)
    name_match = re.search(r"^\s*#\s+(.*)", content, re.MULTILINE)
    if not name_match:
        raise ValueError(f"Could not find H1 heading for 'name' in: {markdown_path}")
    name = name_match.group(1).strip()
    logging.debug(f"Extracted name: {name}")

    # Extract roleDefinition (first match of specified headings)
    role_section_result = _find_section(content, ROLE_DEFINITION_HEADINGS)
    if not role_section_result:
        raise ValueError(f"Could not find any role definition heading ({', '.join(ROLE_DEFINITION_HEADINGS)}) in: {markdown_path}")
    role_definition, _, _ = role_section_result
    logging.debug(f"Extracted roleDefinition starting with: {role_definition[:50]}...")

    # Extract and concatenate customInstructions (all matches)
    custom_instructions_list = []
    current_offset = 0
    while True:
        instruction_section_result = _find_section(content, CUSTOM_INSTRUCTIONS_HEADINGS, start_offset=current_offset)
        if not instruction_section_result:
            break
        section_content, start_idx, end_idx = instruction_section_result
        custom_instructions_list.append(section_content)
        current_offset = end_idx # Start next search after the current section ends

    custom_instructions_final = None
    if custom_instructions_list:
        logging.debug(f"Found {len(custom_instructions_list)} custom instruction sections.")
        # Concatenate: keep heading of the first, append content of the rest
        first_section = custom_instructions_list[0]
        concatenated_parts = [first_section]

        for subsequent_section in custom_instructions_list[1:]:
            # Find the end of the heading line in the subsequent section
            heading_line_end = subsequent_section.find('\n')
            if heading_line_end != -1:
                content_part = subsequent_section[heading_line_end+1:].strip()
                if content_part: # Only append if there's actual content after the heading
                    concatenated_parts.append(content_part)
            # else: If no newline, it's just a heading, ignore content part

        custom_instructions_final = "\n\n".join(concatenated_parts).strip()
        logging.debug(f"Extracted customInstructions starting with: {custom_instructions_final[:50]}...")


    try:
        config_data = {
            "slug": slug,
            "name": name,
            "roleDefinition": role_definition,
        }
        if custom_instructions_final:
            config_data["customInstructions"] = custom_instructions_final

        agent_config = AgentConfig(**config_data)
        logging.info(f"Successfully parsed AgentConfig for slug: {slug}")
        return agent_config
    except ValidationError as e:
        logging.error(f"Validation error creating AgentConfig for {markdown_path}: {e}")
        raise ValueError(f"Validation error creating AgentConfig for {markdown_path}: {e}")


def load_configs(json_path: Path) -> List[AgentConfig]:
    """Loads agent configurations from the JSON file."""
    if not json_path.is_file():
        logging.warning(f"Target JSON file not found at {json_path}. Returning empty list.")
        return []
    try:
        logging.info(f"Loading configurations from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Expect a dictionary with a 'customModes' key containing the list
        if not isinstance(data, dict) or "customModes" not in data:
            logging.error(f"Invalid format: Target JSON file {json_path} does not contain a top-level 'customModes' key with a list.")
            raise TypeError(f"Target JSON ({json_path}) structure is invalid. Expected {{'customModes': [...]}}.")
        if not isinstance(data["customModes"], list):
             logging.error(f"Invalid format: 'customModes' key in {json_path} does not contain a list.")
             raise TypeError(f"'customModes' in {json_path} is not a list.")
        configs = [AgentConfig.parse_obj(item) for item in data["customModes"]]
        logging.info(f"Successfully loaded {len(configs)} configurations.")
        return configs
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error in {json_path}: {e}")
        raise ValueError(f"Invalid JSON format in {json_path}: {e}")
    except ValidationError as e:
        logging.error(f"Data validation error in {json_path}: {e}")
        raise ValueError(f"Data validation failed for {json_path}: {e}")
    except TypeError as e: # Catch potential issues if data is not list of dicts before parse_obj
         logging.error(f"Type error during config loading from {json_path}: {e}")
         raise ValueError(f"Incorrect data structure in {json_path}: {e}")


def save_configs(json_path: Path, configs: List[AgentConfig]):
    """Saves agent configurations to the JSON file."""
    try:
        logging.info(f"Saving {len(configs)} configurations to: {json_path}")
        # Ensure parent directory exists
        json_path.parent.mkdir(parents=True, exist_ok=True)
        # Convert Pydantic models to dicts for JSON serialization, respecting aliases
        config_dicts = sorted( # Sort by slug for consistency
            [config.dict(by_alias=True, exclude_none=True) for config in configs],
            key=lambda x: x.get('slug', '')
        )
        with open(json_path, 'w', encoding='utf-8') as f:
            # Wrap the list in the expected top-level structure
            output_data = {"customModes": config_dicts}
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved configurations to {json_path}")
    except IOError as e:
        logging.error(f"Error writing to JSON file {json_path}: {e}")
        raise IOError(f"Error writing to JSON file {json_path}: {e}")
    except Exception as e:
        # Log the full traceback for unexpected errors during save
        logging.exception(f"An unexpected error occurred during saving to {json_path}: {e}")
        raise RuntimeError(f"An unexpected error occurred during saving: {e}")


# --- Core Operations ---
def add_config(markdown_path_str: str, target_json_path: Path, markdown_base_dir: Path):
    """Adds a new agent configuration from a Markdown file."""
    # --- Path Validation ---
    markdown_path = Path(markdown_path_str).resolve()
    markdown_base_dir_resolved = markdown_base_dir.resolve()
    if not str(markdown_path).startswith(str(markdown_base_dir_resolved)):
        logging.warning(
            f"Markdown file path '{markdown_path}' is not inside the configured markdown base directory '{markdown_base_dir_resolved}'. "
            f"Ensure this is intended."
        )
        # Consider raising an error if strict containment is required:
        # raise ValueError(f"Markdown file path '{markdown_path}' must be inside '{markdown_base_dir_resolved}'.")

    # --- Add Operation Specific Check ---
    # For 'add', the target JSON file should ideally exist, but load_configs handles creation if not.
    # Let's ensure the directory exists though.
    target_json_path.parent.mkdir(parents=True, exist_ok=True)
    logging.info(f"Attempting to add configuration from: {markdown_path}")
    new_config = parse_markdown(markdown_path)
    configs = load_configs(target_json_path)

    if any(config.slug == new_config.slug for config in configs):
        logging.error(f"Agent with slug '{new_config.slug}' already exists in {target_json_path}.")
        raise ValueError(f"Error: Agent with slug '{new_config.slug}' already exists in {target_json_path}.")

    configs.append(new_config)
    save_configs(target_json_path, configs)
    logging.info(f"Successfully added agent '{new_config.slug}'.")


def update_config(markdown_path_str: str, target_json_path: Path, markdown_base_dir: Path):
    """Updates an existing agent configuration from a Markdown file."""
    markdown_path = Path(markdown_path_str)
    logging.info(f"Attempting to update configuration from: {markdown_path_str}")
    # --- Path Validation ---
    markdown_path = Path(markdown_path_str).resolve()
    markdown_base_dir_resolved = markdown_base_dir.resolve()
    if not str(markdown_path).startswith(str(markdown_base_dir_resolved)):
        logging.warning(
            f"Markdown file path '{markdown_path}' is not inside the configured markdown base directory '{markdown_base_dir_resolved}'. "
            f"Ensure this is intended."
        )
        # Consider raising an error if strict containment is required:
        # raise ValueError(f"Markdown file path '{markdown_path}' must be inside '{markdown_base_dir_resolved}'.")
    updated_config = parse_markdown(markdown_path)
    configs = load_configs(target_json_path)

    found = False
    for i, config in enumerate(configs):
        if config.slug == updated_config.slug:
            configs[i] = updated_config
            found = True
            logging.debug(f"Found existing config for slug '{updated_config.slug}' at index {i}.")
            break

    if not found:
        logging.error(f"Agent with slug '{updated_config.slug}' not found in {target_json_path} for update.")
        raise ValueError(f"Error: Agent with slug '{updated_config.slug}' not found in {target_json_path}.")

    save_configs(target_json_path, configs)
    logging.info(f"Successfully updated agent '{updated_config.slug}'.")


def delete_config(slug: str, target_json_path: Path):
    """Deletes an agent configuration by slug."""
    logging.info(f"Attempting to delete configuration with slug: {slug}")
    configs = load_configs(target_json_path)
    initial_length = len(configs)
    configs = [config for config in configs if config.slug != slug]

    if len(configs) == initial_length:
        logging.error(f"Agent with slug '{slug}' not found in {target_json_path} for deletion.")
        raise ValueError(f"Error: Agent with slug '{slug}' not found in {target_json_path}.")

    save_configs(target_json_path, configs)
    logging.info(f"Successfully deleted agent '{slug}'.")

# --- CLI ---
def main():
    # Basic logging configuration
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # --- Load Configuration from YAML ---
    config_path = Path("scripts/cli_config.yaml")
    if not config_path.is_file():
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        logging.debug(f"Loading configuration from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            cli_config = yaml.safe_load(f)
        if not cli_config or 'target_json_path' not in cli_config or 'markdown_base_dir' not in cli_config:
            logging.error(f"Invalid configuration format in {config_path}. Missing required keys.")
            sys.exit(1)
        target_json_path = Path(cli_config['target_json_path']).resolve()
        markdown_base_dir = Path(cli_config['markdown_base_dir']).resolve()
        logging.debug(f"Target JSON path loaded: {target_json_path}")
        logging.debug(f"Markdown base directory loaded: {markdown_base_dir}")
    except yaml.YAMLError as e:
        logging.error(f"Error parsing configuration file {config_path}: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred loading configuration: {e}")
        sys.exit(1)

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(prog="rawr", description="Manage agent configurations using definitions from Markdown files.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (DEBUG) logging.")
    subparsers = parser.add_subparsers(dest="operation", required=True, help="Subcommand to execute")

    # Add operation
    parser_add = subparsers.add_parser("add", help="Add a new agent config from a Markdown file. Fails if slug already exists.")
    parser_add.add_argument("path_to_markdown_file", type=str, help="Path to the agent definition Markdown file.")

    # Update operation
    parser_update = subparsers.add_parser("update", help="Update an existing agent config from a Markdown file. Fails if slug does not exist.")
    parser_update.add_argument("path_to_markdown_file", type=str, help="Path to the agent definition Markdown file.")

    # Delete operation
    parser_delete = subparsers.add_parser("delete", help="Delete an agent config by its slug. Fails if slug does not exist.")
    parser_delete.add_argument("agent_slug", type=str, help="Slug of the agent configuration to delete.")

    # Sync operation (Placeholder - Not fully implemented as per convention doc)
    # parser_sync = subparsers.add_parser("sync", help="Sync configs from a directory of Markdown files.")
    # parser_sync.add_argument("directory_path", type=str, help="Directory containing agent Markdown files.")
    # parser_sync.add_argument("--delete-stale", action="store_true", help="Remove JSON entries for non-existent Markdown files.")


    args = parser.parse_args()

    # Adjust logging level if verbose flag is set
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled.")

    # target_json_path is now loaded from config
    logging.debug(f"Target JSON path resolved to: {target_json_path}")

    try:
        if args.operation == "add":
            add_config(args.path_to_markdown_file, target_json_path, markdown_base_dir)
        elif args.operation == "update":
            update_config(args.path_to_markdown_file, target_json_path, markdown_base_dir)
        elif args.operation == "delete":
            delete_config(args.agent_slug, target_json_path)
        # elif args.operation == "sync":
        #     logging.warning("Sync operation is not fully implemented yet.")
            # sync_configs(args.directory_path, args.delete_stale, target_json_path)
        else:
            # This case should not be reachable due to `required=True` on subparsers
            logging.error("No valid operation specified.")
            parser.print_help(sys.stderr)
            exit(1)
    except (FileNotFoundError, ValueError, IOError, RuntimeError) as e:
        # Log known error types specifically
        logging.error(f"{type(e).__name__}: {e}")
        exit(1)
    except Exception as e:
        # Log unexpected errors with traceback
        logging.exception(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()