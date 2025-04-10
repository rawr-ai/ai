# Documentation Assessment Report: Refactor CLI YAML Config

This report summarizes the state of documentation relevant to the scoped refactoring effort.

## Current Scope

The current refactoring scope is focused on: **Refactor CLI to use `config.yaml` solely for updating the global `custom_modes.json` registry.**

## Relevant Documents

The following documents are considered definitive and directly relevant to the current scope:

*   `implementation_plan_scoped.md` (Definitive Plan)
*   `refactoring_map.md` (Strategic Overview)
*   `config_findings.md` (Current System Context)

## Outdated/Partially Outdated Documents

The following documents contain information related to a broader or future vision and are considered outdated or only partially relevant for the *current* specific scope:

*   `proposal_analysis.md` (Broader vision)
*   `refactor_proposal_yaml_transition.md` (Broader vision)
*   `target_architecture.md` (Describes full/later vision; partially relevant conceptually)

## Unreferenced Files (Require Review)

The following files located in the `tmp/` directory were not referenced in the `project_index.md`. Their status (e.g., draft, superseded, still relevant) needs review and clarification:

*   `tmp/ambiguities_review.md`
*   `tmp/cli_structure_analysis.md`
*   `tmp/diagram_compile_flow.md`
*   `tmp/diagram_components.md`
*   `tmp/draft_implementation_plan.md`
*   `tmp/implementation_plan.md`
*   `tmp/implementation_plan_analysis.md`
*   `tmp/plan_review.md`

## Proposed File Organization Plan

To maintain clarity for the current refactoring effort, it is proposed that the identified "Outdated/Partially Outdated Documents" be moved to the `tmp/` directory for archival.

**Files to Move:**

*   `proposal_analysis.md`
*   `refactor_proposal_yaml_transition.md`
*   `target_architecture.md`