# Global Registry Access (`custom_modes.json`)

**Date:** 2025-04-10

## 1. Purpose

This document specifies the definitive path, necessary permissions, and key assumptions for accessing the global `custom_modes.json` file. This file serves as the central registry for Roo Code custom modes available across different workspaces within the user's environment. The `registry_manager.py` component, as outlined in the `implementation_plan_scoped.md`, will rely on this information.

## 2. Definitive Path

The canonical path for the global `custom_modes.json` file, as configured for the CLI tool (`cli/config.yaml`), is:

```
/Users/mateicanavra/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json
```

## 3. Required Permissions

The process executing the CLI tool (specifically the `registry_manager.py` component responsible for updates) requires standard operating system permissions to:

*   **Read:** Access the contents of `custom_modes.json`.
*   **Write:** Modify and save changes to `custom_modes.json`.
*   **Directory Access:** Traverse the directory structure leading to the file and potentially create backups within the `settings` directory if implemented as part of the rollback strategy.

Typically, this means the CLI must be run by the user who owns the configuration directory, which is standard for user-level application settings.

## 4. Key Assumptions

*   **Environment Specificity:** The specified path is valid for the **macOS** operating system and the **Cursor** editor environment. This path structure is likely different on other operating systems (e.g., Windows, Linux) and potentially other VS Code distributions (e.g., standard VS Code, VSCodium). The `registry_manager.py` might need logic to determine the correct path based on the environment if cross-platform compatibility becomes a requirement beyond the current scope.
*   **Path Stability:** Assumes the VS Code/Cursor extension storage path and the extension ID (`rooveterinaryinc.roo-cline`) remain consistent. Changes by the editor or extension publisher could break this path.
*   **User Privileges:** Assumes the CLI tool runs with the necessary user privileges to access the specified path within the user's `Library` directory. Elevated privileges (e.g., `sudo`) should *not* be required.
*   **File Integrity:** Assumes the `registry_manager.py` will implement safe write operations (e.g., atomic writes via temporary files or appropriate file locking) to prevent corruption of `custom_modes.json` during updates, especially if multiple processes could potentially access it (though unlikely in this specific scenario). The details of this safety mechanism are to be defined during the implementation of `registry_manager.py`.
*   **Configuration Source:** Assumes the path defined in `cli/config.yaml` is the single source of truth for the CLI regarding the global registry location.