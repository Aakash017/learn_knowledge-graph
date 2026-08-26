# Energy Knowledge Graph

A Python library for building and querying knowledge graphs focused on energy market data. Built on top of NetworkX for efficient graph operations.

## Features

- Create entities with types (Markets, Hubs, Regions, etc.)
- Define relationships between entities
- Query related entities by relationship type
- Traverse multi-hop paths through the graph
- Filter entities by type

## Installation

Requires Python 3.12+

```bash
uv sync
```

## Usage

```python
from src.energy_kg.graph import EnergyKnowledgeGraph

# Create a knowledge graph
kg = EnergyKnowledgeGraph()

# Add entities
kg.add_entity("ERCOT", "Market")
kg.add_entity("HB_SOUTH", "Hub")
kg.add_entity("South Texas", "Region")

# Add relationships
kg.add_relationship("ERCOT", "HB_SOUTH", "HAS_HUB")
kg.add_relationship("HB_SOUTH", "South Texas", "LOCATED_IN")

# Query related entities
hubs = kg.get_related_entities("ERCOT", "HAS_HUB")
# Returns: ['HB_SOUTH']

# Traverse multiple relationships
regions = kg.traverse("ERCOT", ["HAS_HUB", "LOCATED_IN"])
# Returns: ['South Texas']

# Get entities by type
all_regions = kg.get_entity_by_type("Region")

# Get entity type
entity_type = kg.get_entity_type("ERCOT")
# Returns: 'Market'
```

## Running the Example

```bash
uv run python main.py
```

## Dependencies

- networkx >= 3.6.1
