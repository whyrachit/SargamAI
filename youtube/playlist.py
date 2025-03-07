# youtube/playlist.py
import difflib
import concurrent.futures
import time
from typing import List, Dict, Any, Optional

def create_youtube_playlist(ytmusic, playlist_name: str, description: str) -> Optional[str]:
    """
    Creates a new playlist in the authenticated user's YouTube Music account.
    
    Args:
        ytmusic: Authenticated YTMusic instance
        playlist_name: Name for the new playlist
        description: Description for the new playlist
        
    Returns:
        str: Playlist ID if successful, None otherwise
    """
    try:
        playlist_id = ytmusic.create_playlist(title=playlist_name, description=description)
        return playlist_id
    except Exception as e:
        print(f"Error creating YouTube Music playlist: {e}")
        return None

def find_youtube_track_id(song: Dict[str, Any], ytmusic) -> Optional[str]:
    """
    Searches for a YouTube Music track based on the song's title and artist.
    
    Args:
        song: Dictionary containing 'name' and 'artist' keys
        ytmusic: Authenticated YTMusic instance
        
    Returns:
        str: YouTube video ID if found, None otherwise
    """
    song_name = song.get('name', '').strip()
    artist_name = song.get('artist', '').strip()
    
    if not song_name:
        return None
        
    query = f"{song_name} {artist_name}".strip()
    
    try:
        results = ytmusic.search(query, filter="songs", limit=5)
        
        if not results:
            # Try with just the song name if no results found
            results = ytmusic.search(song_name, filter="songs", limit=5)
            
        if results:
            # Use fuzzy matching to determine the best candidate
            best_match = None
            highest_ratio = 0
            
            for result in results:
                # Get artist names as a string
                artist_strings = []
                for artist in result.get("artists", []):
                    if isinstance(artist, dict) and "name" in artist:
                        artist_strings.append(artist["name"])
                    elif isinstance(artist, str):
                        artist_strings.append(artist)
                
                candidate_artists = " ".join(artist_strings).lower()
                candidate_title = result.get("title", "").lower()
                
                # Calculate match ratio based on both artist and title
                artist_ratio = difflib.SequenceMatcher(None, artist_name.lower(), candidate_artists).ratio()
                title_ratio = difflib.SequenceMatcher(None, song_name.lower(), candidate_title).ratio()
                combined_ratio = (artist_ratio * 0.4) + (title_ratio * 0.6)  # Weight title more
                
                if combined_ratio > highest_ratio:
                    highest_ratio = combined_ratio
                    best_match = result
            
            # Only return if we have a decent match
            if best_match and highest_ratio > 0.6:
                return best_match.get("videoId")
                
    except Exception as e:
        print(f"Error finding YouTube track ID for '{song_name}' by '{artist_name}': {e}")
        
    return None

def add_tracks_to_youtube_playlist(ytmusic, playlist_id: str, song_recommendations: List[Dict[str, Any]]) -> int:
    """
    Searches for tracks on YouTube Music and adds them to the playlist.
    
    Args:
        ytmusic: Authenticated YTMusic instance
        playlist_id: ID of the playlist to add tracks to
        song_recommendations: List of song dictionaries with 'name' and 'artist' keys
        
    Returns:
        int: Number of songs successfully added to the playlist
    """
    if not playlist_id or not song_recommendations:
        return 0
        
    # Find video IDs for songs
    video_ids = []
    successful_songs = []
    failed_songs = []
    
    # Process in batches to prevent rate limiting
    batch_size = 10
    for i in range(0, len(song_recommendations), batch_size):
        batch = song_recommendations[i:i+batch_size]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_song = {
                executor.submit(find_youtube_track_id, song, ytmusic): song 
                for song in batch
            }
            
            for future in concurrent.futures.as_completed(future_to_song):
                song = future_to_song[future]
                try:
                    video_id = future.result()
                    if video_id:
                        video_ids.append(video_id)
                        successful_songs.append(f"{song.get('name')} by {song.get('artist')}")
                    else:
                        failed_songs.append(f"{song.get('name')} by {song.get('artist')}")
                except Exception as e:
                    print(f"Error processing {song.get('name')}: {e}")
                    failed_songs.append(f"{song.get('name')} by {song.get('artist')}")
        
        # Add a short delay between batches to avoid rate limiting
        if i + batch_size < len(song_recommendations):
            time.sleep(1)
    
    # Add videos to playlist in batches
    successfully_added = 0
    if video_ids:
        batch_size = 50  # YouTube typically limits to 50 items per add operation
        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i+batch_size]
            try:
                status = ytmusic.add_playlist_items(playlist_id, batch)
                successfully_added += len(batch)
            except Exception as e:
                print(f"Error adding tracks to playlist: {e}")
            
            # Add a short delay between batches
            if i + batch_size < len(video_ids):
                time.sleep(1)
    
    # Print summary for debugging
    print(f"Successfully found {len(video_ids)} out of {len(song_recommendations)} songs")
    print(f"Successfully added {successfully_added} songs to playlist {playlist_id}")
    
    return successfully_added