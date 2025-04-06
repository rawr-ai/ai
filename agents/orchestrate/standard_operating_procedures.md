# Standard Operating Procedures

## Git Workflow

All development work (features, fixes, refactoring) MUST be done on a dedicated feature branch created from the `main` branch.

Work MUST be committed incrementally to the feature branch.

Before merging, the work SHOULD be reviewed/verified (details may depend on the task).

Once complete and verified, the feature branch MUST be merged back into the `main` branch.

## Development Logging

Upon successful completion and merging of any significant development task, a development log entry MUST be created.

The process outlined in `agents/orchestrate/playbooks/playbook_development_logging.md` MUST be followed to generate and commit this log entry to the `main` branch.