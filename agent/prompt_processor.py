import json
import re
from agno.agent import Agent
from agno.tools.website import WebsiteTools
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
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            return match.group(0).strip()
        return "[]"
    except Exception as e:
        logger.error(f"Error extracting JSON: {e}")
        return "[]"

def process_prompt(user_prompt: str, uploaded_images=None):
    """
    Processes the user prompt to generate a playlist recommendation.
    Now supports image analysis for playlist inspiration.
    
    Args:
        user_prompt: The text prompt from the user
        uploaded_images: Optional list of uploaded image files
    """
    # Base instructions that force a live search call:
    base_instruction = """
    You are an expert music recommendation specialist with real-time web access. Your goal is to provide up-to-date and accurate song recommendations based solely on current web data. Follow these steps:

    Real-Time Search:

    Before recommending any songs, initiate a query using:
    CALL GOOGLE SEARCH TOOL NOW: followed by your specific query 
    also you may scrape the data from the search results to generate recommendations 
    as well if the search results are not sufficient enough.
    (e.g., new releases, trending hits, or artist updates).

    Data Analysis & Verification:

    Analyze the search results and extract key details such as release dates, artist names, genres, 
    chart positions, and relevant news.
    Immediately cite credible sources after each fact.

    Language Detection & Playlist Generation:

    Detect the language from the user's input text.
    If the user hasn’t explicitly mentioned a specific genre or language, 
    generate playlists based on the detected language.
    Recommendation Generation:

    Provide detailed recommendations that include the song title, artist, 
    release date, genre, and any additional interesting context in a clear, structured format.
    Fallback Guidelines:

    If no relevant data is found, state your uncertainty and note that 
    recommendations might not reflect the most recent information.

    """
    
    # Additional concise instructions:
    song_instructions = """
    Instructions:
    - Generate a curated playlist of exactly 20-25 songs.
    - For each song, output an object with exactly two keys: "name" (song title) and "artist" (primary artist).
    - Do not include any extra commentary.
    """
    
    # Image instructions if images are provided
    image_instructions = """
    - When images are provided, first analyze each image.
    - Use Google Search to find more information about what's in the images.
    - Consider the mood, style, colors, objects, and themes in the images when curating songs.
    - Include songs that match the aesthetic or emotional quality of the images.
    """
    
    # Combine instructions based on whether images are provided
    if uploaded_images and len(uploaded_images) > 0:
        description = base_instruction + "\n" + image_instructions + "\n" + song_instructions
    else:
        description = base_instruction + "\n" + song_instructions
    
    try:
        # Create the GoogleSearchTools instance with specific parameters
        search_tool = GoogleSearchTools(
            fixed_max_results=10,
            fixed_language="en",
            timeout=10
        )

        scrape_tool=WebsiteTools()
        
        # Create the agent with the search tool
        agent = Agent(
            model=Gemini(
                api_key=GEMINI_API_KEY,
                id="gemini-2.0-flash-exp",
                temperature=0.9
            ),
            tools=[search_tool,scrape_tool],
            description=description,
            markdown=True,
        )
        
        # Build the enhanced prompt based on whether images are provided
        if uploaded_images and len(uploaded_images) > 0:
            # Process images for Gemini - using the correct format
            # Instead of manually encoding, we'll pass the raw image data
            images = []
            for img in uploaded_images:
                # The agno library expects an image object with 'content' field
                # containing the raw bytes of the image
                images.append({
                    'content': img.getvalue(),  # This passes the raw bytes directly
                    'mime_type': img.type
                })
            
            # Add image analysis and search instructions to the prompt
            enhanced_prompt = f"""
            Given the user request: "{user_prompt}" and {len(images)} uploaded images:
            
            FIRST: Analyze the provided images and identify key themes, colors, moods, and objects.
            
            SECOND: CALL GOOGLE SEARCH TOOL NOW: Search for information about what's in these images.
            
            THIRD: CALL GOOGLE SEARCH TOOL NOW: Search for current song details relevant to both the user query and the image themes.
            
            FINALLY: Based on the search results and image analysis, generate a curated playlist of exactly 20-25 songs.
            Each song must be output as an object with keys "name" and "artist".
            Ensure songs match both the text prompt and visual aesthetic of the images.
            Do not include any additional text.
            """
            
            # Run the agent with text and images
            response = agent.run(enhanced_prompt, images=images)
        else:
            # Original text-only prompt
            enhanced_prompt = f"""
            Given the user request: "{user_prompt}"
            FIRST: CALL GOOGLE SEARCH TOOL NOW: Search for current song details relevant to this query.
            THEN: Based solely on the live search results, generate a curated playlist of exactly 20-25 songs.
            Each song must be output as an object with keys "name" and "artist".
            Do not include any additional text.
            """
            
            # Run with text only
            response = agent.run(enhanced_prompt)
        
        json_text = extract_json(response.content)
        try:
            recommendations = json.loads(json_text)
            if len(recommendations) < 15:
                logger.warning(f"Generated only {len(recommendations)} recommendations. Expected at least 15.")
            logger.info(f"Generated {len(recommendations)} song recommendations")
            return recommendations
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}\nResponse Content: {json_text}")
            return []
    except Exception as e:
        logger.error(f"Error in prompt processing: {e}")
        return []