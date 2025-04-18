# cli/models.py

from typing import List, Optional, Union, Dict, Any, Tuple
from pydantic import BaseModel, HttpUrl, Field, Extra

# Model for Group Restrictions (as defined in step_01_definition.md)
class GroupRestriction(BaseModel):
    """Defines restrictions for a specific group."""
    fileRegex: str = Field(..., description="Regex pattern for allowed files.")
    description: Optional[str] = Field(None, description="Optional description for the restriction.")

    class Config:
        extra = Extra.forbid # Ensure no extra fields are allowed

# Model for API Configuration (as defined in step_01_definition.md)
class ApiConfig(BaseModel):
    """Configuration for external API usage by an agent."""
    model: str = Field(..., description="The specific model identifier to use.")
    url: Optional[HttpUrl] = Field(None, description="Optional URL endpoint for the API.")
    params: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the API call.")

    class Config:
        extra = Extra.forbid # Ensure no extra fields are allowed

# Main Model for Global Agent Configuration (as defined in step_01_definition.md)
class GlobalAgentConfig(BaseModel):
    """Represents the configuration for a global agent/mode."""
    slug: str = Field(..., description="Unique identifier slug for the agent/mode.")
    name: str = Field(..., description="Display name for the agent/mode.")
    description: Optional[str] = Field(None, description="Optional human‑readable summary of the agent.")
    roleDefinition: str = Field(..., description="The core role definition or system prompt.")
    customInstructions: Optional[str] = Field(None, description="Optional user-defined instructions for the agent.")
    groups: List[Union[str, Tuple[str, GroupRestriction]]] = Field(
        ...,
        description="List of groups the agent belongs to. Can be simple names or tuples with restrictions."
    )
    apiConfiguration: Optional[ApiConfig] = Field(None, description="Optional API configuration for the agent.")

    class Config:
        extra = Extra.forbid # Ensure no extra fields are allowed, as per scope limitation