# Rollback Strategy: Global Registry Update (`custom_modes.json`)

**Date:** 2025-04-10
**Version:** 1.1 (Updated)

## 1. Purpose

This document outlines the rollback strategy for the process of updating the global agent mode registry (`custom_modes.json`) using the `cli compile <agent-slug>` command with `config.yaml` files. The primary goal is to ensure the integrity of the `custom_modes.json` file and provide clear steps to revert to a known good state in case of failure during the update process.

This strategy addresses Task 4.1 of the `implementation_plan_scoped.md`.

## 2. Scope & Components Involved

This strategy applies exclusively to failures occurring during the execution of `cli compile <agent-slug>` when its objective is to update the **global** `custom_modes.json` file based on a provided `config.yaml`. It does *not* cover project-level configuration or other CLI commands.

The key components involved in this pathway are:
*   The `cli compile` command itself.
*   `cli/config_loader.py` (loading and validating `config.yaml`).
*   `cli/compiler.py` (extracting metadata).
*   `cli/registry_manager.py` (reading, backing up, writing, restoring `custom_modes.json`).
*   The `config.yaml` file format.
*   The target global `custom_modes.json` file.

## 3. Core Rollback Mechanism: Automatic Backup & Restore

The primary rollback mechanism relies on an automatic backup performed by the `registry_manager.py` component immediately before attempting to write the modified content to the global `custom_modes.json`. This recovery mechanism complements preventative measures like safe/atomic writes (see Section 4).

**Process Flow:**

1.  **Initiation:** User runs `cli compile <agent-slug>` targeting a global mode update.
2.  **Pre-computation:** The CLI loads `config.yaml` (`config_loader.py`), validates it, and extracts the necessary metadata (`compiler.py`).
3.  **Read Existing Registry:** `registry_manager.py` reads the current global `custom_modes.json`.
4.  **Prepare Update:** `registry_manager.py` prepares the new content for `custom_modes.json` based on the extracted metadata.
5.  **BACKUP:** `registry_manager.py` creates a backup copy of the *current* `custom_modes.json` file before attempting any write operation. The backup should ideally be timestamped (e.g., `custom_modes.json.bak.YYYYMMDDHHMMSS`). The exact location and naming convention should be finalized during implementation of `registry_manager.py`.
6.  **Attempt Write:** `registry_manager.py` attempts to write the new, updated content to the original `custom_modes.json` file, ideally using a safe/atomic write pattern (e.g., write to temp file, then rename).
7.  **Success:** If the write is successful, the backup file (from step 5) may be optionally removed or kept for a short retention period (TBD). Clear success message logged/displayed.
8.  **FAILURE:** If the write operation (step 6) fails for any reason (e.g., disk full, permissions error, unexpected interruption, validation error during write):
    *   The `cli compile` command MUST log and report a clear error message indicating the write failure.
    *   The `registry_manager.py` (or the calling `cli` command logic) MUST attempt to automatically restore the original `custom_modes.json` by renaming or copying the backup file (created in step 5) back to `custom_modes.json`.
    *   The error message should also indicate whether the automatic restoration was successful and log the outcome.

## 4. Potential Failure Points & Handling

Failures can occur at various stages. The rollback mechanism primarily addresses failures *during or after* the attempt to write the file. Preventative measures like schema validation (`config_loader`) and safe writes (`registry_manager`) aim to minimize the need for rollback.

*   **Configuration Loading/Validation Failure (`config_loader.py`):**
    *   **Symptom:** Error message during `cli compile` indicating invalid `config.yaml`.
    *   **State:** `custom_modes.json` is untouched. No backup is created.
    *   **Rollback Action:** None required for the registry file itself. User needs to fix `config.yaml`.
*   **Metadata Extraction Failure (`compiler.py`):**
    *   **Symptom:** Error message during `cli compile` indicating issues processing the configuration data.
    *   **State:** `custom_modes.json` is untouched. No backup is created.
    *   **Rollback Action:** None required for the registry file itself. Requires debugging the compiler logic or checking `config.yaml`.
