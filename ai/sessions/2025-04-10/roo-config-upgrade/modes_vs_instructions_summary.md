# Summary Report: Custom Modes vs. Custom Instructions & CLI Adaptation Validity

**Date:** 2025-04-10

## 1. Objective of Follow-up Investigation

This report consolidates the findings from a follow-up investigation prompted by the initial analysis of adapting the `cli` tool for Roo Code configuration. The primary objectives were:

*   To precisely clarify the relationship between Roo Code Custom Modes and Custom Instructions.
*   To reassess the validity of the original report's recommendation regarding the `cli` tool's handling of the `customInstructions` field, in light of the clarified relationship.

## 2. Clarified Relationship: Custom Modes and Custom Instructions

The research confirmed that Custom Modes and Custom Instructions are distinct but interconnected:

*   **Custom Mode:** Defines an agent's core persona, capabilities, and potentially default settings via its JSON configuration (`custom_modes.json`).
*   **Custom Instructions:** Provide specific behavioral guidelines or constraints that refine agent operation within a mode.
*   **Sources of Instructions:** Roo Code assembles instructions at runtime from multiple potential sources, including:
    *   The optional `customInstructions` property within the mode's JSON definition.
    *   External files/directories specific to the mode (e.g., `.roo/rules-{modeSlug}/`, `.roorules-{modeSlug}`).
    *   Workspace-wide instruction files/directories (e.g., `.roo/rules/`, `.roorules`).
    *   Global UI settings.
*   **Dual Nature:** Instructions can be part of the static mode definition (JSON `customInstructions`) *and* applied dynamically via external files/directories. Both contribute to the final set used by the agent.

## 3. Assessment of Original Report's Validity

The original report recommended decoupling the `cli` tool from managing the `customInstructions` field in `custom_modes.json` (Option B). This recommendation was reviewed against the clarified understanding:

*   **Recommendation Remains Valid:** Despite confirming that the JSON `customInstructions` field *is* a valid input source for Roo Code, the original recommendation to remove the CLI's logic for populating this field remains the most appropriate course of action.
*   **Core Rationale:**
    *   **Incompleteness:** The CLI, sourcing instructions only from Markdown headers, generates an incomplete and potentially misleading value for `customInstructions`, failing to account for other sources Roo Code uses.
    *   **Complexity Avoidance:** Replicating Roo Code's complex, multi-source instruction assembly logic within the CLI is impractical and creates maintenance challenges.
    *   **Clean Decoupling:** Removing this responsibility simplifies the CLI and correctly places the burden of instruction assembly solely on Roo Code's runtime environment.
    *   **Manual Edits:** This change doesn't prevent manual editing of the `customInstructions` field in the JSON if needed; it only stops the CLI's flawed *automatic* population.

## 4. Conclusion

The follow-up investigation confirms that Custom Instructions can originate from both the mode's JSON definition and external files/directories, being combined by Roo Code at runtime.

This clarified understanding reinforces the validity of the original report's recommendation: **The `cli` tool should be modified to stop extracting instructions from Markdown and cease writing to the `customInstructions` field in `custom_modes.json`.** This approach simplifies the CLI, avoids logic duplication, and ensures that the complex task of instruction assembly remains the sole responsibility of the Roo Code runtime environment.