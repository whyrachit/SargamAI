import streamlit as st

def inject_custom_css():
    """
    Enhanced Spotify-inspired UI with modern styling.
    """
    st.markdown("""
    <style>
        /* Global styling */
        .stApp {
            background: linear-gradient(180deg, #191414 0%, #121212 100%);
            color: #FFFFFF;
        }
        .main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        /* Login Card Styling */
        .login-card {
            border: 2px solid;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            background-color: #121212;
        }
        .login-card img {
            width: 150px;
            margin-bottom: 10px;
        }
        .login-btn {
            border: none;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(
        '<img src="https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_White.png" class="spotify-logo">',
        unsafe_allow_html=True
    )

def display_login_cards():
    """
    Displays two horizontal login cards for Spotify and YouTube Music.
    When a login button is clicked, a session state variable is set accordingly.
    """
    st.markdown("<h2 style='text-align: center;'>Login to Sargam AI</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="login-card" style="border-color: #1DB954;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" alt="Spotify Logo">
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login to Spotify", key="login_spotify_btn", help="Login using your Spotify account"):
            st.session_state.login_platform = "spotify"
    
    with col2:
        st.markdown("""
        <div class="login-card" style="border-color: #FF0000;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/e/e0/YouTube_Music_Logo.png" alt="YouTube Music Logo">
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login to YouTube Music", key="login_ytmusic_btn", help="Login using your YouTube Music account"):
            st.session_state.login_platform = "ytmusic"

def display_interface():
    """
    Displays the main playlist generator interface after login.
    """
    st.title("✨ Sargam AI")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        playlist_name = st.text_input(
            "🎵 Playlist Name",
            placeholder="My Awesome Playlist",
            help="Give your playlist a unique name"
        )
        user_prompt = st.text_area(
            "🎧 Describe Your Perfect Playlist",
            placeholder="Example: I am very sad as I did not get selected into Reyansh College of Hotel Management",
            help="Be specific about the mood, genres, and artists you like",
            height=100
        )
    with col2:
        st.markdown("""
        ### 💡 Tips for Better Results

        - 🎸 Specific genres you love
        - 🎤 Favorite artists for inspiration
        - 🌟 The mood or vibe you want
        - 📅 Era or time period preferences
        - 🎯 Occasion (workout, relaxation, party)
        """)
    
    st.markdown("""
    <div style='background-color: #282828; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
        <strong>🚀 Pro Tips:</strong><br>
        The more specific your description, the better the results! Try including multiple artist references, specific moods or emotions, context for when you'll listen, tempo preferences, and cultural elements.
    </div>
    """, unsafe_allow_html=True)
    
    return playlist_name, user_prompt
