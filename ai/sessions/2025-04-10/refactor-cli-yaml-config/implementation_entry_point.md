# Implementation Entry Point & Guidance

**Date:** 2025-04-10

**Project:** CLI Refactoring (YAML Transition - "Now" Scope)

**Status:** Documentation Preparation Complete

---

This document provides guidance for the agent responsible for implementing the "Now" scope of the CLI refactoring project. All necessary planning, documentation, and supporting artifacts have been prepared and are located within this session directory: `ai/sessions/2025-04-10/refactor-cli-yaml-config/`.

**Recommended Starting Point:**

1.  **Consult the Project Index:** Begin by thoroughly reviewing the updated `project_index.md`. This file provides the definitive overview of the "Now" scope, lists all relevant supporting documents and diagrams, and clarifies the status of older documents.
2.  **Follow the Scoped Plan:** The primary guide for implementation is `implementation_plan_scoped.md`. Adhere strictly to the tasks outlined in this plan for the "Now" scope.
3.  **Utilize Supporting Documents:** Refer to the newly created documents (schema, access, rollback, testing, migration, usage guide) and diagrams within this directory as needed during implementation of specific tasks outlined in the plan.

**Key Constraints:**

*   Focus *exclusively* on the "Now" scope: Updating the global `custom_modes.json` via `config.yaml`.
*   Do *not* implement features planned for "Later" phases (e.g., project-level YAML processing, `.roo/rules` generation).
*   Ensure all code changes align with the defined target architecture (`diagram_target_architecture_global.md`) and testing strategy (`testing_strategy_global.md`).

By following this guidance, the implementation phase should proceed smoothly and align with the prepared documentation and project goals.