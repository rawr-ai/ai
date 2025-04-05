### ISSUES

-   **Issue:**
    -   **Description:** Forgets to use the test-filesystem MCP tool
    -   **Expected Behavior:** Uses the test-filesystem MCP tool to safely manage test directories & files & clean up after themselves
    -   **Actual Behavior:** Attemps to use CLI to manage test directories & files

### Optimizations

-   **Optimization:** Provide test infrastructure context
    -   **Description:** Should provide context on the test infrastructure, including available tools, how to use them, and how to use them to manage test directories & files
    -   **Why:** This will help the agent to understand the test infrastructure and use it to manage test directories & files; addresses root cause of several issues mentioned above