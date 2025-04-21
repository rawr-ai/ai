# Step 6 – Re‑build `cli.py` (Typer Interface)

**Objective:** Move all command‑line interaction into `cli/compiler/cli.py`
where it consumes `AgentCompiler` results to reproduce existing UX.

---

## Actions

1. **Create file** `cli/compiler/cli.py`

```python
import typer, logging
from pathlib import Path

from .core import AgentCompiler

app = typer.Typer(help="Compile agent configuration(s) into the global registry")

_log = logging.getLogger(__name__)


@app.command()
def agents(slug: str | None = typer.Argument(None, help="Optional agent slug")):
    """Compile a single agent or all agents when *slug* is omitted."""

    compiler = AgentCompiler()

    if slug:
        result = compiler.compile_agent(_slug_to_path(slug))
        _echo_result(result)
    else:
        results = compiler.compile_all(_default_agent_base())
        for r in results:
            _echo_result(r)


# … plus helper functions mirroring current messaging style …
```

2. **Update `cli/compiler/__init__.py`**

Expose both the Typer app and the backwards‑compat function:

```python
from .cli import app as ty_compile
from .core import AgentCompiler


def compile_agents(slug: str | None = None):
    compiler = AgentCompiler()
    if slug is None:
        compiler.compile_all(_default_agent_base())
    else:
        compiler.compile_agent(_slug_to_path(slug))
```

3. **Integration test** (`tests/cli/test_new_cli.py`)

Leverage `typer.testing.CliRunner` to invoke the new command, assert exit code
and output strings.

---

## Deliverables

* `cli/compiler/cli.py` Typer application.
* Updated `__init__.py` façade.
* Integration test.

---

## Risks & Mitigations

* **Risk:** Output text deviates causing snapshot tests to fail.  
  **Mitigation:** Copy original strings verbatim where feasible.

* **Risk:** Duplicate CLI entry points.  
  **Mitigation:** Mark old Typer command as deprecated; log warning.
