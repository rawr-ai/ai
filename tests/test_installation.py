import subprocess
import sys
import pytest
import shutil
from pathlib import Path
import os
import venv

# Define the project root relative to this test file
PROJECT_ROOT = Path(__file__).parent.parent

# Define a temporary directory for isolated testing
TEST_ENV_DIR = PROJECT_ROOT / "test_install_env"


@pytest.fixture(scope="module")
def isolated_install_env():
    """
    Pytest fixture to create an isolated environment for installation testing.

    1. Creates a temporary directory.
    2. Copies the project source (excluding the test env itself and potentially large files/dirs).
    3. Creates a virtual environment within the temporary directory.
    4. Installs the package in editable mode (`pip install -e .`) inside the venv.
    5. Yields the path to the temporary directory and the python executable in the venv.
    6. Cleans up the temporary directory after tests are done.
    """
    if TEST_ENV_DIR.exists():
        shutil.rmtree(TEST_ENV_DIR)
    TEST_ENV_DIR.mkdir()

    # Define what to ignore during copy
    ignore_patterns = shutil.ignore_patterns(
        ".git",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "test_install_env", # Ignore the directory we are creating
        ".venv", # Ignore common virtual env names
        "*.egg-info"
    )

    # Copy project source to the isolated directory
    temp_project_path = TEST_ENV_DIR / PROJECT_ROOT.name
    shutil.copytree(PROJECT_ROOT, temp_project_path, ignore=ignore_patterns, dirs_exist_ok=True)

    venv_path = temp_project_path / ".venv_test_install"
    try:
        # Create virtual environment
        print(f"\nCreating virtual environment at: {venv_path}")
        venv.create(venv_path, with_pip=True)

        # Determine python/pip executables based on OS
        if sys.platform == "win32":
            python_executable = venv_path / "Scripts" / "python.exe"
            pip_executable = venv_path / "Scripts" / "pip.exe"
        else:
            python_executable = venv_path / "bin" / "python"
            pip_executable = venv_path / "bin" / "pip"

        # Ensure pip is up-to-date within the venv
        print(f"Upgrading pip in venv: {pip_executable}")
        subprocess.run([str(pip_executable), "install", "--upgrade", "pip"], check=True, capture_output=True, text=True, cwd=temp_project_path)

        # Install the package in editable mode
        print(f"Installing package in editable mode from: {temp_project_path}")
        install_command = [str(pip_executable), "install", "-e", "."]
        result = subprocess.run(install_command, check=True, capture_output=True, text=True, cwd=temp_project_path)
        print("Installation stdout:")
        print(result.stdout)
        print("Installation stderr:")
        print(result.stderr)

        yield temp_project_path, python_executable

    finally:
        # Cleanup
        print(f"\nCleaning up test environment: {TEST_ENV_DIR}")
        if TEST_ENV_DIR.exists():
            shutil.rmtree(TEST_ENV_DIR)


def run_rawr_command(command_args, env_path, python_exec):
    """Helper function to run the rawr command within the isolated venv."""
    # Determine rawr executable path created by setuptools
    venv_path = Path(python_exec).parent.parent # Assumes python_exec is like venv/bin/python
    if sys.platform == "win32":
        rawr_script_path = venv_path / "Scripts" / "rawr.exe"
    else:
        rawr_script_path = venv_path / "bin" / "rawr"

    if not rawr_script_path.exists():
        raise FileNotFoundError(f"rawr script not found at expected location: {rawr_script_path}")

    if not isinstance(command_args, list):
        command_args = [command_args]

    full_command = [str(rawr_script_path)] + command_args
    print(f"\nRunning command: {' '.join(full_command)} in {env_path}")
    result = subprocess.run(full_command, capture_output=True, text=True, cwd=env_path)
    print(f"Command stdout:\n{result.stdout}")
    print(f"Command stderr:\n{result.stderr}")
    return result


def test_package_installation(isolated_install_env):
    """Verify that the package installation itself didn't raise errors (fixture handles this)."""
    env_path, _ = isolated_install_env
    assert env_path.exists(), "Isolated environment directory should exist after setup."
    # The fixture's success implies installation worked. Add more checks if needed,
    # e.g., check for specific files created by installation if applicable.
    print("test_package_installation: Fixture setup completed successfully.")


def test_rawr_entry_point_help(isolated_install_env):
    """Test if the 'rawr --help' command works after installation."""
    env_path, python_exec = isolated_install_env
    result = run_rawr_command("--help", env_path, python_exec)
    assert result.returncode == 0, f"rawr --help exited with code {result.returncode}"
    assert "Usage: rawr [OPTIONS] COMMAND [ARGS]..." in result.stdout, "'Usage:' string not found in rawr --help output."
    assert "CLI tool to manage Agent Configurations from Markdown files." in result.stdout # Check for description
    assert "add" in result.stdout # Check for a command
    print("test_rawr_entry_point_help: Successfully executed rawr --help.")


def test_rawr_add_command_help(isolated_install_env):
    """Test if a subcommand like 'rawr add --help' works."""
    env_path, python_exec = isolated_install_env
    result = run_rawr_command(["add", "--help"], env_path, python_exec)
    assert result.returncode == 0, f"rawr add --help exited with code {result.returncode}"
    assert "Usage: rawr add [OPTIONS]" in result.stdout, "'Usage:' string not found in rawr add --help output."
    # Add more specific checks based on the expected output of 'rawr add --help'
    assert "Adds a new agent configuration from a Markdown file to the JSON store." in result.stdout # Check for description
    print("test_rawr_add_command_help: Successfully executed rawr add --help.")

# Add more tests as needed, e.g., running a basic functional command if one exists
# that doesn't require complex setup within the test environment.