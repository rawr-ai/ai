# cli/compiler.py
from typing import Dict, Any
from cli.models import GlobalAgentConfig

def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
    """
    Extracts metadata suitable for the custom_modes.json registry
    from a validated GlobalAgentConfig object.
    Excludes fields not relevant to the registry (e.g., customInstructions).
    """
    # Use Pydantic's .dict() method to serialize the relevant fields.
    # 'include' specifies the fields we want.
    # 'exclude_none=True' ensures that if apiConfiguration is None, it's not included in the output dict.
    # The structure of nested fields like 'groups' and 'apiConfiguration' is preserved.
    registry_data = config.dict(
        include={'slug', 'name', 'roleDefinition', 'groups', 'apiConfiguration'},
        exclude_none=True
    )
    return registry_data