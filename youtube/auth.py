# youtube/auth.py
import uuid
import streamlit as st
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import (
    YTMUSIC_CLIENT_ID,
    YTMUSIC_CLIENT_SECRET,
    YTMUSIC_REDIRECT_URI
)
from google.oauth2.credentials import Credentials
from ytmusicapi import YTMusic

def youtube_authenticate():
    """
    Authenticates the user for YouTube Music using OAuth 2.0 via the YouTube Data API.
    Expects ytmusic_client_id, ytmusic_client_secret, ytmusic_redirect_uri in config or secrets.
    """
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    
    # Prepare a client_config dict for InstalledAppFlow
    client_config = {
        "installed": {  # Changed from "web" to "installed" for InstalledAppFlow
            "client_id": YTMUSIC_CLIENT_ID,
            "client_secret": YTMUSIC_CLIENT_SECRET,
            "redirect_uris": [YTMUSIC_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    # Use a unique file for caching tokens
    if 'youtube_cache_path' not in st.session_state:
        st.session_state.youtube_cache_path = f".ytmusic_token_{uuid.uuid4()}.pkl"
    
    # Check if we already have valid credentials
    credentials = None
    if os.path.exists(st.session_state.youtube_cache_path):
        with open(st.session_state.youtube_cache_path, "rb") as token_file:
            try:
                credentials = pickle.load(token_file)
                if credentials and credentials.expired and credentials.refresh_token:
                    try:
                        credentials.refresh(Request())
                    except Exception:
                        credentials = None
            except Exception:
                # Handle corrupt token file
                credentials = None
                os.remove(st.session_state.youtube_cache_path)
    
    # If not valid, start the flow
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_config(client_config, scopes)
        flow.redirect_uri = YTMUSIC_REDIRECT_URI  # Explicitly set redirect_uri
        
        auth_url, _ = flow.authorization_url(  # Fixed syntax error
            prompt='consent',
            include_granted_scopes='true',
            access_type='offline'
        )
        
        # Show a direct link for the user to initiate OAuth
        if "yt_code" not in st.session_state:
            st.markdown(
                f"<a style='color: white; font-weight: bold;' href='{auth_url}'>"
                "Click here to log in with YouTube Music</a>",
                unsafe_allow_html=True
            )
            
            # Add a text input for the user to enter the auth code
            code = st.text_input("After authorizing, paste the authorization code here:", key="youtube_auth_code")
            if code:
                st.session_state.yt_code = code
                st.experimental_rerun()
            
            return None
        else:
            # The user has returned with a code
            try:
                flow.fetch_token(code=st.session_state.yt_code)
                credentials = flow.credentials
                # Cache the credentials
                with open(st.session_state.youtube_cache_path, "wb") as token_file:
                    pickle.dump(credentials, token_file)
            except Exception as e:
                st.error(f"Failed to get YouTube credentials: {e}")
                # Clear the code so the user can try again
                if "yt_code" in st.session_state:
                    del st.session_state.yt_code
                return None
    
    # At this point, we have valid credentials
    try:
        # Use header_auth=True to ensure proper authentication with tokens
        ytmusic = YTMusic()
        ytmusic.setup(credentials.token)
        return ytmusic
    except Exception as e:
        st.error(f"YTMusic authentication failed: {e}")
        return None