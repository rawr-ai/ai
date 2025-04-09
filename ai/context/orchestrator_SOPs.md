# Standard Operating Procedures

## Git Workflow

All development work (features, fixes, refactoring) MUST be done on a dedicated feature branch created from the `main` branch.

Work MUST be committed incrementally to the feature branch.

Before merging, the work SHOULD be reviewed/verified (details may depend on the task).

Once complete and verified, the feature branch MUST be merged back into the `main` branch.

## Development Logging

Upon successful completion and merging of any significant development task, a development log entry MUST be created.

The process outlined in `ai/playbooks/pb_session_journaling.md` MUST be followed to generate and commit this log entry to the `main` branch.

## Plan Review

For complex or large-scale plans involving multiple agents or significant modifications, the Orchestrator SHOULD first submit the proposed plan to an `analyze` or `ask` agent for review and feedback before presenting it to the user or initiating the first step. The Orchestrator MUST incorporate feedback before finalizing the plan.

## General Workflow Principles

1.  **Define Conventions:** Before generating artifacts (logs, code, documentation), establish and adhere to clear conventions (e.g., naming, storage paths, formats).
2.  **Specify Before Execution:** Synthesize research findings or plans into a clear specification or set of instructions. As part of this specification, generate a visual representation (e.g., a Mermaid diagram using the 'Diagram' agent) of the planned workflow before initiating the main execution step or presenting the plan for review/approval.
3.  **Verify & Iterate:** Verify task outputs against defined objectives, requirements, or specifications. Iterate based on verification results and feedback, refining the approach or output until criteria are met. For structured iteration, refer to the pattern in `ai/playbooks/pb_iterative_execution_verification.md`.
4.  **Mode Switching for Content Generation:** Agents generating substantial content (e.g., Markdown, code) SHOULD switch to an appropriate mode (like `code` or `document`) within their task loop. After successful generation, they MUST return only the path to the created file.
5.  **Utilize Core Process Playbooks:** For standard meta-tasks, consult the relevant playbooks:
    *   Agent Creation: `ai/playbooks/pb_create_new_agent.md`
    *   Playbook Creation (from Session Analysis): `ai/playbooks/pb_create_playbook.md`
    *   Development Logging: `ai/playbooks/pb_session_journaling.md` (as mentioned in Development Logging section)
6.  **Manage Complex Workflow Artifacts:** For multi-step workflows generating intermediate files (drafts, diagrams, analysis, reviews), consider using a dedicated session directory (e.g., `ai/sessions/YYYY-MM-DD/workflow_name/`) to keep artifacts organized before finalizing outputs in their canonical project locations.