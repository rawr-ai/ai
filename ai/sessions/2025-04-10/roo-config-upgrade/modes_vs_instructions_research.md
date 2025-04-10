# Relationship Between Roo Code Custom Modes and Custom Instructions

## Summary

Custom Instructions and Custom Modes are distinct but closely related concepts in Roo Code. A Custom Mode defines an agent's core persona, capabilities (tool access, file restrictions), and potentially default model settings. Custom Instructions provide specific behavioral guidelines, preferences, or constraints that refine how the agent operates within that mode.

The relationship can be summarized as follows:

1.  **Mode Definition:** A Custom Mode is defined by its configuration (typically in JSON), which includes mandatory fields like `slug`, `name`, `roleDefinition`, and `groups`.
2.  **Instructions within Mode Definition:** The Custom Mode JSON definition *can optionally* include a `customInstructions` property. Instructions defined here are considered part of the mode's static definition.
3.  **Instructions Applied Externally:** Custom Instructions can also be defined *outside* the mode's JSON definition using dedicated files or directories in the workspace (e.g., `.roo/rules-{modeSlug}/` or `.roorules-{modeSlug}`). These are applied dynamically at runtime based on the active mode's slug.
4.  **Combined Application:** When a mode is active, Roo Code combines instructions from multiple sources into the final system prompt. This includes:
    *   Global instructions (UI).
    *   Mode-specific instructions defined in the mode's JSON (`customInstructions` property).
    *   Mode-specific instructions loaded from files/directories (`.roo/rules-{modeSlug}/` or `.roorules-{modeSlug}`).
    *   Workspace-wide instructions (from `.roo/rules/` or `.roorules`).
    *   (The exact order of combination is specified in the Custom Instructions documentation, ensuring more specific instructions take precedence).

**Conclusion:**

Custom Instructions are **not solely* part of a Custom Mode definition, nor are they entirely separate. They exist in a dual state:

*   They **can be** an optional part of the mode's static JSON definition (`customInstructions` property).
*   They **can also be** defined externally and applied dynamically to the mode at runtime based on its slug (via `.roo/rules-{modeSlug}/` or `.roorules-{modeSlug}`).

Both methods contribute to the final set of instructions used by the agent when operating in that specific mode. The core `roleDefinition` sets the fundamental persona, while `customInstructions` (from JSON and/or files) provide specific operational guidance.

## Supporting Documentation Evidence

*   **Custom Instructions Documentation:** Explicitly details the different ways instructions can be provided (Global UI, Workspace files/dirs, Mode-specific UI, Mode-specific files/dirs) and the final combination order. Mentions "Combining with Custom Modes".
*   **Custom Modes Documentation:** Shows the JSON structure including the optional `customInstructions` property. Explicitly describes the loading mechanism for mode-specific instruction files/directories (`.roo/rules-{modeSlug}/` and `.roorules-{modeSlug}`) and states they are combined with the JSON `customInstructions`.
*   **Boomerang Tasks Documentation:** Reinforces that modes have configurations and are used for specific tasks, with context (including instructions) passed explicitly between parent and subtasks. It doesn't contradict the relationship established by the other two documents.