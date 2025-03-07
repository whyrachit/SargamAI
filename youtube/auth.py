import streamlit as st
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ytmusicapi import YTMusic

def youtube_authenticate():
    """
    Authenticates the user for YouTube Music using OAuth 2.0 via the YouTube Data API.
    Expects the following keys to be set in Streamlit secrets:
      - ytmusic_client_id
      - ytmusic_client_secret
      - ytmusic_redirect_uri

    Once authenticated, it creates a Bearer token header required for YTMusic API requests.
    A token is cached locally in ".ytmusic_token.pkl" to avoid repeated logins.
    """
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    client_config = {
        "installed": {
            "client_id": st.secrets.get("ytmusic_client_id"),
            "client_secret": st.secrets.get("ytmusic_client_secret"),
            "redirect_uris": [st.secrets.get("ytmusic_redirect_uri")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    
    token_file = ".ytmusic_token.pkl"
    credentials = None
    
    # Load credentials from file if available
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            credentials = pickle.load(token)
    
    # If no valid credentials, perform the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                st.error(f"Token refresh failed: {e}")
                credentials = None
        if not credentials:
            flow = InstalledAppFlow.from_client_config(client_config, scopes)
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.session_state.ytmusic_auth_url = auth_url
            st.markdown(f"Please [click here to authorize]({auth_url}) and then paste the full redirect URL below.")
            auth_response = st.text_input("Paste the full redirect URL here:")
            if auth_response:
                try:
                    flow.fetch_token(authorization_response=auth_response)
                    credentials = flow.credentials
                    with open(token_file, "wb") as token:
                        pickle.dump(credentials, token)
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
                    return None

    if not credentials:
        return None

    try:
        # Build headers using Bearer token authentication
        headers = {"Authorization": f"Bearer {credentials.token}"}
        # Instantiate YTMusic with the headers
        ytmusic = YTMusic(headers)
        return ytmusic
    except Exception as e:
        st.error(f"YTMusic authentication failed: {e}")
        return None
