"""Light-weight smoke tests for the rawr CLI.

This module purposefully contains only a *very* small set of assertions that
run quickly. The goal is to ensure that the command-line entry-point can be
imported and that the global ``--help`` flag works. More granular tests will be
re-added once the CLI stabilises.
"""

from typer.testing import CliRunner

# Typer application object exported by cli.main
from cli.main import app  # noqa: WPS433 – runtime import required for test


runner = CliRunner()


def test_help_flag_exits_successfully() -> None:
    """`rawr --help` should exit with status 0 and print a usage banner."""

    result = runner.invoke(app, ["--help"], catch_exceptions=False)

    assert result.exit_code == 0, result.stdout
    # Typer always prints a "Usage:" line. Checking for it confirms that
    # basic CLI parsing worked.
    assert "Usage:" in result.stdout
