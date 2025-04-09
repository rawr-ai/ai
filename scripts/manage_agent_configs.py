#!/usr/bin/env python3
import sys
import os

# Ensure the script's directory (or the project root) is in the Python path
# This allows importing the 'agent_config_manager' package.
# Adjust if your execution context differs.
script_dir = os.path.dirname(os.path.abspath(__file__))
# If scripts/ is directly under the project root added to PYTHONPATH, this might work:
# from agent_config_manager.cli import main
# If running directly from the project root (e.g., python scripts/manage_agent_configs.py),
# Python might find the package automatically.
# A more robust way might be to add the parent directory (project root) to sys.path
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Now try importing from the package relative to the project root
    from scripts.agent_config_manager.cli import main
except ImportError as e:
    print(f"Error importing agent_config_manager.cli: {e}", file=sys.stderr)
    print(f"Current sys.path: {sys.path}", file=sys.stderr)
    print("Ensure the project root directory is in your PYTHONPATH or accessible.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()