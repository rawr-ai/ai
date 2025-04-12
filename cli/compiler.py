# cli/compiler.py
import typer
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import yaml
from pydantic import ValidationError as ConfigValidationError

# Assuming these modules exist and provide the necessary functions/classes
from . import config_loader
from . import registry_manager
from .models import GlobalAgentConfig

# --- Logging Setup ---
# Use the same logger name pattern as main.py or a dedicated one
logger = logging.getLogger(__name__)

# --- Constants ---
# Load paths using the centralized config loader
AGENT_CONFIG_DIR = config_loader.get_agent_config_dir()
GLOBAL_REGISTRY_PATH = config_loader.get_global_registry_path()

# --- Custom Exceptions (Copied from main.py) ---
class AgentProcessingError(Exception):
    """Base exception for errors during agent processing."""
    def __init__(self, message: str, agent_slug: str, original_exception: Optional[Exception] = None):
        self.agent_slug = agent_slug
        self.original_exception = original_exception
        super().__init__(f"Error processing agent '{agent_slug}': {message}")

class AgentLoadError(AgentProcessingError):
    """Exception for errors loading or parsing agent config."""
    pass

class AgentValidationError(AgentProcessingError):
    """Exception for config validation errors."""
    pass

class AgentCompileError(AgentProcessingError):
    """Exception for errors during metadata extraction or registry update."""
    pass


# --- Internal Helper Functions (Adapted from main.py) ---

