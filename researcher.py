import json
import re
import os
from groq import Groq

class ResearcherAgent:
    def generate_viral_atoms(self, topic, output_path, scout_method="ai"):
        # The prompt is now much stricter about formatting
        if scout_method == "ai":
            # Refined to emphasize lighting and composition for AI generators (like Veo or Sora)
            metadata_rule = ("**VIDEO PROMPTS**: Generate 3 cinematic, highly detailed text-to-video prompts. "
                     "Requirements: 9:16 aspect ratio, subject always in center-frame, use descriptive lighting "
                     "(e.g., volumetric, neon, or golden hour) and realistic textures.")
            metadata_json_schema = '"video_prompts": ["Prompt 1", "Prompt 2", "Prompt 3"],'
        else:
            # Refined for high-intent stock footage searching
            metadata_rule = ("**STOCK KEYWORDS**: Provide 5 high-intent search keywords. "
                     "Focus on visual actions and specific objects rather than abstract concepts.")
            metadata_json_schema = '"keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5"],'

# Improved prompt with "Chain of Thought" and clearer formatting constraints
        prompt = f"""
        Act as a world-class viral YouTube Shorts Scriptwriter specializing in high-retention storytelling. 
        Your goal is to write a script about: {topic}

        ### SCRIPT RULES:
        1. **NARRATION**: Write exactly 200-250 words. Do NOT include stage directions, [Music], or speaker names. 
        2. **THE HOOK**: Start with a polarizing or "contrarian" statement that stops the scroll immediately.
        3. **BODY**: Deliver 3 rapid-fire, high-value facts or points. Every sentence must build tension or curiosity.
        4. **CTA**: End with a 2-second call to action directing the viewer to "check the link in the description".
        5. **TONE**: Punchy, high-energy, and direct. Use short, impactful sentences.

        ### TECHNICAL CONSTRAINTS:
        * {metadata_rule}
        * **ONE PARAGRAPH**: The "script" value in the JSON must be one continuous string with no newlines (\\n).
        * **ESCAPE QUOTES**: If you use quotation marks inside the script, escape them with a backslash (\\").

        ### OUTPUT FORMAT:
        Return ONLY a valid JSON object. No preamble, no conversational filler.
        {{
            "title": "Enter a high-CTR headline here",
            "script": "The full 200-250 word script goes here...",
            {metadata_json_schema}
            "tags": ["tag1", "tag2", "tag3"]
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
            fallback_data = {
                "title": f"{topic} EXPLAINED",
                "script": raw_content.strip(), # Fallback
                "tags": ["ai", "wealth"]
            }
            
            if scout_method == "ai":
                fallback_data["video_prompts"] = [f"Cinematic high quality shot representing {topic}"]
            else:
                fallback_data["keywords"] = [topic] if topic else ["ai"]
                
            return fallback_data