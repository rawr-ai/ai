"""DEPRECATED – shim preserved for backwards compatibility.

Importing from this module is discouraged; use `cli.compiler` (the package)
for forward-compatible imports.
"""
import warnings
import logging

from cli.compiler.legacy import compile_agents  # noqa: F401 – re-export

warnings.warn(
    "`cli.compiler.py` is deprecated; please import `cli.compiler` instead.",
    DeprecationWarning,
    stacklevel=2,
)

logging.getLogger(__name__).warning(
    "cli/compiler.py is deprecated; use cli.compiler.* instead."
)

__all__ = ["compile_agents"]
