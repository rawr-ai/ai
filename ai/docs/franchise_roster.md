# Agent Roster

## Agent Roles

### Franchise Owner (CEO)

-   **Purpose:** Sets the high level product vision, strategy, goals, and roadmap.
-   **Inputs:** Market research, user feedback, vibes, etc.
-   **Functions / Key Responsibilities:**
    -   Sets the high level product vision, strategy, goals, and roadmap (works with Assistant to maintain a living document).
    -   Initiates the process ("Hits Enter").
-   **Outputs:**
    -   High level product vision, strategy, goals, and roadmap.
    -   Initial Roster of agents (implied).
-   **Coordination / Key Interactions:** (Implied: Head Coach, General Manager)

### General Manager (GM)

-   **Purpose:** Oversees the strategic pipeline of agent creation, skill development, prompt optimization, and overall agent roster management. Ensures the long-term quality, availability, and continuous improvement of agents to meet strategic goals and operational needs. Focuses on the "out-of-game" aspects of team building and capability enhancement. Responsible for scouting, composition, and overall development of the team (agents).
-   **Inputs:**
    -   Strategic goals and vision from the Franchise Owner.
    -   Post-game feedback from the Franchise Owner and Head Coach.
    -   New team or capability requirements from the Franchise Owner or Head Coach.
-   **Unique Context:**
    -   Agent roster, organization chart, and agent capabilities from the Roster Manager.
-   **Functions / Key Responsibilities:**
    -   **Agent Talent Pipeline Management:** Oversees agent creation, skill development strategy.
    -   **Roster Strategy & Composition:** Understands future needs, plans roster balance, manages inventory via Roster Manager.
    -   **Performance Oversight & Optimization:** Receives high-level feedback, coordinates optimization efforts with HT/Performance Coach, ensures continuous improvement loop.
    -   **Resource Management & Coordination:** Manages development resources, coordinates support staff (Scout, Position Coach, Head Trainer, Performance Coach, Roster Manager).
    -   **Strategic Alignment:** Aligns roster with vision, provides capability input to HC.
-   **Outputs:**
    -   An optimized, well-documented, and high-quality roster of agents.
    -   Strategic agent development roadmap.
    -   Guidance and direction for the agent support staff.
    -   Reports on roster health, capabilities, and development progress to FO and HC.
    -   Updated agent configurations and documentation (via coordination).
-   **Coordination / Key Interactions:**
    -   **Franchise Owner:** Receives strategic direction, reports on roster strategy/health.
    -   **Head Coach:** Receives capability requirements/feedback, provides input on talent.
    -   **Scout:** Defines needs for new agents.
    -   **Position Coach (Builder):** Oversees agent creation.
    -   **Head Trainer:** Coordinates agent training/development.
    -   **Performance Coach:** Coordinates agent optimization.
    -   **Roster Manager:** Oversees agent inventory management.

### Head Coach (HC)

-   **Purpose:** Translates high-level vision/goals from the Franchise Owner into actionable "Game Plans" (project plans/strategies). Orchestrates overall execution by coordinating Coordinators, making high-level tactical decisions during the "game," and ensuring alignment. Focuses on "in-game" execution and coordination. Coordinates the product development process.
-   **Inputs:**
    -   High-level vision, strategy, goals from the Franchise Owner.
    -   Agent roster capabilities and limitations from the General Manager.
    -   Progress reports, status updates, and issues from Coordinators.
    -   Real-time execution data and feedback.
    -   Historical data from past "games."
    -   Directives from owner, past games, structured feedback.
-   **Functions / Key Responsibilities:**
    -   **Game Plan Management:** Develops, maintains, adapts the overall strategy and sequence of major phases.
    -   **Coordinator Orchestration:** Assigns objectives to Coordinators, coordinates handoffs, facilitates communication, resolves conflicts.
    -   **Execution Oversight & Tactical Decisions:** Monitors progress, makes high-level tactical decisions/pivots.
    -   **Performance Monitoring & Feedback:** Receives updates, provides feedback to Coordinators (OC, DC, STC) and GM (on roster performance).
    -   **Stakeholder Communication:** Reports progress/risks to Franchise Owner, communicates plan to stakeholders.
    -   Assembles the roster (works with Scout, Trainer, etc.).
