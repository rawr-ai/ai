import json
from pathlib import Path
import yaml # Need to import yaml here now

# Copied from tests/integration/test_compile_command.py
# Dictionary Keys needed by helpers (Consider centralizing if used elsewhere)
KEY_CUSTOM_MODES = "customModes"
KEY_RAW_CONTENT = "raw_content"
KEY_ERROR = "error"
CONFIG_FILENAME = "config.yaml" # Needed by create_mock_config

def create_mock_config(agents_dir: Path, slug: str, config_data: dict):
    """Creates a mock config.yaml file for a given agent slug."""
    # agent_dir = agents_dir / slug # REMOVED - No longer creating subdirectories
    # agent_dir.mkdir(parents=True, exist_ok=True) # REMOVED
    # Create the config file directly in the agents_dir with the slug as the filename stem
    config_path = agents_dir / f"{slug}.yaml"
    # import yaml # Import yaml safely inside the function - Moved to top level
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        print(f"DEBUG: Created mock config at {config_path}") # Keep debug print for now
    except Exception as e:
        print(f"ERROR creating mock config: {e}")
        raise
    return config_path

def read_mock_registry(registry_path: Path) -> dict:
    """Reads the content of the mock registry file."""
    if not registry_path.exists():
        return {KEY_CUSTOM_MODES: []} # Return default empty structure if file doesn't exist
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from {registry_path}")
        # Return raw content for debugging if needed, or raise/return empty
        try:
            return {KEY_RAW_CONTENT: registry_path.read_text()}
        except Exception:
            return {KEY_ERROR: "Could not read or decode file"}
    except Exception as e:
        print(f"ERROR reading mock registry: {e}")
        return {KEY_ERROR: str(e)}