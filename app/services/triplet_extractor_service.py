import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

class TripletExtractorService:
    def __init__(self):
        gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def extract_triples(self, text: str):
        prompt = f"""
Given the following text from a Software Requirements Specification (SRS) document, generate a list of tripets in the format [Entity, Relationship, Object]. Focus on key requirements, features, and system components.

Text: {text}

Generate the triplets and format the output as a JSON array of objects, where each object has "entity", "relationship", and "object" keys.
        """

        response = self.model.generate_content(prompt)

        try:
            triplets = json.loads(response.text)
            return triplets
        except json.JSONDecodeError:
            print("Failed to parse JSON from modal response. Raw response:")
            print(response.text)
            return []