# Suggested Module Docstring for `cli/compiler.py`

The following docstring is suggested to be added at the top of the `cli/compiler.py` file to explain its purpose:

```python
"""
Handles the core logic for compiling agent configurations.

This module is responsible for:
- Locating agent configuration files (`config.yaml`).
- Loading and validating the configuration against the defined schema (models.GlobalAgentConfig).
- Extracting relevant metadata for the global agent registry.
- Orchestrating the compilation of single or multiple agents.
- Interacting with the registry manager to read and write the global registry file.

It is invoked by the CLI commands defined in `cli/main.py`.
"""