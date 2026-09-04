from src.energy_kg.graph import EnergyKnowledgeGraph

kg = EnergyKnowledgeGraph()

kg.add_entity(
    "ERCOT",
    "Market",
    country="USA",
    active=True,
)

kg.add_entity(
    "HB_SOUTH",
    "Hub",
    zone="South",
    active=True,
)

kg.add_entity(
    "HB_NORTH",
    "Hub",
    zone="North",
    active=True,
)

kg.add_relationship(
    source="ERCOT",
    target="HB_SOUTH",
    relationship="HAS_HUB"
)


kg.add_relationship(
    source="ERCOT",
    target="HB_NORTH",
    relationship="HAS_HUB"
)


kg.add_entity(
    "South Texas",
    "Region",
    country="USA",
)

kg.add_entity(
    "North Texas",
    "Region",
    country="USA",
)


kg.add_relationship(
    source="HB_SOUTH",
    target="South Texas",
    relationship="LOCATED_IN"
)
kg.add_relationship(
    source="HB_NORTH",
    target="North Texas",
    relationship="LOCATED_IN"
)


# print(kg.get_related_entities(source="ERCOT", relationship="HAS_HUB"))
print(kg.traverse("ERCOT",relationships=["HAS_HUB", "LOCATED_IN"]))

print(kg.get_entity_by_type("Region"))

print(kg.get_entity_type("ERCOT"))
print(kg.get_entity_type("HB_NORTH"))


print(kg.get_hubs_with_regions("ERCOT"))

print(kg.traverse("ERCOT", relationships=["HAS_HUB", "LOCATED_IN"])) 

print(
    kg.get_entity_properties(
        "HB_SOUTH"
    )
)

active_hubs = kg.get_related_entities_with_properties(
    source="ERCOT",
    relationship="HAS_HUB",
    entity_type="Hub",
    active=True,
)

print(active_hubs)


south_hubs = kg.get_related_entities_with_properties(
    source="ERCOT",
    relationship="HAS_HUB",
    entity_type="Hub",
    active=True,
    zone="South",
)

print(south_hubs)


active_hubs = kg.find_entities(
    entity_type="Hub",
    active=True,
)

print(active_hubs)