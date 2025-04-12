# cli/main.py
import typer
import logging
from pathlib import Path
from typing_extensions import Annotated
from typing import Optional, Dict, Any

import os # Needed for os.path.join and os.listdir
import yaml # Added for parsing
from . import config_loader
from . import compiler
from . import registry_manager
from .models import GlobalAgentConfig # Added for validation
from pydantic import ValidationError as ConfigValidationError # Use Pydantic's error
from typing import Tuple # Added for type hinting
# from . import config_loader # This was duplicated, removed. The one above is sufficient.
# --- Constants & Configuration ---
# Assuming the global registry path is defined in constants
# Paths are now loaded via the centralized config_loader
GLOBAL_REGISTRY_PATH = config_loader.get_global_registry_path()
AGENT_CONFIG_DIR = config_loader.get_agent_config_dir()
# --- Logging Setup ---
# Basic logging configuration (can be enhanced later)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Typer App Initialization ---
app = typer.Typer(
    name="agent-config-cli",
    help="CLI tool to manage Agent Configurations.", # Updated help text
    add_completion=False,
)


@app.callback()
def main_callback():
    """
    Main callback for the CLI application. Currently does nothing.
    """
    pass # Explicitly define that the main app takes no arguments itself



# --- CLI Commands ---







# --- Custom Exceptions ---
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


