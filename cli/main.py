# cli/main.py
import typer
import logging
from pathlib import Path
from typing_extensions import Annotated
from typing import Optional, Dict, Any

import os # Needed for os.path.join and os.listdir
# Removed yaml, GlobalAgentConfig, ConfigValidationError, Tuple
from . import config_loader
from . import compiler # Keep this import
from . import registry_manager # Keep this import
# from .models import GlobalAgentConfig # Removed
# from pydantic import ValidationError as ConfigValidationError # Removed
# from typing import Tuple # Removed
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







# --- Custom Exceptions and Helper Functions Removed ---
# The compilation logic, including helpers and exceptions,
# has been moved to the cli.compiler module.


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
    # Delegate the entire compilation process to the compiler module
    try:
        compiler.compile_agents(agent_slug=agent_slug)
        # Success/failure messages and registry writing are handled within compile_agents
    except typer.Exit as e:
        # Re-raise typer.Exit exceptions to allow tests to catch them
        raise e
    except Exception as e:
        # Catch any unexpected errors bubbling up from the compiler
        logger.exception(f"Unexpected error during agent compilation triggered from main CLI: {e}")
        typer.echo(f"❌ An unexpected error occurred during compilation. Details: {e}", err=True)
        raise typer.Exit(code=1)


# --- Entry Point Execution ---
if __name__ == "__main__":
    app()
