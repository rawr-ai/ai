# Recursive Config Loading – Implementation Plan (v1)

_Last updated: 2025‑04‑17_

This plan refines the earlier “next‑steps” list with (a) granular tasks, (b) an **Effort**/ **Complexity** estimate suitable for AI agents, and (c) a recommended **Owner** drawn from the current agent roster (see `custom_modes_starter.json`).

Effort scale (approx. wall‑clock minutes for an AI agent under Codex CLI):

| Code  | Meaning          |
|-------|------------------|
| XS    | < 10 min         |
| S     | 10 – 30 min      |
| M     | 30 – 60 min      |
| L     | 60 – 120 min     |
| XL    | 120 + min        |

Complexity is qualitative: **Low**, **Med**, **High**.

---

## 1 – Data‑model & schema reconciliation

| # | Task | Effort | Complexity | Owner (Agent slug) |
|---|------|--------|------------|--------------------|
| 1.1 | Add optional `description` field to `GlobalAgentConfig` model. | S | Low | **implement** |
| 1.2 | Update `extract_registry_metadata()` to fallback to `roleDefinition` when `description` absent (truncate). | S | Low | **refactor** |
| 1.3 | Regenerate pydantic model docs (if any) & quick unit test. | XS | Low | **test** |

## 2 – Filesystem discovery refactor

| # | Task | Effort | Complexity | Owner |
|---|------|--------|------------|-------|
| 2.1 | Implement `discover_config_files(base_dir)` returning all `config.yaml`. | M | Med | **implement** |
| 2.2 | Remove filename‑based slug derivation; use `agent_config.slug` after validation. | S | Med | **refactor** |
| 2.3 | Adjust single‑agent path resolution (`<slug>/config.yaml`, fallback `<slug>.yaml`). | S | Med | **implement** |

## 3 – Compiler pipeline rewrite

| # | Task | Effort | Complexity | Owner |
|---|------|--------|------------|-------|
| 3.1 | Replace manual `rglob` logic with new discovery helper in `_compile_all_agents`. | S | Low | **refactor** |
| 3.2 | After each validation, call `registry_manager.update_global_registry`. Remove `final_registry_data['agents']` hack. | S | Med | **implement** |
| 3.3 | Review/clean exit‑code logic & messaging. | S | Low | **analyze** (followed by **implement**) |

## 4 – Registry manager polish

| # | Task | Effort | Complexity | Owner |
| 4.1 | Ensure duplicate slug replacement logic efficient. | XS | Low | **refactor** |
| 4.2 | Unit test `update_global_registry` for add & update flows. | XS | Low | **test** |

## 5 – Test suite work

| # | Task | Effort | Complexity | Owner |
| 5.1 | Rename duplicate file `tests/unit/test_compiler.py` to `test_compiler_unit.py`. | XS | Low | **implement** |
| 5.2 | Add unit tests for discovery helper & slug extraction. | M | Med | **test** |
| 5.3 | Add integration tests: (a) compile‑all with 3 mocked agents, (b) compile single. | L | Med | **test** |

## 6 – CI & tooling

| # | Task | Effort | Complexity | Owner |
| 6.1 | Add pipeline step `rm -rf .rawr_registry && rawr compile` and assert non‑zero agents. | XS | Low | **git** / **implement** |
| 6.2 | Run `pytest` after compile to ensure green. | XS | Low | **git** |

## 7 – Documentation

| # | Task | Effort | Complexity | Owner |
| 7.1 | Update `cli/docs/config_loading.md` – canonical file layout. | S | Low | **document** |
| 7.2 | Update `cli/docs/cli_invocation.md` – single vs all compile behaviour. | XS | Low | **document** |

## 8 – YAML migration script (optional but unblocks missing descriptions)

| # | Task | Effort | Complexity | Owner |
| 8.1 | Script to insert placeholder `description` when absent in `ai/agents/**/config.yaml`. | S | Med | **implement** |
| 8.2 | Run script & commit updated YAMLs via **git** agent. | XS | Low | **git** |

---

### Acceptance checklist

* `rawr compile` with an empty `.rawr_registry/` exits 0 and registry contains ≥ 1 agent.
* `rawr compile <slug>` works for any existing slug.
* `pytest -q` passes; integration tests cover new paths.
* Documentation pages updated.

---

## Agent participation matrix

| Agent | Primary responsibilities in this sprint |
|-------|------------------------------------------|
| **analyze** | Deep code inspection, confirm design choices, spot edge cases.
| **implement** | Make code edits, add helper functions, adjust CLI logic.
| **refactor** | Re‑structure existing functions for clarity, small behavioural changes.
| **test** | Create/adjust unit & integration tests.
| **document** | Update Markdown docs.
| **git** | Stage / commit / push changes & PR creation once human review complete.
| **review** | Optional final code review before merging.

> Note: Roles like `orchestrator` or `command` are not required for this focused sprint; the scope is small and linear.

---

### Estimated total effort

Summing approximate minutes: **≈ 360–420 min** of agent active time (i.e., about a single focused coding session for an AI pair or two short iterations including test writing and docs).

_End of plan._
