# Agent Config Generation Script

This directory contains utility scripts for managing agent configurations.

## `generate_agent_configs.py`

This script reads agent configurations from a central JSON source file and generates individual `config.yaml` files for each agent within the `ai/agents/` directory structure.

### Purpose

To automate the creation and updating of agent `config.yaml` files based on a master configuration source, ensuring consistency.

### Source File

The script expects the master configuration data in JSON format at the following absolute path:
`/Users/mateicanavra/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json`

The JSON structure should contain a top-level key `customModes` which holds a list of agent configuration objects. Each object should contain at least a `slug` key.

### Target Directory

Generated `config.yaml` files are placed within subdirectories under `ai/agents/`, where each subdirectory name corresponds to the agent's `slug`.

Example: The configuration for an agent with `slug: "plan"` will be written to `ai/agents/plan/config.yaml`.

### Dependencies

- Python 3
- PyYAML (`pip install PyYAML`)

### Usage

Execute the script from the root project directory (`ai/`).

```bash
# Ensure your virtual environment is active if applicable
# source .venv/bin/activate 

# Run the script (excludes customInstructions by default)
python3 scripts/generate_agent_configs.py

# Run the script including the customInstructions field
python3 scripts/generate_agent_configs.py --include-custom-instructions
```

### Options

- `--include-custom-instructions`: If this flag is provided, the script will include the `customInstructions` field in the generated `config.yaml` files (if the field exists and is not null/empty in the source JSON). By default, this field is excluded.