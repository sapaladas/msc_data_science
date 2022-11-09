"""
This file contains:
- Main function to download tracks and audio features from multiple playlists
- Main function to download audio features for a given list of track IDs
"""

from functions.spotify_source import authenticate_client
from functions.spotify_source import download_multiple_playlists
from functions.spotify_source import get_audio_features_with_ids

# ------------------------------------------------------------------------------
# Download Tracks And Audio Features From Multiple Playlists 
# ------------------------------------------------------------------------------

def download_playlists(playlist_dict):
    """
    Main function to download tracks and audio features from multiple playlists
    Steps:
        1. Authenticate Spotify Client
        2. Call function to download and return tracks and audio features from the playlists provided
        3. Return a dataframe with all tracks and audio features 
    """
    
    # Client authentication
    sp = authenticate_client()
    
    # Download track audio features from multiple playlists
    all_tracks = download_multiple_playlists(playlist_dict, sp)
    
    return all_tracks

# ------------------------------------------------------------------------------
# Download Audio Features Given a List of Track IDs
# ------------------------------------------------------------------------------

def download_track_features_with_ids(track_ids):
    """
    Main function to download audio features given a list of track IDs
    Steps:
        1. Authenticate Spotify Client
        2. Call function to download and return the audio features of the provided track IDs
        3. Return a dataframe with all track IDs and their audio features
    """
    
    # Client authentication
    sp = authenticate_client()
    
    # Download track features given a list of IDs
    track_features = get_audio_features_with_ids(track_ids, sp)
    
    return track_features