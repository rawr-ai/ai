# Roo Code Configuration Findings (2025-04-10)

This document summarizes the findings regarding Roo Code configuration based on the analysis of provided documentation URLs.

## 1. Latest Recommended Configuration Setup

The latest recommended setup prioritizes project-level configurations stored within the workspace for better team collaboration and version control.

*   **Modes:** Define project-specific modes in `.roomodes` (project root). Global modes in `custom_modes.json` serve as defaults or for personal use.
*   **Instructions:** Use the `.roo/` directory structure for instructions:
    *   Workspace-wide: `.roo/rules/` (contains multiple instruction files).
    *   Mode-specific: `.roo/rules-{modeSlug}/` (contains multiple instruction files).
    *   These directory methods are preferred over the older single-file `.roorules` / `.roorules-{modeSlug}` methods and take precedence.
    *   Global UI instructions and Mode-specific UI instructions are still applied but are less suitable for team settings.
*   **MCP Servers:** Define project-specific servers in `.roo/mcp.json`. Global servers in `mcp_settings.json` serve as defaults or for personal use. Project settings override global settings for servers with the same name.

## 2. Configuration Files Overview

This section outlines the various configuration files, their locations, and purposes based on the documentation reviewed.

### Mode Configuration

*   **Global:**
    *   File: `custom_modes.json`
    *   Location: Implied global Roo Code settings location (path not specified in docs).
    *   Purpose: Defines custom modes available across all workspaces.
    *   Structure: JSON object with a `customModes` array.
*   **Project:**
    *   File: `.roomodes`
    *   Location: Project root directory.
    *   Purpose: Defines custom modes specific to the project. Overrides global modes with the same `slug`.
    *   Structure: JSON object with a `customModes` array.

### Custom Instructions Configuration

*   **Global (UI):**
    *   Location: Roo Code Prompts Tab UI ("Custom Instructions for All Modes").
    *   Purpose: Defines instructions applied globally across all modes and workspaces.
*   **Project (Workspace-Wide):**
    *   **Preferred:**
        *   Directory: `.roo/rules/`
        *   Location: Project root directory.
        *   Purpose: Contains multiple instruction files (`.md`, `.txt`, etc.) applied to all modes in the workspace. Loaded recursively and alphabetically. Takes precedence over `.roorules`.
    *   **Fallback:**
        *   File: `.roorules`
        *   Location: Project root directory.
        *   Purpose: Single file containing workspace-wide instructions. Used only if `.roo/rules/` directory is absent or empty.
*   **Mode-Specific:**
    *   **UI:**
        *   Location: Mode-specific text area in Prompts Tab UI.
        *   Purpose: Defines instructions for a specific mode. Applies globally if the mode itself is global.
    *   **Project (Preferred):**
        *   Directory: `.roo/rules-{modeSlug}/` (e.g., `.roo/rules-code/`)
        *   Location: Project root directory.
        *   Purpose: Contains multiple instruction files for a specific mode. Loaded recursively and alphabetically. Takes precedence over `.roorules-{modeSlug}`.
    *   **Project (Fallback):**
        *   File: `.roorules-{modeSlug}` (e.g., `.roorules-code`)
        *   Location: Project root directory.
        *   Purpose: Single file containing mode-specific instructions. Used only if `.roo/rules-{modeSlug}/` directory is absent or empty.
*   **Combination Order:** Global UI -> Mode-Specific UI -> Mode-Specific Files (Dir > File) -> Workspace Files (Dir > File).

### MCP Configuration

*   **Global:**
    *   File: `mcp_settings.json`
    *   Location: Implied global Roo Code settings location (accessible via VS Code settings).
    *   Purpose: Defines MCP server configurations available globally.
    *   Structure: JSON object with a `mcpServers` object.
*   **Project:**
    *   File: `.roo/mcp.json`
    *   Location: `.roo/` directory within the project root.
    *   Purpose: Defines MCP server configurations specific to the project. Overrides global servers with the same name.
    *   Structure: JSON object with a `mcpServers` object.

### Other Configuration Files

*   No other distinct configuration *file types* were identified in the provided documentation snippets specifically for core Mode/Instruction/MCP setup. API configuration profiles exist but are managed differently (per profile settings).

## 3. Deprecated Configurations (DO NOT USE)

*   **`.clinerules`:** Explicitly mentioned as deprecated in v3.11.8 release notes. A deprecation warning was added for this file.
*   **`.roorules` / `.roorules-{modeSlug}` (as primary method):** While technically still functional as *fallbacks*, the documentation consistently promotes the `.roo/rules/` and `.roo/rules-{modeSlug}/` directory structures as the **preferred** and recommended method, especially for organization and team collaboration. Relying solely on the single-file methods is discouraged.

---

## Detailed Findings per Source

### Source: `https://docs.roocode.com/features/custom-modes`

*   **Mode Config Files:**
    *   Global modes are defined in `custom_modes.json` (location implied to be global, path not specified).
    *   Project-specific modes are defined in a `.roomodes` file located in the project's root directory.
