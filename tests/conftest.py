# tests/conftest.py
import pytest
import yaml
import json # <-- Add import
from pathlib import Path

@pytest.fixture
def cli_config_yaml(tmp_path):
    agent_config_file_path = tmp_path / 'agent_configs.json' # Define path first
    markdown_dir_path = tmp_path / 'markdown_files' # Path object for creation

    config_content = {
        'agent_config_file': str(agent_config_file_path),
        'markdown_base_dir': str(markdown_dir_path),
        'target_json_path': str(agent_config_file_path) # Use the path object
    }
    cli_config_path = tmp_path / 'cli_config.yaml'
    with open(cli_config_path, 'w') as f:
        yaml.dump(config_content, f)
    markdown_dir_path.mkdir() # Explicitly create the base markdown directory

    # Create an empty agent_configs.json file by default
    with open(agent_config_file_path, 'w') as f:
        json.dump({'customModes': []}, f) # Create with empty list

    return cli_config_path, agent_config_file_path, markdown_dir_path # Return the Path objects

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