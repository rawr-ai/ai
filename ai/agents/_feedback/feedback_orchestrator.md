### Issues

-   **Issue:**
    -   **Description:** Forgets to test changes after each subtask (or within a subtask)
    -   **Expected Behavior:** Tests changes after each subtask (or within a subtask) or at the end of a loop, change, fix, or feature
    -   **Actual Behavior:** Proceeds to next subtask without testing
-   **Issue:**

    -   **Description:** Orchestrator analyzes and designs solutions instead of delegating to an agent that can do the analysis and design
    -   **Expected Behavior:** Switches to an agent that can do the analysis before putting together a workflow
    -   **Actual Behavior:** Attempts to do analysis on its own in order to construct a workflow instead of switching to an agent that can do the analysis firs

-   **Issue:**
    -   **Description:** Orchestrator and agents consistently attempt to pass large text files to each other instead of writing them to a tmp directory and passing the path to the file
    -   **Expected Behavior:** Writes large text files to a tmp directory and passes the path to the file
    -   **Actual Behavior:** Passes the large text file contents to other agents
    -   **Reason:** Preserve context limits, avoid large file sizes, and better steering because the orchestrator can just point to the file instead of having to read and process the entire file contents
    -   **Mitigation:**
        -   Write large text files to a tmp directory and pass the path to the file instead of passing the file contents
        -   Enforce SOPs for all agents that they must:
            -   Never pass massive text content to other agents
            -   Write all large text content to the tmp directory and pass the path to the file instead of passing the file contents
            -   Never spawn new agents **solely** to read or write large text files. Instead, agents that need to process large text files should do so within their own task loop, and agents that write large text files should switch to an Implementation agent to write the artifact within their own task loop.
-   **Issue:**
    -   **Description:** Orchestrator and agents don't leverage the powerful capabilities of the read
    -   **Expected Behavior:**
    -   **Actual Behavior:**
    -   **Reason:**

# MUST:

-   Include an "anchoring" step by Search Agent (ground in the "current state")
-   Periodically review the workflow plan (after each subtask), make sure it's still valid and up to date, and update it as needed if requirements change or the workflow plan is no longer valid
-   ABSOLUTELY MUST MUST MUST REINFORCE THAT AGENTS WHO PRODUCE ARTIFACTS MUST ALSO BE RESPONSIBLE FOR WRITING THE ARTIFACT TO THE CORRECT LOCATION BY SWITCHING TO AN IMPLEMENTATION AGENT IF NECESSARY

# SHOULD:

1. More frequent reviews of implemented changes (after each subtask, review the changes; possibly test the changes)
2. Must include an "anchoring" step by Search Agent (ground in the "current state")
3. Encourage larger subtasks, delegated to dedicated coordinators (e.g. Offensive Coordinator, Defensive Coordinator, Special Teams Coordinator) who can spin off smaller subtasks to other agents
4. When initiating a conditional loop:
    -   Ensure the orchestrator has a plan for how to handle the loop (e.g. a dedicated coordinator for handling loops or directing agents to switch modes). For example, a review loop could include a coordinator that manages the Review, any necessary modifications (Code/Implement/Fix), and the summary of changes/updates/etc. that would be passed back up to the orchestrator. A dedicated coordinator may not be necessary if the loop is simple, but if the loop is complex, it's best to have a dedicated coordinator manage the loop.
    -   If the loop start condition is not met (e.g. Review agent recommends no changes), the orchestrator should proceed to the next step in the workflow.