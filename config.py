import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load secrets from Streamlit (st.secrets) if available,
# otherwise fallback to using environment variables loaded via .env.
try:
    import streamlit as st
    # Spotify credentials
    SPOTIFY_CLIENT_ID = st.secrets["spotify_client_id"]
    SPOTIFY_CLIENT_SECRET = st.secrets["spotify_client_secret"]
    SPOTIFY_REDIRECT_URI = st.secrets["spotify_redirect_uri"]
    # Gemini API key
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    # YouTube Music credentials
    YTMUSIC_CLIENT_ID = st.secrets["ytmusic_client_id"]
    YTMUSIC_CLIENT_SECRET = st.secrets["ytmusic_client_secret"]
    YTMUSIC_REDIRECT_URI = st.secrets["ytmusic_redirect_uri"]
    logger.info("Loaded API credentials from Streamlit secrets")
except (ImportError, KeyError) as e:
    logger.warning(f"Failed to load secrets from Streamlit: {e}")
    from dotenv import load_dotenv
    load_dotenv()
    # Spotify credentials
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
    # Gemini API key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # YouTube Music credentials
    YTMUSIC_CLIENT_ID = os.getenv("YTMUSIC_CLIENT_ID")
    YTMUSIC_CLIENT_SECRET = os.getenv("YTMUSIC_CLIENT_SECRET")
    YTMUSIC_REDIRECT_URI = os.getenv("YTMUSIC_REDIRECT_URI")
    logger.info("Loaded API credentials from environment variables (.env)")

# Check if required credentials are configured.
missing_creds = []
if not SPOTIFY_CLIENT_ID:
    missing_creds.append("SPOTIFY_CLIENT_ID")
if not SPOTIFY_CLIENT_SECRET:
    missing_creds.append("SPOTIFY_CLIENT_SECRET")
if not GEMINI_API_KEY:
    missing_creds.append("GEMINI_API_KEY")
if not YTMUSIC_CLIENT_ID:
    missing_creds.append("YTMUSIC_CLIENT_ID")
if not YTMUSIC_CLIENT_SECRET:
    missing_creds.append("YTMUSIC_CLIENT_SECRET")
if not YTMUSIC_REDIRECT_URI:
    missing_creds.append("YTMUSIC_REDIRECT_URI")

if missing_creds:
    logger.warning(f"Missing required credentials: {', '.join(missing_creds)}")
else:
    logger.info("All required API credentials are configured")
