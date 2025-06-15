from typing import List
from app.model.triplet import Triplet, TripletResponse
from app.repository.triplet_repository import TripletRepository


class TripletService:
    def __init__(self):
        self.repository = TripletRepository()

    def insert_triplets(self, triplets: List[Triplet]) -> TripletResponse:
        self.repository.insert_triplets(triplets)
        return TripletResponse(triplets=triplets)

    def get_all_relationships(self) -> TripletResponse:
        return self.repository.get_all_relationships()

    def get_relationships_by_entity(self, entity_name: str) -> TripletResponse:
        return self.repository.get_relationships_by_entity(entity_name)

    def get_relationships_by_object(self, object_name: str) -> TripletResponse:
        return self.repository.get_relationships_by_object(object_name)

    def delete_all_relationships(self):
        self.repository.delete_all_relationships()

    def get_unique_entities(self) -> List[str]:
        all_relationships = self.repository.get_all_relationships()
        unique_entities = set(triplet.entity for triplet in all_relationships.triplets)
        return list(unique_entities)

    def get_unique_objects(self) -> List[str]:
        all_relationships = self.repository.get_all_relationships()
        unique_objects = set(triplet.object for triplet in all_relationships.triplets)
        return list(unique_objects)

    def get_relationships_by_entity_and_object(self, entity_name: str, object_name: str) -> TripletResponse:
        all_relationships = self.repository.get_all_relationships()
        filtered_triplets = [
            triplet for triplet in all_relationships.triplets
            if triplet.entity == entity_name and triplet.object == object_name
        ]
        return TripletResponse(triplets=filtered_triplets)