*   **Registry Read Failure (`registry_manager.py`):**
    *   **Symptom:** Error message indicating inability to read `custom_modes.json`.
    *   **State:** `custom_modes.json` is untouched. No backup is created.
    *   **Rollback Action:** None required by this process. Requires investigation of file permissions or existence.
*   **Registry Write Failure / Incorrect Data Written (`registry_manager.py`):**
    *   **Symptom:** Error message indicating failure to write to `custom_modes.json`, or successful write but later discovery of incorrect/corrupt data.
    *   **State:** `custom_modes.json` might be corrupted, empty, partially written, or contain incorrect data. A backup *should* exist from before the failed/incorrect write attempt.
    *   **Rollback Action:**
        *   If failure detected during write: Automatic restore from backup (Section 3, Step 8) should be attempted.
        *   If incorrect data discovered later: Proceed to Manual Rollback (Section 5) using the last known good backup or version control.
        *   If automatic restore fails: Proceed to Manual Rollback (Section 5).
*   **Automatic Restore Failure:**
    *   **Symptom:** Error message indicating write failure *and* failure to restore the backup.
    *   **State:** `custom_modes.json` is likely in a bad state. The backup file should still exist.
    *   **Rollback Action:** Proceed to Manual Rollback (Section 5). Clear logging of this double failure is critical.

## 5. Manual Rollback Procedure

If the automatic restore mechanism fails or incorrect data is discovered post-write, manual intervention is required:

1.  **Identify Backup:** Locate the most recent backup file (e.g., `custom_modes.json.bak.YYYYMMDDHHMMSS`) created by the `registry_manager.py`. The exact location needs to be determined during implementation (e.g., same directory as the original, or a dedicated backup sub-directory like `settings/backups/`).
2.  **Verify Backup:** Briefly inspect the backup file to ensure it appears valid (e.g., check if it's valid JSON, compare size/timestamp to previous versions if known).
3.  **Remove Corrupted File:** Delete or rename the potentially corrupted/incorrect `custom_modes.json` file (e.g., `custom_modes.json.corrupt`).
4.  **Restore from Backup:** Rename or copy the identified backup file back to `custom_modes.json`.
5.  **Verify Permissions:** Ensure the restored `custom_modes.json` has the correct file permissions.

**Alternative (Using Version Control):** If `custom_modes.json` is managed under Git (Note: This is less likely for a global user setting file, but possible):

1.  Navigate to the directory containing `custom_modes.json`.
2.  `git status` to check the state of the file.
3.  `git checkout -- custom_modes.json` to discard local changes and restore the last committed version. *Caution: This discards any other intended changes made since the last commit.*
4.  Alternatively, `git log custom_modes.json` to find the last known good commit hash and `git checkout <commit_hash> -- custom_modes.json`.

## 6. Verification Steps

After any rollback (automatic or manual):

1.  **Check File Existence:** Ensure `custom_modes.json` exists at the expected location (`/Users/mateicanavra/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json`).
2.  **Validate JSON:** Use a JSON validator (e.g., `python -m json.tool <path/to/custom_modes.json>`) to confirm the file is valid JSON.
3.  **Inspect Content:** Briefly review the content to ensure it reflects the expected state before the failed update attempt.
4.  **Test CLI (Read):** Attempt a CLI command that reads the global registry (e.g., `cli list --global` if implemented, or simply re-run `cli compile` on a known-good config) to ensure it can be parsed correctly.

## 7. Future Considerations

*   **Backup Retention:** Define a policy for how long backup files should be kept (e.g., keep last 3 backups, or delete backups older than 7 days). Implement this in `registry_manager.py`.
*   **Backup Location:** Standardize the location for backup files (e.g., a `backups` subdirectory within `settings`). Implement this in `registry_manager.py`.
*   **Monitoring/Alerting:** Consider adding enhanced logging or alerts if rollback events occur frequently, indicating underlying instability.
*   **User Notification:** Ensure error messages clearly guide the user on what happened and if manual steps are needed.