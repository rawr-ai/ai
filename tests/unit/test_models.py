import pytest
from pydantic import ValidationError
from scripts.agent_config_manager.models import AgentConfig

def test_agent_config_minimal_instantiation():
    """Test basic instantiation with required fields."""
    config = AgentConfig(
        slug="test-agent",
        name="Test Agent",
        roleDefinition="This is a test role."
    )
    assert config.slug == "test-agent"
    assert config.name == "Test Agent"
    assert config.roleDefinition == "This is a test role."
    assert config.customInstructions is None
    assert config.groups == ["read"] # Check default value

def test_agent_config_full_instantiation():
    """Test instantiation with all fields."""
    config = AgentConfig(
        slug="full-agent",
        name="Full Agent",
        roleDefinition="A complete role definition.",
        customInstructions="Some custom instructions.",
        groups=["read", "write"]
    )
    assert config.slug == "full-agent"
    assert config.name == "Full Agent"
    assert config.roleDefinition == "A complete role definition."
    assert config.customInstructions == "Some custom instructions."
    assert config.groups == ["read", "write"]

def test_agent_config_missing_required_field():
    """Test validation error when a required field is missing."""
    with pytest.raises(ValidationError) as excinfo:
        AgentConfig(slug="missing-name", roleDefinition="Role without name")
    assert "'name' field required" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        AgentConfig(slug="missing-role", name="Agent without role")
    # Pydantic uses the alias in the error message if defined
    assert "'roleDefinition' field required" in str(excinfo.value)

def test_agent_config_instantiation_with_alias():
    """Test instantiation using the alias 'roleDefinition'."""
    config = AgentConfig(
        slug="alias-test",
        name="Alias Test Agent",
        roleDefinition="Role defined using alias." # Using the alias directly
    )
    assert config.roleDefinition == "Role defined using alias."

def test_agent_config_instantiation_with_field_name():
    """Test instantiation using the field name 'roleDefinition' (due to Config)."""
    # This works because allow_population_by_field_name = True in the model's Config
    config = AgentConfig(
        slug="field-name-test",
        name="Field Name Test Agent",
        roleDefinition="Role defined using field name."
    )
    assert config.roleDefinition == "Role defined using field name."