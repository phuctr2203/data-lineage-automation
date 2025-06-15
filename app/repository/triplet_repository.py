from typing import List
from app.neo4j_connector import Neo4jConnector
from app.model.triplet import Triplet, TripletResponse


class TripletRepository:
    def __init__(self):
        self.connector = Neo4jConnector()
    

    def insert_triplets(self, triplets: List[Triplet]):
        query = (
            "UNWIND $triplets AS triplet "
            "MERGE (e:Entity {name: triplet.entity}) "
            "MERGE (o:Object {name: triplet.object}) "
            "MERGE (e)-[r:RELATIONSHIP {name: triplet.relationship}]->(o)"
        )
        parameters = {"triplets": [t.dict() for t in triplets]}
        self.connector.query(cypher_query=query, parameters=parameters)

    
    def get_all_relationships(self) -> TripletResponse:
        query = (
            "MATCH (e:Entity)-[r:RELATIONSHIP]->(o:Object) "
            "RETURN e.name AS entity, r.name AS relationship, o.name AS object"
        )
        results = self.connector.query(query)
        triplets = [Triplet(**result) for result in results]
        return TripletResponse(triplets=triplets)
    

    def get_relationships_by_entity(self, entity_name: str) -> TripletResponse:
        query = (
            "MATCH (e:Entity {name: $entity_name})-[r:RELATIONSHIP]->(o:Object) "
            "RETURN e.name AS entity, r.name AS relationship, o.name AS object"
        )
        parameters = {"entity_name": entity_name}
        results = self.connector.query(cypher_query=query, parameters=parameters)
        triplets = [Triplet(**result) for result in results]
        return TripletResponse(triplets=triplets)
    

    def get_relationships_by_object(self, object_name: str) -> TripletResponse:
        query = (
            "MATCH (e:Entity)-[r:RELATIONSHIP]->(o:Object {name: $object_name}) "
            "RETURN e.name AS entity, r.name AS relationship, o.name AS object"
        )
        parameters = {"object_name": object_name}
        results = self.connector.query(cypher_query=query, parameters=parameters)
        triplets = [Triplet(**result) for result in results]
        return TripletResponse(triplets=triplets)
    

    def delete_all_relationships(self):
        query = (
            "MATCH (e:Entity)-[r:RELATIONSHIP]->(o:Object) "
            "DELETE r, e, o"
        )
        self.connector.query(query)

    
    def close(self):
        self.connector.close()