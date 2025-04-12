import json
import yaml
import os
import argparse
from pathlib import Path

# --- Configuration ---
# Use absolute path for the source JSON as it's outside the workspace
SOURCE_JSON_PATH = Path('/Users/mateicanavra/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json')
# Use relative path for the target directory within the workspace
TARGET_BASE_DIR = Path('ai/agents')
# --- End Configuration ---

def represent_literal_block(dumper, data):
    """Helper to represent multi-line strings as literal blocks in YAML."""
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, represent_literal_block)

def generate_configs(include_custom_instructions=False):
    """Reads the source JSON and generates individual YAML config files."""
    print(f"Reading source JSON from: {SOURCE_JSON_PATH}")
    if not SOURCE_JSON_PATH.is_file():
        print(f"Error: Source JSON file not found at {SOURCE_JSON_PATH}")
        return

    try:
        with open(SOURCE_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if 'customModes' not in data or not isinstance(data['customModes'], list):
        print("Error: Expected 'customModes' key with a list value in the JSON file.")
        return

    print(f"Found {len(data['customModes'])} modes in the source file.")
    generated_count = 0

    for mode_config in data['customModes']:
        slug = mode_config.get('slug')
        if not slug:
            print("Warning: Skipping mode with missing 'slug'.")
            continue

        target_dir = TARGET_BASE_DIR / slug
        target_yaml_path = target_dir / 'config.yaml'

        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)

        # Prepare data for YAML output
        yaml_data = {
            'slug': slug,
            'name': mode_config.get('name'),
            'roleDefinition': mode_config.get('roleDefinition', ''), # Ensure it exists
            'groups': mode_config.get('groups'),
            'apiConfiguration': mode_config.get('apiConfiguration') # Can be null
        }

        # Conditionally add customInstructions based on the flag and if it exists
        if include_custom_instructions:
            custom_instructions = mode_config.get('customInstructions')
            if custom_instructions: # Only add if it's not null/empty
                yaml_data['customInstructions'] = custom_instructions


        try:
            with open(target_yaml_path, 'w', encoding='utf-8') as f:
                # Use sort_keys=False to maintain order, allow_unicode for broader compatibility
                yaml.dump(yaml_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False, width=1000)
            print(f"Successfully generated: {target_yaml_path}")
            generated_count += 1
        except Exception as e:
            print(f"Error writing YAML file {target_yaml_path}: {e}")

    print(f"\nFinished. Generated {generated_count} config files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate agent config YAML files from JSON.')
    parser.add_argument(
        '--include-custom-instructions',
        action='store_true',
        help='Include the customInstructions field in the output YAML files.'
    )
    args = parser.parse_args()

    generate_configs(include_custom_instructions=args.include_custom_instructions)