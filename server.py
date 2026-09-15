from mcp.server.mcpserver import MCPServer
from typing import Any

mcp = MCPServer("Energy Knowledge Graph")


@mcp.tool()
def list_markets() -> dict[str, Any]:
    """list_markets
    Returns all available markets in the knowledge graph"""
    from services import get_all_markets
    return get_all_markets()


@mcp.tool()
def fetch_market_hubs(market_name:str) -> dict[str, Any]:
    """fetch_market_hubs
    Given a market name, e.g. NYISO or ERCOT etc.,
    Returns Market names and hubs"""
    from services import get_market_hubs
    return get_market_hubs(market_name)

@mcp.tool()
def fetch_hubs_regions(hub_name:str):
    """fetch_hubs_regions
    Given a hub name, e.g. NYISO_HUB or ERCOT_HUB etc.,
    Returns Regions associated with the hub"""
    from services import get_hub_region
    return get_hub_region(hub_name)

@mcp.tool()
def fetch_region_data(region_name:str):
    """fetch_region_data
    Given a region name, e.g. NYISO_NORTH or ERCOT_SOUTH etc.,
    Returns data associated with the region"""
    from services import get_region_data
    return get_region_data(region_name)

@mcp.tool()
def fetch_market_hubs_with_regions(market_name:str):
    """fetch_market_hubs_with_regions
    Given a market name, e.g. NYISO or ERCOT etc.,
    Returns Market names and hubs with regions"""
    from services import fetch_market_hubs_with_regions
    return fetch_market_hubs_with_regions(market_name)


@mcp.tool()
def fetch_fuel_types(market_name: str) -> dict[str, Any]:
    """fetch_fuel_types
    Given a market name, e.g. ERCOT,
    Returns all fuel types used by power plants in that market"""
    from services import get_fuel_types_for_market
    return get_fuel_types_for_market(market_name)


@mcp.tool()
def fetch_power_plants(market_name: str) -> dict[str, Any]:
    """fetch_power_plants
    Given a market name, e.g. ERCOT,
    Returns all power plants connected to that market with their capacity, fuel type, and hub"""
    from services import get_power_plants_for_market
    return get_power_plants_for_market(market_name)


@mcp.tool()
def fetch_power_plants_by_fuel(fuel_type: str) -> dict[str, Any]:
    """fetch_power_plants_by_fuel
    Given a fuel type, e.g. Wind, Solar, Coal, Natural Gas, Nuclear,
    Returns all power plants that use that fuel type"""
    from services import get_power_plants_by_fuel
    return get_power_plants_by_fuel(fuel_type)
