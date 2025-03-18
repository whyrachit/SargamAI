import streamlit as st
from ui.interface import display_interface, inject_custom_css,display_playlist_preview,create_action_buttons
from agent.prompt_processor import process_prompt
from spotify.auth import spotify_authenticate
from spotify.playlist import create_spotify_playlist, add_tracks_to_playlist
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    st.set_page_config(
        page_title="Sargam AI",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Inject global CSS and logo for a Spotify-like UI
    inject_custom_css()
    
    # Initialize session state for progress tracking
    if 'processing_state' not in st.session_state:
        st.session_state.processing_state = None
    
    # Authenticate the user with Spotify
    sp = spotify_authenticate()
    if sp is None:
        return
    else:
        st.session_state["sp"] = sp
        if st.session_state.get('first_login', True):
            st.success("✅ Successfully connected to Spotify!")
            st.session_state.first_login = False
            
    # Image upload in the sidebar
    st.sidebar.header("🎨 Upload Images")
    uploaded_images = st.sidebar.file_uploader(
        "Upload images to influence your playlist (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="image_uploader"
    )
    st.session_state.uploaded_images = uploaded_images or []
    
    # Show how many images are uploaded
    if st.session_state.uploaded_images:
        st.sidebar.success(f"✅ {len(st.session_state.uploaded_images)} image(s) uploaded")
    
    # Display UI for playlist prompt and custom playlist name
    playlist_name, user_prompt = display_interface()
    
    # Create action buttons
    generate_clicked, preview_clicked, save_clicked = create_action_buttons()
    
    if generate_clicked:
        if user_prompt:
            with st.spinner("🎧 Processing your prompt and fetching song recommendations..."):
                st.session_state.processing_state = "generating"
                
                # Pass the uploaded images to the prompt processor
                song_suggestions = process_prompt(
                    user_prompt, 
                    uploaded_images=st.session_state.uploaded_images
                )
                
                st.session_state['playlist_details'] = song_suggestions
                st.session_state.processing_state = "generated"
            st.success("✨ Playlist generated successfully!")
        else:
            st.warning("⚠️ Please enter a prompt to generate the playlist.")

    if preview_clicked:
        if 'playlist_details' in st.session_state and st.session_state['playlist_details']:
            display_playlist_preview(st.session_state['playlist_details'])
        else:
            st.warning("⚠️ No playlist generated yet. Please generate a playlist first.")

    if save_clicked:
        if 'playlist_details' in st.session_state and st.session_state['playlist_details']:
            with st.spinner("📝 Creating your playlist on Spotify..."):
                name_to_use = playlist_name if playlist_name else "My Generated Playlist"
                
                # Add image information to the description if images were used
                description = f"Playlist created using AI: {user_prompt}"
                if st.session_state.uploaded_images:
                    description += f" (Created with {len(st.session_state.uploaded_images)} image(s) for inspiration)"
                
                try:
                    playlist_id = create_spotify_playlist(
                        st.session_state["sp"],
                        playlist_name=name_to_use,
                        description=description
                    )
                    add_tracks_to_playlist(
                        st.session_state["sp"],
                        playlist_id,
                        st.session_state['playlist_details']
                    )
                    st.success("🎉 Playlist successfully created in your Spotify account!")
                except Exception as e:
                    st.error(f"❌ Error creating playlist: {str(e)}")
        else:
            st.warning("⚠️ No playlist to save. Please generate a playlist first.")

if __name__ == '__main__':
    main()