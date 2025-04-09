
# Agent Updates
- [ ] [FIX] Update agent prompts in @custom_modes with the new output handling instructions. Use the new CLI!
- [ ] [CHANGE] Migrate all agent prompts to the new YAML config format when possible.

# New Agents
- [ ] [NEW] Create a new `agent_project` agent that can manage long-term project files (e.g. todo lists, project plans, etc.)
	- [ ] [FUTURE] Possibly integrate with Linear via MCP.

# Playbooks
- [ ] [NEW] Define the XML schema for the playbooks. Or decide on a better format -- JSON? YAML? XML in MD?

# CLI
- [ ] [CRITICAL] Add groups definition for each mode when adding/updating an agent. Otherwise breaks all existing agent configs.
- [ ] [UPGRADE] Switch to new directory-based config structure released by Roo in v3.11.1
- [ ] [FIX] Update `scripts/manage_agent_configs.py` to remove all magic strings and use the config file (e.g. for the config file path itself).
- [ ] [FIX] Creating new agents via CLI silently fails if the markdown file does not exist. (I think, but this should be captured in a test.)
- [ ] [FIX] Remove `manage_agent_configs.py` and just use the CLI.
- [ ] [FIX] Use agent filename (or specified name property in YAML config) as the agent name when creating a new agent via CLI, not the directory name.
- [ ] [CHANGE] Create structure YAML config files for agent prompts instead of flat MD files.
- [ ] [NEW] Turn into MCP server so agents can manage agents programmatically.
- [ ] [NEW] Enable "Hot Swap" for MCP config based on the current Mode. This enables mode-specific MCP configs that allow for granular control over agent capabilities.
- [ ] [NEW] Allow option to choose between global vs. project-specific agent configs.
  - This will allow for more complex prompt configurations and easier management of agent settings.
  - Also enables real-time updates to agent prompts (i.e. dynamic updates based on the current state of the project).
  - YAML can be used to produce the flat MD files when needed.
  - Easy to define YAML schema for agent configs.

# Documentation
- [ ] [CHANGE] Update the CLI README to reflect the new functionality.

# Testing
- [ ] [NEW] Set up test suite for the CLI.
- [ ] [TEST] Test the CLI to ensure it works as expected.

# System
- [ ] [NEW] Enable agents to manage long-term project files (e.g. todo lists, project plans, etc.)

---

# Features

### Agent Config