def _compile_specific_agent(
    agent_slug: str,
    agent_config_dir: Path,
    current_registry_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Loads, validates, compiles a single agent config and updates registry data in memory.

    Args:
        agent_slug: The slug of the agent to compile.
        agent_config_dir: The base directory containing agent configurations.
        current_registry_data: The current state of the global registry data.

    Returns:
        The updated registry data containing the compiled agent's metadata.

    Raises:
        AgentLoadError: If the config file cannot be found, read, or parsed.
        AgentValidationError: If the config data fails schema validation.
        AgentCompileError: If metadata extraction or registry update fails.
        AgentProcessingError: For other unexpected errors during processing.
    """
    logger.info(f"Attempting to compile agent: {agent_slug}")
    agent_config_path = agent_config_dir / agent_slug / "config.yaml"

    # 1. Load and Validate Agent Config
    typer.echo(f"Processing '{agent_slug}': Loading and validating config...")
    try:
        config_content = agent_config_path.read_text()
        config_data = yaml.safe_load(config_content)
        if not isinstance(config_data, dict):
             raise ValueError(f"Config file {agent_config_path} did not parse into a dictionary.")
        agent_config = GlobalAgentConfig.model_validate(config_data)
        logger.info(f"Successfully loaded and validated config for {agent_slug}")
    except FileNotFoundError as e:
        logger.error(f"Agent config file not found at {agent_config_path}")
        msg = f"Config file not found at {agent_config_path}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentLoadError(msg, agent_slug, e)
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing failed for {agent_config_path}: {e}")
        msg = f"Failed to parse YAML. Details:\n{e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentLoadError(msg, agent_slug, e)
    except ConfigValidationError as e:
        logger.error(f"Config validation failed for {agent_slug}: {e}")
        msg = f"Config validation failed. Details:\n{e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentValidationError(msg, agent_slug, e)
    except Exception as e:
        logger.exception(f"Unexpected error loading/validating config for {agent_slug}")
        msg = f"An unexpected error occurred loading/validating config. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentProcessingError(msg, agent_slug, e)

    # 2. Extract Metadata
    typer.echo(f"Processing '{agent_slug}': Extracting metadata...")
    try:
        # Assuming compiler.extract_registry_metadata exists and works as before
        # If this function was also in main.py, it needs to be moved here too.
        # For now, assuming it's correctly placed or imported.
        # Let's define a placeholder if it's not imported elsewhere
        # TODO: Ensure extract_registry_metadata is defined/imported correctly
        def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
             # Placeholder implementation - replace with actual logic if needed
             logger.warning("Using placeholder extract_registry_metadata")
             return {
                 "slug": config.slug,
                 "name": config.name,
                 "description": config.description,
                 "version": config.version,
                 # Add other relevant metadata extraction
             }

        registry_metadata = extract_registry_metadata(agent_config)
        logger.info(f"Successfully extracted metadata for {agent_slug}")
    except Exception as e:
        logger.exception(f"Unexpected error extracting metadata for {agent_slug}")
        msg = f"An unexpected error occurred extracting metadata. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentCompileError(msg, agent_slug, e)

    # 3. Update Global Registry (In Memory)
    typer.echo(f"Processing '{agent_slug}': Updating registry data...")
    try:
        # Use a copy to avoid modifying the input dict directly if update fails
        temp_registry_data = current_registry_data.copy()
        updated_registry_data = registry_manager.update_global_registry(
            registry_data=temp_registry_data,
            agent_metadata=registry_metadata
        )
        logger.info(f"Successfully updated registry data in memory for {agent_slug}")
        typer.echo(f"✅ Successfully processed agent: '{agent_slug}'") # Moved success message here
        return updated_registry_data # Return the updated data
    except Exception as e:
        logger.exception(f"Unexpected error updating global registry data for {agent_slug}")
        msg = f"An unexpected error occurred updating registry data. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentCompileError(msg, agent_slug, e)


def _compile_all_agents(
    agent_config_dir: Path,
    initial_registry_data: Dict[str, Any]
) -> Tuple[Dict[str, Any], int, int]:
    """
    Scans the agent directory, compiles all valid agents, and accumulates results.

    Args:
        agent_config_dir: The directory containing agent configurations.
        initial_registry_data: The starting state of the global registry.

    Returns:
        A tuple containing:
        - final_registry_data: The registry data after processing all agents.
        - compiled_count: The number of successfully compiled agents.
        - failed_count: The number of agents that failed to compile.
    """
    logger.info(f"Scanning for agent configurations in: {agent_config_dir}")
    typer.echo(f"Scanning for agent configurations in: {agent_config_dir}")

    compiled_count = 0
    failed_count = 0
    final_registry_data = initial_registry_data.copy() # Start with initial data

    if not agent_config_dir or not agent_config_dir.is_dir():
         logger.error(f"Agent configuration directory not found or invalid: {agent_config_dir}")
         # Check if the path matches the default, implying rawr.config.yaml might be missing/invalid
         if agent_config_dir == config_loader.DEFAULT_AGENT_CONFIG_DIR:
              expected_rawr_config = config_loader.DEFAULT_CONFIG_PATH
              if not expected_rawr_config.exists():
                   typer.echo(f"❌ Error: RAWR configuration file not found at {expected_rawr_config} and default agent directory is invalid.", err=True)
              else:
                   typer.echo(f"❌ Error: Agent configuration directory specified or defaulted to '{agent_config_dir}' is invalid. Check rawr.config.yaml.", err=True)
         else:
              typer.echo(f"❌ Error: Agent configuration directory not found at the configured path: {agent_config_dir}", err=True)
         # Return immediately if the directory is invalid
         return final_registry_data, compiled_count, failed_count


    for item in agent_config_dir.iterdir():
        if item.is_dir():
            potential_config_path = item / "config.yaml"
            if potential_config_path.is_file():
                slug_to_compile = item.name
                try:
                    # Pass the *current* state of final_registry_data
                    updated_data = _compile_specific_agent(
                        slug_to_compile,
                        agent_config_dir, # Pass the base dir
                        final_registry_data
                    )
                    final_registry_data = updated_data # Accumulate successful updates
                    compiled_count += 1
                    # Success message now printed by _compile_specific_agent
                except AgentProcessingError as e: # Catch specific processing errors
                    # Error message already printed by _compile_specific_agent
                    logger.warning(f"Compilation failed for agent '{e.agent_slug}'. Skipping registry update for this agent.")
                    typer.echo(f"ℹ️ Skipping registry update for failed agent: '{e.agent_slug}'")
                    failed_count += 1
                except Exception as e: # Catch any other unexpected errors during the loop
                    logger.exception(f"Unexpected error processing directory for agent '{item.name}'")
                    typer.echo(f"❌ Unexpected Error processing directory for agent '{item.name}'. Details: {e}", err=True)
                    failed_count += 1 # Count as failure
            else:
                logger.debug(f"Skipping directory {item.name}, no config.yaml found.")
        else:
             logger.debug(f"Skipping non-directory item: {item.name}")

    return final_registry_data, compiled_count, failed_count


# --- Public Compilation Function ---

def compile_agents(agent_name: Optional[str] = None): # Renamed parameter
    """
    Loads, validates, and compiles agent configuration(s), updating the global registry.

    Args:
        agent_name: The specific agent to compile. If None, compiles all agents. # Updated docstring

    Raises:
        typer.Exit: If compilation fails or critical errors occur (e.g., cannot read/write registry).
    """
    global_registry_path = GLOBAL_REGISTRY_PATH
    agent_config_dir = AGENT_CONFIG_DIR

    # --- Read Initial Global Registry ---
    typer.echo(f"Reading global registry from {global_registry_path}...")
    try:
        initial_registry_data = registry_manager.read_global_registry(global_registry_path)
        typer.echo("✅ Global registry read successfully.")
        logger.info(f"Successfully read global registry from {global_registry_path}")
    except FileNotFoundError:
        logger.warning(f"Global registry file not found at {global_registry_path}. Will create a new one.")
        typer.echo(f"ℹ️ Global registry file not found at {global_registry_path}. A new registry will be created.")
        initial_registry_data = {} # Start with an empty registry
    except Exception as e:
        logger.exception(f"Unexpected error reading global registry from {global_registry_path}")
        typer.echo(f"❌ Error: An unexpected error occurred while reading the global registry. Details: {e}", err=True)
        raise typer.Exit(code=1)

    compiled_count = 0
    failed_count = 0
    final_registry_data = initial_registry_data # Default to initial if no changes

    if agent_name: # Use the renamed parameter
        # --- Compile Single Agent ---
        logger.info(f"Compiler invoked for single agent name: {agent_name}") # Updated log message
        typer.echo(f"--- Compiling Single Agent: {agent_name} ---") # Updated echo message
        try:
            # Pass agent_config_dir explicitly
            # Pass agent_name (which is the slug) to _compile_specific_agent
            final_registry_data = _compile_specific_agent(
                agent_name, agent_config_dir, initial_registry_data
            )
            compiled_count = 1
            # Success message printed by helper
        except AgentProcessingError as e: # agent_slug is still correct within the exception context
            # Error message already printed by helper
            typer.echo(f"\n❌ Compilation failed for agent: '{e.agent_slug}'. Registry not written.", err=True) # Keep e.agent_slug
            raise typer.Exit(code=1)
        except Exception as e:
            logger.exception(f"Unexpected error during single agent compilation flow for '{agent_name}'") # Use agent_name
            typer.echo(f"❌ Unexpected Error during compilation for '{agent_name}'. Details: {e}", err=True) # Use agent_name
            raise typer.Exit(code=1)

    else:
        # --- Compile All Agents ---
        logger.info("Compiler invoked to compile all agents.")
        typer.echo("--- Compiling All Agents ---")

        # Configuration directory check is now inside _compile_all_agents

        try:
            final_registry_data, compiled_count, failed_count = _compile_all_agents(
                agent_config_dir, initial_registry_data
            )
        except Exception as e:
             logger.exception(f"Unexpected error during 'compile all' execution in directory {agent_config_dir}")
             typer.echo(f"❌ Unexpected Error during 'compile all'. Details: {e}", err=True)
             raise typer.Exit(code=1)

        # --- Report Results for Compile All ---
        if compiled_count == 0 and failed_count == 0:
            # This case might happen if the directory exists but contains no valid agent subdirs
            logger.warning(f"No valid agent configurations found to compile in {agent_config_dir}")
            typer.echo(f"\nℹ️ No valid agent configurations found to compile in {agent_config_dir}. Registry not written.")
            # Don't exit with error here, just don't write the registry
        elif failed_count > 0 and compiled_count == 0:
            typer.echo(f"\n❌ Compilation finished. All {failed_count} attempted agent(s) failed. Registry not updated.", err=True)
            raise typer.Exit(code=1)
        elif failed_count > 0:
            typer.echo(f"\n⚠️ Compilation finished with {failed_count} error(s). Registry will be written with {compiled_count} successful update(s).")
        else: # compiled_count > 0 and failed_count == 0
             typer.echo(f"\n✅ Successfully processed {compiled_count} agent(s).")
             typer.echo(f"\n🎉 Finished compiling all {compiled_count} agents successfully.")


    # --- Write Final Global Registry ---
    should_write_registry = compiled_count > 0

    if should_write_registry:
        typer.echo(f"\nWriting updated global registry to {global_registry_path}...")
        try:
            registry_manager.write_global_registry(
                registry_path=global_registry_path,
                registry_data=final_registry_data
            )
            typer.echo(f"✅ Global registry successfully written.")
            logger.info(f"Successfully wrote updated global registry to {global_registry_path}")
        except Exception as e:
            logger.exception(f"Unexpected error writing final global registry to {global_registry_path}")
            typer.echo(f"❌ Error: An unexpected error occurred while writing the final global registry. Details: {e}", err=True)
            raise typer.Exit(code=1)
    elif not agent_name and failed_count == 0: # Use agent_name
         pass # Message already printed above for this case
    elif failed_count > 0: # Don't print if errors occurred (already handled)
         pass
    else: # Should not happen unless single agent failed (already handled)
         logger.debug("Registry write skipped as no agents were successfully compiled.")


    # Final summary message
    if agent_name and compiled_count > 0: # Use agent_name
         typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent: '{agent_name}'") # Use agent_name
    # 'compile all' summary messages are handled within the 'else' block above