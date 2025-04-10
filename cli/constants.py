# cli/constants.py
"""Centralized constants for the CLI application."""

# --- Configuration Keys ---
TARGET_JSON_PATH = "target_json_path"
MARKDOWN_BASE_DIR = "markdown_base_dir"

# --- JSON/Data Structure Keys ---
CUSTOM_MODES = "customModes"
SLUG = "slug"
NAME = "name"
ROLE_DEFINITION = "roleDefinition"
CUSTOM_INSTRUCTIONS = "customInstructions"

# --- Command Names ---
CMD_ADD = "add"
CMD_UPDATE = "update"
CMD_DELETE = "delete"

# --- Environment Variables ---
ENV_CONFIG_PATH = "AGENT_CLI_CONFIG_PATH"

# --- Markdown Parsing Headings ---
# Note: Add all headings defined in markdown_utils.py as needed.
MD_HEADING_CORE_ID = "# Core Identity & Purpose"
MD_HEADING_ROLE = "# Role"
MD_HEADING_PERSONA = "# Persona"
MD_HEADING_CUSTOM_INSTRUCTIONS = "## Custom Instructions"
MD_HEADING_MODE_INSTRUCTIONS = "## Mode-specific Instructions"
MD_HEADING_SOP = "## Standard Operating Procedure (SOP) / Workflow"

# List of headings that signify the start of a role definition section
ROLE_DEFINITION_HEADINGS = [
    MD_HEADING_CORE_ID,
    MD_HEADING_PERSONA,
    MD_HEADING_ROLE,
]

# --- Default Paths/Files ---
DEFAULT_CONFIG_PATH = "cli/config.yaml"
DEFAULT_TARGET_JSON = "configs/agents.json"
DEFAULT_MARKDOWN_DIR = "docs/agents/"

# --- User-Facing Messages (Example) ---
# Add common error/success message formats if needed