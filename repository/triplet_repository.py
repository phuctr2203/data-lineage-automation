from neo4j import GraphDatabase
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jRepository:
    def __init__(self):
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')
        self.driver = GraphDatabase.driver(uri=uri, auth=(user, password))