from neo4j import GraphDatabase
from app.config import Config

class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_entity(self, entity_name, properties):
        with self.driver.session() as session:
            result = session.run(
                f"""
                CREATE (e:{entity_name} $properties)
                RETURN e
                """,
                properties=properties
            )
            return result.single()[0]

    def create_relationship(self, entity1_label, entity1_prop, entity2_label, entity2_prop, relationship_type):
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (a:{entity1_label}), (b:{entity2_label})
                WHERE a.name = $a_name AND b.name = $b_name
                CREATE (a)-[r:{relationship_type}]->(b)
                RETURN r
                """,
                a_name=entity1_prop["name"],
                b_name=entity2_prop["name"]
            )
            return result.single()[0]

    def get_entities(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN n")
            return [record["n"] for record in result]

    def get_relationships(self):
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN r")
            return [record["r"] for record in result]