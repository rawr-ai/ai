# Test Plan for `scripts/manage_agent_configs.py`

## 1. Argument Handling

### 1.1 Missing Arguments for `add`
**Setup:**
*   No CLI config YAML file required.
*   No target JSON file required.
*   Command: `python scripts/manage_agent_configs.py add`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating missing required arguments (slug, agent_type, description, markdown_file).

**Mocking:**
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 1.2 Invalid Arguments for `add`
**Setup:**
*   No CLI config YAML file required.
*   No target JSON file required.
*   Command: `python scripts/manage_agent_configs.py add invalid-slug agent --description "Test Agent" --markdown_file docs/agent_template.md` (invalid slug format)

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating invalid slug format.

**Mocking:**
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 1.3 Missing Arguments for `update`
**Setup:**
*   CLI config YAML file not strictly required, but presence should not affect this test.
*   No target JSON file required.
*   Command: `python scripts/manage_agent_configs.py update`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating missing required arguments (slug).

**Mocking:**
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 1.4 Invalid Arguments for `update`
**Setup:**
*   CLI config YAML file not strictly required, but presence should not affect this test.
*   No target JSON file required.
*   Command: `python scripts/manage_agent_configs.py update invalid-slug --description "Updated Description"` (invalid slug format)

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating invalid slug format.

**Mocking:**
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 1.5 Missing Arguments for `delete`
**Setup:**
*   CLI config YAML file not strictly required, but presence should not affect this test.
*   No target JSON file required.
*   Command: `python scripts/manage_agent_configs.py delete`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating missing required arguments (slug).

**Mocking:**
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 1.6 `--verbose` Flag
**Setup:**
*   Valid CLI config YAML and target JSON files (can be minimal valid files).
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md --verbose`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 0
*   Console output:
    *   Verbose output messages during script execution (e.g., file read/write operations, configuration loading).
    *   Confirmation message of successful agent addition.

**Mocking:**
*   `sys.argv` to simulate command-line arguments.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.

## 2. Configuration File (`scripts/cli_config.yaml`)

### 2.1 Missing `scripts/cli_config.yaml`
**Setup:**
*   `scripts/cli_config.yaml` does not exist.
*   Target JSON file exists (can be empty or valid).
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that `scripts/cli_config.yaml` is missing and instructions to create it.

**Mocking:**
*   `Path.is_file` to mock the absence of `scripts/cli_config.yaml`.
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 2.2 Malformed `scripts/cli_config.yaml` (Invalid YAML)
**Setup:**
*   `scripts/cli_config.yaml` exists but contains invalid YAML syntax.
*   Target JSON file exists (can be empty or valid).
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating YAML parsing error in `scripts/cli_config.yaml`.

**Mocking:**
*   `Path.is_file` to mock the presence of `scripts/cli_config.yaml`.
*   `Path.read_text` to return malformed YAML content.
*   `yaml.safe_load` to raise a YAML parsing exception.
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

### 2.3 Malformed `scripts/cli_config.yaml` (Missing `agent_config_file`)
**Setup:**
*   `scripts/cli_config.yaml` exists but is missing the `agent_config_file` key.
*   Target JSON file exists (can be empty or valid).
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that `agent_config_file` is missing in `scripts/cli_config.yaml`.

**Mocking:**
*   `Path.is_file` to mock the presence of `scripts/cli_config.yaml`.
*   `Path.read_text` to return YAML content without `agent_config_file`.
*   `yaml.safe_load`.
*   `sys.argv` to simulate command-line arguments.
*   `sys.exit` to capture exit code.

## 3. Core Operations (Happy Paths)

### 3.1 Successful `add`
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists (can be empty or contain existing agent configs).
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 0
*   Console output: Confirmation message of successful agent addition.
*   Target JSON file: Updated to include the new agent configuration.

**Mocking:**
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 3.2 Successful `update`
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists and contains configuration for `test-agent`.
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py update test-agent --description "Updated Test Agent Description"`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 0
*   Console output: Confirmation message of successful agent update.
*   Target JSON file: Updated to reflect the new description for `test-agent`.

**Mocking:**
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 3.3 Successful `delete`
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists and contains configuration for `test-agent`.
*   Command: `python scripts/manage_agent_configs.py delete test-agent`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 0
*   Console output: Confirmation message of successful agent deletion.
*   Target JSON file: Updated to remove the configuration for `test-agent`.

**Mocking:**
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

## 4. Core Operations (Error Cases)

### 4.1 `add` - Slug Exists
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists and already contains configuration for `test-agent`.
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the agent slug `test-agent` already exists.
*   Target JSON file: Unchanged.

**Mocking:**
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 4.2 `add` - Invalid Markdown File (Non-Existent)
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists (can be empty or valid).
*   Markdown file `docs/non_existent_agent.md` does not exist.
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/non_existent_agent.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the Markdown file `docs/non_existent_agent.md` does not exist.
*   Target JSON file: Unchanged.

