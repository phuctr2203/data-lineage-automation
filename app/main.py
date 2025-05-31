from fastapi import FastAPI

app = FastAPI(title="Knowledge Graph Schema Generator",
              description="A service to extract triplets from text and generate a schema for a knowledge graph.")

@app.get("/")
def root():
    return {"message": "Knowledge Graph Schema Generator is running"}

@app.post("/hello-world/")
def hello_world(name: str):
    return {"message": f"Hello, {name}!"}

