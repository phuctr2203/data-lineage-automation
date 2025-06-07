from fastapi import FastAPI, HTTPException
from app.neo4j_connector import Neo4jConnector
from app.services.schema_generator import generate_sql_schema
from pydantic import BaseModel

app = FastAPI(title="Knowledge Graph Schema Generator",
              description="A service to extract triplets from text and generate a schema for a knowledge graph.")

neo4j = Neo4jConnector()

class QueryPayload(BaseModel):
    cypher: str
    
@app.post("/run-query/")
def run_query(payload: QueryPayload):
    try:
        result = neo4j.query(payload.cypher)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@app.get("/generate-schema/")
def generate_schema():
    sql_schema = generate_sql_schema(neo4j)
    return {"sql_schema": sql_schema}