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








# --- Helper Function for Single Agent Compilation ---
def _compile_single_agent(agent_slug: str, current_registry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Loads, validates, compiles a single agent config and updates registry data in memory.

    Args:
        agent_slug: The slug of the agent to compile.
        current_registry_data: The current state of the global registry data.

    Returns:
        The updated registry data if successful, None otherwise.
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
        typer.echo(f"❌ Error: Config file not found for agent '{agent_slug}' at {agent_config_path}", err=True)
        return None # Indicate failure
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing failed for {agent_config_path}: {e}")
        typer.echo(f"❌ Error: Failed to parse YAML for agent '{agent_slug}'. Details:\n{e}", err=True)
        return None # Indicate failure
    except ConfigValidationError as e:
        logger.error(f"Config validation failed for {agent_slug}: {e}")
        typer.echo(f"❌ Error: Config validation failed for agent '{agent_slug}'. Details:\n{e}", err=True)
        return None # Indicate failure
    except Exception as e:
        logger.exception(f"Unexpected error loading/validating config for {agent_slug}")
        typer.echo(f"❌ Error: An unexpected error occurred loading/validating config for '{agent_slug}'. Details: {e}", err=True)
        return None # Indicate failure

    # 2. Extract Metadata
    typer.echo(f"Processing '{agent_slug}': Extracting metadata...")
    try:
        registry_metadata = compiler.extract_registry_metadata(agent_config)
        logger.info(f"Successfully extracted metadata for {agent_slug}")
    except Exception as e:
        logger.exception(f"Unexpected error extracting metadata for {agent_slug}")
        typer.echo(f"❌ Error: An unexpected error occurred extracting metadata for '{agent_slug}'. Details: {e}", err=True)
        return None # Indicate failure

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
        typer.echo(f"❌ Error: An unexpected error occurred updating registry data for '{agent_slug}'. Details: {e}", err=True)
        return None # Indicate failure


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
    global_registry_path = GLOBAL_REGISTRY_PATH # Use module-level constant

    # --- Read Initial Global Registry ---
    # This needs to be done regardless of single or all, before any compilation attempts.
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

    final_registry_data = initial_registry_data.copy() # Start with the initial data

    if agent_slug:
        # --- Compile Single Agent ---
        logger.info(f"CLI 'compile' command invoked for single agent slug: {agent_slug}")
        typer.echo(f"--- Compiling Single Agent: {agent_slug} ---")

        updated_data = _compile_single_agent(agent_slug, final_registry_data)

        if updated_data is None:
            typer.echo(f"\n❌ Compilation failed for agent: '{agent_slug}'. Registry not written.", err=True)
            raise typer.Exit(code=1) # Exit with error if single compile fails
        else:
            final_registry_data = updated_data # Update the data to be written
            typer.echo(f"✅ Successfully processed agent: '{agent_slug}'")

    else:
        # --- Compile All Agents ---
        logger.info("CLI 'compile' command invoked to compile all agents.")
        typer.echo("--- Compiling All Agents ---")

        if not AGENT_CONFIG_DIR or not AGENT_CONFIG_DIR.is_dir():
             logger.error(f"Agent config directory not found or not configured: {AGENT_CONFIG_DIR}")
             typer.echo(f"❌ Error: Agent configuration directory not found or invalid: {AGENT_CONFIG_DIR}", err=True)
             raise typer.Exit(code=1)

        typer.echo(f"Scanning for agent configurations in: {AGENT_CONFIG_DIR}")
        compiled_count = 0
        failed_count = 0

        # Basic non-recursive scan for now (as per initial TDD step)
        for item in AGENT_CONFIG_DIR.iterdir():
            if item.is_dir():
                potential_config_path = item / "config.yaml"
                if potential_config_path.is_file():
                    slug_to_compile = item.name
                    typer.echo(f"\nFound potential agent: {slug_to_compile}")
                    # Pass the *current* state of final_registry_data
                    updated_data = _compile_single_agent(slug_to_compile, final_registry_data)
                    if updated_data is not None:
                        final_registry_data = updated_data # Accumulate successful updates
                        compiled_count += 1
                        typer.echo(f"✅ Successfully processed agent: '{slug_to_compile}'")
                    else:
                        failed_count += 1
                        typer.echo(f"ℹ️ Skipping registry update for failed agent: '{slug_to_compile}'")
                else:
                    logger.debug(f"Skipping directory {item.name}, no config.yaml found.")
            else:
                 logger.debug(f"Skipping non-directory item: {item.name}")


        if compiled_count == 0 and failed_count == 0:
             typer.echo("\n⚠️ No valid agent configurations found to compile.", err=True)
             # Decide if this should be an error exit or not. Test spec implies error.
             # Let's make it an error for now based on Scenario: No valid configurations found
             raise typer.Exit(code=1)
        elif failed_count > 0:
             typer.echo(f"\n⚠️ Compilation finished with {failed_count} error(s). Registry will be written with successful updates only.")
        else:
             typer.echo(f"\n✅ Successfully processed {compiled_count} agent(s).")


    # --- Write Final Global Registry (Common for both single and all) ---
    # Only write if at least one agent was processed successfully (or if single agent was successful)
    if final_registry_data != initial_registry_data: # Check if any changes were actually made
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
            raise typer.Exit(code=1) # Exit if final write fails
    else:
        typer.echo("\nℹ️ No changes detected in the registry. File not written.")


    # Final success message
    if agent_slug:
         typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent: '{agent_slug}'")
    else:
         typer.echo(f"\n🎉 Finished compiling all agents. Successful: {compiled_count}, Failed: {failed_count}.")

    # Removed the outer try...except typer.Exit block
    # The individual try...except blocks within each step already handle raising typer.Exit(1)
    # A final catch-all might be added later if needed, but this structure should allow
    # the patched typer.Exit in tests to be asserted correctly.


# --- Entry Point Execution ---
if __name__ == "__main__":
    app()
