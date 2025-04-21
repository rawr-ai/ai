# Playbook: Linear Sprint/Cycle Orchestration with AI Agents

**Version:** 1.0
**Date:** 2025-04-20
**Author:** AI Implementation Agent (for future self/Orchestrator)

## 1. Objective

To guide an orchestrator agent (like myself) in managing a standard Linear sprint/cycle using a multi-agent AI team. This involves planning, assigning tasks, tracking progress, facilitating reviews, and ensuring the status of work is accurately reflected in Linear throughout the cycle.

## 2. Key Roles/Modes Involved

*   **Orchestrator (Self):** Manages the overall workflow, assigns tasks to agents, monitors progress, interacts with Linear, handles exceptions.
*   **Planner (`plan`):** (Optional) Assists in breaking down larger issues or defining implementation strategies if needed.
*   **Implementer (`implement`, `refactor`, etc.):** Executes the core development tasks based on Linear issue descriptions and plans.
*   **Tester/Reviewer (`test`, `review`):** Verifies the implemented work against requirements, runs tests, provides feedback.
*   **Documenter (`document`):** Updates documentation related to the completed work.
*   **Linear Expert (`linear-expert`):** (Advisory) Provides guidance on Linear best practices or specific feature usage if the Orchestrator encounters uncertainty.
*   **Git (`git`):** Handles branching, committing, merging as per project standards.

## 3. Inputs

*   **Sprint/Cycle Goal:** The high-level objective for the current cycle.
*   **Linear Project/Team Context:** The relevant Linear Project ID and Team ID.
*   **List of Candidate Issues:** Identified Linear issues potentially suitable for the cycle (can be fetched via `IntegrationsLinearSearchIssues` using relevant filters like project, team, status=Backlog/Todo).
*   **(Optional) Team Capacity/Agent Availability:** Information on which agents are available and their potential workload.

## 4. Workflow Diagram

```mermaid
graph TD
    subgraph "Sprint/Cycle Orchestration"
        direction TB

        A[Start Cycle] --> B(1. Planning & Assignment);
        B --> C{2. Execution Loop};
        C -- Task Ready --> D[2a. Assign & Execute (Implementer/Git)];
        D --> E[2b. Verify & Review (Tester/Reviewer)];
        E -- Approved --> F[2c. Document (Documenter)];
        F --> G[2d. Update Linear (Orchestrator)];
        G --> C;
        E -- Issues Found --> D; // Re-assign/Fix
        C -- All Tasks Done --> H(3. Cycle Review & Close);
        H --> I[End Cycle];

    end

    subgraph "Linear Interactions (Orchestrator)"
        B --> L1[SearchIssues: Identify cycle issues];
        D --> L2[UpdateIssues: Assign agent, set state=InProgress];
        E --> L3[UpsertComment: Add review feedback/link];
        G --> L4[UpdateIssues: Set state=Done, add PR link];
        H --> L5[CreateProjectUpdate: Post cycle summary];
    end

    style L1 fill:#ddd,stroke:#333,stroke-width:1px
    style L2 fill:#ddd,stroke:#333,stroke-width:1px
    style L3 fill:#ddd,stroke:#333,stroke-width:1px
    style L4 fill:#ddd,stroke:#333,stroke-width:1px
    style L5 fill:#ddd,stroke:#333,stroke-width:1px
```

## 5. Steps

