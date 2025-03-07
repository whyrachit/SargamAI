import streamlit as st
from ui.interface import (
    display_login_cards,
    display_interface,
    inject_custom_css
)
from agent.prompt_processor import process_prompt
from spotify.auth import spotify_authenticate
from spotify.playlist import create_spotify_playlist, add_tracks_to_playlist
from youtube.auth import youtube_authenticate
from youtube.playlist import create_youtube_playlist, add_tracks_to_youtube_playlist
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    st.set_page_config(
        page_title="Sargam AI",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    inject_custom_css()

    # Capture any query params (e.g., code from YouTube's OAuth)
    query_params = st.query_params  # <--- Updated to the new API
    if "code" in query_params:
        st.session_state.yt_code = query_params["code"][0]

    # If no login platform chosen yet, show the login cards
    if "login_platform" not in st.session_state:
        display_login_cards()
        return  # Stop execution until a platform is selected

    # Determine which platform user chose
    platform = st.session_state.login_platform

    # Authenticate the user
    if platform == "spotify":
        sp = spotify_authenticate()
        if sp is None:
            st.stop()
        else:
            st.session_state["sp"] = sp
            if st.session_state.get('first_login_spotify', True):
                st.success("✅ Successfully connected to Spotify!")
                st.session_state.first_login_spotify = False
    else:  # YouTube Music
        ytmusic = youtube_authenticate()
        if ytmusic is None:
            st.stop()
        else:
            st.session_state["ytmusic"] = ytmusic
            if st.session_state.get('first_login_ytmusic', True):
                st.success("✅ Successfully connected to YouTube Music!")
                st.session_state.first_login_ytmusic = False

    # Display the main interface for generating a playlist
    playlist_name, user_prompt = display_interface()

    if st.button("🎵 Generate Playlist", key="generate"):
        if user_prompt:
            with st.spinner("🎧 Processing your prompt and fetching song recommendations..."):
                song_suggestions = process_prompt(user_prompt)
                st.session_state['playlist_details'] = song_suggestions
            st.success("✨ Playlist generated successfully!")
        else:
            st.warning("⚠️ Please enter a prompt to generate the playlist.")

    if st.button("👀 Preview Playlist", key="preview"):
        if 'playlist_details' in st.session_state and st.session_state['playlist_details']:
            st.subheader("🎵 Generated Playlist Preview")
            for idx, song in enumerate(st.session_state['playlist_details'], start=1):
                st.markdown(
                    f"""
                    <div class="playlist-item">
                        <strong>{idx}. {song.get('name', 'Unknown Song')}</strong><br>
                        <em>by {song.get('artist', 'Unknown Artist')}</em>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("⚠️ No playlist generated yet. Please generate a playlist first.")

    if st.button("💾 Save to Playlist", key="save"):
        if 'playlist_details' in st.session_state and st.session_state['playlist_details']:
            with st.spinner("📝 Creating your playlist..."):
                name_to_use = playlist_name if playlist_name else "My Generated Playlist"
                if platform == "spotify":
                    try:
                        playlist_id = create_spotify_playlist(
                            st.session_state["sp"],
                            playlist_name=name_to_use,
                            description=f"Playlist created using AI: {user_prompt}"
                        )
                        add_tracks_to_playlist(
                            st.session_state["sp"],
                            playlist_id,
                            st.session_state['playlist_details']
                        )
                        st.success("🎉 Playlist successfully created in your Spotify account!")
                    except Exception as e:
                        st.error(f"❌ Error creating Spotify playlist: {str(e)}")
                else:
                    try:
                        playlist_id = create_youtube_playlist(
                            st.session_state["ytmusic"],
                            playlist_name=name_to_use,
                            description=f"Playlist created using AI: {user_prompt}"
                        )
                        add_tracks_to_youtube_playlist(
                            st.session_state["ytmusic"],
                            playlist_id,
                            st.session_state['playlist_details']
                        )
                        st.success("🎉 Playlist successfully created in your YouTube Music account!")
                    except Exception as e:
                        st.error(f"❌ Error creating YouTube Music playlist: {str(e)}")
        else:
            st.warning("⚠️ No playlist to save. Please generate a playlist first.")

if __name__ == '__main__':
    main()
