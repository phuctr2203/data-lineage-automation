from neo4j import GraphDatabase
from app.config import Config

class Neo4jConnector:
    def __init__(self):
        print("NEO4J_URI:", Config.NEO4J_URI)
        print("NEO4J_USER:", Config.NEO4J_USER)
        print("NEO4J_PASSWORD:", Config.NEO4J_PASSWORD)
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        # self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def query(self, cypher_query, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [record.data() for record in result]
