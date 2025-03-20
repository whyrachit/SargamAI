import streamlit as st 

def inject_custom_css():
    """
    Updated CSS with minimal playlist preview
    """
    custom_css = """
    <style>
        /* ... keep previous styles unchanged ... */

        /* Compact playlist preview */
        .playlist-preview-container {
            background: #121212;
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        }

        .song-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 16px;
        }

        .song-item {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #181818;
            border-radius: 4px;
            transition: background 0.2s ease;
        }

        .song-item:hover {
            background: #282828;
        }

        .song-index {
            color: var(--spotify-gray);
            font-size: 14px;
            min-width: 40px;
            padding-right: 12px;
        }

        .song-info {
            flex-grow: 1;
            min-width: 0;
        }

        .compact-song-title {
            font-size: 14px;
            color: var(--spotify-white);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .compact-song-artist {
            font-size: 12px;
            color: var(--spotify-gray);
        }

        .song-duration {
            color: var(--spotify-gray);
            font-size: 14px;
            padding-left: 16px;
            min-width: 60px;
            text-align: right;
        }

        .play-button {
            color: var(--spotify-white);
            margin-left: 16px;
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .song-item:hover .play-button {
            opacity: 1;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def display_interface():
    """
    Updated Spotify-like interface
    """
    st.markdown("""
    <div class="logo-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" width="40">
        <h1 style="color: #fffff; margin: 0;">SargamAI</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Wrap main content in a container for better styling
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    with col1:
        playlist_name = st.text_input(
            "🎵 Playlist Name",
            placeholder="My Awesome Playlist",
            help="Give your playlist a unique name"
        )
        user_prompt = st.text_area(
            "🎧 Describe Your Perfect Playlist",
            placeholder=("Example: I am very sad as I did not get selected into Reyansh College of Hotel Management"),
            help="Be specific about the mood, genres, and artists you like",
            height=100
        )
    
    with col2:
        st.markdown("""
        <div class="tips-section">
            <h3 style="color: #fff; margin-bottom: 16px;">💡 Tips for Better Results</h3>
            <div style="color: #b3b3b3; font-size: 14px;">
                <div class="tip-item">🎸 <strong>Specific genres</strong> you love</div>
                <div class="tip-item">🎤 <strong>Favorite artists</strong> for inspiration</div>
                <div class="tip-item">🌟 The <strong>mood or vibe</strong> you want</div>
                <div class="tip-item">📅 <strong>Era or time period</strong> preferences</div>
                <div class="tip-item">🎯 <strong>Occasion</strong> (workout, relaxation, party)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Return values
    return playlist_name, user_prompt

def create_action_buttons():
    """
    Create evenly spaced action buttons in a container
    """
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        generate_clicked = st.button("🎵 Generate Playlist", key="generate", use_container_width=True)
    
    with col2:
        preview_clicked = st.button("👀 Preview Playlist", key="preview", use_container_width=True)
    
    with col3:
        save_clicked = st.button("💾 Save to Spotify", key="save", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return generate_clicked, preview_clicked, save_clicked

def display_playlist_preview(songs):
    """
    Display songs in a compact list format
    """
    st.markdown('<div class="playlist-preview-container">', unsafe_allow_html=True)
    st.subheader("🎵 Generated Playlist Preview")
    
    # Create a compact list for the songs
    st.markdown('<div class="song-list">', unsafe_allow_html=True)
    
    for idx, song in enumerate(songs, 1):
        st.markdown(
            f"""
            <div class="song-item">
                <div class="song-index">{idx}</div>
                <div class="song-info">
                    <div class="compact-song-title">{song.get('name', 'Unknown Song')}</div>
                    <div class="compact-song-artist">{song.get('artist', 'Unknown Artist')}</div>
                </div>
                <button class="play-button">
                    <svg width="24" height="24" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M8 5v14l11-7z"/>
                    </svg>
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    inject_custom_css()
    display_interface()

if __name__ == "__main__":
    main()