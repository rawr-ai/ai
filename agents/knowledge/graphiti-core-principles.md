# Graphiti's Core Idea

Graphiti creates **dynamic, temporally aware Knowledge Graphs (KGs)**. Unlike static KGs, Graphiti is designed to represent how facts and relationships between entities change over time. It ingests both structured and unstructured data to build these evolving graphs. (Source: [Graphiti GitHub](https://github.com/getzep/graphiti), [Graphiti Overview](https://help.getzep.com/graphiti/graphiti/overview)).

# Building Blocks

## Entities

These are the core nodes in the graph, representing distinct concepts, objects, or abstractions (e.g., people, companies, products, or even abstract concepts like `Agent` or `Persona` as shown in `ai/resources/entity-design-example.md`). An entity should have a distinct identity and be meaningful enough to be queried or related to other entities. The `ai/resources/entity-design-guidelines.md` document provides excellent guidance on distinguishing between what should be an entity versus just a property of another entity (e.g., "Candidate" is a good entity, while "email address" is typically a property of a Candidate entity). Graphiti can extract entities and allows defining custom entity types with specific attributes for more domain-specific modeling ([Graphiti Custom Entity Types](https://help.getzep.com/graphiti/graphiti/custom-entity-types)).

## Facts (Triplets)

These are the fundamental units of information representing a connection between two entities via a relationship. They form the edges in the graph. A fact is often represented as a triplet: `(Entity 1) -[Relationship]-> (Entity 2)`. For example: `(Kendra) -[Loves]-> (Adidas Shoes)`. Graphiti extracts these facts from the data it ingests. (Source: [Graphiti Overview](https://help.getzep.com/graphiti/graphiti/overview)).

## Episodes

This is how Graphiti ingests data. An episode is a discrete unit of information (like a text snippet, a document, or structured JSON data) that is processed at a specific point in time. Graphiti extracts entities and facts *from* these episodes. This episodic processing is key to Graphiti's temporal awareness, as it maintains data provenance and allows the graph to be updated incrementally based on new information arriving in subsequent episodes. Each episode typically has associated metadata, like a timestamp (`reference_time`). (Source: [Graphiti GitHub](https://github.com/getzep/graphiti), [Graphiti Quick Start](https://help.getzep.com/graphiti/graphiti/quick-start), [Adding Episodes](https://help.getzep.com/graphiti/graphiti/adding-episodes)).

## Communities

The term "community" in graph theory usually refers to groups of nodes that are densely interconnected internally but sparsely connected to nodes outside the group (identified via community detection algorithms). While Graphiti builds the underlying graph structure where such analysis *could* be performed, the provided documentation and resources **do not emphasize "communities" as a fundamental building block or input concept** in the same way as entities, facts (relationships), and episodes for constructing and evolving the graph itself. Communities are more likely an emergent property or an analytical result derived *from* the graph Graphiti builds, rather than a core input element like an episode.

# Temporal Evolution

Graphiti's unique strength lies in handling change. Because data is ingested as time-stamped episodes, Graphiti can track how relationships and entity attributes evolve. Edges (facts) can include temporal metadata, allowing you to query the state of the graph "as of" a specific point in time. This contrasts with approaches like the original GraphRAG, which was more focused on static document corpora. (Source: [Graphiti GitHub](https://github.com/getzep/graphiti), [Graphiti Overview](https://help.getzep.com/graphiti/graphiti/overview)).

# How it Relates to Your Resources

* `ai/resources/entity-design-guidelines.md`: Provides the crucial "why" and "how" for defining what constitutes a good **Entity** within your Graphiti KG, ensuring the graph is meaningful and queryable.
* `ai/resources/entity-design-example.md`: Shows a practical application of these guidelines, defining specific **Entities** (`Agent`, `Persona`, `Objective`, `Core Capability`, `Constraint`, `Tool`, `Interaction Model`) that could be extracted from **Episodes** (like agent prompts) to build a self-discoverable agent KG.

# In Summary

* You feed Graphiti **Episodes** (time-stamped chunks of data).
* Graphiti processes these episodes to extract **Entities** (nodes) and **Facts/Triplets** (relationships/edges between entities).
* The graph evolves over time as new episodes add or modify facts, with temporal tracking built-in.
* Well-designed **Entities** (following guidelines like those in `entity-design-guidelines.md`) are crucial for the graph's utility.
* **Communities** are a graph analysis concept, not a primary structural element defined during Graphiti's ingestion process based on the available information.
