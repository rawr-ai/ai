
# Agent Updates
[] Update agent prompts in @custom_modes with the new output handling instructions. Use the new CLI!
[] Migrate all agent prompts to the new YAML config format when possible.

# New Agents
[] Create a new `agent_project` agent that can manage long-term project files (e.g. todo lists, project plans, etc.)
	- Possibly integrate with Linear via MCP.

# CLI
[] Update `scripts/manage_agent_configs.py` to remove all magic strings and use the config file (e.g. for the config file path itself).
[] Create structure YAML config files for agent prompts instead of flat MD files.
	- This will allow for more complex prompt configurations and easier management of agent settings.
	- Also enables real-time updates to agent prompts (i.e. dynamic updates based on the current state of the project).
	- YAML can be used to produce the flat MD files when needed.
	- Easy to define YAML schema for agent configs.

# Documentation
[] Update the CLI README to reflect the new functionality.

# Testing
[] Set up test suite for the CLI.
[] Test the CLI to ensure it works as expected.

# System
[] Enable agents to manage long-term project files (e.g. todo lists, project plans, etc.)