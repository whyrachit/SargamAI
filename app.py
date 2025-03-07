import streamlit as st
from ui.interface import (
    inject_custom_css,
    display_login_cards,
    display_interface,
    display_playlist_preview
)
from agent.prompt_processor import process_prompt
from spotify.auth import spotify_authenticate
from spotify.playlist import create_spotify_playlist, add_tracks_to_playlist
from youtube.auth import youtube_authenticate
from youtube.playlist import create_youtube_playlist, add_tracks_to_youtube_playlist
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Configure the page
    st.set_page_config(
        page_title="Sargam AI",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Apply custom CSS styling
    inject_custom_css()

    # Initialize session state variables if they don't exist
    if "playlist_details" not in st.session_state:
        st.session_state.playlist_details = None

    # Handle auth redirect parameters
    query_params = st.query_params
    if "code" in query_params:
        st.session_state.yt_code = query_params["code"][0]
        # Clear the URL to avoid reusing the same code
        st.query_params.clear()

    # If no login platform chosen yet, show the login cards
    if "login_platform" not in st.session_state:
        display_login_cards()
        return  # Stop execution until a platform is selected

    # Determine which platform user chose
    platform = st.session_state.login_platform
    
    # Handle authentication for the selected platform
    if platform == "spotify":
        # Authenticate with Spotify if not already done
        if "sp" not in st.session_state:
            sp = spotify_authenticate()
            if sp is None:
                st.stop()
            else:
                st.session_state["sp"] = sp
                st.success("✅ Successfully connected to Spotify!")
    else:  # YouTube Music
        # Authenticate with YouTube Music if not already done
        if "ytmusic" not in st.session_state:
            ytmusic = youtube_authenticate()
            if ytmusic is None:
                st.stop()
            else:
                st.session_state["ytmusic"] = ytmusic
                st.success("✅ Successfully connected to YouTube Music!")

    # Display the main interface for generating a playlist
    # and capture button clicks from the custom UI
    playlist_name, user_prompt, generate_clicked, preview_clicked, save_clicked = display_interface()

    # Handle Generate button click
    if generate_clicked:
        if user_prompt:
            with st.spinner("🎧 Processing your prompt and crafting your personalized playlist..."):
                try:
                    song_suggestions = process_prompt(user_prompt)
                    st.session_state.playlist_details = song_suggestions
                    st.success("✨ Playlist generated successfully!")
                    
                    # Automatically show preview after generation
                    display_playlist_preview(song_suggestions)
                except Exception as e:
                    logger.error(f"Error generating playlist: {str(e)}")
                    st.error("❌ Something went wrong while generating your playlist. Please try again.")
        else:
            st.warning("⚠️ Please enter a description of the playlist you want to create.")

    # Handle Preview button click
    if preview_clicked:
        if st.session_state.playlist_details:
            display_playlist_preview(st.session_state.playlist_details)
        else:
            st.warning("⚠️ No playlist generated yet. Please generate a playlist first.")

    # Handle Save button click
    if save_clicked:
        if st.session_state.playlist_details:
            with st.spinner("📝 Saving your playlist to your account..."):
                name_to_use = playlist_name if playlist_name else "My Sargam AI Playlist"
                description = f"Playlist created with Sargam AI based on: {user_prompt}"
                
                try:
                    # Save to the appropriate platform
                    if platform == "spotify":
                        playlist_id = create_spotify_playlist(
                            st.session_state["sp"],
                            playlist_name=name_to_use,
                            description=description
                        )
                        add_tracks_to_playlist(
                            st.session_state["sp"],
                            playlist_id,
                            st.session_state.playlist_details
                        )
                        st.success("🎉 Playlist successfully saved to your Spotify account!")
                    else:
                        playlist_id = create_youtube_playlist(
                            st.session_state["ytmusic"],
                            playlist_name=name_to_use,
                            description=description
                        )
                        add_tracks_to_youtube_playlist(
                            st.session_state["ytmusic"],
                            playlist_id,
                            st.session_state.playlist_details
                        )
                        st.success("🎉 Playlist successfully saved to your YouTube Music account!")
                    
                    # Add a message with the link (if available)
                    if platform == "spotify":
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 1rem;">
                            <a href="https://open.spotify.com/playlist/{playlist_id}" target="_blank" 
                               style="color: #1DB954; text-decoration: none; font-weight: bold;">
                                Open playlist in Spotify
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    logger.error(f"Error saving playlist: {str(e)}")
                    st.error(f"❌ Error saving your playlist: {str(e)}")
        else:
            st.warning("⚠️ No playlist to save. Please generate a playlist first.")

if __name__ == '__main__':
    main()