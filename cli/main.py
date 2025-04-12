# cli/main.py
import typer
import logging
from pathlib import Path
from typing_extensions import Annotated

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








@app.command("compile")
def compile_agent_config(
    agent_slug: Annotated[
        str,
        typer.Argument(
            help="The unique slug of the agent whose config.yaml should be compiled."
        ),
    ]
):
    """
    Loads, validates, and compiles an agent's config.yaml, updating the global registry.
    """
    logger.info(f"CLI 'compile' command invoked for agent slug: {agent_slug}")

    # Use paths loaded from the config system
    # Use the module-level constant which can be patched by tests
    agent_config_path = AGENT_CONFIG_DIR / agent_slug / "config.yaml"
    # Use the module-level constant which can be patched by tests
    global_registry_path = GLOBAL_REGISTRY_PATH

    logger.debug(f"Agent config path determined: {agent_config_path}")
    logger.debug(f"Global registry path determined: {global_registry_path}")

    # Removed outer try...except block that was causing TypeError

    # 1. Load and Validate Agent Config
    typer.echo(f"Loading and validating config for '{agent_slug}' from {agent_config_path}...")
    try:
        # Read the config file content
        config_content = agent_config_path.read_text()
        # Parse the YAML content
        config_data = yaml.safe_load(config_content)
        if not isinstance(config_data, dict):
             raise ConfigValidationError(f"Config file {agent_config_path} did not parse into a dictionary.")
        # Validate the data using the Pydantic model
        agent_config = GlobalAgentConfig.model_validate(config_data)
        typer.echo(f"✅ Config for '{agent_slug}' loaded and validated successfully.")
        logger.info(f"Successfully loaded and validated config for {agent_slug}")
    except FileNotFoundError:
        logger.error(f"Agent config file not found at {agent_config_path}")
        typer.echo(f"❌ Error: Config file not found for agent '{agent_slug}' at expected path: {agent_config_path}", err=True)
        raise
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing failed for {agent_config_path}: {e}")
        typer.echo(f"❌ Error: Failed to parse YAML for agent '{agent_slug}'. Details:\n{e}", err=True)
        raise e # Re-raise YAML error
    except ConfigValidationError as e: # Catches Pydantic validation errors
        logger.error(f"Config validation failed for {agent_slug}: {e}")
        typer.echo(f"❌ Error: Config validation failed for agent '{agent_slug}'. Details:\n{e}", err=True)
        raise e # Re-raise validation error
    except Exception as e:
        logger.exception(f"Unexpected error loading/validating config for {agent_slug}")
        typer.echo(f"❌ Error: An unexpected error occurred while loading/validating config for '{agent_slug}'. Details: {e}", err=True)
        raise e

    # 2. Extract Metadata
    typer.echo(f"Extracting registry metadata from config for '{agent_slug}'...")
    try:
        registry_metadata = compiler.extract_registry_metadata(agent_config)
        typer.echo("✅ Metadata extracted successfully.")
        logger.info(f"Successfully extracted metadata for {agent_slug}")
    except Exception as e: # Catch broad exception for now, refine if compiler raises specific errors
        logger.exception(f"Unexpected error extracting metadata for {agent_slug}")
        typer.echo(f"❌ Error: An unexpected error occurred while extracting metadata for '{agent_slug}'. Details: {e}", err=True)
        raise typer.Exit(code=1)

    # 3. Read Global Registry
    typer.echo(f"Reading global registry from {global_registry_path}...")
    try:
        global_registry_data = registry_manager.read_global_registry(global_registry_path)
        typer.echo("✅ Global registry read successfully.")
        logger.info(f"Successfully read global registry from {global_registry_path}")
    except FileNotFoundError:
        logger.warning(f"Global registry file not found at {global_registry_path}. Will create a new one.")
        typer.echo(f"ℹ️ Global registry file not found at {global_registry_path}. A new registry will be created.")
        global_registry_data = {} # Start with an empty registry
    except Exception as e:
        logger.exception(f"Unexpected error reading global registry from {global_registry_path}")
        typer.echo(f"❌ Error: An unexpected error occurred while reading the global registry. Details: {e}", err=True)
        raise e # Re-raise the original exception

    # 4. Update Global Registry
    typer.echo(f"Updating global registry with metadata for '{agent_slug}'...")
    try:
        updated_registry_data = registry_manager.update_global_registry(
            registry_data=global_registry_data, # Corrected keyword argument
            agent_metadata=registry_metadata
        )
        typer.echo("✅ Global registry updated in memory.")
        logger.info(f"Successfully updated global registry data in memory for {agent_slug}")
    except Exception as e: # Catch broad exception, refine if manager raises specific errors
        logger.exception(f"Unexpected error updating global registry data for {agent_slug}")
        typer.echo(f"❌ Error: An unexpected error occurred while updating the global registry data. Details: {e}", err=True)
        raise e # Re-raise the original exception

    # 5. Write Global Registry
    typer.echo(f"Writing updated global registry to {global_registry_path}...")
    try:
        registry_manager.write_global_registry(
            registry_path=global_registry_path,
            registry_data=updated_registry_data
        )
        typer.echo(f"✅ Global registry successfully written to {global_registry_path}.")
        logger.info(f"Successfully wrote updated global registry to {global_registry_path}")
    except Exception as e:
        logger.exception(f"Unexpected error writing global registry to {global_registry_path}")
        typer.echo(f"❌ Error: An unexpected error occurred while writing the global registry. Details: {e}", err=True)
        raise e # Re-raise the original exception

    typer.echo(f"\n🎉 Successfully compiled and updated global registry for agent: '{agent_slug}'")

    # Removed the outer try...except typer.Exit block
    # The individual try...except blocks within each step already handle raising typer.Exit(1)
    # A final catch-all might be added later if needed, but this structure should allow
    # the patched typer.Exit in tests to be asserted correctly.


# --- Entry Point Execution ---
if __name__ == "__main__":
    app()
