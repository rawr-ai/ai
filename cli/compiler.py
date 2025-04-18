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
from .config_loader import discover_config_files # <-- Added import
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
        # Determine the description, prioritizing config.description
        description = config.description
        if not description: # Fallback to roleDefinition if description is None or empty
            description = config.roleDefinition
            # Truncate roleDefinition if it's used as the description
            max_len = 150
            if len(description) > max_len:
                description = description[:max_len] + "..."

        metadata = {
            "slug": config.slug,
            "name": config.name,
            "description": description, # Use the determined description
            # Add other fields from GlobalAgentConfig as needed for the registry
            # e.g., "author": config.author, "tags": config.tags
        }
        logger.debug(f"Successfully extracted metadata for {config.slug}")
        return metadata
    except AttributeError as e:
        logger.error(f"Missing expected attribute in GlobalAgentConfig for slug '{config.slug}': {e}", exc_info=True)
        # Re-raise as this indicates a programming error (model vs. access)
        raise AttributeError(f"Internal Error: Missing expected attribute '{e.name}' in validated config for agent '{config.slug}'.")


def _compile_specific_agent(
    config_path: Path, # Changed: Now accepts the full path
    current_registry_data: Dict[str, Any]
) -> Tuple[Optional[GlobalAgentConfig], bool]: # Return config object and success flag
    """
    Loads, validates, and extracts metadata for a single agent config using its full path.

    Args:
        config_path: The full path to the agent configuration file (e.g., 'agents/subdir/my_agent.yaml').
        current_registry_data: The current state of the global registry data (passed for context, not modified here).

    Returns:
        A tuple containing:
            - agent_config: The validated GlobalAgentConfig object if successful, None otherwise.
            - success: Boolean indicating if the compilation was successful.

    Raises:
        AgentLoadError: If the config file cannot be found, read, or parsed.
        AgentValidationError: If the config data fails schema validation.
        AgentCompileError: If metadata extraction fails (due to internal errors).
        AgentProcessingError: For other unexpected errors during processing.
        (These exceptions are caught by the caller, _compile_all_agents or compile_agents)
    """
    # Use the full path for initial identification before we know the validated slug
    config_identifier = str(config_path)
    logger.info(f"Attempting to compile agent config: {config_identifier}")

    # 1. Load and Validate Agent Config
    typer.echo(f"Processing '{config_identifier}': Loading and validating config...")
    try:
        if not config_path.exists():
             raise FileNotFoundError(f"Agent config file not found at {config_identifier}")
        config_content = config_path.read_text()
        config_data = yaml.safe_load(config_content)
        if not isinstance(config_data, dict):
             raise ValueError(f"Config file {config_identifier} did not parse into a dictionary.")
        # Validate the configuration using the Pydantic model
        agent_config = GlobalAgentConfig.model_validate(config_data)
        # --- Slug is now definitively known from the validated config ---
        validated_slug = agent_config.slug
        logger.info(f"Successfully loaded and validated config for agent '{validated_slug}' from {config_identifier}")
    except FileNotFoundError as e:
        logger.error(f"Agent config file not found at {config_identifier}")
        msg = f"Config file not found at {config_identifier}"
        # Use config_identifier for error reporting as slug is unknown
        raise AgentLoadError(msg, agent_slug=config_identifier, original_exception=e)
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing failed for {config_identifier}: {e}")
        msg = f"Failed to parse YAML for {config_identifier}. Details:\n{e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        # Use config_identifier for error reporting as slug is unknown
        raise AgentLoadError(msg, agent_slug=config_identifier, original_exception=e)
    except PydanticValidationError as e: # Catch Pydantic's specific error
        logger.error(f"Config validation failed for {config_identifier}: {e}")
        # Format Pydantic errors for better readability
        error_details = "\n".join([f"  - {'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()])
        msg = f"Config validation failed for {config_identifier}. Details:\n{error_details}"
        typer.echo(f"❌ Error validating {config_identifier}: {msg}", err=True)
        # Use config_identifier for error reporting as slug is unknown
        raise AgentValidationError(msg, agent_slug=config_identifier, original_exception=e)
    except Exception as e:
        logger.exception(f"Unexpected error loading/validating config from {config_identifier}")
        msg = f"An unexpected error occurred loading/validating config from {config_identifier}. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        # Use config_identifier for error reporting as slug is unknown
        raise AgentProcessingError(msg, agent_slug=config_identifier, original_exception=e)

    # 2. Extract Metadata
    typer.echo(f"Processing '{validated_slug}': Extracting metadata...") # Use validated slug
    try:
        # Call the extraction function (already uses agent_config.slug internally)
        registry_metadata = extract_registry_metadata(agent_config)
        logger.info(f"Successfully extracted metadata for {validated_slug}") # Use validated slug
    except Exception as e:
        # Catch AttributeError specifically from metadata extraction, or any other Exception
        logger.exception(f"Error extracting metadata for {validated_slug}") # Use validated slug
        msg = f"Failed to extract metadata for {validated_slug}. Details: {e}" # Use validated slug
        typer.echo(f"❌ Error extracting metadata for {validated_slug}: {msg}", err=True) # Use validated slug
        # Raise AgentCompileError for issues during this phase
        raise AgentCompileError(msg, agent_slug=validated_slug, original_exception=e) # Use validated slug

    # 3. Return Metadata and Success
    # The registry update happens in the calling function (_compile_all_agents or compile_agents)
    typer.echo(f"✅ Successfully processed agent: '{validated_slug}' from {config_identifier}") # Use validated slug
    return agent_config, True # Return the full validated config object


def _compile_all_agents(
    agent_config_base_dir: Path,
    initial_registry_data: Dict[str, Any]
) -> Tuple[Dict[str, Any], list[str], list[str]]: # Return lists of slugs/paths
    """
    Scans the agent directory, compiles all valid agents, and accumulates results.

    Args:
        agent_config_base_dir: The directory containing agent configurations.
        initial_registry_data: The starting state of the global registry.

    Returns:
        A tuple containing:
        - final_registry_data: The registry data (note: actual updates happen via RegistryManager).
        - successful_agents: A list of slugs for successfully compiled agents.
        - failed_agents: A list of slugs/paths for agents that failed compilation or registry update.
    """
    logger.info(f"Scanning for agent configurations in: {agent_config_base_dir}")
    typer.echo(f"Scanning for agent configurations in: {agent_config_base_dir}")

    successful_agents = []
    failed_agents = []
    # Note: final_registry_data is less relevant now as updates happen via manager
    final_registry_data = initial_registry_data.copy()

    if not agent_config_base_dir or not agent_config_base_dir.exists() or not agent_config_base_dir.is_dir():
         msg = f"Invalid base directory provided: {agent_config_base_dir}"
         logger.error(msg)
         typer.echo(f"❌ Error: {msg}", err=True)
         # Raise error instead of returning, let caller handle it
         raise AgentProcessingError(msg) # No specific agent slug here


    # Use the new helper function to discover config files
    config_files = discover_config_files(agent_config_base_dir)
    logger.info(f"Discovered {len(config_files)} potential agent config files.")

    if not config_files:
        logger.warning(f"No config files found in {agent_config_base_dir}.")
        # Return early if no files found, lists remain empty
        return final_registry_data, successful_agents, failed_agents

    for config_path in config_files:
        config_identifier = str(config_path) # Use path for initial logging/error reporting
        actual_slug = config_identifier # Default slug to path if validation fails early
        logger.debug(f"Processing discovered config file: {config_identifier}")
        try:
            agent_config, success = _compile_specific_agent(
                config_path,
                initial_registry_data
            )
            if success and agent_config:
                actual_slug = agent_config.slug # Get validated slug
                try:
                    logger.debug(f"Attempting registry update for agent: {actual_slug}")
                    registry_manager.update_global_registry(agent_config)
                    successful_agents.append(actual_slug) # Add slug to success list
                    logger.info(f"Successfully updated registry for '{actual_slug}' via RegistryManager.")
                except Exception as update_err:
                    logger.error(f"Failed to update registry for agent '{actual_slug}': {update_err}", exc_info=True)
                    typer.echo(f"❌ Error updating registry for '{actual_slug}': {update_err}", err=True)
                    failed_agents.append(actual_slug) # Add slug to failure list
            elif success: # Should not happen
                logger.error(f"Compilation reported success for {config_identifier}, but agent_config object was None.")
                failed_agents.append(config_identifier) # Add path to failure list
            # else case removed as _compile_specific_agent raises exceptions

        except AgentProcessingError as e:
            # e.agent_slug might be the path or the validated slug depending on where error occurred
            logger.warning(f"Compilation failed for agent config '{config_identifier}' (reported slug/path: '{e.agent_slug}'). Skipping registry update.")
            failed_agents.append(e.agent_slug) # Add reported slug/path to failure list
        except Exception as e:
            logger.exception(f"Unexpected error processing file: {config_identifier}")
            typer.echo(f"❌ Unexpected Error processing file '{config_identifier}'. Details: {e}", err=True)
            failed_agents.append(config_identifier) # Add path to failure list

    return final_registry_data, successful_agents, failed_agents


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
    # Message moved to later, before write attempt
    try:
        initial_registry_data = registry_manager.read_global_registry(global_registry_path)
        logger.info(f"Successfully read global registry from {global_registry_path}")
    except FileNotFoundError:
        logger.warning(f"Global registry file not found at {global_registry_path}. Will create a new one.")
        typer.echo(f"ℹ️ Global registry file not found at {global_registry_path}. A new registry will be created.")
        initial_registry_data = {} # Start with an empty registry
    except Exception as e:
        logger.exception(f"Unexpected error reading global registry from {global_registry_path}")
        msg = f"An unexpected error occurred while reading the global registry. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        # Exit immediately if registry read fails critically
        raise typer.Exit(code=1)

    compiled_count = 0 # Keep track for single agent case
    failed_count = 0   # Keep track for single agent case
    successful_agents = [] # For 'all' case
    failed_agents = []     # For 'all' case
    final_registry_data = initial_registry_data # Still needed for write operation

    if agent_slug:
        # --- Compile Single Agent ---
        logger.info(f"Compiler invoked for single agent slug: {agent_slug}") # Updated log message
        typer.echo(f"--- Compiling Single Agent: {agent_slug} ---") # Updated echo message
        try:
            # Pass agent_config_dir explicitly
            # Pass agent_slug to _compile_specific_agent
            # _compile_specific_agent now returns (metadata, success)

            # --- Resolve Config Path for Single Agent ---
            # Primary path: <agents_base_dir>/<slug>/config.yaml
            primary_path = agent_config_dir / agent_slug / "config.yaml"
            # Fallback path: <agents_base_dir>/<slug>.yaml
            fallback_path = agent_config_dir / f"{agent_slug}.yaml"

            single_agent_config_path = None
            if primary_path.exists():
                single_agent_config_path = primary_path
                logger.info(f"Found agent config for '{agent_slug}' at primary path: {primary_path}")
            elif fallback_path.exists():
                single_agent_config_path = fallback_path
                logger.info(f"Found agent config for '{agent_slug}' at fallback path: {fallback_path}")
                typer.echo(f"ℹ️ Using fallback config path: {fallback_path}") # Inform user about fallback
            else:
                msg = (f"Agent config file not found for slug '{agent_slug}'. "
                       f"Checked primary path: {primary_path} and fallback path: {fallback_path}")
                logger.error(msg)
                typer.echo(f"❌ Error: {msg}", err=True)
                raise AgentLoadError(msg, agent_slug=agent_slug) # Raise specific error

            # Pass the resolved path
            # Now returns agent_config object instead of metadata
            agent_config, success = _compile_specific_agent(
                single_agent_config_path, initial_registry_data # Pass initial data for context
            )
            if success and agent_config: # Check agent_config is not None
                 # --- Update registry using the manager ---
                 try:
                     actual_slug = agent_config.slug # Get slug directly from validated config
                     # Warn if the slug in the file doesn't match the filename/input slug
                     if actual_slug != agent_slug:
                         logger.warning(f"Slug in config file ('{actual_slug}') does not match the requested slug/filename ('{agent_slug}') for path {single_agent_config_path}. Using slug from config file.")
                         typer.echo(f"⚠️ Warning: Slug in config file ('{actual_slug}') differs from filename ('{agent_slug}'). Using '{actual_slug}'.")

                     logger.debug(f"Attempting registry update for agent: {actual_slug}")
                     registry_manager.update_global_registry(agent_config) # Call the manager method
                     compiled_count = 1
                     logger.info(f"Successfully updated registry for '{actual_slug}' via RegistryManager.")
                     # Note: We are no longer directly modifying final_registry_data here.
                 except Exception as update_err:
                     # Handle potential errors during the update itself
                     logger.error(f"Failed to update registry for agent '{actual_slug}': {update_err}", exc_info=True)
                     typer.echo(f"❌ Error updating registry for '{actual_slug}': {update_err}", err=True)
                     failed_count = 1 # Mark as failed
                     compiled_count = 0 # Reset compiled count on update failure
            elif success: # Safety check
                 logger.error(f"Compilation reported success for {single_agent_config_path}, but agent_config object was None.")
                 failed_count = 1
                 compiled_count = 0
            else:
                 # Should not happen if exceptions are raised correctly
                 failed_count = 1
                 compiled_count = 0
            # Success message printed by helper
        except AgentProcessingError as e: # agent_slug from exception might be path or validated slug
            # Error message already printed by helper
            typer.echo(f"\n❌ Compilation failed for agent config related to '{agent_slug}'. Registry not written.", err=True)
            raise typer.Exit(code=1) # Exit on single agent failure
        except Exception as e:
            logger.exception(f"Unexpected error during single agent compilation flow for requested slug '{agent_slug}'")
            typer.echo(f"❌ Unexpected Error during compilation for requested slug '{agent_slug}'. Details: {e}", err=True)
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
    # Use the *actual* slug from metadata for the final success message if available
    if agent_slug and compiled_count > 0 and 'actual_slug' in locals() and actual_slug:
         typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent: '{actual_slug}'")
    elif agent_slug and compiled_count > 0: # Fallback if actual_slug wasn't set (shouldn't happen on success)
         typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent related to input: '{agent_slug}'")
    # 'compile all' summary messages are handled within the 'else' block above