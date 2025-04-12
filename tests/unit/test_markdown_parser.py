import pytest
from pathlib import Path
# Removed import: from cli.agent_config.markdown_utils import ( # Updated path
#     parse_markdown,
#     _find_section,
#     ROLE_DEFINITION_HEADINGS,
#     CUSTOM_INSTRUCTIONS_HEADINGS,
# )
# Removed import: from cli.agent_config.models import AgentConfig # Updated path

# --- Fixtures ---

@pytest.fixture
def valid_markdown_content():
    return """
# Test Agent Name
Some introductory text.

# Core Identity & Purpose
This is the role definition.
It spans multiple lines.

## Custom Instructions
Instruction section 1.
More instructions here.

## Another Heading (H2)
This should not be part of role def or custom instructions.

## Standard Operating Procedure (SOP) / Workflow
Instruction section 2.
Final instructions.

### Sub Heading (H3)
Details within section 2.
"""

@pytest.fixture
def minimal_markdown_content():
    return """
# Minimal Agent
Only has the required role.

# Role
The minimal role definition.
"""

@pytest.fixture
def missing_role_markdown_content():
    return """
# Missing Role Agent
This agent has no role definition heading.

## Custom Instructions
Some instructions.
"""

@pytest.fixture
def missing_name_markdown_content():
    # Note: No H1 heading
    return """
## Core Identity & Purpose
Role definition present.

## Custom Instructions
Instructions present.
"""

@pytest.fixture
def multiple_role_headings_content():
    return """
# Multi Role Agent

# Persona
This is the first role heading.

Some text.

# Core Identity & Purpose
This is the second role heading, should be ignored.

## Custom Instructions
Instructions here.
"""

@pytest.fixture
def valid_markdown_file(tmp_path, valid_markdown_content):
    agent_dir = tmp_path / "test-agent"
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.write_text(valid_markdown_content, encoding="utf-8")
    return p

@pytest.fixture
def minimal_markdown_file(tmp_path, minimal_markdown_content):
    agent_dir = tmp_path / "minimal-agent"
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.write_text(minimal_markdown_content, encoding="utf-8")
    return p

@pytest.fixture
def missing_role_file(tmp_path, missing_role_markdown_content):
    agent_dir = tmp_path / "missing-role-agent"
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.write_text(missing_role_markdown_content, encoding="utf-8")
    return p

@pytest.fixture
def missing_name_file(tmp_path, missing_name_markdown_content):
    agent_dir = tmp_path / "missing-name-agent"
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.write_text(missing_name_markdown_content, encoding="utf-8")
    return p

@pytest.fixture
def multiple_role_headings_file(tmp_path, multiple_role_headings_content):
    agent_dir = tmp_path / "multi-role-agent"
    agent_dir.mkdir()
    p = agent_dir / "agent.md"
    p.write_text(multiple_role_headings_content, encoding="utf-8")
    return p


# --- Tests for _find_section ---



# --- Tests for parse_markdown ---


# Add a test case where Pydantic validation might fail if needed,
# although the current parser structure makes this less likely if headings are found.
# Example: If roleDefinition was somehow extracted as empty string and was required.