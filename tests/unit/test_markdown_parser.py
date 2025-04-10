import pytest
from pathlib import Path
from cli.agent_config.markdown_utils import ( # Updated path
    parse_markdown,
    _find_section,
    ROLE_DEFINITION_HEADINGS,
    CUSTOM_INSTRUCTIONS_HEADINGS,
)
from cli.agent_config.models import AgentConfig # Updated path

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

def test_find_section_basic():
    content = "# Title\nText\n## Section 1\nContent 1\n## Section 2\nContent 2"
    result = _find_section(content, ["## Section 1"])
    assert result is not None
    section, start, end = result
    assert section == "## Section 1\nContent 1"
    assert start == content.find("## Section 1")
    assert end == content.find("## Section 2")

def test_find_section_multiple_options():
    content = "# Title\nText\n### Section B\nContent B\n## Section A\nContent A"
    result = _find_section(content, ["## Section A", "### Section B"])
    assert result is not None
    section, _, _ = result
    assert section == "### Section B\nContent B" # Finds the first occurrence

def test_find_section_stops_at_lower_level():
    content = "## Section 1\nContent 1\n# Main Title\nMore text"
    result = _find_section(content, ["## Section 1"])
    assert result is not None
    section, _, end = result
    assert section == "## Section 1\nContent 1"
    assert end == content.find("# Main Title")

def test_find_section_stops_at_eof():
    content = "# Title\n## Section 1\nContent 1"
    result = _find_section(content, ["## Section 1"])
    assert result is not None
    section, _, end = result
    assert section == "## Section 1\nContent 1"
    assert end == len(content)

def test_find_section_not_found():
    content = "# Title\n## Section 2\nContent 2"
    result = _find_section(content, ["## Section 1"])
    assert result is None

def test_find_section_with_offset():
    content = "## Section 1\nContent 1\n## Section 1\nContent 2"
    offset = content.find("Content 1")
    result = _find_section(content, ["## Section 1"], start_offset=offset)
    assert result is not None
    section, start, _ = result
    assert section == "## Section 1\nContent 2"
    assert start == content.rfind("## Section 1")


# --- Tests for parse_markdown ---

def test_parse_markdown_success(valid_markdown_file):
    """Test parsing a valid markdown file with all sections."""
    config = parse_markdown(valid_markdown_file)
    assert isinstance(config, AgentConfig)
    assert config.slug == "test-agent"
    assert config.name == "Test Agent Name"
    assert config.roleDefinition.startswith("# Core Identity & Purpose")
    assert "This is the role definition." in config.roleDefinition
    assert config.customInstructions is not None
    assert config.customInstructions.startswith("## Custom Instructions")
    assert "Instruction section 1." in config.customInstructions
    assert "Instruction section 2." in config.customInstructions
    # Ensure the intermediate H2 was not included
    assert "## Another Heading (H2)" not in config.roleDefinition
    assert "## Another Heading (H2)" not in config.customInstructions
    # Ensure content from second custom instructions section (excluding heading) is present
    assert "Final instructions." in config.customInstructions
    assert "### Sub Heading (H3)" not in config.customInstructions
    assert "## Standard Operating Procedure (SOP) / Workflow" not in config.customInstructions.splitlines()[2:] # Check heading isn't repeated


def test_parse_markdown_minimal(minimal_markdown_file):
    """Test parsing a markdown file with only required sections."""
    config = parse_markdown(minimal_markdown_file)
    assert isinstance(config, AgentConfig)
    assert config.slug == "minimal-agent"
    assert config.name == "Minimal Agent"
    assert config.roleDefinition == "# Role\nThe minimal role definition."
    assert config.customInstructions is None

def test_parse_markdown_multiple_role_headings(multiple_role_headings_file):
    """Test that the first matching role heading is used."""
    config = parse_markdown(multiple_role_headings_file)
    assert config.slug == "multi-role-agent"
    assert config.name == "Multi Role Agent"
    assert config.roleDefinition.startswith("# Persona")
    assert "This is the first role heading." in config.roleDefinition
    assert "# Core Identity & Purpose" not in config.roleDefinition # Ensure second wasn't used

def test_parse_markdown_file_not_found(tmp_path):
    """Test parsing when the markdown file does not exist."""
    non_existent_path = tmp_path / "non-existent-agent" / "agent.md"
    with pytest.raises(FileNotFoundError):
        parse_markdown(non_existent_path)

def test_parse_markdown_missing_name(missing_name_file):
    """Test parsing when the H1 'name' heading is missing."""
    with pytest.raises(ValueError, match="Could not find H1 heading for 'name'"):
        parse_markdown(missing_name_file)

def test_parse_markdown_missing_role(missing_role_file):
    """Test parsing when no role definition heading is found."""
    expected_headings = ', '.join(ROLE_DEFINITION_HEADINGS)
    with pytest.raises(ValueError, match=f"Could not find any role definition heading"):
        parse_markdown(missing_role_file)

# Add a test case where Pydantic validation might fail if needed,
# although the current parser structure makes this less likely if headings are found.
# Example: If roleDefinition was somehow extracted as empty string and was required.