*   **Mode Config Structure:** Both files use a JSON format with a top-level `customModes` array. Each object defines a mode with:
    *   Required properties: `slug`, `name`, `roleDefinition`, `groups` (tool access).
    *   File restrictions can be added to the `edit` group: `["edit", { "fileRegex": "\\.md$", "description": "Markdown files only" }]`.
    *   Optional properties: `customInstructions`, `apiConfiguration`.
*   **Mode-Specific Instruction Files (Project Level):** Instructions can be provided via files in the workspace, combined with the JSON `customInstructions`.
    *   **Preferred Method:** Directory `.roo/rules-{mode-slug}/` in the workspace root. Contains instruction files (e.g., `.md`, `.txt`). Files are loaded recursively and alphabetically.
    *   **Fallback Method:** Single file `.roorules-{mode-slug}` in the workspace root. Used only if the preferred directory (`.roo/rules-{mode-slug}/`) does not exist or is empty.
*   **Precedence:**
    *   Mode Definitions: Project (`.roomodes`) overrides Global (`custom_modes.json`).
    *   Mode-Specific Instruction Files: Directory (`.roo/rules-{mode-slug}/`) overrides File (`.roorules-{mode-slug}`).
*   **Instructions Combination:** Instructions loaded from files/directories are combined with the `customInstructions` property from the mode's JSON definition (typically appended after).

---

### Source: `https://docs.roocode.com/features/custom-instructions`

*   **Sources:** Instructions can come from Global UI settings, Workspace files/dirs, and Mode-specific files/dirs/JSON properties.
*   **Global Instructions:** Set via Prompts Tab UI ("Custom Instructions for All Modes"). Apply across all workspaces.
*   **Workspace-Level Instructions (Project-Specific):** Apply to all modes in the current workspace. Defined via files/dirs in workspace root:
    *   **Preferred Method:** Directory `.roo/rules/`. Contains instruction files (e.g., `.md`, `.txt`). Loaded recursively and alphabetically. Takes precedence.
    *   **Fallback Method:** Single file `.roorules`. Used only if `.roo/rules/` doesn't exist or is empty.
*   **Mode-Specific Instructions:** Apply only to a specific mode. Can be set via:
    1.  **Prompts Tab UI:** Mode-specific text area. (Global if the mode is global).
    2.  **Files/Directories (Project Level):**
        *   **Preferred Method:** Directory `.roo/rules-{modeSlug}/` (e.g., `.roo/rules-code/`). Loaded recursively and alphabetically. Takes precedence.
        *   **Fallback Method:** Single file `.roorules-{modeSlug}` (e.g., `.roorules-code`). Used only if the preferred directory doesn't exist or is empty.
*   **Combination Order:** Instructions are combined in the system prompt in this order: Global UI -> Mode-Specific UI -> Mode-Specific Files (Dir > File) -> Workspace Files (Dir > File).
*   **Recommendation:** Using `.roo/rules/` and `.roo/rules-{modeSlug}/` directories under version control is recommended for teams.

---

### Source: `https://docs.roocode.com/update-notes/v3.11.8`

*   **Introduced `.roorules` Files:** Added support for `.roorules` (workspace-wide) and `.roorules-{mode-slug}` (mode-specific) files for managing custom instructions within the project.
*   **Deprecated `.clinerules`:** Added a deprecation warning for the older `.clinerules` file.

---

### Source: `https://docs.roocode.com/update-notes/v3.11.9`

*   **Introduced `.roo/` Directories:** Formally introduced the directory-based approach for custom instructions: `.roo/rules/` (workspace-wide) and `.roo/rules-{modeSlug}/` (mode-specific).
*   **Directory Features:** Support multiple files, recursive loading, alphabetical appending.
*   **Precedence Confirmed:** Directory method (`.roo/rules...`) takes precedence over single-file method (`.roorules...`) if the directory exists and contains files.

---

### Source: `https://www.reddit.com/r/RooCode/comments/1juucj9/release_notes_3119_31110_custom_instruction/`

*   **Status:** Failed to scrape.
*   **Error:** `firecrawl_scrape` returned a 403 error, indicating the site is unsupported by the tool at this time.

---

### Source: `https://docs.roocode.com/features/mcp/using-mcp-in-roo`

*   **MCP Config Files:**
    *   Global MCP settings are in `mcp_settings.json` (location implied global, accessible via VS Code settings).
    *   Project-level MCP settings are in `.roo/mcp.json` (project root - Correction: located in `.roo/` directory).
*   **MCP Config Structure:** Both use JSON format with a top-level `mcpServers` object. Keys are server names, values are server config objects (STDIO: `command`, `args`, `env`, etc.; SSE: `url`, `headers`, etc.). Optional: `alwaysAllow`, `disabled`.
*   **Precedence:** Project (`.roo/mcp.json`) overrides Global (`mcp_settings.json`) for servers with the same name.

---