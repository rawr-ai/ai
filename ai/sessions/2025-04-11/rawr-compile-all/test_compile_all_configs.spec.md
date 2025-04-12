# Test Specification: Compile All Configurations

**Feature:** Compile all configurations when no slug is provided

**Scenario:** Running `rawr compile` without a slug compiles all valid configs found recursively in the root directory specified in `rawr.config.yaml`

**Assumptions for this Test Specification:**
*   Valid configurations are identified by the presence of a `config.yaml` file within subdirectories of the `agent_config_dir`. (Needs confirmation)
*   The compilation process generates an output artifact for each valid configuration found. (Needs confirmation)
*   Compiled artifacts are placed in a `./compiled_agents/` directory relative to the project root. (Needs confirmation)
*   Compiled artifacts are named based on the subdirectory name (agent slug), e.g., `agent_slug.out`. (Needs confirmation)
*   Initial implementation might only scan the root `agent_config_dir`, but the test reflects the final recursive goal.

**Given** a `rawr.config.yaml` file exists at the project root containing `agent_config_dir: ./ai/agents/`
**And** the directory `./ai/agents/` exists
**And** the directory `./ai/agents/agent1/` exists and contains a `config.yaml` file
**And** the directory `./ai/agents/agent2/` exists and contains a `config.yaml` file
**And** the directory `./ai/agents/not_an_agent/` exists but does *not* contain `config.yaml`
**And** the directory `./ai/agents/agent3/sub_agent/` exists and contains a `config.yaml` file (for future recursive testing)
**And** the assumed output directory `./compiled_agents/` is initially empty

**When** the command `rawr compile` is executed without any arguments from the project root

**Then** the command should exit successfully (exit code 0)
**And** the file `./compiled_agents/agent1.out` should exist (Assumption: `.out` extension)
**And** the file `./compiled_agents/agent2.out` should exist (Assumption: `.out` extension)
**And** the file `./compiled_agents/agent3/sub_agent.out` should exist (Assumption: `.out` extension, for future recursive testing)
**And** no compiled artifact for `not_an_agent` should exist in `./compiled_agents/`
**And** the content of the compiled artifacts should be correct based on their respective source configurations (Verification details depend on the actual 'compile' definition)

**Scenario:** Error handling - Missing `rawr.config.yaml`

**Given** the `rawr.config.yaml` file does not exist at the project root
**When** the command `rawr compile` is executed without any arguments
**Then** the command should exit with a non-zero status code
**And** an informative error message indicating the missing configuration file should be displayed

**Scenario:** Error handling - Missing `agent_config_dir`

**Given** a `rawr.config.yaml` file exists at the project root containing `agent_config_dir: ./non_existent_dir/`
**And** the directory `./non_existent_dir/` does not exist
**When** the command `rawr compile` is executed without any arguments
**Then** the command should exit with a non-zero status code
**And** an informative error message indicating the missing agent config directory should be displayed

**Scenario:** Error handling - No valid configurations found

**Given** a `rawr.config.yaml` file exists at the project root containing `agent_config_dir: ./ai/agents/`
**And** the directory `./ai/agents/` exists but contains no subdirectories with `config.yaml` (based on assumption)
**When** the command `rawr compile` is executed without any arguments
**Then** the command should exit with a non-zero status code
**And** an informative error message indicating that no valid configurations were found to compile should be displayed

**(Note: These tests are expected to FAIL initially as the functionality is not implemented.)**