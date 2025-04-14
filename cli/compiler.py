"""
Handles the loading, validation, and compilation of agent configurations
into the global agent registry.
"""
import typer
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import yaml
from pydantic import ValidationError as PydanticValidationError # Alias for clarity

# Local imports
from . import config_loader
from . import registry_manager
from .models import GlobalAgentConfig
from .exceptions import ( # Import new exceptions
    AgentProcessingError,
    AgentLoadError,
    AgentValidationError,
    AgentCompileError,
    RegistryReadError,
    RegistryWriteError
)

# --- Logging Setup ---
# Use the same logger name pattern as main.py or a dedicated one
logger = logging.getLogger(__name__)

# --- Constants ---
# Load paths using the centralized config loader
AGENT_CONFIG_DIR = config_loader.get_agent_config_dir()
GLOBAL_REGISTRY_PATH = config_loader.get_global_registry_path()

# Custom exceptions are now defined in cli/exceptions.py


# --- Internal Helper Functions (Adapted from main.py) ---

def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
    """
    Extracts relevant metadata from a validated GlobalAgentConfig object.

    Args:
        config: The validated GlobalAgentConfig object.

    Returns:
        A dictionary containing the agent's metadata for the registry.

    Raises:
        AttributeError: If required attributes are missing from the config object.
                        (This indicates an issue with the model or validation)
    """
    logger.debug(f"Extracting metadata for agent: {config.slug}")
    try:
        # Access required fields directly. If validation passed, these should exist.
        # Pydantic models raise AttributeError if a field is accessed but missing
        # (though validation should prevent this unless the model itself is flawed).
        # Extract all fields intended for the registry from the validated config
        # Use direct access for required fields, getattr for optional ones
        metadata = {
            "slug": config.slug,
            "name": config.name,
            "roleDefinition": config.roleDefinition, # Required field
            "groups": config.groups, # Required field
            "description": getattr(config, 'description', None),
            "version": getattr(config, 'version', '0.1.0'), # Default handled here if not in config
            # Note: customInstructions is explicitly excluded by registry_manager.update_global_registry
        }

        # Handle optional apiConfiguration: serialize if present
        api_config = getattr(config, 'apiConfiguration', None)
        if api_config:
            # Use model_dump() for Pydantic v2+ serialization
            metadata["apiConfiguration"] = api_config.model_dump(mode='json') # Use mode='json' for JSON-compatible types

        # Filter out None values for optional fields AFTER potentially adding apiConfiguration
        metadata = {k: v for k, v in metadata.items() if v is not None}
        logger.debug(f"Successfully extracted metadata for {config.slug}")
        return metadata
    except AttributeError as e:
        logger.error(f"Missing expected attribute in GlobalAgentConfig for slug '{config.slug}': {e}", exc_info=True)
        # Re-raise as this indicates a programming error (model vs. access)
        raise AttributeError(f"Internal Error: Missing expected attribute '{e.name}' in validated config for agent '{config.slug}'.")


