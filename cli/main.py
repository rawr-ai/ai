# cli/main.py
import typer
import logging
from pathlib import Path
from typing_extensions import Annotated

# Temporarily import from current structure - will be updated in Step 6
try:
    from cli.agent_config.commands import (
        add_config,
        update_config,
        delete_config,
    )
    from cli.agent_config.settings import (
        load_cli_config,
    )  # Updated import from settings.py
except ImportError as e:
    print(f"Initial import failed (expected during refactor): {e}")

    # Provide dummy functions or raise error if needed for basic structure validation
    def add_config(*args, **kwargs):
        print("Dummy add_config called")

    def update_config(*args, **kwargs):
        print("Dummy update_config called")

    def delete_config(*args, **kwargs):
        print("Dummy delete_config called")

    def load_cli_config():
        return {"target_json_path": "dummy.json", "markdown_base_dir": "."}


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
    help="CLI tool to manage Agent Configurations from Markdown files.",
    add_completion=False,
)


# --- Helper to load config ---
# This might need adjustment based on the actual structure of config loading
def get_config_paths():
    """Loads configuration paths."""
    try:
        config = load_cli_config()
        target_json = Path(
            config.get("target_json_path", "configs/agents.json")
        ).resolve()
        markdown_dir = Path(
            config.get("markdown_base_dir", "docs/agents/")
        ).resolve()
        logger.debug(
            f"Loaded config: target_json='{target_json}', markdown_dir='{markdown_dir}'"
        )
        # Ensure base directories exist for safety, although commands might also do this
        target_json.parent.mkdir(parents=True, exist_ok=True)
        markdown_dir.mkdir(parents=True, exist_ok=True)
        return target_json, markdown_dir
    except Exception as e:
        logger.error(f"Failed to load CLI configuration: {e}", exc_info=True)
        typer.echo(
            f"Error: Failed to load CLI configuration. Check config file and paths. Details: {e}",
            err=True,
        )
        raise typer.Exit(code=1)


# --- CLI Commands ---


@app.command("add")
def add_agent_config(
    markdown_path: Annotated[
        str,
        typer.Argument(help="Path to the Markdown file defining the agent."),
    ],
):
    """
    Adds a new agent configuration from a Markdown file to the JSON store.
    """
    logger.info(f"CLI 'add' command invoked for path: {markdown_path}")
    try:
        target_json_path, markdown_base_dir = get_config_paths()
        add_config(
            markdown_path_str=markdown_path,
            target_json_path=target_json_path,
            markdown_base_dir=markdown_base_dir,
        )
        typer.echo(
            f"Successfully added agent configuration from: {markdown_path}"
        )
    except ValueError as e:
        typer.echo(f"Error adding agent: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during 'add': {e}", exc_info=True
        )
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("update")
def update_agent_config(
    markdown_path: Annotated[
        str,
        typer.Argument(
            help="Path to the Markdown file with updated agent definition."
        ),
    ],
    preserve_groups: Annotated[
        bool,
        typer.Option(
            "--preserve-groups",
            help="Keep the existing group assignments for the agent.",
        ),
    ] = False,
):
    """
    Updates an existing agent configuration in the JSON store from a Markdown file.
    Uses the 'slug' within the Markdown file to find the agent to update.
    """
    logger.info(
        f"CLI 'update' command invoked for path: {markdown_path} (preserve_groups={preserve_groups})"
    )
    try:
        target_json_path, markdown_base_dir = get_config_paths()
        update_config(
            markdown_path_str=markdown_path,
            target_json_path=target_json_path,
            markdown_base_dir=markdown_base_dir,
            preserve_groups=preserve_groups,
        )
        typer.echo(
            f"Successfully updated agent configuration from: {markdown_path}"
        )
    except ValueError as e:
        typer.echo(f"Error updating agent: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during 'update': {e}", exc_info=True
        )
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("delete")
def delete_agent_config(
    slug: Annotated[
        str,
        typer.Argument(
            help="The unique slug of the agent configuration to delete."
        ),
    ]
):
    """
    Deletes an agent configuration from the JSON store using its slug.
    """
    logger.info(f"CLI 'delete' command invoked for slug: {slug}")
    try:
        target_json_path, _ = (
            get_config_paths()
        )  # Markdown base dir not needed for delete
        delete_config(slug=slug, target_json_path=target_json_path)
        typer.echo(
            f"Successfully deleted agent configuration with slug: {slug}"
        )
    except ValueError as e:
        typer.echo(f"Error deleting agent: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during 'delete': {e}", exc_info=True
        )
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)


# --- Entry Point Execution ---
if __name__ == "__main__":
    app()
