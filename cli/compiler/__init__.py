"""Temporary façade to keep public API stable during the incremental refactor
of the compiler module.

All functionality is re-exported from *cli.compiler.legacy* so that external
call-sites (and our existing test-suite) continue to work without change.
Once the refactor is complete these re-exports will be replaced by the new
modular implementation.
"""

from importlib import import_module as _imp

# Import the legacy implementation only once; this guarantees that every
# re-exported attribute refers to the exact same object that downstream code
# would have received before the refactor started.
_legacy = _imp("cli.compiler.legacy")

# ---------------------------------------------------------------------------
# Public helpers re-exported for backwards compatibility
# ---------------------------------------------------------------------------
compile_agents = _legacy.compile_agents  # type: ignore[attr-defined]
extract_registry_metadata = _legacy.extract_registry_metadata  # type: ignore[attr-defined]
_compile_specific_agent = _legacy._compile_specific_agent  # type: ignore[attr-defined]
# Modules referenced directly by the test-suite for monkey-patching.
_compile_all_agents = _legacy._compile_all_agents  # type: ignore[attr-defined]
registry_manager = _legacy.registry_manager  # type: ignore[attr-defined]
config_loader = _legacy.config_loader  # type: ignore[attr-defined]

# Baseline list of public names – this *must* be defined before we attempt to
# extend it below.
__all__: list[str] = [
    "compile_agents",
    "extract_registry_metadata",
    "_compile_specific_agent",
    "_compile_all_agents",
    "registry_manager",
    "config_loader",
]

# Expose every public attribute from the legacy module so existing import
# patterns used by the test-suite (e.g. `patch('cli.compiler.Path')`) keep
# working unchanged.  This is a temporary measure until the refactor replaces
# those usages with more focused imports.

for _name, _value in _legacy.__dict__.items():
    if _name.startswith("__"):
        continue
    if _name in globals():
        # We've already set an explicit alias for this symbol above.
        continue
    globals()[_name] = _value
    __all__.append(_name)