-   **Outputs:**
    -   The overall "Game Plan" for the project/objective.
    -   High-level objectives and assignments for Coordinators.
    -   Tactical decisions and adjustments.
    -   Structured performance feedback for Coordinators.
    -   Feedback on agent/roster performance for the General Manager.
    -   Progress reports and status updates for the Franchise Owner.
    -   Roster of agents.
-   **Coordination / Key Interactions:**
    -   **Franchise Owner:** Receives goals, reports progress/outcomes.
    -   **General Manager:** Consults on roster capabilities, provides feedback on agent performance.
    -   **Offensive Coordinator:** Assigns objectives, receives progress, provides feedback.
    -   **Defensive Coordinator:** Assigns objectives, receives progress, provides feedback.
    -   **Special Teams Coordinator:** Assigns objectives, receives progress, provides feedback.
    -   **Quarterback (potentially):** May receive direction or delegate sequences.
    -   **Assistant, Scout, Head Trainer** (from `feedback_orchestrate.md`)

### Offensive Coordinator (OC)

-   **Purpose:** Designs and coordinates the execution of "offensive plays" - workflows focused on creating net-new value (new features, experiments, major architectural changes). Designs offensive plays ("net-new" workflows).
-   **Inputs:**
    -   High-level objectives and game plan from the Head Coach.
    -   Feature requirements, user stories, design specifications, architectural documents.
    -   Performance data and feedback from ongoing plays.
    -   Post-game analysis and feedback from HC/FO.
    -   The Offensive Playbook.
-   **Functions / Key Responsibilities:**
    -   **Playbook Management:** Develops, curates, maintains the Offensive Playbook.
    -   **Play Design & Selection:** Translates objectives into technical plans/workflows, selects agents ("players") for plays, designs new plays.
    -   **Execution Coordination & Advisory:** Provides guidance to executing agents (e.g., Quarterback), advises on play selection/strategy/challenges.
    -   **Performance Assessment & Feedback:** Monitors agent performance, assesses against standards, provides structured feedback to Head Trainer.
    -   **Cross-Functional Collaboration:** Coordinates with DC (testability/security) and STC (build/deployment/infra needs), reports to HC.
    -   Selects players for offensive plays.
    -   Advises quarterback on plays.
-   **Outputs:**
    -   Detailed offensive plays (workflows, task breakdowns).
    -   Agent assignments for specific plays.
    -   Updates to the Offensive Playbook.
    -   Structured performance feedback for the Head Trainer.
    -   Progress reports and status updates for the Head Coach.
    -   Advice and guidance for the Quarterback and executing agents.
-   **Coordination / Key Interactions:**
    -   **Head Coach:** Receives objectives, reports progress, discusses strategy.
    -   **Quarterback:** Advises on play execution, provides direction.
    -   **Head Trainer:** Provides performance feedback on agents.
    -   **Defensive Coordinator:** Collaborates on testing/security integration.
    -   **Special Teams Coordinator:** Collaborates on build/deployment/infrastructure.
    -   **Executing Agents:** Assigns tasks, monitors progress.

### Defensive Coordinator (DC)

-   **Purpose:** Designs and coordinates the execution of "defensive plays" - workflows focused on ensuring quality, stability, security, and reliability (testing, debugging, security analysis, code reviews, vulnerability management).
-   **Inputs:**
    -   Quality standards, security policies, objectives from HC/FO.
    -   Code changes, new features, system updates from OC/Quarterback.
    -   Security advisories, threat intelligence, vulnerability reports.
    -   Performance data/results from ongoing defensive plays.
    -   Post-game analysis and feedback.
    -   The Defensive Playbook.
-   **Functions / Key Responsibilities:**
    -   **Playbook Management:** Develops, curates, maintains the Defensive Playbook (QA, security auditing, debugging, review standards).
    -   **Play Design & Selection:** Translates requirements into test plans/security reviews/debugging strategies, selects specialized agents, designs/adapts plays.
    -   **Execution Coordination & Advisory:** Guides executing agents (Test, Security, Debug), advises QB/OC on security/testability/debugging, oversees review/testing/validation loops.
    -   **Performance Assessment & Feedback:** Monitors agent performance/effectiveness, assesses against standards, provides structured feedback to Head Trainer.
    -   **Cross-Functional Collaboration:** Coordinates with OC ("shift-left"), STC (secure deployment/monitoring), reports quality/security/bugs to HC.
    -   Selects players for defensive plays.
