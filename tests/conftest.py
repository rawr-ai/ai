# tests/conftest.py
import pytest
import yaml
import json
import os
from pathlib import Path

from cli import constants as cli_constants
from . import constants as test_constants
@pytest.fixture
def cli_config_yaml(tmp_path):
    agent_config_file_path = tmp_path / test_constants.TEST_AGENTS_FILENAME # Define path first
    markdown_dir_path = tmp_path / test_constants.TEST_MARKDOWN_DIRNAME # Path object for creation

    config_content = {
        # 'agent_config_file': str(agent_config_file_path), # Removed old key
        cli_constants.MARKDOWN_BASE_DIR: str(markdown_dir_path),
        cli_constants.TARGET_JSON_PATH: str(agent_config_file_path)
    }
    cli_config_path = tmp_path / test_constants.TEST_CONFIG_FILENAME # Renamed file
    with open(cli_config_path, 'w') as f:
        yaml.dump(config_content, f)
    markdown_dir_path.mkdir()

    with open(agent_config_file_path, 'w') as f:
        json.dump({cli_constants.CUSTOM_MODES: []}, f)

    # Set environment variable for settings.py to find this config
    env_var_name = cli_constants.ENV_CONFIG_PATH
    original_env_value = os.environ.get(env_var_name)
    os.environ[env_var_name] = str(cli_config_path)

    yield cli_config_path, agent_config_file_path, markdown_dir_path # Yield for cleanup

    # Cleanup: Unset environment variable
    if original_env_value is None:
        del os.environ[env_var_name]
    else:
        os.environ[env_var_name] = original_env_value

@pytest.fixture
def create_markdown_file_factory():
    def _create(markdown_dir, slug, content=""):
        # Ensure markdown_dir is a Path object if it isn't already
        # Although it should be coming from cli_config_yaml which returns a Path
        markdown_dir_path = Path(markdown_dir)
        agent_dir = markdown_dir_path / slug
        agent_dir.mkdir(parents=True, exist_ok=True) # Ensure parent dirs exist
        md_file = agent_dir / f"{slug}.md"
        with open(md_file, 'w') as f:
            f.write(content)
        return md_file
    return _create