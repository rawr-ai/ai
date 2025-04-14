import pytest
import json
from pathlib import Path
from cli.models import GlobalAgentConfig, ApiConfig, GroupRestriction
from cli.compiler import extract_registry_metadata

# Test Case ID: TC_EXTRACT_001 - Happy Path - Full Data Input
def test_extract_full_data():
    """Verify correct metadata extraction with all fields populated."""
    input_config = GlobalAgentConfig(
        slug="test-agent",
        name="Test Agent",
        roleDefinition="This is a test role.",
        groups=["groupA", ("groupB", GroupRestriction(fileRegex=".*\\.py", description="Python files"))],
        apiConfiguration=ApiConfig(model="gpt-4", url="http://example.com/api", params={"temp": 0.5})
    )
    asset_path = Path(__file__).parent.parent / 'assets' / 'unit' / 'test_compiler' / 'expected_output_full.json'
    with open(asset_path, 'r') as f:
        expected_output = json.load(f)
    actual_output = extract_registry_metadata(input_config)
    # Convert HttpUrl to string for comparison if present
    if actual_output.get("apiConfiguration") and isinstance(actual_output["apiConfiguration"].get("url"), object):
         actual_output["apiConfiguration"]["url"] = str(actual_output["apiConfiguration"]["url"])
    # Compare field by field for complex structures like groups
    assert actual_output['slug'] == expected_output['slug']
    assert actual_output['name'] == expected_output['name']
    assert actual_output['roleDefinition'] == expected_output['roleDefinition']
    assert actual_output['apiConfiguration'] == expected_output['apiConfiguration']
    assert actual_output['version'] == expected_output['version']
    # Special handling for groups: compare lengths and individual elements carefully
    assert len(actual_output['groups']) == len(expected_output['groups'])
    assert actual_output['groups'][0] == expected_output['groups'][0] # Simple string comparison
    # Compare the tuple part: check group name and GroupRestriction fields
    assert isinstance(actual_output['groups'][1], tuple)
    assert actual_output['groups'][1][0] == expected_output['groups'][1][0] # Compare group name 'groupB'
    assert isinstance(actual_output['groups'][1][1], GroupRestriction)
    assert actual_output['groups'][1][1].fileRegex == expected_output['groups'][1][1]['fileRegex']
    assert actual_output['groups'][1][1].description == expected_output['groups'][1][1]['description']

    assert set(actual_output.keys()) == set(expected_output.keys()) # Explicit key check (should pass now with version added to JSON)

# Test Case ID: TC_EXTRACT_002 - Happy Path - Minimal Data Input
def test_extract_minimal_data():
    """Verify correct metadata extraction with only required fields and None for optional."""
    input_config = GlobalAgentConfig(
        slug="minimal-agent",
        name="Minimal Agent",
        roleDefinition="Minimal role.",
        groups=["core"],
        apiConfiguration=None
    )
    asset_path = Path(__file__).parent.parent / 'assets' / 'unit' / 'test_compiler' / 'expected_output_minimal.json'
    with open(asset_path, 'r') as f:
        expected_output = json.load(f)
    actual_output = extract_registry_metadata(input_config)

    # Check if apiConfiguration is None or absent, depending on implementation choice
    if "apiConfiguration" in actual_output:
         assert actual_output["apiConfiguration"] is None
         assert actual_output == expected_output # Check full dict if key is present
    else:
        # If key is absent, remove it from expected for comparison
        del expected_output["apiConfiguration"]
        assert actual_output == expected_output # This should pass now that version is in the JSON

    # Update the expected keys set to include 'version'
    assert set(actual_output.keys()) <= {'slug', 'name', 'roleDefinition', 'groups', 'apiConfiguration', 'version'}


# Test Case ID: TC_EXTRACT_003 - Groups Variation - Simple String List
def test_extract_groups_simple_list():
    """Verify correct extraction when groups is a simple list of strings."""
    input_config = GlobalAgentConfig(
        slug="simple-groups",
        name="Simple Groups Agent",
        roleDefinition="Role def.",
        groups=["groupX", "groupY"],
        apiConfiguration=None
    )
    expected_groups = ["groupX", "groupY"]
    actual_output = extract_registry_metadata(input_config)
    assert "groups" in actual_output
    assert actual_output["groups"] == expected_groups

# Test Case ID: TC_EXTRACT_004 - Groups Variation - Mixed String and Tuple List
def test_extract_groups_mixed_list():
    """Verify correct extraction when groups is a mixed list of strings and tuples."""
    input_config = GlobalAgentConfig(
        slug="mixed-groups",
        name="Mixed Groups Agent",
        roleDefinition="Role def.",
        groups=["groupA", ("groupB", GroupRestriction(fileRegex=".*\\.md"))], # No description provided
        apiConfiguration=None
    )
    # Expecting description to default to None in the GroupRestriction model if not provided
    # Expecting the tuple structure to be preserved in the output dict
    # Define expected structure using the actual GroupRestriction object
    expected_groups = ["groupA", ("groupB", GroupRestriction(fileRegex=".*\\.md", description=None))]
    actual_output = extract_registry_metadata(input_config)
    assert "groups" in actual_output
    # Compare directly with the expected structure containing the object
    assert actual_output["groups"] == expected_groups

# Test Case ID: TC_EXTRACT_005 - Groups Variation - Empty List
def test_extract_groups_empty_list():
    """Verify correct extraction when groups list is empty."""
    input_config = GlobalAgentConfig(
        slug="empty-groups",
        name="Empty Groups Agent",
        roleDefinition="Role def.",
        groups=[],
        apiConfiguration=None
    )
    expected_groups = []
    actual_output = extract_registry_metadata(input_config)
    assert "groups" in actual_output
    assert actual_output["groups"] == expected_groups

# Test Case ID: TC_EXTRACT_006 - Field Exclusion Verification
def test_extract_field_exclusion():
    """Explicitly verify that only required/optional registry fields are included."""
    input_config = GlobalAgentConfig(
        slug="test-agent-exclusion",
        name="Test Agent Exclusion",
        roleDefinition="This is a test role for exclusion.",
        groups=["groupA"],
        apiConfiguration=ApiConfig(model="gpt-3.5", url="http://test.com") # Minimal ApiConfig
        # No customInstructions field exists on GlobalAgentConfig, so exclusion is implicit
    )
    # Add 'version' to the expected keys
    expected_keys = {'slug', 'name', 'roleDefinition', 'groups', 'apiConfiguration', 'version'}
    actual_output = extract_registry_metadata(input_config)
    assert set(actual_output.keys()) == expected_keys