| Step        | Phase                     | Action                                                                                                                               | Actor(s)                                | Linear Tool (Orchestrator)                     | Key Outputs                                                                 |
| :---------- | :------------------------ | :----------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------- | :--------------------------------------------- | :-------------------------------------------------------------------------- |
| 1.1         | **Planning**              | Define cycle goal. Identify candidate issues using filters (Project, Team, Status).                                                  | Orchestrator                            | `IntegrationsLinearSearchIssues`               | List of potential cycle issues.                                             |
| 1.2         |                           | Select issues for the cycle based on goal and priority. (Optional: Use `plan` agent for complex breakdown).                          | Orchestrator, (Planner)                 | -                                              | Final list of cycle issues with IDs.                                        |
| 1.3         |                           | Assign selected issues to appropriate agents (Implementer, Tester roles). Update Linear issues: set assignee, move state to 'Todo'. | Orchestrator                            | `IntegrationsLinearUpdateIssues` (batch/single) | Linear issues assigned and in 'Todo' state. Agent task assignments noted. |
| 2a.i        | **Execution Loop**        | Orchestrator identifies a ready task (status 'Todo', assigned agent available).                                                      | Orchestrator                            | -                                              | Task identified for execution.                                              |
| 2a.ii       |                           | Dispatch `git` agent to create a feature branch (if applicable).                                                                     | Orchestrator -> `git`                   | -                                              | Feature branch created.                                                     |
| 2a.iii      |                           | Dispatch Implementer agent with Linear issue details and branch name. Update Linear issue state to 'In Progress'.                    | Orchestrator -> Implementer             | `IntegrationsLinearUpdateIssues`               | Agent begins work. Linear issue 'In Progress'.                              |
| 2b.i        |                           | Implementer completes work, commits changes, signals completion (e.g., via `attempt_completion` with commit details/PR link).        | Implementer -> Orchestrator             | -                                              | Completed code, commit hash/PR link.                                        |
| 2b.ii       |                           | Dispatch Tester/Reviewer agent with issue details and commit/PR info.                                                                | Orchestrator -> Tester/Reviewer         | -                                              | Review/Testing begins.                                                      |
| 2b.iii      |                           | Tester/Reviewer provides feedback/approval. (Optional: Add comment to Linear issue).                                                 | Tester/Reviewer -> Orchestrator         | `IntegrationsLinearUpsertComment` (optional)   | Test results, review feedback/approval.                                     |
| 2b.iv       |                           | **Decision:** If issues found, synthesize feedback, re-dispatch Implementer (back to 2a.iii or specific fix step). If approved, proceed. | Orchestrator                            | -                                              | Decision on next step.                                                      |
| 2c.i        |                           | (If applicable) Dispatch Documenter agent to update relevant docs based on completed issue.                                          | Orchestrator -> Documenter              | -                                              | Documentation updated.                                                      |
| 2d.i        |                           | Dispatch `git` agent to merge feature branch (if applicable).                                                                        | Orchestrator -> `git`                   | -                                              | Code merged.                                                                |
| 2d.ii       |                           | Update Linear issue: set state to 'Done', add PR link/commit hash, potentially add closing comment.                                  | Orchestrator                            | `IntegrationsLinearUpdateIssues`, `UpsertComment` | Linear issue marked 'Done' with relevant links/info.                        |
| 2d.iii      |                           | **Loop:** Check for more 'Todo' issues for the cycle. If yes, return to 2a.i. If no, proceed to Step 3.                               | Orchestrator                            | -                                              | Cycle continues or moves to review.                                         |
| 3.1         | **Cycle Review & Close** | Review completed issues against the cycle goal.                                                                                      | Orchestrator                            | `IntegrationsLinearSearchIssues` (filter=Done) | Assessment of cycle success.                                                |
| 3.2         |                           | (Optional) Use `analyze` agent to generate a summary of the cycle's accomplishments, challenges, learnings.                          | Orchestrator -> `analyze`               | -                                              | Cycle summary document/text.                                                |
| 3.3         |                           | Post a Project Update in Linear summarizing the cycle.                                                                               | Orchestrator                            | `IntegrationsLinearCreateProjectUpdate`        | Cycle summary posted to Linear Project.                                     |
| 3.4         |                           | Archive the cycle in Linear (if applicable via UI or future API).                                                                    | Orchestrator                            | -                                              | Cycle formally closed.                                                      |

## 6. Outputs

*   Completed features/fixes as defined by the cycle issues.
*   Updated codebase merged into the main development branch.
*   Accurately updated Linear issues reflecting the work done (status, assignees, comments, links).
*   A Linear Project Update summarizing the cycle's outcome.
*   (Optional) Updated documentation.
*   (Optional) Cycle review/retrospective summary.

## 7. Considerations & Best Practices

*   **Granularity:** Keep Linear issues focused and small enough for agents to complete within a reasonable timeframe. Use sub-issues if necessary.
*   **Linear Sync:** Ensure the Orchestrator consistently updates Linear states and adds relevant links (commits, PRs) to maintain a single source of truth.
*   **Agent Handoffs:** Clearly define the inputs/outputs for each agent transition (e.g., Implementer provides commit hash/PR link for Tester).
*   **Error Handling:** Define how the Orchestrator should handle agent failures (e.g., retry, reassign, escalate to user).
*   **Branching Strategy:** Adhere to the project's defined Git branching strategy (e.g., feature branches per issue).
*   **Idempotency:** Be mindful when using `UpdateIssues` or `UpsertComment` to avoid duplicate actions if the playbook restarts. Check current state before updating.
*   **Tool Usage:** Use batch operations (`IntegrationsLinearUpdateIssues` with multiple IDs) where possible for efficiency.
*   **Feedback Loop:** Incorporate review feedback effectively, potentially requiring loops back to the Implementer.
*   **Linear Philosophy:** While this provides structure, remember Linear encourages momentum. Adapt the process; don't let it become overly bureaucratic if simpler updates suffice for certain tasks.