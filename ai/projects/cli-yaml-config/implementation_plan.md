# Implementation Plan: Add `--preserve-groups` Flag to `agent_config_manager update`

This plan details the steps required to add a `--preserve-groups` flag to the `update` command of the `scripts/agent_config_manager` CLI tool. This flag will allow users to update an agent configuration from a Markdown file while keeping the existing `groups` assignment intact.

**Target Files:**
*   `scripts/agent_config_manager/cli.py`
*   `scripts/agent_config_manager/commands.py`

---

## 1. Modify `cli.py` to Add the CLI Argument

**Goal:** Add the `--preserve-groups` flag to the `update` subcommand parser and pass its value to the command function.

**Steps:**

1.  **Locate Parser:** Open `scripts/agent_config_manager/cli.py` and find the `parser_update = subparsers.add_parser("update", ...)` line (around line 41).
2.  **Add Argument:** After the existing `add_argument` call for `path_to_markdown_file` within the `parser_update` definition, add the following:
    ```python
    parser_update.add_argument(
        '--preserve-groups',
        action='store_true',
        default=False, # Explicitly default to False
        help='Preserve the existing group assignments of the agent configuration being updated.'
    )
    ```
3.  **Locate Command Call:** Find the line within the `main` function where `commands.update_config` is called inside the `elif args.operation == "update":` block (around line 91).
4.  **Pass Argument:** Modify the call to `commands.update_config` to pass the value of the new flag from the parsed `args` object:
    ```python
    # Previous call:
    # commands.update_config(args.path_to_markdown_file, target_json_path, markdown_base_dir)

    # Updated call:
    commands.update_config(args.path_to_markdown_file, target_json_path, markdown_base_dir, args.preserve_groups)
    ```

---

## 2. Modify `commands.py` to Handle the Flag

**Goal:** Update the `update_config` function signature and logic to use the `preserve_groups` flag.

**Steps:**

1.  **Locate Function:** Open `scripts/agent_config_manager/commands.py` and find the `update_config` function definition (around line 52).
2.  **Modify Signature:** Change the function signature to accept the new boolean flag:
    ```python
    # Previous signature:
    # def update_config(markdown_path_str: str, target_json_path: Path, markdown_base_dir: Path):

    # Updated signature:
    def update_config(markdown_path_str: str, target_json_path: Path, markdown_base_dir: Path, preserve_groups: bool):
    ```
3.  **Locate Update Logic:** Inside the `update_config` function, find the loop that iterates through the loaded configurations (`configs`) to find the one matching the `slug` (around line 73):
    ```python
    for i, config in enumerate(configs):
        if config.slug == updated_config.slug:
            # ... existing logic ...
            configs[i] = updated_config # This is the replacement line
            found = True
            logger.debug(f"Found existing config for slug '{updated_config.slug}' at index {i}. Replacing.")
            break
    ```
4.  **Add Conditional Logic:** Within the `if config.slug == updated_config.slug:` block, insert the conditional logic *before* the line `configs[i] = updated_config`:
    ```python
            # --- Start: Added logic ---
            if preserve_groups:
                logger.debug(f"Preserving existing groups for slug '{config.slug}': {config.groups}")
                # Ensure the existing config actually has groups before copying
                if hasattr(config, 'groups') and config.groups is not None:
                     updated_config.groups = config.groups
                else:
                     # Handle case where existing config might somehow lack groups (though model default should prevent this)
                     logger.warning(f"Existing config for slug '{config.slug}' lacked groups attribute or was None. Cannot preserve.")
            # --- End: Added logic ---

            # Existing assignment (should be after the added logic)
            configs[i] = updated_config
            logger.debug(f"Found existing config for slug '{updated_config.slug}' at index {i}. Replacing.") # Existing log
    ```
    *Note: Added a check `hasattr(config, 'groups') and config.groups is not None` for robustness, although the Pydantic model default should typically ensure `groups` exists.*

---

## 3. Confirm No Changes Needed in Other Files

*   **`config.py`:** No changes are required. `load_configs` correctly loads existing `groups` or applies defaults, and `save_configs` correctly saves the final state of the `groups` attribute on the `AgentConfig` objects.
*   **`models.py`:** No changes are required. The `AgentConfig` model already defines the `groups` field with a default.

---

## 4. Edge Case Handling

The proposed changes integrate smoothly with existing error handling:

*   **Target Config File Doesn't Exist:** Handled by `load_configs` returning an empty list or raising an error before the new logic is reached.
*   **Config with Matching Slug Not Found:** Handled by the existing `if not found:` check after the loop. The new logic is only executed if a match is found.
*   **Existing Config Has No `groups` Field/Value:** The Pydantic model (`models.py`) assigns a default value (`["read"]`) during loading if the `groups` key is missing in the JSON. The added robustness check (`if hasattr...`) handles potential unexpected scenarios, but typically the copy (`updated_config.groups = config.groups`) will correctly transfer the default value if `preserve_groups` is true.

---