"""
Load CSV data into Neo4j Knowledge Graph
"""
import csv
from src.energy_kg.neo4j_graph import Neo4jKnowledgeGraph


def load_power_plants(kg: Neo4jKnowledgeGraph, filepath: str):
    """Load power plants from CSV"""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create power plant entity
            kg.add_entity(
                name=row['name'],
                entity_type='PowerPlant',
                capacity_mw=int(row['capacity_mw']),
                online_year=int(row['online_year'])
            )
            
            # Create fuel type if not exists, connect plant to fuel
            kg.add_entity(row['fuel'], 'FuelType')
            kg.add_relationship(row['name'], row['fuel'], 'USES_FUEL')
            
            # Connect plant to hub
            kg.add_relationship(row['name'], row['hub'], 'SUPPLIES')
            
            print(f"Loaded: {row['name']} ({row['capacity_mw']} MW)")


def load_hubs(kg: Neo4jKnowledgeGraph, filepath: str):
    """Load hubs from CSV"""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kg.add_entity(
                name=row['name'],
                entity_type=row['type'],
                zone=row['zone']
            )
            
            # Connect to market
            kg.add_relationship(row['market'], row['name'], 'HAS_HUB')
            
            print(f"Loaded: {row['name']} ({row['type']})")


def main():
    kg = Neo4jKnowledgeGraph(uri="bolt://localhost:7687")
    
    print("Loading hubs...")
    load_hubs(kg, 'data/hubs.csv')
    
    print("\nLoading power plants...")
    load_power_plants(kg, 'data/power_plants.csv')
    
    print("\n--- Verification ---")
    
    # Count entities
    plants = kg.get_entity_by_type('PowerPlant')
    print(f"Total power plants: {len(plants)}")
    
    hubs = kg.get_entity_by_type('Hub')
    zones = kg.get_entity_by_type('LoadZone')
    print(f"Total hubs: {len(hubs)}")
    print(f"Total load zones: {len(zones)}")
    
    kg.close()
    print("\nData loaded successfully!")


if __name__ == "__main__":
    main()
