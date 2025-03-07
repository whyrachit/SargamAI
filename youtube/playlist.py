import difflib
import concurrent.futures
from ytmusicapi import YTMusic

def create_youtube_playlist(ytmusic, playlist_name: str, description: str):
    """
    Creates a new playlist in the authenticated user's YouTube Music account.
    If the API doesn't allow creating an empty playlist, you may need to add a dummy track.
    """
    # Attempt to create an empty playlist
    playlist_id = ytmusic.create_playlist(playlist_name, description, [])
    return playlist_id

def find_youtube_track_id(song: dict, ytmusic):
    """
    Searches for a YouTube Music track based on the song's title and artist.
    Returns the video's ID if found.
    """
    song_name = song.get('name', '').strip()
    artist_name = song.get('artist', '').strip()
    query = f"{song_name} {artist_name}"
    try:
        results = ytmusic.search(query, filter="songs")
        if results:
            # Use fuzzy matching to determine the best candidate
            best_match = None
            highest_ratio = 0
            for result in results:
                candidate_artists = result.get("artists", [])
                candidate_str = " ".join(candidate_artists).lower() if candidate_artists else ""
                ratio = difflib.SequenceMatcher(None, artist_name.lower(), candidate_str).ratio()
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match = result
            if best_match:
                return best_match.get("videoId")
    except Exception as e:
        print(f"Error finding YouTube track ID for '{song_name}' by '{artist_name}': {e}")
    return None

def add_tracks_to_youtube_playlist(ytmusic, playlist_id: str, song_recommendations: list):
    """
    Searches for tracks on YouTube Music based on the song recommendations and adds them to the playlist.
    Utilizes parallel processing for improved performance.
    """
    video_ids = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_song = {executor.submit(find_youtube_track_id, song, ytmusic): song for song in song_recommendations}
        for future in concurrent.futures.as_completed(future_to_song):
            video_id = future.result()
            if video_id:
                video_ids.append(video_id)
    if video_ids:
        ytmusic.add_playlist_items(playlist_id, video_ids)
