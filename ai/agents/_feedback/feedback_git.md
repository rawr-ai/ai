# MUST:

### Check Git Status Before Running
*   Check the current branch; verify it is the one specified in the task. Raise flag if anything is off.
*   Check if there are any uncommitted changes in the repository.
*   If there are uncommitted changes, ask the user if they should be committed.
*   If the user is on a branch other than the one specified in the task, ask if they should switch to the correct branch or abort the task or continue on the current branch.

# SHOULD:

### Push New Branch to Remote
*   Push the new branch to the remote repository if one is created AND if best practice indicates it should be committed for the nature of the task.
*   If the task is a meta task, or pushing is not best practice, don't push the branch.


