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
4. **CTA**: End with a 2-second call to action.
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