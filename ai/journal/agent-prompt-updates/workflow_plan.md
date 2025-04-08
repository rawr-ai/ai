# Workflow Plan: Agent Prompt File Output Directive Update

**Objective:** Systematically review agent prompts in `agents/` (excluding `orchestrate`, `meta`), identify those generating substantial outputs (reports, analysis, diagrams, etc.), and update their prompts to instruct them to switch modes (e.g., `code`) to save output to a file and return only the path.

**Workflow Plan:**

1.  **Setup (Git Agent):** Create feature branch `feature/agent-prompt-file-output-directive`.
2.  **Plan Review, Diagram & Documentation (Analyze Agent -> Code Agent):** Review *this* plan, refine if needed, generate Mermaid diagram, switch to `code` mode, write plan to `ai/journal/agent-prompt-updates/workflow_plan.md`, write diagram to `ai/journal/agent-prompt-updates/workflow_diagram.mmd`. Output: Paths to created files.
3.  **Agent Identification (Analyze Agent):** Scan `agents/` (excluding specified dirs), read prompts, identify agents needing the file-output directive based on their purpose. Output: List of prompt file paths.
4.  **Prompt Modification Loop (Code Agent):** Iterate through identified files. Read, append/integrate the specified file-output instruction, write back modified content. Output: Confirmation per file.
    *   **Instruction Text:**
        ```markdown
        **Output Handling for Substantial Content:**
        If your task involves generating substantial output (e.g., analysis reports, documentation, diagrams, test results, complex plans), you MUST switch to a mode capable of writing files (e.g., `code`, `document`) to save this output to an appropriate file path (e.g., within `ai/journal/<task-specific-dir>/` or another suitable location). After successfully saving the file, your final output for this task MUST be ONLY the relative path to the created or updated file. Do not output the full content itself.
        ```
5.  **Verification (Review Agent):** Review each modified prompt for correct instruction addition and overall coherence. Output: Verification status or list of issues.
6.  **Commit Changes (Git Agent):** Stage and commit modified prompts and journal files to the feature branch. Output: Commit confirmation.
7.  **Development Logging (Orchestrator -> Initiate `pb_development_logging.md`):** Follow playbook to log the completed work. Output: Path to devlog file.
8.  **Merge to Main (Optional - Ask User -> Git Agent):** Ask user for approval to merge the feature branch. If yes, merge. Output: Merge status.