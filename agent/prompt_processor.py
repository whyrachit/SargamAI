import json
import re
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.googlesearch import GoogleSearchTools
from config import GEMINI_API_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_json(raw_text: str) -> str:
    """
    Robustly extract a JSON array from raw_text.
    Uses a simple search for the first occurrence of a bracketed array.
    """
    try:
        # Improved regex pattern to better match JSON arrays
        match = re.search(r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]', raw_text, re.DOTALL)
        if match:
            return match.group(0).strip()
        # Try an alternate approach if first pattern fails
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            return match.group(0).strip()
        logger.warning("No JSON array found in the response")
        return "[]"
    except Exception as e:
        logger.error(f"Error extracting JSON: {e}")
        return "[]"

def process_prompt(user_prompt: str):
    """
    Processes the user prompt to generate a playlist recommendation.
    Uses the Google Search tool to fetch live song data and enforces output formatting.
    """
    # Base instructions with clear formatting requirements
    base_instruction = """
    You are an expert music curator with real-time web access.
    BEFORE generating any song recommendations, you MUST use the provided Google Search tool 
    to look up the most recent song details. DO NOT rely on internal knowledge.
    Use the tool call command: "CALL GOOGLE SEARCH TOOL NOW:" followed by your query.
    """
    
    # Explicit JSON formatting instructions
    song_instructions = """
    Instructions:
    - Generate a curated playlist of exactly 20-25 songs.
    - Return ONLY a JSON array with objects containing exactly two keys: "name" (song title) and "artist" (primary artist).
    - Ensure all response is properly formatted as a valid JSON array.
    - Do not include any extra commentary or text outside the JSON array.
    - Example format: [{"name":"Song Title", "artist":"Artist Name"}, {...}]
    """
    
    description = base_instruction + "\n" + song_instructions
    
    try:
        # Create the GoogleSearchTools with retry capability
        search_tool = GoogleSearchTools(
            fixed_max_results=10,
            fixed_language="en",
            timeout=15  # Increased timeout for more reliable results
        )
        
        # Create the agent with a lower temperature for more consistent outputs
        agent = Agent(
            model=Gemini(
                api_key=GEMINI_API_KEY,
                id="gemini-2.0-flash-exp",  # Using flash for faster responses
                temperature=0.1
            ),
            tools=[search_tool],
            description=description,
            markdown=True,
        )
        
        # Enhanced prompt with explicit JSON output instructions
        enhanced_prompt = f"""
        Given the user request: "{user_prompt}"
        
        FIRST: CALL GOOGLE SEARCH TOOL NOW: Search for current songs that match this query: {user_prompt}
        
        THEN: Based solely on the search results, generate a curated playlist of 20-25 songs.
        
        IMPORTANT: Return ONLY a JSON array of song objects with the format:
        [
          {{"name": "Song Title 1", "artist": "Artist Name 1"}},
          {{"name": "Song Title 2", "artist": "Artist Name 2"}},
          ...
        ]
        
        Do not include any explanatory text, commentary, or additional fields.
        """
        
        # Set a retry mechanism for agent runs
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = agent.run(enhanced_prompt)
                json_text = extract_json(response.content)
                recommendations = json.loads(json_text)
                
                # Verify we have a valid result
                if isinstance(recommendations, list) and len(recommendations) >= 15:
                    logger.info(f"Successfully generated {len(recommendations)} song recommendations")
                    return recommendations
                else:
                    logger.warning(f"Generated only {len(recommendations) if isinstance(recommendations, list) else 0} recommendations. Expected at least 15.")
                    if attempt < max_retries:
                        logger.info(f"Retrying... Attempt {attempt + 2}/{max_retries + 1}")
                        continue
                    return recommendations if isinstance(recommendations, list) else []
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error on attempt {attempt + 1}: {e}\nResponse Content: {json_text}")
                if attempt < max_retries:
                    continue
                return []
            except Exception as e:
                logger.error(f"Error in agent run on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    continue
                return []
    except Exception as e:
        logger.error(f"Error in prompt processing: {e}")
        return []