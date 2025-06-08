import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
import re

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

        # Parse response to JSON
        try:
            triplets = json.loads(response.text)
            return triplets
        except json.JSONDecodeError:
            print("Failed to parse JSON from modal response")

        # Parse response to JSON using regex
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            try:
                triplets = json.loads(json_match.group())
                return triplets
            except json.JSONDecodeError:
                print("Failed to parse extracted content as JSON")
        
        # Parse response to JSON "tù đày" way
        lines = response.text.strip().split('\n')
        triplets = []
        for line in lines:
            parts = line.split(',')
            if len(parts) == 3:
                triplet = {
                    "entity": parts[0].strip(),
                    "relationship": parts[1].strip(),
                    "object": parts[2].strip()
                }
                triplets.append(triplet)
        if triplets:
            return triplets
        else:
            print("Unable to extract triplets from the response")
            return []
            