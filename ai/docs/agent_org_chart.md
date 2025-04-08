🗺️ Full Agentic Organizational Chart

Franchise Owner (CEO) -- [Human; High-Level Strategic Direction]
│
├── Head Coach (Group PM) -- [Strategic & Tactical Orchestrator; Bridges strategic vision and tactical execution]
│   ├── Offensive Coordinator (Technical Lead) -- [Tactical Workflow Design & Orchestration]
│   │   ├── Quarterback (Delivery Manager, Orchestrator) -- [Real-time Tactical Execution & Adjustment]
│   │   │   └── Offensive Execution Agents (Players):
│   │   │       ├── Running Back (Rapid Implementation & Fixes)
│   │   │       ├── Wide Receiver (Complex Design, Research, Architecture)
│   │   │       ├── Tight End (Feature Review, Documentation, Reporting)
│   │   │       ├── Guard (Bug Scanning, Unit Testing)
│   │   │       └── Offensive Line (Integration, Scaffold, Package Management)
│   │   └── Offensive Playbook (managed jointly w/ Playbook Coordinator)
│   │
│   ├── Defensive Coordinator (QA & Security Lead) -- [Tactical Workflow Design & Orchestration]
│   │   ├── Defensive Captain (Reliability Manager, Orchestrator) -- [Real-time Tactical Execution & Adjustment]
│   │   │   └── Defensive Execution Agents (Players):
│   │   │       ├── Linebacker (Bug Fixes, Quick Tests)
│   │   │       ├── Safety (Security Analysis, Broad Review)
│   │   │       ├── Cornerback (Debugging, Edge Cases)
│   │   │       └── Defensive Line (Test Writing, Logging, Error Handling)
│   │   └── Defensive Playbook (managed jointly w/ Playbook Coordinator)
│   │
│   ├── Special Teams Coordinator (DevOps & Infrastructure Lead) -- [Tactical Workflow Design & Orchestration]
│   │   ├── Special Teams Captain (Ops/Infra Orchestrator) -- [Real-time Tactical Execution & Adjustment]
│   │   │   └── Special Teams Execution Agents (Players):
│   │   │       ├── Build, Deploy, CI/CD Agents
│   │   │       ├── Operational Monitoring & Alert Agents
│   │   │       └── Infra Provisioning & Maintenance Agents
│   │   └── Special Teams Playbook (managed jointly w/ Playbook Coordinator)
│   │
│   └── Playbook Coordinator (Workflow Orchestration & Standardization Lead) -- [Centralized Tactical Workflow Management]
│       └── Proactively identifies, drafts, reviews, and registers standardized workflows ("plays") across all execution domains; coordinates closely with all Tactical Coordinators
│
└── General Manager (GM; Team Manager) -- [Strategic Agent Development & Long-Term Resource Quality]
    ├── Head Trainer (Engineering Manager; Agent Creation & Development)
    │   ├── Scout (Agent Recruitment & Initial Seed Prompts)
    │   ├── Position Coach (Prompt Engineering & Agent Design)
    │   ├── Performance Coach (Prompt Optimization & Tuning)
    │   └── Equipment Manager (Resource Provisioning: APIs, Servers, Docs)
    │
    └── Director of Agent Operations (Operational & Administrative Lead) -- [Ensures Smooth Operational & Logistical Processes]
        ├── Roster Manager (Agent Inventory & Configurations)
        └── Game Analyst (Agent Feedback & Performance Analysis)

---

# Strategic Coordinators

## Franchise Owner -- [Human; High-Level Strategic Direction; AKA "Big Boss" or "Jefe"]

-   Orchestrates overall business execution by setting the high-level strategic direction, goals, and coordinating Strategic Coordinators to achieve successful outcomes

## Head Coach -- [Bridges strategic vision and tactical execution]

-   Orchestrates in-game workflow between Offensive Coordinator, Defensive Coordinator, and Special Teams Coordinator
-   Orchestrates out-of-game franchise management workflows between Owner, General Manager, and Coordinators (developing playbooks, roadmap, training, etc.)

