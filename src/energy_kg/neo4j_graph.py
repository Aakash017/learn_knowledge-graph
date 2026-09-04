from neo4j import GraphDatabase


class Neo4jKnowledgeGraph:
    """
    Knowledge graph backed by Neo4j.
    Same API as EnergyKnowledgeGraph but persists to Neo4j.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str | None = None,
        password: str | None = None,
    ):
        auth = (user, password) if user and password else None
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()

    def clear(self):
        """Delete all nodes and relationships (use with caution)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def add_entity(
        self,
        name: str,
        entity_type: str,
        **properties,
    ) -> None:
        """Add an entity (node) to the graph."""
        with self.driver.session() as session:
            # Merge to avoid duplicates
            query = """
            MERGE (e:Entity {name: $name})
            SET e.type = $entity_type
            SET e += $properties
            """
            session.run(
                query,
                name=name,
                entity_type=entity_type,
                properties=properties,
            )

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship: str,
    ) -> None:
        """Add a relationship (edge) between two entities."""
        with self.driver.session() as session:
            # Dynamic relationship type using APOC or string formatting
            # Using a workaround since relationship types can't be parameterized
            query = f"""
            MATCH (s:Entity {{name: $source}})
            MATCH (t:Entity {{name: $target}})
            MERGE (s)-[r:{relationship}]->(t)
            """
            session.run(query, source=source, target=target)

    def get_related_entities(
        self,
        source: str,
        relationship: str,
    ) -> list[str]:
        """Get all entities connected via a specific relationship."""
        with self.driver.session() as session:
            query = f"""
            MATCH (s:Entity {{name: $source}})-[:{relationship}]->(t:Entity)
            RETURN t.name AS name
            """
            result = session.run(query, source=source)
            return [record["name"] for record in result]

    def traverse(
        self,
        source: str,
        relationships: list[str],
    ) -> list[str]:
        """Traverse multiple relationships in sequence."""
        current_nodes = [source]

        for relationship in relationships:
            next_nodes = []
            for node in current_nodes:
                related = self.get_related_entities(node, relationship)
                next_nodes.extend(related)
            current_nodes = next_nodes

        return current_nodes

    def get_entity_by_type(
        self,
        entity_type: str,
    ) -> list[str]:
        """Get all entities of a specific type."""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {type: $entity_type})
            RETURN e.name AS name
            """
            result = session.run(query, entity_type=entity_type)
            return [record["name"] for record in result]

    def get_entity_type(
        self,
        entity: str,
    ) -> str | None:
        """Get the type of an entity."""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {name: $name})
            RETURN e.type AS type
            """
            result = session.run(query, name=entity)
            record = result.single()
            return record["type"] if record else None

    def get_entity_properties(
        self,
        entity: str,
    ) -> dict | None:
        """Get all properties of an entity."""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {name: $name})
            RETURN e AS entity
            """
            result = session.run(query, name=entity)
            record = result.single()
            if record:
                return dict(record["entity"])
            return None

    def get_hubs_with_regions(
        self,
        market: str,
    ) -> list[dict]:
        """Get all hubs and their regions for a market."""
        with self.driver.session() as session:
            query = """
            MATCH (m:Entity {name: $market})-[:HAS_HUB]->(h:Entity {type: 'Hub'})
            MATCH (h)-[:LOCATED_IN]->(r:Entity {type: 'Region'})
            RETURN h.name AS hub, r.name AS region
            """
            result = session.run(query, market=market)
            return [{"hub": r["hub"], "region": r["region"]} for r in result]

    def find_entities(
        self,
        entity_type: str | None = None,
        **properties,
    ) -> list[str]:
        """Find entities matching type and/or properties."""
        with self.driver.session() as session:
            conditions = []
            params = {}

            if entity_type:
                conditions.append("e.type = $entity_type")
                params["entity_type"] = entity_type

            for key, value in properties.items():
                param_name = f"prop_{key}"
                conditions.append(f"e.{key} = ${param_name}")
                params[param_name] = value

            where_clause = " AND ".join(conditions) if conditions else "TRUE"

            query = f"""
            MATCH (e:Entity)
            WHERE {where_clause}
            RETURN e.name AS name
            """
            result = session.run(query, **params)
            return [record["name"] for record in result]

    def get_related_entities_with_properties(
        self,
        source: str,
        relationship: str,
        entity_type: str | None = None,
        **properties,
    ) -> list[str]:
        """Get related entities filtered by type and properties."""
        related = self.get_related_entities(source, relationship)
        results = []

        for entity in related:
            props = self.get_entity_properties(entity)
            if props is None:
                continue

            if entity_type and props.get("type") != entity_type:
                continue

            matches = all(
                props.get(key) == value
                for key, value in properties.items()
            )

            if matches:
                results.append(entity)

        return results
