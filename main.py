from src.energy_kg.graph import EnergyKnowledgeGraph

kg = EnergyKnowledgeGraph()

kg.add_entity(
    name="ERCOT",
    entity_type="Market"
)

kg.add_entity(
    name="HB_SOUTH",
    entity_type="Hub"
)

kg.add_entity(
    name="HB_NORTH",
    entity_type="Hub"
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
)

kg.add_entity(
    "North Texas",
    "Region",
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