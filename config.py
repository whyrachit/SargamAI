import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Fallback: load from .env file.
from dotenv import load_dotenv
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logger.info("Loaded API credentials from environment variables (.env)")

# Check if required credentials are configured.
if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET and GEMINI_API_KEY:
    logger.info("All required API credentials are configured")
else:
    missing_creds = []
    if not SPOTIFY_CLIENT_ID:
        missing_creds.append("SPOTIFY_CLIENT_ID")
    if not SPOTIFY_CLIENT_SECRET:
        missing_creds.append("SPOTIFY_CLIENT_SECRET")
    if not GEMINI_API_KEY:
        missing_creds.append("GEMINI_API_KEY")
    logger.warning(f"Missing required credentials: {', '.join(missing_creds)}")
