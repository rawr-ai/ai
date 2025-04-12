# Updated Data Flow: `customInstructions`

This diagram illustrates the data flow for agent configuration loading, incorporating the new `customInstructions` field.

```mermaid
flowchart TD
    A[Agent Config YAML File\n(e.g., agent.yaml)] --> B{Load YAML Content\n(e.g., using PyYAML)};
    B --> C[Parse & Validate\n(using `cli.models.GlobalAgentConfig`)];
    C -- Contains --> D[GlobalAgentConfig Object\n- name: str\n- description: str\n- ...\n- **customInstructions: Optional[str]**];
    D --> E{Potential Usage\n(e.g., in `cli/compiler.py`)};

    style D fill:#f9f,stroke:#333,stroke-width:2px
```

**Explanation:**

1.  An agent's configuration is defined in a YAML file.
2.  The raw YAML content is loaded by a Python process (likely triggered indirectly by the compiler or main CLI logic).
3.  The loaded dictionary is parsed and validated against the `GlobalAgentConfig` Pydantic model defined in `cli/models.py`. This step now includes validation for the optional `customInstructions` field.
4.  A validated `GlobalAgentConfig` Python object is created, now potentially holding a value for `customInstructions`.
5.  This object is then used by downstream components, such as the `cli/compiler.py` script identified in the discovery report. The compiler needs to be aware of the new optional field.