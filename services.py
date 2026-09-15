
from src.energy_kg.neo4j_graph import Neo4jKnowledgeGraph

kg = Neo4jKnowledgeGraph(
        uri="bolt://localhost:7687",
    )

def get_all_markets():
    """Get all available markets in the knowledge graph."""
    markets = kg.get_entity_by_type("Market")
    return {
        "markets": markets,
        "count": len(markets)
    }

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

def fetch_market_hubs_with_regions(market_name):
    """Fetch all hubs for a market along with their regions in a single query."""
    query = """
    MATCH (m:Entity {name: $market_name})-[:HAS_HUB]->(hub)
    OPTIONAL MATCH (hub)-[:LOCATED_IN]->(region)
    RETURN hub.name AS hub, collect(region.name) AS regions
    """
    with kg.driver.session() as session:
        result = session.run(query, market_name=market_name)
        hubs_with_regions = []
        for record in result:
            hubs_with_regions.append({
                "hub": record["hub"],
                "regions": [r for r in record["regions"] if r is not None]
            })
    
    return {
        "market_name": market_name,
        "hubs_with_regions": hubs_with_regions
    }


def get_fuel_types_for_market(market_name):
    """Get all fuel types used by power plants connected to a market's hubs."""
    query = """
    MATCH (m:Entity {name: $market_name})-[:HAS_HUB]->(hub)
    MATCH (plant:Entity {type: 'PowerPlant'})-[:SUPPLIES]->(hub)
    MATCH (plant)-[:USES_FUEL]->(fuel:Entity {type: 'FuelType'})
    RETURN DISTINCT fuel.name AS fuel_type
    """
    with kg.driver.session() as session:
        result = session.run(query, market_name=market_name)
        fuel_types = [record["fuel_type"] for record in result]
    
    return {
        "market_name": market_name,
        "fuel_types": fuel_types
    }


def get_power_plants_for_market(market_name):
    """Get all power plants connected to a market's hubs."""
    query = """
    MATCH (m:Entity {name: $market_name})-[:HAS_HUB]->(hub)
    MATCH (plant:Entity {type: 'PowerPlant'})-[:SUPPLIES]->(hub)
    MATCH (plant)-[:USES_FUEL]->(fuel:Entity {type: 'FuelType'})
    RETURN plant.name AS name, plant.capacity_mw AS capacity_mw, 
           fuel.name AS fuel_type, hub.name AS hub
    """
    with kg.driver.session() as session:
        result = session.run(query, market_name=market_name)
        plants = []
        for record in result:
            plants.append({
                "name": record["name"],
                "capacity_mw": record["capacity_mw"],
                "fuel_type": record["fuel_type"],
                "hub": record["hub"]
            })
    
    return {
        "market_name": market_name,
        "power_plants": plants,
        "count": len(plants)
    }


def get_power_plants_by_fuel(fuel_type):
    """Get all power plants that use a specific fuel type."""
    query = """
    MATCH (plant:Entity {type: 'PowerPlant'})-[:USES_FUEL]->(fuel:Entity {name: $fuel_type})
    MATCH (plant)-[:SUPPLIES]->(hub)
    RETURN plant.name AS name, plant.capacity_mw AS capacity_mw, hub.name AS hub
    """
    with kg.driver.session() as session:
        result = session.run(query, fuel_type=fuel_type)
        plants = []
        for record in result:
            plants.append({
                "name": record["name"],
                "capacity_mw": record["capacity_mw"],
                "hub": record["hub"]
            })
    
    return {
        "fuel_type": fuel_type,
        "power_plants": plants,
        "count": len(plants)
    }


