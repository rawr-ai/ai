# Implementation Plan: WunderGraph Operation - integrations/linear/updateProject

## 1. Objective

Create a new WunderGraph mutation operation, `integrations/linear/updateProject`, allowing users to update specific fields of an existing Linear project. This operation will follow the established pattern of a TypeScript wrapper (`.ts`) calling an internal GraphQL mutation (`.graphql`).

## 2. Assumptions

*   The implementation will closely mirror the structure, logic, and conventions used in the existing `integrations/linear/createProject` operation, particularly regarding team/status resolution, priority mapping, date formatting, and Zod schema definitions.
*   The Linear API endpoint for updating projects accepts optional fields, allowing partial updates without affecting unspecified fields.
*   Necessary utility functions (e.g., for resolving team/status IDs, mapping priorities) from `createProject.ts` or a shared location are available and can be reused.
*   The required Linear API token/authentication is correctly configured in the WunderGraph environment.

## 3. Implementation Steps

### Step 3.1: Create Internal GraphQL Mutation

**File:** `.wundergraph/operations/integrations/linear/internal/updateProject.graphql`

**Action:** Define the GraphQL mutation to interact with the underlying Linear API (via WunderGraph's datasource).

**Content Structure:**

```graphql
# .wundergraph/operations/integrations/linear/internal/updateProject.graphql
mutation InternalUpdateLinearProject(
    $projectId: String! # Mandatory project ID
    $name: String # Optional new name
    $description: String # Optional new description
    $teamIds: [String!] # Optional list of team IDs
    $statusId: String # Optional new status ID
    $priority: Int # Optional new priority (numeric)
    $targetDate: TimelessDate # Optional new target date (formatted)
    # Add any other optional fields supported by the underlying Linear API update mutation
) {
    # Replace 'linear_updateProject' with the actual WunderGraph datasource mutation field
    # Ensure the 'input' structure matches what the Linear API expects for updates
    linear_updateProject(
        id: $projectId
        input: {
            # Conditionally include fields based on provided variables in the TS wrapper
            # The TS wrapper will ensure only non-null values are passed here.
            name: $name
            description: $description
            teamIds: $teamIds
            stateId: $statusId # Assuming Linear uses 'stateId' for status
            priority: $priority
            targetDate: $targetDate
            # Add other fields as needed
        }
    ) {
        # Mirror the return fields from createProject.graphql for consistency
        success
        project {
            id
            name
            description
            url
            state {
                id
                name
                type
            }
            priority
            priorityLabel
            createdAt
            updatedAt
            targetDate
            teams {
                nodes {
                    id
                    name
                }
            }
            # Include any other relevant fields returned by the Linear API
        }
    }
}

# Define the TimelessDate scalar if not already globally defined
scalar TimelessDate
```

**Key Considerations:**

*   The exact field names within the `input` object (`stateId`, `targetDate`, etc.) must match the Linear API's expectations for the project update mutation.
*   The return fields should match `createProject.graphql` to provide a consistent response structure.

### Step 3.2: Create TypeScript Wrapper Operation

**File:** `.wundergraph/operations/integrations/linear/updateProject.ts`

**Action:** Define the public-facing TypeScript operation, including input validation, logic for resolving/mapping inputs, calling the internal GraphQL mutation, and defining the response structure.

**Content Structure:**

```typescript
// .wundergraph/operations/integrations/linear/updateProject.ts
import { createOperation, z } from '../../../../generated/wundergraph.factory';
// Import enums, utility functions (resolveTeamIds, resolveStatusId, mapPriority, formatDate)
// potentially from createProject.ts or a shared utils file.
import {
    LinearProjectPriority,
    LinearProjectStatus,
    // ... other necessary imports
} from './createProject'; // Adjust path if utils are shared

export default createOperation.mutation({
    // Define Input Schema using Zod
    inputSchema: z.object({
        projectId: z.string().min(1, 'Project ID is required.'),
        name: z.string().optional(),
        description: z.string().optional(),
        teamIdentifiers: z.array(z.string()).optional().describe('List of team names or IDs'),
        statusName: z.nativeEnum(LinearProjectStatus).optional(),
        priority: z.nativeEnum(LinearProjectPriority).optional(),
        targetDate: z.string().datetime().optional().describe('Target date in ISO 8601 format'),
        // Add other optional fields corresponding to the .graphql mutation
    }),

    // Define Response Schema using Zod (mirroring createProject response)
    responseSchema: z.object({
        success: z.boolean(),
        project: z
            .object({
                id: z.string(),
                name: z.string(),
                description: z.string().nullable(),
                url: z.string(),
                state: z.object({
                    id: z.string(),
                    name: z.string(),
                    type: z.string(),
                }),
                priority: z.number(),
                priorityLabel: z.string(),
                createdAt: z.string().datetime(),
                updatedAt: z.string().datetime(),
                targetDate: z.string().nullable(), // Adjust type based on Linear API response
                teams: z.object({
                    nodes: z.array(
                        z.object({
                            id: z.string(),
                            name: z.string(),
                        })
                    ),
                }),
                // Add other fields matching the .graphql return structure
            })
            .nullable(), // Project might be null if update fails but success is handled differently
    }),

    // Define the handler function
    handler: async ({ input, operations, log, user }) => {
        log.info(`Attempting to update Linear project: ${input.projectId}`);

        let teamIds: string[] | undefined = undefined;
        let statusId: string | undefined = undefined;

        // 1. Conditional Fetching & Resolution (only if relevant inputs provided)
        if (input.teamIdentifiers || input.statusName) {
            // Reuse or adapt logic from createProject to fetch all teams/statuses
            // This might involve calling another internal operation like 'linear/teamsAndStatuses'
            const teamsAndStatuses = await operations.query({
                operationName: 'integrations/linear/internal/teamsAndStatuses', // Example name
            });
            // Handle potential errors fetching teams/statuses

            if (input.teamIdentifiers) {
                // Reuse or adapt resolveTeamIds function
                teamIds = await resolveTeamIds(input.teamIdentifiers, teamsAndStatuses.data?.teams?.nodes, log);
                if (!teamIds) {
                    // Handle error: Could not resolve team identifiers
                    throw new Error('Failed to resolve one or more team identifiers.');
                }
            }

            if (input.statusName) {
                // Reuse or adapt resolveStatusId function
                statusId = await resolveStatusId(input.statusName, teamsAndStatuses.data?.projectUpdateStates?.nodes, log); // Adjust path based on actual query
                 if (!statusId) {
                    // Handle error: Could not resolve status name
                    throw new Error(`Failed to resolve status name: ${input.statusName}`);
                }
            }
        }

        // 2. Conditional Mapping/Formatting
        const priorityNumber = input.priority ? mapPriority(input.priority) : undefined;
        const formattedTargetDate = input.targetDate ? formatDate(input.targetDate) : undefined; // Ensure format matches Linear API expectation (e.g., 'YYYY-MM-DD')

        // 3. Construct Payload for Internal Mutation (Include ONLY provided fields)
        const updatePayload = {
            projectId: input.projectId,
            ...(input.name !== undefined && { name: input.name }),
            ...(input.description !== undefined && { description: input.description }),
            ...(teamIds !== undefined && { teamIds: teamIds }),
            ...(statusId !== undefined && { statusId: statusId }),
            ...(priorityNumber !== undefined && { priority: priorityNumber }),
            ...(formattedTargetDate !== undefined && { targetDate: formattedTargetDate }),
            // Add other optional fields similarly
        };

        log.debug('Calling internal updateProject mutation with payload:', updatePayload);

        // 4. Call Internal GraphQL Mutation
        const result = await operations.mutate({
            operationName: 'integrations/linear/internal/updateProject',
            input: updatePayload,
        });

        // 5. Error Handling & Response
        if (!result.data?.linear_updateProject?.success || result.errors) {
            log.error('Failed to update Linear project:', result.errors || 'API reported failure');
            // Consider throwing a more specific error or returning a structured error response
             throw new Error(`Failed to update project ${input.projectId}. Errors: ${JSON.stringify(result.errors)}`);
        }

        log.info(`Successfully updated Linear project: ${input.projectId}`);
        return {
            success: result.data.linear_updateProject.success,
            project: result.data.linear_updateProject.project,
        };
    },
});

// Helper function placeholders (to be imported or defined)
// async function resolveTeamIds(identifiers: string[], teams: any[], log: any): Promise<string[] | undefined> { /* ... */ }
// async function resolveStatusId(statusName: string, statuses: any[], log: any): Promise<string | undefined> { /* ... */ }
// function mapPriority(priority: LinearProjectPriority): number { /* ... */ }
// function formatDate(dateString: string): string { /* ... */ } // Ensure correct format for Linear API
```

**Key Considerations:**

*   Ensure all imported enums and utility functions (`resolveTeamIds`, `resolveStatusId`, `mapPriority`, `formatDate`) are correctly referenced and function as expected for updates.
*   The logic for fetching teams/statuses should be efficient, potentially reusing a dedicated internal operation if available.
*   The construction of `updatePayload` is critical: only fields explicitly provided in the `input` should be included to avoid unintentionally clearing existing values in Linear. The spread syntax `...(condition && { key: value })` achieves this.
*   Robust error handling is needed for failed resolutions (teams, status) and failed API calls.
*   The `responseSchema` should accurately reflect the fields returned by the `.graphql` mutation.

## 4. Acceptance Criteria (for Implementation)

*   The `.graphql` file is created at the specified path with the correct mutation definition, variables, and return fields.
*   The `.ts` file is created at the specified path with correct Zod schemas (`inputSchema`, `responseSchema`) and handler logic.
*   The handler correctly resolves team/status identifiers *only* when provided.
*   The handler correctly maps priority and formats the date *only* when provided.
*   The handler constructs the input for the internal mutation including *only* the fields present in the operation's input.
*   The operation successfully updates a Linear project when valid inputs (including various combinations of optional fields) are provided.
*   The operation returns the correct response structure upon success.
*   The operation handles errors gracefully (e.g., invalid `projectId`, unresolved identifiers, API errors).

## 5. Risks and Dependencies

*   **Dependency:** Relies heavily on the structure and utility functions established in `integrations/linear/createProject.ts` or shared utility modules. Changes there could impact this operation.
*   **Dependency:** Assumes the existence and correctness of an internal operation to fetch teams and statuses if needed for resolution.
*   **Risk:** The exact field names and structure required by the Linear API's *update* mutation might differ slightly from the *create* mutation. Requires careful verification during implementation.
*   **Risk:** Ensuring the conditional inclusion of fields in the `updatePayload` is implemented correctly is crucial to prevent accidental data loss in Linear.
*   **Risk:** Rate limits or specific permissions required by the Linear API for updates.

## 6. Handoff Recommendation

This plan provides the necessary details to create the two required files (`.graphql` and `.ts`). It is recommended to proceed with implementation.

**Suggested Next Step:** Switch to the `implement` agent to execute this plan.