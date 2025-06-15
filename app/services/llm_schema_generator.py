from google.generativeai import configure, GenerativeModel
from app.config import Config

class LLMSchemaGenerator:
    def __init__(self, neo4j_connector):
        self.neo4j = neo4j_connector
        configure(api_key=Config.GEMINI_API_KEY)
        self.model = GenerativeModel("gemini-2.0-flash")

    def extract_nodes(self):
        query = """
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels, properties(n) AS props
        """
        return self.neo4j.query(query)

    def extract_relationships(self):
        query = """
        MATCH (a)-[r]->(b)
        RETURN labels(a) AS from_labels, a.id AS from_id, 
               type(r) AS rel_type, 
               labels(b) AS to_labels, b.id AS to_id
        """
        return self.neo4j.query(query)

    def build_prompt(self, nodes, relationships):
        triplets = []
        for node in nodes:
            label = node['labels'][0] if node['labels'] else 'Unknown'
            props = node['props']
            props_str = ", ".join(f"{k}: {v}" for k, v in props.items())
            triplets.append(f"Node: {label} ({props_str})")

        for rel in relationships:
            from_label = rel['from_labels'][0] if rel['from_labels'] else 'Unknown'
            to_label = rel['to_labels'][0] if rel['to_labels'] else 'Unknown'
            rel_type = rel['rel_type']
            triplets.append(f"{from_label} --[{rel_type}]--> {to_label}")

        knowledge_graph = "\n".join(triplets)

        prompt = f"""
        You are a data modeling expert. Given the following knowledge graph, generate:

        1. SQL table schema with columns, primary keys, foreign keys.
        2. A JSON object representing tables, columns, keys and relationships.

        IMPORTANT: Return pure JSON only, no markdown or formatting.
        
        Example Output Format:
        {{
        "json_schema": {{
            "tables": [
            {{
                "name": "TableName",
                "columns": [
                {{ "name": "ColumnName", "type": "VARCHAR(255)", "primary_key": true/false, "foreign_key": {{ "references": "OtherTable(ColumnName)" }} }}
                ]
            }}
            ]
        }},
        "sql_script": "CREATE TABLE ... ;"
        }}

        Knowledge Graph:
        {knowledge_graph}
        """
        return prompt

    def generate_sql_schema(self):
        nodes = self.extract_nodes()
        relationships = self.extract_relationships()
        prompt = self.build_prompt(nodes, relationships)
        response = self.model.generate_content(prompt)
        return response.text
