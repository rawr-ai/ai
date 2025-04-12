# Architectural Review: `rawr` CLI Command Structure (`compile` vs. `add/update/delete`)

**Date:** 2025-04-11

**Session Directory:** `ai/sessions/2025-04-11/refactor-cli-command/`

## 1. Objective

Review prior planning documents and recent user input to provide an architectural recommendation on the `rawr` CLI's command structure, specifically deciding between retaining only the `compile` command (Option A) or reintroducing `add`, `update`, and `delete` commands (Option B) in the current refactoring phase (`refactor/cli-compile-only` branch).

## 2. Context Summary

-   **Initial Goal:** Refactor `rawr` CLI to support only `compile [agent-slug]` based on `config.yaml` for updating the global `custom_modes.json` registry.
-   **User Clarification:** A decision is needed on the fate of the commented-out `add`, `update`, `delete` commands.
-   **Planning Documents:**
    -   `ai/projects/cli-yaml-config/plans_strategies/implementation_plan_scoped.md`: Task 2.2 explicitly defers the decision on `add/update/delete`.
    -   `ai/projects/cli-yaml-config/refactoring_map.md`: Line 50 marks `add/update/delete` for the "Later" phase.
-   **Completed "Now" Scope:** Migration of global registry update functionality to use `config.yaml` via a `compile` command (handling all agents based on config path) is complete.
-   **Architectural Options:**
    -   **Option A:** `compile` handles *all* agents based on config path; `add/update/delete` are removed entirely for now.
    -   **Option B:** `compile [agent-slug]` handles specific agents; `add/update` become wrappers calling `compile [agent-slug]`; `delete` removes entry from registry JSON.

## 3. Analysis of Options

### Option A: `compile` Only (Handles all agents)

-   **Pros:**
    -   **Alignment:** Directly aligns with the completed "Now" scope and the explicit deferral in planning documents.
    -   **Simplicity:** Reduces CLI complexity and implementation effort *for the current phase*.
    -   **Focus:** Keeps the focus on the core `config.yaml` -> global registry update mechanism.
    -   **Unified Mechanism:** Provides a single command (`compile`) to synchronize the registry with the configuration file(s).
-   **Cons:**
    -   **Workflow:** Requires users to manually edit `config.yaml` and then run `compile` for all changes, lacking dedicated commands for specific add/update/delete registry operations.
    -   **Future Need:** May eventually require dedicated management commands, but deferring allows for better-informed design later.

### Option B: `compile [agent-slug]`, `add`, `update`, `delete`

-   **Pros:**
    -   **User Experience:** Offers explicit commands for common agent registry management tasks.
    -   **Leverages Core Logic:** `add/update` can wrap the `compile [agent-slug]` logic.
    -   **Specific Deletion:** Provides a clear mechanism to deregister an agent without deleting its source config.
-   **Cons:**
    -   **Scope Creep:** Contradicts the original "Now" scope and the explicit deferral in planning documents.
    -   **Increased Complexity:** Adds more commands and implementation effort *now*.
    -   **Potential Divergence:** The `compile [agent-slug]` variant needs consideration alongside the already implemented `compile` (all agents) logic.
    -   **Premature Decision:** Implementing now prevents potential future rethinking of the best agent management approach based on usage.

## 4. Recommendation

**Recommendation: Proceed with Option A.**

**Justification:**

1.  **Adherence to Plan:** Option A respects the original, agreed-upon scope and the explicit decision documented in `implementation_plan_scoped.md` and `refactoring_map.md` to defer the `add/update/delete` functionality.
2.  **Reduced Complexity (Now):** Focusing solely on the `compile` command simplifies the current refactoring effort, allowing for thorough testing and validation of the core configuration-to-registry mechanism.
3.  **Avoids Scope Creep:** Prevents expanding the scope prematurely before the initial refactoring goals are fully stabilized and potentially reviewed.
4.  **Informed Future Decisions:** Deferring the decision allows the team to gather feedback on the `compile`-only workflow and make a more informed choice about the necessity and design of `add/update/delete` commands in a subsequent phase. The best long-term approach for agent management might differ from the previous implementation.

Therefore, the `add`, `update`, and `delete` commands should remain commented out or be removed entirely from the `refactor/cli-compile-only` branch for this phase. The focus should be on ensuring the `compile` command robustly handles updating the global registry based on the specified configuration path(s).

## 5. Next Steps (Implied)

-   Ensure the `compile` command functions correctly according to the "Now" scope (handling all agents based on config path).
-   Remove or ensure the `add/update/delete` command code is cleanly separated/commented out in the `refactor/cli-compile-only` branch.
-   Future work can revisit the need for `add/update/delete` commands based on user feedback and evolving requirements.