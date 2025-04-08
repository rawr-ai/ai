
# Agent Updates
- [ ] [FIX] Update agent prompts in @custom_modes with the new output handling instructions. Use the new CLI!
- [ ] [CHANGE] Migrate all agent prompts to the new YAML config format when possible.

# New Agents
- [ ] [NEW] Create a new `agent_project` agent that can manage long-term project files (e.g. todo lists, project plans, etc.)
	- Possibly integrate with Linear via MCP.

# CLI
- [ ] [CRITICAL] Add groups definition for each mode when adding/updating an agent. Otherwise breaks all existing agent configs.
- [ ] [FIX] Update `scripts/manage_agent_configs.py` to remove all magic strings and use the config file (e.g. for the config file path itself).
- [ ] [CHANGE] Create structure YAML config files for agent prompts instead of flat MD files.
- [ ] [NEW] Turn into MCP server so agents can manage agents programmatically.
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
