# cli/config_loader.py
import yaml
import os
from pathlib import Path
import sys

# Determine the project root directory dynamically
# Assumes this script is in 'cli/' subdirectory relative to the project root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "rawr.config.yaml"
LOCAL_CONFIG_PATH = PROJECT_ROOT / "rawr.config.local.yaml"

# Default values in case config files or keys are missing
DEFAULT_AGENT_CONFIG_DIR = PROJECT_ROOT / "cli/agent_config"
DEFAULT_GLOBAL_REGISTRY_PATH = PROJECT_ROOT / ".rawr_registry/custom_modes.json"

def load_config():
    """
    Loads configuration from default, local, and environment variables.
    Precedence: Env Vars > Local Config > Main Config > Code Defaults.
    Returns paths as absolute Path objects.
    """
    # Start with code defaults
    config = {
        'agent_config_dir': DEFAULT_AGENT_CONFIG_DIR,
        'global_registry_path': DEFAULT_GLOBAL_REGISTRY_PATH,
    }

    # Helper to load and merge from a YAML file
    def merge_from_yaml(file_path, current_config):
        if file_path.exists() and file_path.is_file():
            try:
                with open(file_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if isinstance(yaml_config, dict): # Ensure it's a dictionary
                        # Only update keys present in the YAML file
                        for key in current_config.keys():
                            if key in yaml_config:
                                # Resolve path relative to project root
                                current_config[key] = PROJECT_ROOT / yaml_config[key]
                    else:
                         print(f"Warning: Config file {file_path} is not a valid dictionary. Ignoring.", file=sys.stderr)

            except yaml.YAMLError as e:
                print(f"Warning: Error parsing {file_path}: {e}. Using previous config values.", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}. Using previous config values.", file=sys.stderr)
        return current_config

    # 1. Load main config file (rawr.config.yaml)
    config = merge_from_yaml(DEFAULT_CONFIG_PATH, config.copy()) # Use copy to avoid modifying defaults directly yet

    # 2. Load local override config file (rawr.config.local.yaml)
    config = merge_from_yaml(LOCAL_CONFIG_PATH, config.copy()) # Use copy, local overrides main

    # 3. Load from environment variables (highest precedence)
    env_agent_config_dir = os.getenv('RAWR_AGENT_CONFIG_DIR')
    if env_agent_config_dir:
        # Assume env var path is relative to CWD or absolute
        config['agent_config_dir'] = Path(env_agent_config_dir).resolve()

    env_global_registry_path = os.getenv('RAWR_GLOBAL_REGISTRY_PATH')
    if env_global_registry_path:
        # Assume env var path is relative to CWD or absolute
        config['global_registry_path'] = Path(env_global_registry_path).resolve()

    # Ensure all paths are absolute Path objects at the end
    config['agent_config_dir'] = Path(config['agent_config_dir']).resolve()
    config['global_registry_path'] = Path(config['global_registry_path']).resolve()

    return config

# Load config once on import to be used by other modules
settings = load_config()

# Provide accessors that return absolute Path objects
def get_agent_config_dir() -> Path:
    # Fallback needed if initial loading failed completely for some reason
    return settings.get('agent_config_dir', DEFAULT_AGENT_CONFIG_DIR).resolve()

def get_global_registry_path() -> Path:
     # Fallback needed
    return settings.get('global_registry_path', DEFAULT_GLOBAL_REGISTRY_PATH).resolve()

if __name__ == '__main__':
    # Example usage/test
    print("Loaded Configuration (Absolute Paths):")
    print(f"  Agent Config Dir: {get_agent_config_dir()}")
    print(f"  Global Registry Path: {get_global_registry_path()}")
    print(f"\nProject Root used for relative paths: {PROJECT_ROOT}")

    # Test precedence (requires setting env vars or creating local/default files)
    # Example: export RAWR_AGENT_CONFIG_DIR=/tmp/rawr_agents
    # Example: echo "global_registry_path: etc/rawr/registry.json" > rawr.config.local.yaml
    # Example: echo "agent_config_dir: configs/agents" > rawr.config.yaml