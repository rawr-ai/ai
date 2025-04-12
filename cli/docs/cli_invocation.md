# Rawr CLI Invocation Patterns

This document clarifies the relationship between different ways to invoke the `rawr` command-line interface, specifically concerning agent compilation.

## `rawr compile [agent-slug]`

This is the explicitly defined command for compiling an agent's configuration.

*   **Mechanism:** The `compile` command is registered within the Typer application (`cli/main.py`). When invoked, it directly calls the `compile_agent_config` function.
*   **Functionality:** This function handles loading the agent's `config.yaml`, validating it, extracting metadata, and updating the global agent registry. (See `config_loading.md` for details on configuration path resolution).
*   **Use Case:** Provides a clear, explicit way to trigger the compilation process, suitable for scripting and documentation.

## `rawr [agent-slug]`

This pattern acts as a convenient shortcut or alias for the `compile` command.

*   **Mechanism:** This invocation pattern is *not* directly defined as a command within the Typer application (`cli/main.py`). Instead, the main `rawr` executable script (likely configured via `pyproject.toml` or a similar packaging mechanism) preprocesses the command-line arguments. When it detects only an agent slug is provided (without an explicit command like `compile`), it implicitly inserts the `compile` command before passing the arguments to the underlying Typer application.
*   **Functionality:** The end result is identical to running `rawr compile [agent-slug]`; the same agent compilation logic is executed.
*   **Use Case:** Offers brevity and convenience for interactive use, especially when compiling is the most frequent action performed on an agent slug.

## Conclusion

Both `rawr [agent-slug]` and `rawr compile [agent-slug]` trigger the same agent compilation functionality. The shorter form (`rawr [agent-slug]`) serves as a user-friendly alias for the explicit `compile` command, likely handled by argument preprocessing in the main entry point script. While functionally redundant, retaining both forms is recommended for clarity (explicit command) and convenience (shortcut).