import re
import time
import concurrent.futures
from spotipy.exceptions import SpotifyException
import difflib  # For fuzzy matching
import logging

logger = logging.getLogger(__name__)

def create_spotify_playlist(sp, playlist_name: str, description: str):
    """
    Creates a new playlist in the authenticated user's Spotify account.
    """
    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=description)
        logger.info(f"Created Spotify playlist: {playlist_name}")
        return playlist['id']
    except SpotifyException as e:
        logger.error(f"Failed to create Spotify playlist: {e}")
        raise

def is_valid_spotify_id(spotify_id: str) -> bool:
    """
    Checks if the given spotify_id is a valid Spotify track ID.
    Spotify track IDs are typically 22 characters in base62.
    """
    return bool(re.fullmatch(r'[0-9A-Za-z]{22}', spotify_id))

def playlist_add_items_with_retry(sp, playlist_id, track_uris, max_retries=3, batch_size=50):
    """
    Adds track URIs to a playlist with retry logic and batch processing.
    Spotify API has a limit of 100 tracks per request, but we use a smaller batch size for reliability.
    """
    # Process in batches to avoid API limits
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        attempt = 0
        while attempt < max_retries:
            try:
                sp.playlist_add_items(playlist_id, batch)
                logger.info(f"Added batch of {len(batch)} tracks to playlist")
                break
            except SpotifyException as e:
                if e.http_status in [429, 502, 503, 504]:
                    # Rate limiting or server error, apply exponential backoff
                    retry_after = int(e.headers.get("Retry-After", "5"))
                    wait_time = retry_after * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited or server error. Retrying in {wait_time}s. Attempt {attempt+1}/{max_retries}")
                    time.sleep(wait_time)
                    attempt += 1
                else:
                    logger.error(f"Spotify API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error adding tracks: {e}")
                attempt += 1
                if attempt >= max_retries:
                    raise Exception(f"Failed to add tracks after {max_retries} attempts: {e}")
                time.sleep(5 * attempt)  # Simple backoff for other errors

def find_track_uri(song: dict, sp):
    """
    Searches for a Spotify track URI based on the song's title and artist.
    Uses an exact match first, and falls back to a fuzzy match approach.
    """
    song_name = song.get('name', '').strip()
    artist_name = song.get('artist', '').strip()
    
    if not song_name or not artist_name:
        logger.warning(f"Missing song name or artist: {song}")
        return None
    
    try:
        # Exact match query first (most reliable)
        query = f'track:"{song_name}" artist:"{artist_name}"'
        result = sp.search(q=query, type='track', limit=1)
        tracks = result.get('tracks', {}).get('items', [])
        
        # If no exact match, try a broader search with fuzzy matching
        if not tracks:
            query = f"{song_name} {artist_name}"
            result = sp.search(q=query, type='track', limit=10)
            tracks = result.get('tracks', {}).get('items', [])
            
            # Use fuzzy matching to find the best candidate
            if tracks:
                best_match = None
                highest_ratio = 0
                for track in tracks:
                    # Get all artists for this track
                    artists = [artist["name"].lower() for artist in track["artists"]]
                    track_name = track["name"].lower()
                    
                    # Calculate similarity score for title
                    title_ratio = difflib.SequenceMatcher(None, song_name.lower(), track_name).ratio()
                    
                    # Calculate similarity for artists (check each artist)
                    artist_ratio = 0
                    for track_artist in artists:
                        current_ratio = difflib.SequenceMatcher(None, artist_name.lower(), track_artist).ratio()
                        artist_ratio = max(artist_ratio, current_ratio)
                    
                    # Combined score (weight title slightly more than artist)
                    combined_ratio = (title_ratio * 0.6) + (artist_ratio * 0.4)
                    
                    if combined_ratio > highest_ratio:
                        highest_ratio = combined_ratio
                        best_match = track
                
                # Only use the match if it's reasonably close
                if highest_ratio > 0.5:
                    tracks = [best_match]
                else:
                    tracks = []
        
        if tracks:
            track_uri = tracks[0]['uri']
            if track_uri.startswith("spotify:track:"):
                logger.info(f"Found track: {song_name} by {artist_name}")
                return track_uri
            
        logger.warning(f"No matching track found for: {song_name} by {artist_name}")
        return None
    except Exception as e:
        logger.error(f"Error finding track URI for '{song_name}' by '{artist_name}': {e}")
        return None

def add_tracks_to_playlist(sp, playlist_id: str, song_recommendations: list):
    """
    Searches for tracks on Spotify based on the song recommendations and adds them to the playlist.
    Uses parallelization for improved performance.
    """
    if not song_recommendations:
        logger.warning("No song recommendations provided")
        return
    
    track_uris = []
    songs_to_search = []
    
    # Check if any recommendations contain spotify_id
    for song in song_recommendations:
        spotify_id = song.get('spotify_id', '').strip()
        if spotify_id and is_valid_spotify_id(spotify_id):
            track_uri = f"spotify:track:{spotify_id}"
            track_uris.append(track_uri)
        else:
            songs_to_search.append(song)
    
    # Use parallel processing to find tracks
    if songs_to_search:
        logger.info(f"Searching for {len(songs_to_search)} tracks...")
        found_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_song = {executor.submit(find_track_uri, song, sp): song for song in songs_to_search}
            for future in concurrent.futures.as_completed(future_to_song):
                track_uri = future.result()
                if track_uri:
                    track_uris.append(track_uri)
                    found_count += 1
        
        logger.info(f"Found {found_count} out of {len(songs_to_search)} tracks")
    
    if track_uris:
        logger.info(f"Adding {len(track_uris)} tracks to playlist {playlist_id}")
        playlist_add_items_with_retry(sp, playlist_id, track_uris)
    else:
        logger.warning("No tracks found to add to playlist")