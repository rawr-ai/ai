### CLI to YAML Migration

Goal: Migrate all agent prompts to a new agnostic YAML config format.

Why: A standard YAML format will be easier to manage for the CLI, agents, and developers. Also allows for more complex prompt configurations, extensions, and easier management of agent settings.

Secondary goal: Use this YAML format as the basis for mcparty.ai MCP server.

### CLI to MCP Server

Goal: Enable MCP server to manage agents programmatically via same functions as CLI.

Why: This will allow for more complex agent management & franchise growth over time, plus easier integration with other systems.

Outcomes:
- Agents can be created, updated, and deleted programmatically.
- Agents can create and update themselves (self-awareness).
- Agents can create, update, and delete other agents.
- Entire "franchise" can be managed programmatically.