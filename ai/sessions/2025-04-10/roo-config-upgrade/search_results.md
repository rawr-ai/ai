# Roo Code Configuration Changes Summary (v3.11.8, v3.11.9, Custom Instructions/Modes)

Based on the analysis of Roo Code documentation pages:
*   `https://docs.roocode.com/update-notes/v3.11.9`
*   `https://docs.roocode.com/update-notes/v3.11.8`
*   `https://docs.roocode.com/features/custom-instructions`
*   `https://docs.roocode.com/features/custom-modes`

The key changes relevant to agent configuration and management are:

1.  **File-Based Custom Instructions:**
    *   Roo Code introduced methods to manage custom instructions using files within the workspace.
    *   **v3.11.8:** Introduced single files: `.roorules` (workspace-wide) and `.roorules-{modeSlug}` (mode-specific). Deprecated older `.clinerules`.
    *   **v3.11.9:** Introduced a preferred directory structure: `.roo/rules/` (workspace-wide) and `.roo/rules-{modeSlug}/` (mode-specific), supporting multiple instruction files loaded alphabetically.

2.  **Loading Precedence:**
    *   The directory-based method (`.roo/rules/...`) takes precedence over the single-file method (`.roorules...`) if the directory exists and contains files.
    *   Instructions from files/directories are combined with those set in the UI and the `customInstructions` property in the mode's JSON definition.

3.  **Core Mode JSON Structure:**
    *   The fundamental JSON structure for defining custom modes (agents) in `custom_modes.json` (global) or `.roomodes` (project-specific) – including `slug`, `name`, `roleDefinition`, `groups` (tool access/file restrictions), `apiConfiguration` – appears unchanged in these updates based on the documentation reviewed.

4.  **Configuration Impact:**
    *   The main impact is on *how custom instructions are sourced and assembled* for an agent's configuration. The new file/directory methods offer more flexible, organized, and version-controllable ways to manage instructions compared to relying solely on the single JSON property or UI settings.