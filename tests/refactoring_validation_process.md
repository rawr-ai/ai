# Generic Post-Refactoring Validation Process

This document outlines a general iterative process for validating code after significant refactoring.

## Goal & Overall Strategy

The primary goal is to ensure the refactored code remains functional, integrated correctly, and meets quality standards. The recommended strategy involves an iterative cycle:

1.  **Run Validation Check:** Execute a specific quality or functionality check (e.g., static analysis, unit tests, integration tests, build process).
2.  **Analyze Results:** Carefully examine the output to identify any failures, errors, warnings, or unexpected behavior (e.g., missing dependencies, type mismatches, test assertion failures, style violations).
3.  **Diagnose & Fix Issues:** Determine the root cause of each issue and implement the necessary corrections. This may involve:
    *   **Dependency Management:** Adding, removing, or updating dependencies using the project's package manager and requirements files (e.g., `pip`, `npm`, `requirements.txt`, `package.json`).
    *   **Code Correction:** Fixing logic errors, type errors, or other bugs identified in the application code.
    *   **Test Code Updates:** Modifying test cases to reflect changes in the application code (e.g., updating mock targets, adjusting assertions, passing new arguments).
    *   **Tooling Application:** Using relevant development tools like code formatters or linters to address specific issues or maintain standards.
    *   **Agent Assistance:** Leveraging AI agent capabilities (like file reading/writing, command execution) to perform fixes efficiently. This might occasionally require switching agent modes if file permissions are restricted (e.g., needing a 'Code' mode to edit source files when in a 'Test' mode).
4.  **Re-run Check:** Execute the *same* validation check again to confirm the fix was successful and didn't introduce new problems.
5.  **Proceed:** Once a validation stage passes consistently, move to the next stage in the planned validation sequence (e.g., from static analysis to unit tests, then to integration tests).

## Recommended Validation Stages

A typical sequence of validation stages includes:

1.  **Static Analysis:**
    *   **Tools:** Linters (e.g., Flake8, ESLint), Type Checkers (e.g., MyPy, TypeScript Compiler), Code Formatters (e.g., Black, Prettier).
    *   **Focus:** Catching style inconsistencies, potential bugs, type errors, and formatting issues early without executing code. Iterate on fixing reported issues and re-running the tools. Address dependency issues for these tools as needed.

2.  **Unit Testing:**
    *   **Tools:** Testing frameworks (e.g., Pytest, Jest, JUnit).
    *   **Focus:** Verifying individual components or functions in isolation. Debug failures by examining test logic, application code, and mock configurations. Ensure tests accurately reflect the refactored code's behavior and interfaces.

3.  **Integration Testing:**
    *   **Tools:** Testing frameworks, potentially with test runners or helpers (e.g., `CliRunner`, `supertest`).
    *   **Focus:** Verifying the interaction between different components or modules. Debug failures by analyzing component interactions, API contracts, mock setups, and expected vs. actual outputs or side effects. Ensure core application dependencies are correctly installed and available.

## Summary of Approach

This iterative validation process emphasizes a systematic approach: check, analyze, fix, re-check. It leverages static analysis for early feedback and relies on comprehensive unit and integration tests to confirm functional correctness after refactoring. Effective dependency management and the use of appropriate development and agent tools are key to efficiently resolving issues encountered during validation. The process concludes when all planned validation stages pass successfully.