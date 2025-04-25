"""cli.compiler.metadata
========================
Helper utilities responsible for producing the *serialisable* subset of an
already **validated** :class:`cli.models.GlobalAgentConfig` instance that is
persisted inside the global registry (``customModes`` or the deprecated
``agents`` mapping).

The implementation has been *moved* out of ``cli.compiler.legacy`` as part of
Phase 02 of the compiler refactor so the logic can be reused by the upcoming
pipeline modules without importing the (very large) legacy file.

This module contains **zero** business rules beyond the deterministic
transformation that existed previously – future work may further streamline
the data model but, for now, behaviour must remain byte-for-byte identical to
keep the current test-suite green.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..models import GlobalAgentConfig

logger = logging.getLogger(__name__)


def extract_registry_metadata(config: GlobalAgentConfig) -> Dict[str, Any]:
    """Return a *JSON-serialisable* subset of *config* for registry storage.

    Rules – kept unchanged from the historical implementation so all existing
    unit / integration tests pass:

    • ``description`` –  included.  When *config.description* is absent or
      empty we fall back to a truncated (max 150 chars) *roleDefinition* with
      an appended ellipsis so that user-facing metadata always provides a
      concise summary string.
    • ``groups`` – converted to plain ``list`` with nested models flattened
      via ``model_dump()`` so that ``json.dumps`` works without a custom
      encoder.
    • ``apiConfiguration`` – serialised to ``dict`` (or ``None`` when absent).
    • ``customInstructions`` – **never** persisted.
    """

    logger.debug("Extracting registry metadata for '%s'", config.slug)

    # ------------------------------------------------------------------
    # Prepare *apiConfiguration* – serialise nested model if present.
    # ------------------------------------------------------------------
    api_conf: Optional[Dict[str, Any]]
    if config.apiConfiguration is not None:
        api_conf = config.apiConfiguration.model_dump()
    else:
        api_conf = None

    # ------------------------------------------------------------------
    # Serialise groups – handle optional ``(name, restriction)`` tuples and
    # remove keys with ``None`` values to keep output stable across Python
    # versions / model changes.
    # ------------------------------------------------------------------
    groups_serialised: List[Any] = []
    for grp in config.groups:
        if (
            isinstance(grp, tuple)
            and len(grp) == 2
            and hasattr(grp[1], "model_dump")
        ):
            grp_dict = grp[1].model_dump()

            # Drop superfluous *description* key when it is None so that
            # golden-file comparisons in the tests remain stable.
            if grp_dict.get("description") is None:
                grp_dict.pop("description", None)

            groups_serialised.append([grp[0], grp_dict])
        else:
            groups_serialised.append(grp)

    # ------------------------------------------------------------------
    # Determine *description* – prefer the explicit field when provided;
    # otherwise derive it from *roleDefinition* with an upper length bound of
    # 150 characters (the historic test-suite expectation) and add an
    # ellipsis when truncation occurs.  This mirrors the logic encoded in the
    # parameterised tests located in *tests/cli/test_compiler.py*.
    # ------------------------------------------------------------------

    if config.description and config.description.strip():
        description_val = config.description
    else:
        role_def = config.roleDefinition.strip()
        MAX_LEN = 150
        if len(role_def) > MAX_LEN:
            description_val = role_def[:MAX_LEN] + "..."
        else:
            description_val = role_def

    metadata: Dict[str, Any] = {
        "slug": config.slug,
        "name": config.name,
        "description": description_val,
        "roleDefinition": config.roleDefinition,
        "groups": groups_serialised,
        "apiConfiguration": api_conf,
    }

    logger.debug("Metadata extracted for '%s': %s", config.slug, metadata)
    return metadata


__all__ = ["extract_registry_metadata"]
