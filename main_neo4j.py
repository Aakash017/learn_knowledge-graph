"""
Example using Neo4j-backed Knowledge Graph.
Make sure Neo4j is running: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=none neo4j:latest
"""

from src.energy_kg.neo4j_graph import Neo4jKnowledgeGraph


def main():
    # Connect to Neo4j (no auth since we used NEO4J_AUTH=none)
    kg = Neo4jKnowledgeGraph(
        uri="bolt://localhost:7687",
    )

    # Clear any existing data
    print("Clearing existing data...")
    kg.clear()

    # Add entities - same API as EnergyKnowledgeGraph
    print("\nAdding entities...")
    kg.add_entity("ERCOT", "Market", country="USA", state="Texas")
    kg.add_entity("HB_SOUTH", "Hub", zone="South", active=True)
    kg.add_entity("HB_NORTH", "Hub", zone="North", active=True)
    kg.add_entity("HB_WEST", "Hub", zone="West", active=False)
    kg.add_entity("South Texas", "Region", population=5000000)
    kg.add_entity("North Texas", "Region", population=8000000)

    # Add relationships
    print("Adding relationships...")
    kg.add_relationship("ERCOT", "HB_SOUTH", "HAS_HUB")
    kg.add_relationship("ERCOT", "HB_NORTH", "HAS_HUB")
    kg.add_relationship("ERCOT", "HB_WEST", "HAS_HUB")
    kg.add_relationship("HB_SOUTH", "South Texas", "LOCATED_IN")
    kg.add_relationship("HB_NORTH", "North Texas", "LOCATED_IN")

    # Query the graph - same methods work!
    print("\n--- Queries ---")

    # Get hubs for ERCOT
    hubs = kg.get_related_entities("ERCOT", "HAS_HUB")
    print(f"ERCOT Hubs: {hubs}")

    # Traverse: Market -> Hub -> Region
    regions = kg.traverse("ERCOT", ["HAS_HUB", "LOCATED_IN"])
    print(f"Regions via ERCOT hubs: {regions}")

    # Get all hubs
    all_hubs = kg.get_entity_by_type("Hub")
    print(f"All Hubs: {all_hubs}")

    # Get entity properties
    props = kg.get_entity_properties("HB_SOUTH")
    print(f"HB_SOUTH properties: {props}")

    # Find active hubs
    active_hubs = kg.find_entities(entity_type="Hub", active=True)
    print(f"Active Hubs: {active_hubs}")

    # Get hubs with their regions
    hubs_regions = kg.get_hubs_with_regions("ERCOT")
    print(f"Hubs with Regions: {hubs_regions}")

    # Close connection
    kg.close()

    print("\n✓ Neo4j Knowledge Graph working!")
    print("Open http://localhost:7474 to visualize the graph")


if __name__ == "__main__":
    main()