def _compile_specific_agent(
    agent_slug: str,
    agent_config_base_dir: Path, # Renamed for clarity
    current_registry_data: Dict[str, Any] # Keep this for potential future use? Or remove? Test implies it's needed.
) -> Tuple[Dict[str, Any], bool]: # Return metadata and success flag
    """
    Loads, validates, and extracts metadata for a single agent config.

    Args:
        agent_slug: The slug of the agent to compile.
        agent_config_base_dir: The base directory containing agent configurations (e.g., 'agents/').
        current_registry_data: The current state of the global registry data (passed for context, not modified here).

    Returns:
        A tuple containing:
            - agent_metadata: Dictionary of extracted metadata if successful, empty dict otherwise.
            - success: Boolean indicating if the compilation was successful.

    Raises:
        AgentLoadError: If the config file cannot be found, read, or parsed.
        AgentValidationError: If the config data fails schema validation.
        AgentCompileError: If metadata extraction fails (due to internal errors).
        AgentProcessingError: For other unexpected errors during processing.
        (These exceptions are caught by the caller, _compile_all_agents)
    """
    logger.info(f"Attempting to compile agent: {agent_slug}")
    # Config file is expected to be directly in the base dir, named <slug>.yaml
    agent_config_path = agent_config_base_dir / f"{agent_slug}.yaml"

    # 1. Load and Validate Agent Config
    typer.echo(f"Processing '{agent_slug}': Loading and validating config...")
    try:
        if not agent_config_path.exists():
             raise FileNotFoundError(f"Agent config file not found at {agent_config_path}")
        config_content = agent_config_path.read_text()
        config_data = yaml.safe_load(config_content)
        if not isinstance(config_data, dict):
             raise ValueError(f"Config file {agent_config_path} did not parse into a dictionary.")
        # Assuming a validation function exists or using Pydantic directly
        # Replace `validate_config` if it was a placeholder
        agent_config = GlobalAgentConfig.model_validate(config_data)
        logger.info(f"Successfully loaded and validated config for {agent_slug}")
    except FileNotFoundError as e:
        logger.error(f"Agent config file not found at {agent_config_path}")
        msg = f"Config file not found at {agent_config_path}"
        raise AgentLoadError(msg, agent_slug=agent_slug, original_exception=e)
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing failed for {agent_config_path}: {e}")
        msg = f"Failed to parse YAML. Details:\n{e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentLoadError(msg, agent_slug=agent_slug, original_exception=e)
    except PydanticValidationError as e: # Catch Pydantic's specific error
        logger.error(f"Config validation failed for {agent_slug}: {e}")
        # Format Pydantic errors for better readability if desired
        error_details = "\n".join([f"  - {err['loc']}: {err['msg']}" for err in e.errors()])
        msg = f"Config validation failed. Details:\n{error_details}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentValidationError(msg, agent_slug=agent_slug, original_exception=e)
    except Exception as e:
        logger.exception(f"Unexpected error loading/validating config for {agent_slug}")
        msg = f"An unexpected error occurred loading/validating config. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentProcessingError(msg, agent_slug=agent_slug, original_exception=e)

    # 2. Extract Metadata
    typer.echo(f"Processing '{agent_slug}': Extracting metadata...")
    try:
        # Call the actual (now defined) extraction function
        registry_metadata = extract_registry_metadata(agent_config)
        logger.info(f"Successfully extracted metadata for {agent_slug}")
    except Exception as e:
        # Catch AttributeError specifically from metadata extraction, or any other Exception
        logger.exception(f"Error extracting metadata for {agent_slug}")
        msg = f"Failed to extract metadata. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        # Raise AgentCompileError for issues during this phase
        raise AgentCompileError(msg, agent_slug=agent_slug, original_exception=e)

    # 3. Return Metadata and Success
    # The registry update happens in the calling function (_compile_all_agents or compile_agents)
    typer.echo(f"✅ Successfully processed agent: '{agent_slug}'")
    return registry_metadata, True


def _compile_all_agents(
    agent_config_base_dir: Path, # Renamed for clarity
    initial_registry_data: Dict[str, Any] # Keep initial registry state
) -> Tuple[Dict[str, Any], int, int]:
    """
    Scans the agent directory, compiles all valid agents, and accumulates results.

    Args:
        agent_config_base_dir: The directory containing agent configurations (e.g., 'agents/').
        initial_registry_data: The starting state of the global registry (used as base).

    Returns:
        A tuple containing:
        - final_registry_data: The registry data after processing all agents.
        - compiled_count: The number of successfully compiled agents.
        - failed_count: The number of agents that failed to compile.
    """
    logger.info(f"Scanning for agent configurations in: {agent_config_base_dir}")
    typer.echo(f"Scanning for agent configurations in: {agent_config_base_dir}")

    compiled_count = 0
    failed_count = 0
    final_registry_data = initial_registry_data.copy() # Start with initial data

    if not agent_config_base_dir or not agent_config_base_dir.exists() or not agent_config_base_dir.is_dir():
         msg = f"Invalid base directory provided: {agent_config_base_dir}"
         logger.error(msg)
         typer.echo(f"❌ Error: {msg}", err=True)
         # Raise error instead of returning, let caller handle it
         raise AgentProcessingError(msg) # No specific agent slug here


    # Iterate through .yaml files in the base directory
    for item in agent_config_base_dir.iterdir():
        if item.is_file() and item.suffix.lower() == '.yaml':
            slug_to_compile = item.stem # Use filename stem as slug
            logger.debug(f"Found potential agent config: {item.name}, slug: {slug_to_compile}")
            try:
                # Pass the initial registry data for context, but don't expect modification
                agent_metadata, success = _compile_specific_agent(
                    slug_to_compile,
                    agent_config_base_dir,
                    initial_registry_data # Pass initial for context if needed by helper
                )
                if success:
                    # Use the registry manager helper to correctly update the list structure
                    final_registry_data = registry_manager.update_global_registry(
                        final_registry_data, agent_metadata
                    )
                    compiled_count += 1
                    # Logger message in update_global_registry is sufficient
                else:
                    # _compile_specific_agent should raise an exception on failure now
                    # This 'else' block might be redundant if exceptions are always raised on failure.
                    # However, keeping it handles the theoretical case where it returns False without exception.
                    logger.warning(f"Compilation reported as failed for agent '{slug_to_compile}' but no exception was caught.")
                    failed_count += 1

            except AgentProcessingError as e: # Catch specific processing errors from helper
                # Error message already printed by _compile_specific_agent
                logger.warning(f"Compilation failed for agent '{e.agent_slug}'. Skipping registry update for this agent.")
                # typer.echo(f"ℹ️ Skipping registry update for failed agent: '{e.agent_slug}'") # Redundant? Helper prints error.
                failed_count += 1
            except Exception as e: # Catch any other unexpected errors during the loop
                logger.exception(f"Unexpected error processing file for agent '{slug_to_compile}'")
                typer.echo(f"❌ Unexpected Error processing file for agent '{slug_to_compile}'. Details: {e}", err=True)
                failed_count += 1 # Count as failure
        else:
             logger.debug(f"Skipping non-YAML file or directory: {item.name}")

    return final_registry_data, compiled_count, failed_count


