from fastapi import FastAPI, File, UploadFile, HTTPException
from app.neo4j_connector import Neo4jConnector
import os
from app.services.ocr_service import OCRService
from app.services.triplet_extractor_service import TripletExtractorService
from app.model.triplet import TripletResponse

app = FastAPI(title="Knowledge Graph Schema Generator",
              description="A service to extract triplets from text and generate a schema for a knowledge graph.")

neo4j = Neo4jConnector()

@app.on_event("shutdown")
def shutdown():
    neo4j.close()

@app.post("/create-entity/")
def create_entity(entity_name: str, name: str, description: str = ""):
    properties = {"name": name, "description": description}
    node = neo4j.create_entity(entity_name, properties)
    return {"message": "Entity created", "node": dict(node)}

@app.post("/create-relationship/")
def create_relationship(entity1_label: str, entity1_name: str,
                        entity2_label: str, entity2_name: str,
                        relationship_type: str):
    rel = neo4j.create_relationship(
        entity1_label, {"name": entity1_name},
        entity2_label, {"name": entity2_name},
        relationship_type
    )
    return {"message": "Relationship created", "relationship": str(rel)}

@app.get("/entities/")
def get_entities():
    entities = neo4j.get_entities()
    return {"entities": [dict(node) for node in entities]}

@app.get("/relationships/")
def get_relationships():
    rels = neo4j.get_relationships()
    return {"relationships": [str(rel) for rel in rels]}

@app.post("/extract-triplets/")
async def extract_triplets(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_extension = os.path.splitext(file.filename)[1].lower()
        extracted_text = OCRService.ocr_file(content, file_extension)
        triplets = TripletExtractorService.extract_triples(extracted_text)
        return TripletResponse(triplets)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))