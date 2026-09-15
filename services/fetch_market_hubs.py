
from src.energy_kg.neo4j_graph import Neo4jKnowledgeGraph

kg = Neo4jKnowledgeGraph(
        uri="bolt://localhost:7687",
    )
def get_market_hubs(market_name):
    result={}
    
    hubs = kg.get_related_entities(market_name, "HAS_HUB")
    print(f"{market_name} has Hubs: {hubs}")
    return {
        "market_name": market_name,
        "hubs": hubs,
    }
    return hubs

def get_hub_region(hub_name):
    region = kg.get_related_entities(hub_name, "LOCATED_IN")
    print(f"{hub_name} is located in: {region}")
    return {
        "hub_name": hub_name,
        "region": region,
    }