-   **Outputs:**
    -   Detailed defensive plays (test plans, audit procedures, checklists).
    -   Agent assignments for defensive tasks.
    -   Updates to the Defensive Playbook.
    -   Bug reports, vulnerability assessments, security recommendations, quality metrics.
    -   Structured performance feedback for the Head Trainer.
    -   Progress reports and risk assessments for the Head Coach.
    -   Advice and guidance for other Coordinators/agents on quality/security.
-   **Coordination / Key Interactions:**
    -   **Head Coach:** Receives objectives, reports quality/security posture, escalates issues.
    -   **Offensive Coordinator:** Collaborates on integrating quality/security.
    -   **Special Teams Coordinator:** Collaborates on secure deployment/infrastructure.
    -   **Quarterback:** Advises on defensive considerations.
    -   **Head Trainer:** Provides performance feedback on agents.
    -   **Executing Agents (Test, Security, Debug):** Assigns tasks, monitors results, provides guidance.

### Special Teams Coordinator (STC)

-   **Purpose:** Designs and coordinates "special teams plays" - workflows related to infrastructure, build, deployment, release, monitoring, operations (CI/CD, environment management, IaC, observability, feedback loops).
-   **Inputs:**
    -   Deployment schedules, release plans, operational objectives from HC.
    -   Infrastructure requirements from OC/DC.
    -   Monitoring data, alerts, incident reports.
    -   Build artifacts and test results.
    -   Cloud provider docs, IaC templates, security policies.
    -   Post-game analysis/feedback on operations/deployments.
    -   The Special Teams Playbook.
    -   Game-time direction from HC.
-   **Functions / Key Responsibilities:**
    -   **Playbook Management:** Develops, curates, maintains Special Teams Playbook (builds, testing integration, deployment patterns, IaC, monitoring, incident response).
    -   **Play Design & Selection:** Translates requirements into automation/pipelines/procedures, selects agents/tools (build systems, cloud, containers, monitoring), designs/adapts plays.
    -   **Execution Coordination & Advisory:** Guides/oversees execution of build/deployment/ops tasks, advises HC/OC/DC on infra/deployment/costs/observability/CI/CD, ensures critical steps/gates in workflows.
    -   **Performance Assessment & Feedback:** Monitors performance/reliability/efficiency of pipelines/infra/ops, assesses agents/tools against SLOs/standards, provides structured feedback to Head Trainer.
    -   **Cross-Functional Collaboration:** Works with OC (deployability), DC (security in pipelines/infra), manages infra/environments, reports metrics (deployment freq, uptime, health) to HC.
    -   Assembles Special Teams player roster (potentially project-specific agents).
    -   Advises trainer on skills needed.
    -   Ensures critical steps aren't skipped (QB guardrails).
    -   Selects players for special teams plays.
-   **Outputs:**
    -   Detailed special teams plays (CI/CD configs, IaC scripts, runbooks, dashboards).
    -   Agent/tool assignments for operational tasks.
    -   Updates to the Special Teams Playbook.
    -   Provisioned infrastructure and environments.
    -   Deployment status reports, health metrics, incident post-mortems.
    -   Structured performance feedback for the Head Trainer.
    -   Advice and guidance for other Coordinators on operational matters.
-   **Coordination / Key Interactions:**
    -   **Head Coach:** Receives objectives, reports operational health/deployment status.
    -   **Offensive Coordinator:** Collaborates on build/deployment requirements.
    -   **Defensive Coordinator:** Collaborates on integrating security.
    -   **Head Trainer:** Provides performance feedback.
    -   **Executing Agents/Tools (CI/CD, IaC, Monitoring):** Configures, monitors, manages.

### Head Trainer (HT)

-   **Purpose:** Oversees the development, training, and performance improvement of all agents ("players"). Ensures agents have necessary skills, configurations, and support. Monitors agent performance, system health, resource usage, identifies bottlenecks, handles error recovery/rehabilitation. Ensures agents are "fit" to perform.
-   **Inputs:**
    -   Structured performance feedback from Coordinators, HC, etc.
    -   Role requirements and seed prompts from Scout/Builder.
    -   Agent performance metrics and operational data.
    -   Requests for new agent capabilities or improvements.
    -   The Training Playbook.
    -   Existing agent prompts and configurations.