# --- Public Compilation Function ---

def compile_agents(agent_slug: Optional[str] = None): # Renamed parameter
    """
    Loads, validates, and compiles agent configuration(s), updating the global registry.

    Args:
        agent_slug: The specific agent slug to compile. If None, compiles all agents. # Updated docstring

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
        msg = f"An unexpected error occurred while reading the global registry. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise RegistryReadError(msg) from e # Raise specific registry error

    compiled_count = 0
    failed_count = 0
    final_registry_data = initial_registry_data # Default to initial if no changes

    if agent_slug: # Use the renamed parameter
        # --- Compile Single Agent ---
        logger.info(f"Compiler invoked for single agent slug: {agent_slug}") # Updated log message
        typer.echo(f"--- Compiling Single Agent: {agent_slug} ---") # Updated echo message
        try:
            # Pass agent_config_dir explicitly
            # Pass agent_slug to _compile_specific_agent
            # _compile_specific_agent now returns (metadata, success)
            agent_metadata, success = _compile_specific_agent(
                agent_slug, agent_config_dir, initial_registry_data
            )
            if success:
                 # Use the registry manager helper to correctly update the list structure
                 final_registry_data = registry_manager.update_global_registry(
                     final_registry_data, agent_metadata
                 )
                 compiled_count = 1
            else:
                 # Should not happen if exceptions are raised correctly
                 failed_count = 1
                 compiled_count = 0
            compiled_count = 1
            # Success message printed by helper
        except AgentProcessingError as e: # agent_slug is still correct within the exception context
            # Error message already printed by helper
            # Error message already printed by helper
            typer.echo(f"\n❌ Compilation failed for agent: '{e.agent_slug}'. Registry not written.", err=True)
            raise typer.Exit(code=1) # Exit on single agent failure
        except Exception as e:
            logger.exception(f"Unexpected error during single agent compilation flow for '{agent_slug}'") # Use agent_slug
            typer.echo(f"❌ Unexpected Error during compilation for '{agent_slug}'. Details: {e}", err=True) # Use agent_slug
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
            # Don't necessarily exit here, allow reporting below
            # Set counts to indicate failure
            failed_count = failed_count or 1 # Ensure failure is marked if exception occurred before loop finished

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
    # Determine if registry should be written based on outcome
    # Write if at least one agent succeeded, even if others failed (for 'all' mode)
    # Write if the single agent succeeded (for 'single' mode)
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
            msg = f"An unexpected error occurred while writing the final global registry. Details: {e}"
            logger.exception(msg)
            typer.echo(f"❌ Error: {msg}", err=True)
            raise RegistryWriteError(msg) from e # Raise specific registry error
    elif not agent_slug and failed_count == 0 and compiled_count == 0: # Use agent_slug
         pass # Message already printed above for this case
    elif failed_count > 0: # Don't print if errors occurred (already handled)
         pass
    else: # Should not happen unless single agent failed (already handled)
         logger.debug("Registry write skipped as no agents were successfully compiled.")


    # Final summary message for single agent success
    if agent_slug and compiled_count > 0: # Use agent_slug
         typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent: '{agent_slug}'") # Use agent_slug
    # 'compile all' summary messages are handled within the 'else' block above