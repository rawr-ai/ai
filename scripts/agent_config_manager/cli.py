# scripts/agent_config_manager/cli.py
import argparse
import logging
import sys
import yaml
from pathlib import Path

from . import commands

# Configure root logger initially - level will be set based on args
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = logging.StreamHandler(sys.stdout) # Log to stdout
log_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.addHandler(log_handler)
# Set a default level; will be overridden by args
root_logger.setLevel(logging.INFO)

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(prog="agent_config_manager", description="Manage agent configurations using definitions from Markdown files.")
    parser.add_argument(
        "--log-level",
        type=str.upper,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO."
    )
    parser.add_argument("--config", type=str, required=True, help="Path to the CLI configuration YAML file.")
    subparsers = parser.add_subparsers(dest="operation", required=True, help="Subcommand to execute")

    # Add operation
    parser_add = subparsers.add_parser("add", help="Add a new agent config from a Markdown file. Fails if slug already exists.")
    parser_add.add_argument("path_to_markdown_file", type=str, help="Path to the agent definition Markdown file.")

    # Update operation
    parser_update = subparsers.add_parser("update", help="Update an existing agent config from a Markdown file. Fails if slug does not exist.")
    parser_update.add_argument("path_to_markdown_file", type=str, help="Path to the agent definition Markdown file.")

    # Delete operation
    parser_delete = subparsers.add_parser("delete", help="Delete an agent config by its slug. Fails if slug does not exist.")
    parser_delete.add_argument("agent_slug", type=str, help="Slug of the agent configuration to delete.")

    # Sync operation (Placeholder - Not fully implemented as per convention doc)
    # parser_sync = subparsers.add_parser("sync", help="Sync configs from a directory of Markdown files.")
    # parser_sync.add_argument("directory_path", type=str, help="Directory containing agent Markdown files.")
    # parser_sync.add_argument("--delete-stale", action="store_true", help="Remove JSON entries for non-existent Markdown files.")


    args = parser.parse_args()

    # Set the logging level based on the command-line argument
    log_level_name = args.log_level
    log_level = logging.getLevelName(log_level_name)
    root_logger.setLevel(log_level)
    logger.info(f"Logging level set to {log_level_name}")
    logger.debug("Debug logging enabled.") # This will only show if level is DEBUG

    # Load configuration from YAML using the provided --config argument
    config_path = Path(args.config)
    if not config_path.is_file():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    try:
        logger.debug(f"Loading configuration from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            cli_config = yaml.safe_load(f)
        if not cli_config or 'target_json_path' not in cli_config or 'markdown_base_dir' not in cli_config:
            logger.error(f"Invalid configuration format in {config_path}. Missing required keys.")
            sys.exit(1)
        target_json_path = Path(cli_config['target_json_path']).resolve()
        markdown_base_dir = Path(cli_config['markdown_base_dir']).resolve()
        logger.debug(f"Target JSON path loaded: {target_json_path}")
        logger.debug(f"Markdown base directory loaded: {markdown_base_dir}")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file {config_path}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred loading configuration: {e}")
        sys.exit(1)

    logger.info(f"Executing operation: {args.operation}")
    try:
        if args.operation == "add":
            commands.add_config(args.path_to_markdown_file, target_json_path, markdown_base_dir)
        elif args.operation == "update":
            commands.update_config(args.path_to_markdown_file, target_json_path, markdown_base_dir)
        elif args.operation == "delete":
            commands.delete_config(args.agent_slug, target_json_path)
        # elif args.operation == "sync":
        #     logger.warning("Sync operation is not fully implemented yet.")
            # sync_configs(args.directory_path, args.delete_stale, target_json_path)
        else:
            # This case should not be reachable due to `required=True` on subparsers
            logger.error("No valid operation specified.")
            parser.print_help(sys.stderr)
            sys.exit(1) # Exit with error if no valid operation matched

        # If we reach here, the command executed successfully (or raised an exception handled below)
        sys.exit(0) # Explicitly exit with success code
    except (FileNotFoundError, ValueError, IOError, RuntimeError) as e:
        # Log known error types specifically
        error_message = f"{type(e).__name__}: {e}"
        logger.error(error_message)
        print(f"ERROR: {error_message}", file=sys.stderr) # Print to stderr for CLI feedback/testing
        sys.exit(1)
    except Exception as e:
        # Log unexpected errors with traceback
        logger.exception(f"An unexpected error occurred during operation '{args.operation}'")
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stderr) # Print to stderr
        sys.exit(1)

# Note: The if __name__ == "__main__": block is intentionally omitted here.
# This module is meant to be imported and its main() function called by the entry point script.