## Input Format for Requesting Tasks from the Expert Test Agent

To effectively utilize the Expert Test Agent, please provide prompts using the following structure:

1.  **Overall Goal:** Briefly state the high-level objective (e.g., "Ensure the new checkout API is robust," "Increase test coverage for the auth module," "Validate the LLM's response format").
2.  **Target Agent Persona:** `Expert Test Agent` (This clarifies who should handle the request).
3.  **Specific Task(s) for this Interaction:** Clearly list which of the agent's core capabilities you want it to perform *in this specific interaction*. Choose from:
    *   `Testability Analysis & Criticality Assessment`
    *   `Test Plan Generation`
    *   `Test Execution` (Specify which plan/suites, if applicable)
    *   `Test Result Summarization` (Specify which run, if applicable)
    *   `Test Runner Implementation/Specification`
    *   `Test Implementation Strategy` (Often part of Planning, but can be requested standalone)
    *   *Example:* `["Testability Analysis & Criticality Assessment", "Test Plan Generation"]`
    *   *Example:* `["Test Execution"]` (Assuming a plan exists)
4.  **Relevant Context:** Provide necessary details:
    *   **Codebase Information:** Path(s) to relevant code directories/files, primary language(s), key frameworks used.
    *   **Recent Changes:** Links to PRs, commit hashes, summaries of recent modifications or features added.
    *   **Requirements/Specifications:** Links to docs, user stories, or descriptions of the functionality under test.
    *   **Previous Interactions:** Summaries of past test runs, known flaky tests, areas of concern identified previously.
    *   **Constraints:** Time limits, resource limitations (e.g., "Cannot use external APIs"), required testing libraries/tools, specific environment details (e.g., "Must run within existing Docker setup defined in `docker-compose.test.yml`").
    *   **Architecture Notes:** Brief overview if relevant (e.g., "This is a microservice interacting with X and Y," "Uses a PostgreSQL database").
5.  **Desired Output(s):** Specify the expected artifact(s) for *this interaction*, corresponding to the requested task(s).
    *   *Example (for Analysis & Plan):* "A Markdown report detailing critical areas to test, followed by a separate Markdown document containing the step-by-step test plan."
    *   *Example (for Execution):* "Real-time updates after each test suite, requesting confirmation to proceed. No final summary report needed in *this* interaction (will request separately)."
6.  **Any Known Pitfalls or Areas to Emphasize:** Highlight specific challenges, tricky logic, areas *not* to test, or aspects needing special attention. (e.g., "Pay close attention to error handling in the payment gateway integration," "Do not test the legacy reporting module yet," "Ensure date/time logic handles timezones correctly").
