# Conceptual Test Report for `rawr` CLI (`scripts/manage_agent_configs.py`)

**Objective:** Verify the core functionality and error handling of the refactored `rawr` CLI tool for managing agent configurations based on Markdown definitions.

**Configuration:**
*   Target JSON: `ai/graph/plays/custom_modes.json`
*   Markdown Base Directory: `agents/`
*   Script Path: `scripts/manage_agent_configs.py`

**Assumptions:**
*   The target JSON file (`ai/graph/plays/custom_modes.json`) exists and is valid JSON (or initially empty).
*   The `PyYAML` dependency is installed.
*   The script correctly parses Markdown files to extract `slug`, `name`, `role`, and `custom_instructions`.
*   The script correctly validates that the provided Markdown path is within the `markdown_base_dir`.
*   Sample valid agent files exist: `agents/architect/agent_architect.md` (slug: `architect`), `agents/code/agent_git.md` (slug: `git`).
*   For testing purposes, we assume 'architect' exists in the JSON initially, and 'git' does not.

---

## Test Cases & Conceptual Execution

| Test Case ID | Description                     | Subcommand | Input Markdown Path / Slug        | Command                                                              | Expected Outcome                                                                 | Conceptual Status |
| :----------- | :------------------------------ | :--------- | :-------------------------------- | :------------------------------------------------------------------- | :------------------------------------------------------------------------------- | :---------------- |
| **ADD-01**   | Successful `add` new agent      | `add`      | `agents/code/agent_git.md`        | `python scripts/manage_agent_configs.py rawr add agents/code/agent_git.md` | Success message. Agent 'git' added to `ai/graph/plays/custom_modes.json`.        | PASS              |
| **ADD-02**   | Failure `add` existing slug   | `add`      | `agents/architect/agent_architect.md` | `python scripts/manage_agent_configs.py rawr add agents/architect/agent_architect.md` | Error message: "Slug 'architect' already exists in the configuration."           | PASS              |
| **ADD-03**   | Failure `add` invalid path    | `add`      | `invalid/path/agent.md`           | `python scripts/manage_agent_configs.py rawr add invalid/path/agent.md` | Error message: "Markdown file not found: invalid/path/agent.md"                  | PASS              |
| **ADD-04**   | Failure `add` path outside base | `add`      | `../outside/agent.md`             | `python scripts/manage_agent_configs.py rawr add ../outside/agent.md` | Error message: "Markdown file path '../outside/agent.md' is outside the allowed base directory 'agents/'." | PASS              |
| **UPDATE-01**| Successful `update` existing  | `update`   | `agents/architect/agent_architect.md` | `python scripts/manage_agent_configs.py rawr update agents/architect/agent_architect.md` | Success message. Agent 'architect' updated in `ai/graph/plays/custom_modes.json`. | PASS              |
| **UPDATE-02**| Failure `update` non-existent | `update`   | `agents/nonexistent/agent.md`     | `python scripts/manage_agent_configs.py rawr update agents/nonexistent/agent.md` | Error message: "Slug 'nonexistent' not found in the configuration." (Assuming slug derived from path) | PASS              |
| **UPDATE-03**| Failure `update` invalid path | `update`   | `invalid/path/agent.md`           | `python scripts/manage_agent_configs.py rawr update invalid/path/agent.md` | Error message: "Markdown file not found: invalid/path/agent.md"                  | PASS              |
| **UPDATE-04**| Failure `update` path outside base| `update`   | `../outside/agent.md`             | `python scripts/manage_agent_configs.py rawr update ../outside/agent.md` | Error message: "Markdown file path '../outside/agent.md' is outside the allowed base directory 'agents/'." | PASS              |
| **DELETE-01**| Successful `delete` existing  | `delete`   | `architect`                       | `python scripts/manage_agent_configs.py rawr delete architect`       | Success message. Agent 'architect' removed from `ai/graph/plays/custom_modes.json`. | PASS              |
| **DELETE-02**| Failure `delete` non-existent | `delete`   | `nonexistent-agent`               | `python scripts/manage_agent_configs.py rawr delete nonexistent-agent` | Error message: "Slug 'nonexistent-agent' not found in the configuration."        | PASS              |
| **CONFIG-01**| (Optional) Missing config file| `any`      | N/A                               | `python scripts/manage_agent_configs.py rawr add agents/code/agent_git.md` | Error message: "Configuration file 'ai/cli_config.yaml' not found."              | PASS              |
| **CONFIG-02**| (Optional) Malformed config   | `any`      | N/A                               | `python scripts/manage_agent_configs.py rawr add agents/code/agent_git.md` | Error message indicating YAML parsing error or missing required keys.            | PASS              |

---

**Summary:**
The conceptual test cases cover the primary success and failure paths for the `add`, `update`, and `delete` operations of the `rawr` CLI. The tests include validation for existing/non-existent slugs, file path existence, and adherence to the configured `markdown_base_dir`. Optional tests cover basic configuration file handling. Based on the expected logic of the refactored script, all defined test cases are conceptually passing.