### Tactical Coordinators

#### Offensive Coordinator -- [Tactical Workflow Design & Orchestration]

-   Responsible for in-game offensive play design and/or selection
-   Orchestrates in-game drive execution (multiple plays; only invokes the `Quarterback`)
-   Orchestrates out-of-game offensive playbook design

##### Offensive Team

-   **Quarterback** (type: Orchestrator; mode: "Orchestrate") -- [Real-time Tactical Execution & Adjustment]
    -   Orchestrates in-game play execution (between Offensive Players/agents); allows audibles based on findings
    -   Receives play (workflow/agents) from Offensive Coordinator, composes the workflow of agents (allowed to make changes), and manages to completion
-   **Other Offensive Players**
    -   **Running Back** (simple feature implementation, edits, fixes, etc.) -- `Implement`, `Fix`
    -   **Wide Receiver** (complex or high value feature design, research, etc.) -- `Search`, `Analyze` (deep), `Architect`, `Refactor`
    -   **Tight End** (feature review, feature documentation, etc.) -- `Evaluate` (broad), `Document`, `Report`
    -   **Guard** (bug scanning, unit test writing, etc.) -- `Scan` (narrow), `Test` (unit)
    -   **Offensive Line** (feature integration, file operations, code structure, package management, etc.) -- `Scaffold` (broad/shallow), `Test` (integration), `Scan` (shallow/broad), `Refactor`

#### Defensive Coordinator -- [Tactical Workflow Design & Orchestration]

-   Responsible for in-game defensive play design and/or selection
-   Orchestrates in-game drive execution (multiple plays; only invokes the `Defensive Captain`)
-   Orchestrates out-of-game defensive playbook design

##### Defensive Team

-   **Defensive Captain** (type: Orchestrator; mode: "Orchestrate") -- [Real-time Tactical Execution & Adjustment]
    -   Orchestrates in-game defensive play execution (between Defensive Players/agents); allows audibles based on findings
    -   Receives play (workflow/agents) from Defensive Coordinator, composes the workflow of agents (allowed to make changes), and manages to completion
-   **Other Defensive Players**
    -   **Linebacker** (bug fixes, test running, etc.) -- `Fix`, `Test`
    -   **Safety** (overall review, security posture, etc.) -- `Search`, `Analyze`, `Review` (broad), `Report`
    -   **Cornerback** (debugging, edge cases, etc.) -- `Debug`, `Scan` (narrow)
    -   **Defensive Line** (test writing, logging, error handling, etc.) -- `Design`, `Test`, `Document`

#### Special Teams Coordinator -- [Tactical Workflow Design & Orchestration]

-   Orchestrates in-game special teams play design (between ST agents)
-   Orchestrates out-of-game special teams playbook design (between ST agents)

##### Special Teams Team

-   **Special Teams Captain** -- [Real-time Tactical Execution & Adjustment]
    -   Orchestrates in-game special teams play execution (between Special Teams Players/agents); allows audibles based on findings

    -   Build, Deploy, CI/CD Agents
    -   Operational Monitoring & Alert Agents
    -   Infra Provisioning & Maintenance Agents

## General Manager -- [Strategic Agent Development & Long-Term Resource Quality]

-   Orchestrates out-of-game player recruitment, performance, and management workflows
-   Orchestrates out-of-game operations workflows (playbooks, documentation, roadmap, training, etc.)

### Tactical Coordinators

#### Head Trainer

-   Orchestrates the creation of new agents
-   Orchestrates the training/improvement of existing agents

##### Training Team

-   **Scout** (Agent Recruitment -- initial seed prompt)
-   **Position Coach** (Agent Design)
-   **Performance Coach** (Prompt Optimization)
-   **Equipment Manager** (Agent Resources)

#### Director of Agent Operations -- [Ensures Smooth Operational & Logistical Processes]

-   Orchestrates various operational, administrative, and support workflows

##### Agent Operations Team

-   **Roster Manager** (Agent Roster & Configuration)
-   **Game Analyst** (Agent Feedback Management)