**Mocking:**
*   `Path.is_file` to mock the absence of `docs/non_existent_agent.md`.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 4.3 `add` - Invalid Markdown Content (Malformed)
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists (can be empty or valid).
*   Markdown file `docs/malformed_agent.md` exists but has invalid structure (e.g., missing required sections).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/malformed_agent.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the Markdown file `docs/malformed_agent.md` has an invalid structure.
*   Target JSON file: Unchanged.

**Mocking:**
*   `Path.is_file` to mock the presence of `docs/malformed_agent.md`.
*   `Path.read_text` to return malformed Markdown content.
*   Markdown parsing logic within the script to detect malformed structure.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 4.4 `update` - Slug Missing
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists but does not contain configuration for `non-existent-agent`.
*   Command: `python scripts/manage_agent_configs.py update non-existent-agent --description "Updated Description"`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the agent slug `non-existent-agent` was not found.
*   Target JSON file: Unchanged.

**Mocking:**
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 4.5 `update` - Invalid Markdown File (Non-Existent)
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists and contains configuration for `test-agent`.
*   Markdown file `docs/non_existent_agent.md` does not exist.
*   Command: `python scripts/manage_agent_configs.py update test-agent --markdown_file docs/non_existent_agent.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the Markdown file `docs/non_existent_agent.md` does not exist.
*   Target JSON file: Unchanged.

**Mocking:**
*   `Path.is_file` to mock the absence of `docs/non_existent_agent.md`.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 4.6 `update` - Invalid Markdown Content (Malformed)
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists and contains configuration for `test-agent`.
*   Markdown file `docs/malformed_agent.md` exists but has invalid structure.
*   Command: `python scripts/manage_agent_configs.py update test-agent --markdown_file docs/malformed_agent.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the Markdown file `docs/malformed_agent.md` has an invalid structure.
*   Target JSON file: Unchanged.

**Mocking:**
*   `Path.is_file` to mock the presence of `docs/malformed_agent.md`.
*   `Path.read_text` to return malformed Markdown content.
*   Markdown parsing logic within the script to detect malformed structure.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.


### 4.7 `delete` - Slug Missing
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a valid target JSON file.
*   Target JSON file exists but does not contain configuration for `non-existent-agent`.
*   Command: `python scripts/manage_agent_configs.py delete non-existent-agent`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating that the agent slug `non-existent-agent` was not found.
*   Target JSON file: Unchanged.

**Mocking:**
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.


## 5. File Handling (Target JSON)

### 5.1 Non-Existent Target JSON
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a target JSON file that does not exist.
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 0
*   Console output: Confirmation message of successful agent addition.
*   Target JSON file: Created and contains the new agent configuration.

**Mocking:**
*   `Path.is_file` to mock the absence of the target JSON file initially.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 5.2 Empty Target JSON
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a target JSON file that exists but is empty.
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 0
*   Console output: Confirmation message of successful agent addition.
*   Target JSON file: Updated to include the new agent configuration.

**Mocking:**
*   `Path.is_file` to mock the presence of the target JSON file.
*   `Path.read_text` to return empty content for the target JSON file.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `json.load`/`dump`.
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

### 5.3 Malformed Target JSON (Invalid JSON)
**Setup:**
*   Valid `scripts/cli_config.yaml` pointing to a target JSON file that exists but contains invalid JSON syntax.
*   Valid Markdown file (`docs/agent_template.md`).
*   Command: `python scripts/manage_agent_configs.py add test-agent agent --description "Test Agent" --markdown_file docs/agent_template.md`

**Action:** Run the command.

**Expected Outcome:**
*   Exit code: 1
*   Console output: Error message indicating JSON parsing error in the target JSON file.
*   Target JSON file: Unchanged.

**Mocking:**
*   `Path.is_file` to mock the presence of the target JSON file.
*   `Path.read_text` to return malformed JSON content for the target JSON file.
*   `json.load` to raise a JSON parsing exception.
*   File system operations (`Path.is_file`, `Path.read_text`, `Path.write_text`, `Path.mkdir`).
*   `yaml.safe_load`.
*   `argparse` results or `sys.argv`.

## 6. Exit Codes

### 6.1 Success Exit Code (0)
**Setup:**
*   Refer to happy path test cases (e.g., 3.1, 3.2, 3.3).

**Action:** Run any happy path command.

**Expected Outcome:**
*   Exit code: 0

**Mocking:**
*   As per the specific happy path test case.
*   `sys.exit` to capture exit code.

### 6.2 Failure Exit Code (1)
**Setup:**
*   Refer to error case test cases (e.g., 4.1, 4.4, 5.3).

**Action:** Run any error case command.

**Expected Outcome:**
*   Exit code: 1

**Mocking:**
*   As per the specific error case test case.
*   `sys.exit` to capture exit code.