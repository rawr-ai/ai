# Rawr CLI

A command-line tool to manage agent configurations for the Rawr framework.

## Installation

```bash
pip install -e .
```

The `rawr` command is then available in your environment (e.g., `rawr --help`).

## Quick Start

### Compile an agent

```bash
rawr compile [AGENT_SLUG]
# or using the shortcut:
rawr [AGENT_SLUG]
```

This command loads, validates, and compiles the specified agent's configuration, updating the global registry.

### Add a new agent

```bash
rawr add agent <AGENT_SLUG> [--template TEMPLATE] [--option key=value ...]
```

Generate a new agent scaffold from a template with optional key=value settings.

## Command Summary

- `rawr compile [AGENT_SLUG]`
- `rawr [AGENT_SLUG]` (alias for `compile`)
- `rawr add agent NAME [--template TEMPLATE] [--option key=value]`

## Notes

- Top-level `rawr add <slug>` is *not* supported; the `agent` subcommand is required.
- Detailed docs available under `cli/docs` (invocation patterns, config loading).
