sequenceDiagram
    participant TA as Test Agent
    participant AA as Architect Agent
    participant RA as Refactor Agent

    Note over TA: Step 3: Reviews refactor_analysis_v1.md, tests/conftest.py, tests/test_installation.py
    TA->>TA: Generate Test Review
    Note over TA: Outputs test_review_v1.md

    Note over AA: Step 4: Reviews refactor_analysis_v1.md, test_review_v1.md, tests/ structure
    AA->>AA: Generate Architectural Review
    Note over AA: Outputs architect_review_v1.md

    Note over RA: Step 5: Synthesizes refactor_analysis_v1.md, test_review_v1.md, architect_review_v1.md
    RA->>RA: Generate Final Consolidated Report
    Note over RA: Outputs final_test_review_report.md