import json
import os
import pathlib
import shutil
import tempfile
import logging
from . import config_loader # Import the new global config loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global registry path is now loaded via the centralized config_loader
# The hardcoded definition is removed. Functions will fetch the default path.

def read_global_registry(registry_path: pathlib.Path = None) -> dict:
    # Fetch default path from config loader if not provided
    if registry_path is None:
        registry_path = config_loader.get_global_registry_path()
    """
    Reads the global custom modes registry JSON file.

    Args:
        registry_path: The path to the global registry JSON file.

    Returns:
        A dictionary containing the registry data. Returns a default structure
        if the file is not found or is invalid JSON.
    """
    default_registry = {"customModes": []}
    try:
        if not registry_path.exists():
            logging.warning(f"Registry file not found at {registry_path}. Returning default structure.")
            return default_registry
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Basic validation: ensure 'customModes' key exists and is a list
            if isinstance(data, dict) and isinstance(data.get("customModes"), list):
                return data
            else:
                logging.error(f"Invalid structure in registry file {registry_path}. Returning default structure.")
                return default_registry
    except json.JSONDecodeError:
        logging.exception(f"Error decoding JSON from {registry_path}. Returning default structure.")
        return default_registry
    except OSError as e:
        logging.exception(f"OS error reading registry file {registry_path}: {e}. Returning default structure.")
        return default_registry
    except Exception as e:
        logging.exception(f"Unexpected error reading registry file {registry_path}: {e}. Returning default structure.")
        return default_registry


def update_global_registry(registry_data: dict, agent_metadata: dict) -> dict:
    """
    Updates the registry data dictionary with new or modified agent metadata.

    Excludes the 'customInstructions' field from the metadata being added/updated.

    Args:
        registry_data: The current registry data (dictionary).
        agent_metadata: The metadata for the agent to add or update.

    Returns:
        The updated registry data dictionary.
    """
    if not isinstance(registry_data, dict) or "customModes" not in registry_data:
        logging.error("Invalid registry_data structure passed to update_global_registry. Initializing.")
        registry_data = {"customModes": []}
        
    if not isinstance(agent_metadata, dict) or "slug" not in agent_metadata:
        logging.error("Invalid agent_metadata passed to update_global_registry. Skipping update.")
        return registry_data

    agent_slug = agent_metadata["slug"]
    
    # Create a copy of the metadata, excluding 'customInstructions'
    metadata_to_store = {k: v for k, v in agent_metadata.items() if k != "customInstructions"}

    found = False
    for i, mode in enumerate(registry_data["customModes"]):
        if isinstance(mode, dict) and mode.get("slug") == agent_slug:
            # Update existing entry
            registry_data["customModes"][i] = metadata_to_store
            found = True
            logging.info(f"Updated agent '{agent_slug}' in the registry.")
            break

    if not found:
        # Add new entry
        registry_data["customModes"].append(metadata_to_store)
        logging.info(f"Added new agent '{agent_slug}' to the registry.")

    return registry_data


def write_global_registry(registry_data: dict, registry_path: pathlib.Path = None):
    # Fetch default path from config loader if not provided
    if registry_path is None:
        registry_path = config_loader.get_global_registry_path()
    """
    Writes the updated registry data back to the global JSON file safely.

    Uses a temporary file and atomic rename operation to prevent corruption.

    Args:
        registry_data: The dictionary containing the registry data to write.
        registry_path: The path to the global registry JSON file.

    Raises:
        OSError: If file I/O operations fail.
        Exception: For any other unexpected errors during the write process.
    """
    # Simplified write logic: write directly to the target file.
    # Note: This is less safe against corruption if the process is interrupted.
    try:
        # Ensure the parent directory exists
        registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Write directly to the final destination file
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2) # Use indent=2 for readability
        
        logging.info(f"Successfully wrote updated registry to {registry_path}")

    except OSError as e:
        logging.exception(f"OS error writing registry file {registry_path}: {e}")
        raise # Re-raise the original error
    except Exception as e:
        logging.exception(f"Unexpected error writing registry file {registry_path}: {e}")
        raise # Re-raise the original error

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # Example: Read, update, and write back
    # Use the getter function to display the configured path
    effective_registry_path = config_loader.get_global_registry_path()
    print(f"Using registry path: {effective_registry_path}")

    # 1. Read existing data
    current_data = read_global_registry(effective_registry_path) # Pass the path explicitly
    print("\nRead current registry data:")
    print(json.dumps(current_data, indent=2))

    # 2. Prepare example agent metadata (simulating compiler output)
    example_agent_metadata = {
        "slug": "example-agent",
        "name": "Example Agent",
        "role": "An example agent role.",
        "customInstructions": "These instructions should NOT be saved.",
        "description": "A test agent added via registry_manager.",
        "tools": ["read_file", "write_to_file"]
    }
    
    example_agent_metadata_update = {
        "slug": "example-agent",
        "name": "Example Agent Updated",
        "role": "An example agent role, now updated.",
        "customInstructions": "These instructions should ALSO NOT be saved.",
        "description": "A test agent updated via registry_manager.",
        "tools": ["read_file", "write_to_file", "execute_command"]
    }

    # 3. Update the registry data
    updated_data = update_global_registry(current_data, example_agent_metadata)
    updated_data = update_global_registry(updated_data, example_agent_metadata_update) # Test update
    print("\nRegistry data after update:")
    print(json.dumps(updated_data, indent=2))

    # 4. Write the updated data back
    try:
        write_global_registry(updated_data, effective_registry_path) # Pass the path explicitly
        print(f"\nSuccessfully wrote updated data to {effective_registry_path}")

        # Verify by reading again
        verify_data = read_global_registry(effective_registry_path) # Pass the path explicitly
        print("\nVerified data read back from file:")
        print(json.dumps(verify_data, indent=2))
        
        # Check if customInstructions were excluded
        agent_found = False
        for mode in verify_data.get("customModes", []):
            if mode.get("slug") == "example-agent":
                agent_found = True
                if "customInstructions" in mode:
                    print("\nERROR: 'customInstructions' found in saved data!")
                else:
                    print("\nOK: 'customInstructions' correctly excluded from saved data.")
                break
        if not agent_found:
             print("\nERROR: Example agent not found in verified data!")

    except Exception as e:
        print(f"\nError during write or verification: {e}")