import uuid
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
import logging

logger = logging.getLogger(__name__)

def show_login_button():
    """
    Displays a styled Spotify login button.
    """
    if 'sp_oauth' not in st.session_state:
        st.error("OAuth client not initialized")
        return
    
    auth_url = st.session_state.sp_oauth.get_authorize_url()
    button_html = f"""
    <a href="{auth_url}" target="_self">
        <button style="
            background-color: #1DB954;
            color: white;
            border: none;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            width: 100%;
        ">
            Login to Spotify
        </button>
    </a>
    """
    st.markdown(button_html, unsafe_allow_html=True)

def spotify_authenticate():
    """
    Handles the Spotify OAuth authentication flow in Streamlit.
    Returns an authenticated Spotify client or None if authentication fails.
    """
    # Define the required permissions
    scope = "playlist-modify-private playlist-modify-public user-read-private user-read-email"
    
    # Initialize session state variables if they don't exist
    if 'spotify_cache_path' not in st.session_state:
        st.session_state.spotify_cache_path = f".spotifycache-{uuid.uuid4()}"
    
    # Create OAuth manager if it doesn't exist
    if 'sp_oauth' not in st.session_state:
        try:
            st.session_state.sp_oauth = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=scope,
                cache_path=st.session_state.spotify_cache_path,
                show_dialog=True
            )
            logger.info("Initialized Spotify OAuth manager")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify OAuth: {e}")
            st.error(f"Failed to initialize Spotify authentication: {str(e)}")
            return None
    
    # Check if we already have a valid token in session state
    if 'token_info' in st.session_state:
        try:
            # Test if the token is still valid
            sp = spotipy.Spotify(auth=st.session_state.token_info['access_token'])
            sp.current_user()  # This will fail if the token is invalid
            logger.info("Using existing Spotify token")
            return sp
        except Exception as e:
            logger.warning(f"Existing token is invalid, clearing: {e}")
            st.session_state.pop('token_info', None)
            st.rerun()
    
    # Check for authorization code in URL query parameters
    query_params = st.query_params
    code = query_params.get("code")
    
    if code and "code_processed" not in st.session_state:
        try:
            logger.info("Received authorization code, exchanging for token")
            token_info = st.session_state.sp_oauth.get_access_token(code)
            st.session_state.token_info = token_info
            st.session_state.code_processed = True
            st.rerun()
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            st.error(f"Authentication failed: {str(e)}")
            st.session_state.pop("token_info", None)
            return None
    
    # Check if we have a token after processing code
    token_info = st.session_state.get("token_info")
    
    if not token_info:
        logger.info("No token available, showing login button")
        show_login_button()
        return None
    
    # Check if token is expired and refresh if needed
    if st.session_state.sp_oauth.is_token_expired(token_info):
        try:
            logger.info("Token expired, refreshing")
            token_info = st.session_state.sp_oauth.refresh_access_token(
                token_info['refresh_token']
            )
            st.session_state.token_info = token_info
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            st.error(f"Failed to refresh token: {str(e)}")
            st.session_state.pop("token_info", None)
            show_login_button()
            return None
    
    # Return the authenticated client
    logger.info("Successfully authenticated with Spotify")
    return spotipy.Spotify(auth=token_info["access_token"])