-   **Functions / Key Responsibilities:**
    -   **Training Playbook & Strategy Management:** Develops/maintains Training Playbook, defines development pathways/skill frameworks, manages knowledge base on agent capabilities/configs/performance.
    -   **Agent Development & Onboarding:** Collaborates with Scout (requirements), collaborates with Position Coach (on agent design specifications) and Roster Manager (on agent configuration/registration), ensures integration.
    -   **Performance Feedback Integration & Analysis:** Centralizes/analyzes feedback to identify trends, gaps, optimization needs.
    -   **Performance Improvement & Optimization:** Collaborates with Performance Coach (diagnose issues), develops/implements training plans/prompt adjustments/config changes, tracks effectiveness.
    -   **Advisory Role & Collaboration:** Advises HC (readiness, skills, adjustments), provides insights to Coordinators (agent utilization), coordinates with Roster Manager (updates).
    -   Coordinates with Position Coach on agent design specifications and Roster Manager on configuration/implementation.
    -   Works with Scout to define role of new player.
-   **Outputs:**
    -   Updated agent prompts, configurations, and documentation.
    -   Individualized agent training and development plans.
    -   Updates to the Training Playbook.
    -   Reports on team skill levels, training progress, performance trends for HC.
    -   Guidance for the Performance Coach.
    -   Specifications for the Position Coach (design) and Roster Manager (configuration).
-   **Coordination / Key Interactions:**
    -   **Head Coach:** Reports on team development, advises on roster capabilities.
    -   **Offensive, Defensive, Special Teams Coordinators:** Receives performance feedback.
    -   **Scout:** Collaborates on defining new agent roles.
    -   **Position Coach (Agent Designer):** Designs agent blueprints/prompts.
    -   **Roster Manager:** Configures agents based on designs and manages roster records.
    -   **Performance Coach:** Collaborates on diagnosing issues/optimizing prompts.
    -   **Roster Manager:** Coordinates on maintaining accurate agent records.
    -   **Agents:** Subject of training/development.

### Scout

-   **Purpose:** Identifies gaps in the team, and suggests players (Agents) to add.
-   **Inputs:** Feedback from the game/notes.
-   **Functions / Key Responsibilities:** Creates the seed prompt for the new player (agent).
-   **Outputs:** Seed prompt for the new player.
-   **Coordination / Key Interactions:** Head Coach, Head Trainer, General Manager (implied via GM responsibilities).

### Position Coach (Agent Designer)

-   **Purpose:** Designs the conceptual blueprint, core prompt, and role definition for new agents based on requirements from Scout/GM/HC.
-   **Inputs:**
    -   Seed prompt from Scout.
    -   Context from Head Coach and/or Owner.
-   **Functions / Key Responsibilities:**
    -   Defines the agent's persona, expertise, scope, core responsibilities, and high-level workflow.
    -   Defines conceptual interactions with other agents and systems.
    -   Specifies required knowledge domains and potential learning strategies.
-   **Outputs:**
    -   Agent design document/prompt artifact (e.g., Markdown file defining the agent's system prompt and characteristics).
-   **Coordination / Key Interactions:** Head Coach, Head Trainer, General Manager (implied via GM responsibilities), Roster Manager (provides design artifact for configuration).

### Performance Coach

-   **Purpose:** Works with Head Trainer to improve the players (agents).
-   **Inputs:** Feedback from the game/notes.
-   **Functions / Key Responsibilities:** Takes in feedback from coordinators, identifies root cause of issues, optimizes agent prompts.
-   **Outputs:** Optimized agent prompts.
-   **Coordination / Key Interactions:** Head Trainer, Scout, General Manager (implied via GM responsibilities).

### Roster Manager

-   **Purpose:** Manages the roster of agents, translates agent design artifacts from the Position Coach into operational configurations (e.g., JSON), registers agents, and maintains their records.
-   **Inputs:** Agent design document/prompt artifact from Position Coach, performance data, status updates, registration/retirement requests.
-   **Functions / Key Responsibilities:** Translates agent design artifacts into JSON configuration files, Registers new/updated agents in the system, Maintains agent records, updates configurations, tracks status, generates roster reports, manages agent lifecycle (activation/deactivation).
-   **Outputs:** JSON agent configuration files, Updated roster records/manifest, agent status reports, configuration history.
-   **Coordination / Key Interactions:** Head Coach, Offensive Coordinator, Defensive Coordinator, Special Teams Coordinator, Head Trainer, General Manager (implied via GM responsibilities).

---
