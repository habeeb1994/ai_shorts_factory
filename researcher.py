import json
import re
import os
from groq import Groq

class ResearcherAgent:
    def generate_viral_atoms(self, topic,output_path):
        # The prompt is now much stricter about formatting
        prompt = f"""
        Act as a viral YouTube Shorts scriptwriter. Create a high-retention script about: {topic}.
        
        RULES:
        1. NARRATION: Write a script of exactly 200-250 words to ensure a 50-second duration. Provide ONLY the words to be spoken. NO stage directions, NO brackets, NO speaker names.
        2. STRUCTURE: Start with a polarizing hook, followed by 3 rapid-fire value points, and a 2-second CTA.
        3. TONE: High-energy, professional, and punchy.
        4. METADATA: Provide search keywords for stock footage.
        5. FORMATTING: Do NOT use line breaks or newlines inside the JSON strings. Keep the script as one continuous paragraph.

        RESPONSE FORMAT (Strict JSON only):
        {{
            "title": "Viral Title Here",
            "script": "The exact spoken words here...",
            "keywords": "5 keywords for video search",
            "tags": ["tag1", "tag2"]
        }}
        """
        
        # Initialize the Groq client (Make sure to set your GROQ_API_KEY environment variable)
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")
        client = Groq(api_key=api_key)        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Llama 3.1 8B model hosted on Groq
            messages=[{'role': 'user', 'content': prompt}]
        )
        raw_content = response.choices[0].message.content
        print(raw_content)
        # Clean up the response to ensure we only get the JSON block
        try:
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            data = json.loads(json_match.group(), strict=False)
            
            # Final Sanitize: Remove any accidental [Stage Directions]
            data['script'] = re.sub(r'\[.*?\]|\(.*?\)', '', data['script'])
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(data['script'])
            print(f"📄 Script saved locally to: {output_path}")
            return data
            
        except Exception as e:
            print(f"⚠️ JSON Parsing Error, falling back to manual split: {e}")
            return {
                "title": f"{topic} EXPLAINED",
                "script": raw_content.strip(), # Fallback
                "keywords": topic,
                "tags": ["ai", "wealth"]
            }