# --- Helper Function for Single Agent Compilation ---
def _compile_single_agent(agent_slug: str, current_registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads, validates, compiles a single agent config and updates registry data in memory.

    Args:
        agent_slug: The slug of the agent to compile.
        current_registry_data: The current state of the global registry data.

    Returns:
        The updated registry data.

    Raises:
        AgentLoadError: If the config file cannot be found, read, or parsed.
        AgentValidationError: If the config data fails schema validation.
        AgentCompileError: If metadata extraction or registry update fails.
        AgentProcessingError: For other unexpected errors during processing.
    """
    logger.info(f"Attempting to compile agent: {agent_slug}")
    agent_config_path = AGENT_CONFIG_DIR / agent_slug / "config.yaml"
    global_registry_path = GLOBAL_REGISTRY_PATH # Needed for logging/messages? Or remove? Keep for now.

    # 1. Load and Validate Agent Config
    typer.echo(f"Processing '{agent_slug}': Loading and validating config...")
    try:
        config_content = agent_config_path.read_text()
        config_data = yaml.safe_load(config_content)
        if not isinstance(config_data, dict):
             # Use Pydantic's validation error structure for consistency if possible,
             # but a simple ValueError is fine for now.
             raise ValueError(f"Config file {agent_config_path} did not parse into a dictionary.")
        agent_config = GlobalAgentConfig.model_validate(config_data)
        logger.info(f"Successfully loaded and validated config for {agent_slug}")
    except FileNotFoundError:
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
        registry_metadata = compiler.extract_registry_metadata(agent_config)
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
        return updated_registry_data # Return the updated data
    except Exception as e:
        logger.exception(f"Unexpected error updating global registry data for {agent_slug}")
        msg = f"An unexpected error occurred updating registry data. Details: {e}"
        typer.echo(f"❌ Error: {msg}", err=True)
        raise AgentCompileError(msg, agent_slug, e)


# --- Helper Function for Compiling All Agents ---
def _compile_all_agents(agent_config_dir: Path, initial_registry_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
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

    for item in agent_config_dir.iterdir():
        if item.is_dir():
            potential_config_path = item / "config.yaml"
            if potential_config_path.is_file():
                slug_to_compile = item.name
                try:
                    # Pass the *current* state of final_registry_data
                    updated_data = _compile_single_agent(slug_to_compile, final_registry_data)
                    final_registry_data = updated_data # Accumulate successful updates
                    compiled_count += 1
                    typer.echo(f"✅ Successfully processed agent: '{slug_to_compile}'")
                except AgentProcessingError as e: # Catch base exception and its children
                    # Error message already printed by _compile_single_agent
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


# --- CLI Command ---

@app.command("compile")
def compile_agent_config(
    agent_slug: Annotated[
        Optional[str], # Make the argument optional
        typer.Argument( # Default value removed from here
            help="The unique slug of the agent to compile. If omitted, compiles all agents found in the config directory."
        ),
    ] = None # Typer needs the default here too
):
    """
    Loads, validates, and compiles agent configuration(s), updating the global registry.
    If AGENT_SLUG is provided, compiles only that agent.
    If AGENT_SLUG is omitted, compiles all valid agents found in the configured directory.
    """
    global_registry_path = GLOBAL_REGISTRY_PATH # Use module-level constant loaded via config_loader
    agent_config_dir = AGENT_CONFIG_DIR # Use module-level constant loaded via config_loader

    # --- Configuration Sanity Checks ---
    # Check if the config loader successfully found/defaulted the paths
    # Note: config_loader prints warnings if files are missing/invalid but provides defaults.
    # We need to check if the *resulting* paths are usable, especially agent_config_dir.

    # Check if the determined agent_config_dir actually exists, crucial for "compile all"
    if not agent_slug and (not agent_config_dir or not agent_config_dir.is_dir()):
         # This error takes precedence over registry reading if compiling all
         logger.error(f"Agent configuration directory not found or invalid: {agent_config_dir}")
         # Check if the path matches the default, implying rawr.config.yaml might be missing/invalid
         if agent_config_dir == config_loader.DEFAULT_AGENT_CONFIG_DIR:
              # Attempt to determine the expected default config path for a better error message
              expected_rawr_config = config_loader.DEFAULT_CONFIG_PATH
              if not expected_rawr_config.exists():
                   typer.echo(f"❌ Error: RAWR configuration file not found at {expected_rawr_config} and default agent directory is invalid.", err=True)
              else:
                   typer.echo(f"❌ Error: Agent configuration directory specified or defaulted to '{agent_config_dir}' is invalid. Check rawr.config.yaml.", err=True)

         else:
              typer.echo(f"❌ Error: Agent configuration directory not found at the configured path: {agent_config_dir}", err=True)
         raise typer.Exit(code=1)


    # --- Read Initial Global Registry ---
    # Proceed with reading the registry only after confirming agent_config_dir is potentially usable (for compile all)
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
        raise typer.Exit(code=1) # Exit if registry read fails fundamentally

    compiled_count = 0
    failed_count = 0
    # final_registry_data will be determined by the compilation functions

    if agent_slug:
        # --- Compile Single Agent ---
        logger.info(f"CLI 'compile' command invoked for single agent slug: {agent_slug}")
        typer.echo(f"--- Compiling Single Agent: {agent_slug} ---")
        try:
            final_registry_data = _compile_single_agent(agent_slug, initial_registry_data)
            compiled_count = 1
            # Success message printed by helper
        except AgentProcessingError as e:
            # Error message already printed by helper
            typer.echo(f"\n❌ Compilation failed for agent: '{e.agent_slug}'. Registry not written.", err=True)
            raise typer.Exit(code=1) # Exit with error if single compile fails
        except Exception as e: # Catch unexpected errors here too
            logger.exception(f"Unexpected error during single agent compilation flow for '{agent_slug}'")
            typer.echo(f"❌ Unexpected Error during compilation for '{agent_slug}'. Details: {e}", err=True)
            raise typer.Exit(code=1)

    else:
        # --- Compile All Agents ---
        logger.info("CLI 'compile' command invoked to compile all agents.")
        typer.echo("--- Compiling All Agents ---")
        # agent_config_dir validity check is done before registry read

        try:
            final_registry_data, compiled_count, failed_count = _compile_all_agents(
                agent_config_dir, initial_registry_data
            )
        except Exception as e: # Catch unexpected errors during the overall 'all' process
             logger.exception(f"Unexpected error during 'compile all' execution in directory {agent_config_dir}")
             typer.echo(f"❌ Unexpected Error during 'compile all'. Details: {e}", err=True)
             raise typer.Exit(code=1)

        # --- Report Results for Compile All ---
        if compiled_count == 0 and failed_count == 0:
            # No agent directories with config.yaml were found at all
            logger.error(f"No valid agent configurations found to compile in {agent_config_dir}")
            typer.echo(f"\n❌ Error: No valid agent configurations found to compile in {agent_config_dir}", err=True)
            raise typer.Exit(code=1)
        elif failed_count > 0 and compiled_count == 0:
            # Agents were found and attempted, but all failed
            typer.echo(f"\n❌ Compilation finished. All {failed_count} attempted agent(s) failed. Registry not updated.", err=True)
            # Do not proceed to write registry if nothing succeeded
            raise typer.Exit(code=1) # Treat as overall failure if nothing compiled
        elif failed_count > 0:
            # Partial success
            typer.echo(f"\n⚠️ Compilation finished with {failed_count} error(s). Registry will be written with {compiled_count} successful update(s).")
        else:
            # All success
            typer.echo(f"\n✅ Successfully processed {compiled_count} agent(s).")
            # Re-add the final summary message for the all-success case
            typer.echo(f"\n🎉 Finished compiling all {compiled_count} agents successfully.")


    # --- Write Final Global Registry (Common for both single and all) ---
    # Only write if at least one agent was processed successfully (or if single agent was successful)
    # Write registry if any agents were successfully compiled
    # (even if initial_registry_data was empty and final_registry_data now has content)
    # Also write if a single agent was successfully compiled (agent_slug case)
    should_write_registry = compiled_count > 0 # Write if at least one agent succeeded (single or all)

    if should_write_registry:
        typer.echo(f"\nWriting updated global registry to {global_registry_path}...")
        try:
            registry_manager.write_global_registry(
                registry_path=global_registry_path,
                registry_data=final_registry_data # Use the potentially updated data
            )
            typer.echo(f"✅ Global registry successfully written.")
            logger.info(f"Successfully wrote updated global registry to {global_registry_path}")
        except Exception as e:
            logger.exception(f"Unexpected error writing final global registry to {global_registry_path}")
            typer.echo(f"❌ Error: An unexpected error occurred while writing the final global registry. Details: {e}", err=True)
            # If write fails after successful compiles, it's still an error
            raise typer.Exit(code=1)
    else:
        # Only print this if we didn't attempt to write
        # Only print this if we didn't attempt to write because nothing succeeded
        if not agent_slug: # Don't print for single agent failure (already handled)
             typer.echo("\nℹ️ No successful compilations. Registry file not written.")


    # Final summary message (already printed for 'compile all' cases above)
    if agent_slug and compiled_count > 0: # Only print for single agent success
         typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent: '{agent_slug}'")
    # 'compile all' summary messages are handled within the 'else' block above

    # Removed the outer try...except typer.Exit block
    # The individual try...except blocks within each step already handle raising typer.Exit(1)
    # A final catch-all might be added later if needed, but this structure should allow
    # the patched typer.Exit in tests to be asserted correctly.


# --- Entry Point Execution ---
if __name__ == "__main__":
    app()
