import networkx as nx


class EnergyKnowledgeGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(
        self,
        name: str,
        entity_type: str,
    ) -> None:
        self.graph.add_node(
            name,
            type=entity_type,
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