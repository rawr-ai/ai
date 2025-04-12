# cli/exceptions.py
from typing import Optional

class AgentProcessingError(Exception):
    """Base exception for errors during agent processing."""
    def __init__(self, message: str, agent_slug: Optional[str] = None, original_exception: Optional[Exception] = None):
        self.agent_slug = agent_slug
        self.original_exception = original_exception
        if agent_slug:
            super().__init__(f"Error processing agent '{agent_slug}': {message}")
        else:
             super().__init__(f"Error during agent processing: {message}")


class AgentLoadError(AgentProcessingError):
    """Exception for errors loading or parsing agent config."""
    pass

class AgentValidationError(AgentProcessingError):
    """Exception for config validation errors."""
    pass

class AgentCompileError(AgentProcessingError):
    """Exception for errors during metadata extraction or registry update."""
    pass

class RegistryError(Exception):
    """Base exception for registry-related errors."""
    pass

class RegistryReadError(RegistryError):
    """Exception for errors reading the registry file."""
    pass

class RegistryWriteError(RegistryError):
    """Exception for errors writing the registry file."""
    pass