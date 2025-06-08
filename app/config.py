import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://localhost:7687")  
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
