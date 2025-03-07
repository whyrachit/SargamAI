import streamlit as st

def inject_custom_css():
    """
    Enhanced custom CSS for a visually appealing music platform interface with centralized elements.
    """
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #191414 50%, #0F0F0F 100%);
            color: #FFFFFF;
        }
        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: 0 auto;
        }
        .sargam-title {
            text-align: center;
            font-size: 4rem;
            font-weight: 800;
            margin-top: 2rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #1DB954 0%, #FF0000 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }
        .sargam-subtitle {
            text-align: center;
            margin-bottom: 2.5rem;
            font-size: 1.2rem;
            color: #CCCCCC;
        }
        .tips-box {
            background-color: #282828;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_login_cards():
    """
    Displays a centered title and two horizontal login cards for Spotify and YouTube Music.
    """
    st.markdown("<h1 class='sargam-title'>Sargam AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sargam-subtitle'>Your personalized music experience awaits</p>", unsafe_allow_html=True)
    
    # Create two columns for the login cards
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png", width=100)
        if st.button("Login to Spotify", key="login_spotify_btn"):
            st.session_state.login_platform = "spotify"
    with col2:
        # Use an alternative YouTube Music logo URL for better reliability
        st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/YouTube_Music_Logo.png", width=100)
        if st.button("Login to YouTube Music", key="login_ytmusic_btn"):
            st.session_state.login_platform = "ytmusic"

def display_interface():
    """
    Main interface for generating a playlist after user is authenticated.
    """
    st.markdown("<h1 class='sargam-title'>Sargam AI</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #CCCCCC; margin-bottom: 2rem;'>Playlist Generator</h2>", unsafe_allow_html=True)
    
    # Center the input fields
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        playlist_name = st.text_input(
            "🎵 Playlist Name",
            placeholder="My Awesome Playlist",
            help="Give your playlist a unique name"
        )
        user_prompt = st.text_area(
            "🎧 Describe Your Perfect Playlist",
            placeholder="e.g. I'm in a mellow mood and love acoustic singer-songwriters from the 90s...",
            help="Be specific about the mood, genres, and artists you like",
            height=120
        )
    
    st.markdown(
        """
        <div class="tips-box">
            <h3>💡 Tips for Better Results</h3>
            <p>
            🎸 <strong>Include specific genres</strong> &nbsp;•&nbsp; 
            🎤 <strong>List favorite artists</strong> &nbsp;•&nbsp; 
            🌟 <strong>Mention the mood or vibe</strong> &nbsp;•&nbsp; 
            📅 <strong>Specify an era</strong> &nbsp;•&nbsp; 
            🎯 <strong>Indicate the occasion</strong>
            </p>
            <p style="margin-top: 1rem;">
            <strong>🚀 Pro Tip:</strong> The more specific your description, the better the results!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create a container for the action buttons using native Streamlit buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        generate_clicked = st.button("🎵 Generate Playlist", key="generate_btn")
        preview_clicked = st.button("👀 Preview Playlist", key="preview_btn")
        save_clicked = st.button("💾 Save to Playlist", key="save_btn")
    
    return playlist_name, user_prompt, generate_clicked, preview_clicked, save_clicked

def display_playlist_preview(playlist_details):
    """
    Displays a visually appealing preview of the generated playlist.
    """
    st.markdown("<h2 style='text-align: center; margin-top: 2rem;'>🎵 Generated Playlist Preview</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        for idx, song in enumerate(playlist_details, start=1):
            st.markdown(
                f"""
                <div style="background:#333333; padding:1rem; border-radius:8px; margin-bottom:0.75rem; text-align:center;">
                    <strong>{idx}. {song.get('name', 'Unknown Song')}</strong><br>
                    <em>by {song.get('artist', 'Unknown Artist')}</em>
                </div>
                """,
                unsafe_allow_html=True
            )
