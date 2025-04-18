Objective  
Deliver a fully‑working recursive config‑loading feature for the RAWR CLI, following the implementation blueprint in `recursive_config_loading_plan_v1.md`.

Key context to ingest first  
1. Status analysis: `recursive_config_loading_status.md` – explains current failures and motivation.  
2. Implementation plan: `recursive_config_loading_plan_v1.md` – granular tasks, effort/complexity, agent owners, acceptance checklist.  
3. Source code & tests already in the repo (paths as referenced in the plan).

High‑level mandate  
1. Read the two Markdown files above to ground yourself.  
2. Design a multi‑agent workflow that executes every task in the plan, respecting the “Owner” column (agent slugs): analyze, implement, refactor, test, document, git (optional review).  
3. Sequence the work logically (model & extractor changes → compiler refactor → tests → docs → git).  
4. Use `new_task` to delegate each task to the appropriate agent, supplying:  
   • concise goal / acceptance criteria for that task  
   • relevant file paths or code snippets  
   • reminder to use `attempt_completion` when done  
5. Track progress, looping until the acceptance checklist in the plan is met:  
   • `rawr compile` with empty `.rawr_registry` exits 0 and registers ≥ 1 agent  
   • `rawr compile <slug>` works for any agent  
   • `pytest -q` passes  
   • docs updated  
6. Escalate blockers or ambiguities per your SOP.  
7. On success, instruct `git` agent to push changes / open PR.

Constraints & notes  
• Do not perform the specialist work yourself; focus on orchestration.  
• Keep delegation instructions concise but complete; let specialist agents decide *how*.  
• Reuse plan section numbers when referencing tasks to make tracking easier.  
• Maintain a running summary of finished vs. pending tasks; surface risks early.  
• Stop when the project meets all acceptance criteria and the PR is ready.
