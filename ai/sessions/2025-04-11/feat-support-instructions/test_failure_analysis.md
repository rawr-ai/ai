# Test Failure Analysis: `test_global_agent_config_extraneous_field`

## 1. Problem Description

The test `test_global_agent_config_extraneous_field` located in `tests/unit/test_models.py` failed during the test run after adding the `customInstructions` field to the `GlobalAgentConfig` model. The test expected a `pydantic.ValidationError` but none was raised.

## 2. Root Cause Analysis

- **Model Definition:** The `GlobalAgentConfig` model in `cli/models.py` now includes `customInstructions: Optional[str]` as a valid field. It also specifies `extra = Extra.forbid` in its `Config` class, meaning any fields provided during instantiation that are *not* defined in the model should cause a `ValidationError`.
- **Test Logic:** The failing test (`test_global_agent_config_extraneous_field`) was designed to verify this `Extra.forbid` behavior. It attempted to instantiate `GlobalAgentConfig` with a dictionary containing `"customInstructions": "Do extra things"`.
- **Conflict:** Before the recent change, `customInstructions` *was* an extraneous field, and providing it correctly triggered the `ValidationError` expected by the `pytest.raises(ValidationError)` context manager in the test. However, since `customInstructions` is now a valid (though optional) field, providing it during instantiation is permitted, and no `ValidationError` is raised. This causes the `pytest.raises` check to fail.

## 3. Proposed Solution

The test's intent—to ensure unknown fields are rejected—is still valid and important. The fix involves modifying the test to use a field that is genuinely not part of the `GlobalAgentConfig` model definition.

**Modify `tests/unit/test_models.py`:**

Change line 268 from:
```python
    data = {"slug": "extra-field", "name": "Extra", "roleDefinition": "...", "groups": ["read"], "customInstructions": "Do extra things"}
```
to:
```python
    data = {"slug": "extra-field", "name": "Extra", "roleDefinition": "...", "groups": ["read"], "some_truly_unknown_field": "value"}
```

This change replaces the now-valid `customInstructions` field with `some_truly_unknown_field`, which is not defined in `GlobalAgentConfig`. This will correctly trigger the `ValidationError` due to `Extra.forbid`, allowing the `pytest.raises` assertion to pass and verifying the intended model behavior.