import streamlit as st

def inject_custom_css():
    """
    Enhanced custom CSS for a more appealing music platform interface.
    """
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #191414 50%, #0F0F0F 100%);
            color: #FFFFFF;
        }
        
        /* Centered title styling with modern typography */
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
        
        /* Row container for the login cards */
        .login-row {
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            gap: 3rem;
            margin-bottom: 3rem;
        }
        
        /* Individual login card */
        .login-card {
            background-color: #222222;
            border-radius: 12px;
            padding: 2.5rem;
            text-align: center;
            width: 280px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        
        .login-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
        }
        
        .login-card img {
            max-width: 100px;
            margin-bottom: 1.5rem;
            transition: transform 0.3s;
        }
        
        .login-card:hover img {
            transform: scale(1.1);
        }
        
        .login-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }
        
        .login-button {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            font-weight: 600;
            transition: background 0.3s, transform 0.2s;
            width: 80%;
            margin: 0 auto;
            cursor: pointer;
        }
        
        .spotify-button:hover {
            background: #1DB954;
        }
        
        .youtube-button:hover {
            background: #FF0000;
        }
        
        stButton > button {
            display: none;
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
    
    # Create a container to hold both cards side by side
    col1, col2 = st.columns(2)
    
    # Spotify card
    with col1:
        spotify_html = """
        <div class="login-card">
            <img src="https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png" alt="Spotify Logo">
            <h3>Spotify</h3>
            <div class="login-button spotify-button" onclick="document.getElementById('login_spotify_btn').click()">
                Login to Spotify
            </div>
        </div>
        """
        st.markdown(spotify_html, unsafe_allow_html=True)
        if st.button("Login to Spotify", key="login_spotify_btn"):
            st.session_state.login_platform = "spotify"
    
    # YouTube Music card with updated logo
    with col2:
        youtube_html = """
        <div class="login-card">
            <img src="https://music.youtube.com/img/on_platform_logo_dark.svg" alt="YouTube Music Logo">
            <h3>YouTube Music</h3>
            <div class="login-button youtube-button" onclick="document.getElementById('login_ytmusic_btn').click()">
                Login to YouTube Music
            </div>
        </div>
        """
        st.markdown(youtube_html, unsafe_allow_html=True)
        if st.button("Login to YouTube Music", key="login_ytmusic_btn"):
            st.session_state.login_platform = "ytmusic"

def display_interface():
    """
    Main interface for generating a playlist after user is authenticated.
    """
    st.title("Sargam AI Playlist Generator")
    col1, col2 = st.columns([2, 1])
    with col1:
        playlist_name = st.text_input(
            "🎵 Playlist Name",
            placeholder="My Awesome Playlist",
            help="Give your playlist a unique name"
        )
        user_prompt = st.text_area(
            "🎧 Describe Your Perfect Playlist",
            placeholder="e.g. I'm in a mellow mood and love acoustic singer-songwriters from the 90s...",
            help="Be specific about the mood, genres, and artists you like",
            height=100
        )
    with col2:
        st.markdown("""
        ### 💡 Tips for Better Results
        - 🎸 Include specific genres
        - 🎤 List favorite artists
        - 🌟 Mention the mood or vibe
        - 📅 Specify an era or time period
        - 🎯 Indicate the occasion (workout, relaxation, party)
        """)
    st.markdown("""
    <div style='background-color: #282828; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
        <strong>🚀 Pro Tips:</strong><br>
        The more specific your description, the better the results! Try including:
        - Multiple artist references
        - Specific moods or emotions
        - Context for when you'll listen
        - Tempo preferences
        - Language or cultural elements
    </div>
    """, unsafe_allow_html=True)
    return playlist_name, user_prompt

# To use these functions:
# 1. Call inject_custom_css() once at the start of your app
# 2. Call display_login_cards() to show the login interface
# 3. After login, call display_interface() to show the playlist generator