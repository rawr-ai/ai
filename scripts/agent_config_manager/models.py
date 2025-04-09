# scripts/agent_config_manager/models.py
import logging
from typing import List, Optional, Any
from pydantic import BaseModel, Field

# Get a logger for this module
logger = logging.getLogger(__name__)

class AgentConfig(BaseModel):
    slug: str
    name: str
    roleDefinition: str = Field(..., alias="roleDefinition")
    customInstructions: Optional[str] = Field(None, alias="customInstructions")
    groups: Optional[List[Any]] = Field(default=["read"])
    class Config:
        allow_population_by_field_name = True # Allows using field names ('roleDefinition') instead of aliases during initialization if needed.