from app.neo4j_connector import Neo4jConnector

class KGCrudService:
    def __init__(self):
        self.neo4j = Neo4jConnector()

    def create_node(self, label: str, properties: dict):
        query = f"CREATE (n:{label} $properties)"
        self.neo4j.query(query, {'properties': properties})

    def create_relationship(self, from_label, from_id, to_label, to_id, rel_type):
        query = f"""
        MATCH (a:{from_label} {{id: $from_id}})
        MATCH (b:{to_label} {{id: $to_id}})
        CREATE (a)-[:{rel_type}]->(b)
        """
        self.neo4j.query(query, {'from_id': from_id, 'to_id': to_id})

    def get_all_nodes_and_relationships(self):
        query = """
        MATCH (a)-[r]->(b)
        RETURN labels(a) AS from_labels, a.id AS from_id, 
            type(r) AS rel_type, 
            labels(b) AS to_labels, b.id AS to_id
        """
        return self.neo4j.query(query)

    def delete_all(self):
        self.neo4j.query("MATCH (n) DETACH DELETE n")
