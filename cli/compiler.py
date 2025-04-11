# cli/compiler.py
from typing import Dict, Any
from cli.models import GlobalAgentConfig

def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
    """
    Extracts metadata suitable for the custom_modes.json registry
    from a validated GlobalAgentConfig object.
    Excludes fields not relevant to the registry (e.g., customInstructions).
    """
    # Use Pydantic's model_dump with mode='json' to handle serialization,
    # including complex types like Union. Explicitly include only registry fields.
    registry_data = config.model_dump(
        mode='json', # Use JSON-compatible serialization
        include={'slug', 'name', 'roleDefinition', 'groups', 'apiConfiguration'},
        exclude_none=True # Exclude apiConfiguration if it's None
    )
    return registry_data