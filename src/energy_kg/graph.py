import networkx as nx


class EnergyKnowledgeGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(
        self,
        name: str,
        entity_type: str,
        **properties,
    ) -> None:
        self.graph.add_node(
            name,
            type=entity_type,
            **properties
        )

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship: str,
    ) -> None:
        self.graph.add_edge(
            source,
            target,
            relation=relationship,
        )

    def get_related_entities(
        self,
        source: str,
        relationship: str,
    ) -> list[str]:

        results = []

        for target in self.graph.successors(source):
            edge = self.graph[source][target]

            if edge["relation"] == relationship:
                results.append(target)

        return results
    
    def traverse(
    self,
    source: str,
    relationships: list[str],
) -> list[str]:

        current_nodes = [source]

        for relationship in relationships:

            next_nodes = []

            for node in current_nodes:

                related = self.get_related_entities(
                    node,
                    relationship,
                )

                next_nodes.extend(related)

            current_nodes = next_nodes

        return current_nodes
    
    def get_entity_by_type(
        self,
        entity_type:str,
    ) -> list[str]:
        results=[]
        for node, data in self.graph.nodes(data=True):
            if data.get("type")==entity_type:
                results.append(node)
        return results
    def get_entity_type(
        self, 
        entity:str,
    )-> list[str]:
        if entity not in self.graph:
            return None
        return self.graph.nodes[entity].get("type")
    
    def get_hubs_with_regions(
        self,
        Market: str,
    )-> list[str]:
        results=[]
        hubs=self.get_related_entities(
            Market,
            "HAS_HUB",
        )
        
        for hub in hubs:

            if self.get_entity_type(hub) != "Hub":
                continue


            regions=self.get_related_entities(
                hub,
                "LOCATED_IN" 
            )
            for region in regions:

                if self.get_entity_type(region) != "Region":
                    continue

                results.append({
                    "hub": hub,
                    "region": region,
                })
                
        return results
    
    def get_entity_properties(
    self,
    entity: str,
) -> dict | None:

        if entity not in self.graph:
            return None

        return dict(
            self.graph.nodes[entity]
        )
    
    def get_related_entities_with_properties(
    self,
    source: str,
    relationship: str,
    entity_type: str | None = None,
    **properties,
) -> list[str]:

        related_entities = self.get_related_entities(
            source,
            relationship,
        )

        results = []

        for entity in related_entities:

            data = self.graph.nodes[entity]

            if (
                entity_type is not None
                and data.get("type") != entity_type
            ):
                continue

            matches = True

            for key, expected_value in properties.items():

                if data.get(key) != expected_value:
                    matches = False
                    break

            if matches:
                results.append(entity)

        return results
    
    def find_entities(
    self,
    entity_type: str | None = None,
    **properties,
) -> list[str]:

        results = []

        for entity, data in self.graph.nodes(data=True):

            if (
                entity_type is not None
                and data.get("type") != entity_type
            ):
                continue

            matches = True

            for key, expected_value in properties.items():

                if data.get(key) != expected_value:
                    matches = False
                    break

            if matches:
                results.append(entity)

        return results