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
    Now deeply analyzes prompt-specific themes and uses search to support those themes.
    
    Args:
        user_prompt: The text prompt from the user
        uploaded_images: Optional list of uploaded image files
    """
    
    # Improved base instruction for better focus
    base_instruction = """
    You are an expert music recommendation specialist with access to real-time web search.
    Your goal is to create a personalized, theme-driven playlist using both the user's input
    and real-time verified information from the internet.

    Never default to generic "trending" songs unless they match the specific mood or theme.
    Focus on extracting the user's **intent** from the prompt and image context — such as mood, genre, emotion, language, time period, and setting.

    Use Google Search as a SUPPORT tool to fetch real-time information about songs, only after extracting themes.
    Search for songs that match the extracted mood and context, NOT just recent songs.
    """

    song_instructions = """
    Final Output Instructions:
    - Curate a playlist of exactly 20–25 songs.
    - Each song must be represented by a JSON object with two keys only: "name" and "artist".
    - Do not include extra commentary, notes, or explanations — only output the JSON array.
    """

    image_instructions = """
    If images are provided:
    - First, analyze each image for key themes, emotional tone, objects, style, colors, or setting.
    - Then combine insights from the images with the user's text to extract a unified aesthetic or vibe.
    - Use that to guide song selection.
    """

    # Merge instructions
    if uploaded_images and len(uploaded_images) > 0:
        description = base_instruction + "\n" + image_instructions + "\n" + song_instructions
    else:
        description = base_instruction + "\n" + song_instructions

    try:
        search_tool = GoogleSearchTools(
            fixed_max_results=10,
            fixed_language="en",
            timeout=10
        )

        scrape_tool = WebsiteTools()

        agent = Agent(
            model=Gemini(
                api_key=GEMINI_API_KEY,
                id="gemini-2.0-flash-exp",
                temperature=0.9
            ),
            tools=[search_tool, scrape_tool],
            description=description,
            markdown=True,
        )

        if uploaded_images and len(uploaded_images) > 0:
            images = [{
                'content': img.getvalue(),
                'mime_type': img.type
            } for img in uploaded_images]

            enhanced_prompt = f"""
            The user said: "{user_prompt}" and uploaded {len(images)} images.

            STEP 1: Analyze the uploaded images for themes, colors, moods, objects, or cultural markers.
            STEP 2: Extract dominant moods/emotions/themes from both the images and user text.
            STEP 3: CALL GOOGLE SEARCH TOOL NOW: Find real-time songs that reflect these extracted themes.
            STEP 4: From results, filter songs based on relevance to mood or aesthetic.
            STEP 5: Generate a list of exactly 20–25 songs, each with "name" and "artist" only.
            DO NOT provide commentary or extra formatting — just output the final JSON.
            """

            response = agent.run(enhanced_prompt, images=images)

        else:
            enhanced_prompt = f"""
            The user said: "{user_prompt}"

            STEP 1: Analyze the user prompt to identify mood, emotion, theme, genre, language, cultural context, time period, or use case (e.g., party, study, heartbreak, road trip).
            STEP 2: CALL GOOGLE SEARCH TOOL NOW: Search for songs that align with these extracted concepts, not just "current" hits.
            STEP 3: Parse the results and select songs that fit thematically.
            STEP 4: Output exactly 20–25 songs, in this JSON format:
            [{{"name": "song title", "artist": "artist name"}}, ...]
            Do not include any other commentary or text.
            """

            response = agent.run(enhanced_prompt)

        json_text = extract_json(response.content)

        try:
            recommendations = json.loads(json_text)
            if len(recommendations) < 15:
                logger.warning(f"Generated only {len(recommendations)} recommendations. Expected at least 15.")
            logger.info(f"Generated {len(recommendations)} song recommendations.")
            return recommendations
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}\nResponse Content: {json_text}")
            return []

    except Exception as e:
        logger.error(f"Error in prompt processing: {e}")
        return []
