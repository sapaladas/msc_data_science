"""
This file contains:
- Helper function for Spotify Client Authentication
- Helper function to download tracks and audio features from a playlist
- Helper function to download tracks and audio features from multiple playlists
- Helper function to download audio features for a given list of track IDs
"""

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ------------------------------------------------------------------------------
# Spotify Client Authentication
# ------------------------------------------------------------------------------

def authenticate_client():
    """
    Function for Spotify Client Authentication
    Steps:
        1. Get client credentials from developer.spotify.com/dashboard
        2. Initialize client credentials manager
        3. Create a spotipy instance
    """
    
    # Initialize client credentials
    CLIENT_ID = "XXXXXXXXXX"
    CLIENT_SECRET = "XXXXXXXXXX"
    
    # Initialize client credentials manager
    client_credentials = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    
    # Create a spotipy instance
    sp = spotipy.Spotify(client_credentials_manager = client_credentials)
    
    print('Client Authentication Successful!', end='\n\n')
    
    return sp

# ------------------------------------------------------------------------------
# Get Audio Features (Given a Spotify Playlist)
# ------------------------------------------------------------------------------

def get_audio_features(creator, playlist_id, sp):
    """
    Function to get the audio features for every track in a given playlist
    Steps:
        1. Define desired features
        2. Loop through every track in the playlist, collect and store its audio features
        3. Return a dataframe with all tracks and their audio features
    """
    
    # Define desired features
    playlist_features_list = ['song_id', 'song_name', 'artist',
                              'acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key',
                              'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'time_signature', 'valence']
    
    # Create empty df
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
    # Download all playlist tracks    
    results = sp.user_playlist_tracks(creator, playlist_id)
    playlist = results['items']
    
    while results['next']:
        results = sp.next(results)
        playlist.extend(results['items'])
    
    # Loop through every track in the playlist
    for i, track in enumerate(playlist):
        
        if track['track'] is None:
            # print('Track not found.')
            continue
        else:            
            # Create empty dict
            playlist_features = {}
            
            # Get song id
            if track['track']['id'] is None:
                continue
            else:
                playlist_features['song_id'] = track['track']['id']
                
            # Get song name
            if track['track']['name'] is None:
                continue
            else:
                playlist_features['song_name'] = track['track']['name']
                
            # Get artist
            if track['track']['artists'][0]['name'] is None:
                continue
            else:
                playlist_features['artist'] = track['track']['artists'][0]['name']
            
            # Get audio features 
            audio_features = sp.audio_features(playlist_features['song_id'])[0]
            if audio_features is None:
                # print(f'Getting track: {i+1}/{len(playlist)} - Audio features not found.')
                continue
            else:
                # print(f'Getting track: {i+1}/{len(playlist)}')
                for feature in playlist_features_list[3:16]:
                    playlist_features[feature] = audio_features[feature]
    
            # Create df to store audio features in each iteration
            track_df = pd.DataFrame(playlist_features, index = [0])
 
            # Concat dfs
            playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)
    
    return playlist_df

# ------------------------------------------------------------------------------
# Get Audio Features (Given a Set of Playlists)
# ------------------------------------------------------------------------------

def download_multiple_playlists(playlist_dict, sp):
    """
    Function to download tracks and their audio features from a set of playlists
    Steps:
        1. Loop through every playlist
        2. Call function to get the audio features for each track in each playlist
        3. Return a dataframe with all tracks and their audio features
    """
    
    # Loop through every playlist in the dictionary
    for i, (key, val) in enumerate(playlist_dict.items()):
        
        print(f'Downloading "{key}"...')
        
        # Call function to get audio features
        playlist_df = get_audio_features(*val, sp)
        
        # Store the playlist name
        playlist_df['playlist'] = key
        
        # Create df to store info
        if i == 0:
            playlist_dict_df = playlist_df
        else:
            playlist_dict_df = pd.concat([playlist_dict_df, playlist_df], ignore_index = True)
            
        print(f'Downloading "{key}"... Done!', end='\n\n')
            
    return playlist_dict_df

# ------------------------------------------------------------------------------
# Get Audio Features (Given a List of Track IDs)
# ------------------------------------------------------------------------------

def get_audio_features_with_ids(track_ids, sp):
    """
    Function to get the audio features for every track given a list of track IDs
    Steps:
        1. Define desired features
        2. Loop through every track ID, collect and store its audio features
        3. Return a dataframe with all track IDs and their audio features
    """
    
    # Define desired features
    playlist_features_list = ['song_id',
                              'acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key',
                              'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'time_signature', 'valence']
    
    # Create empty df
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
    print('Getting audio features...')
    
    # Loop through every track id in the list
    for i, track_id in enumerate(track_ids):
        
        if track_id is None:
            # print('Track ID not found.')
            continue
        else:            
            # Create empty dict
            playlist_features = {}
            
            # Store track ID
            playlist_features['song_id'] = track_id
            
            # Get audio features 
            audio_features = sp.audio_features(track_id)[0]
            if audio_features is None:
                # print(f'Getting track: {i+1}/{len(track_ids)} - Audio features not found.')
                continue
            else:
                # print(f'Getting track: {i+1}/{len(track_ids)}')
                for feature in playlist_features_list[1:14]:
                    playlist_features[feature] = audio_features[feature]
    
            # Create df to store audio features in each iteration
            features_df = pd.DataFrame(playlist_features, index = [0])
            
            # Concat dfs
            playlist_df = pd.concat([playlist_df, features_df], ignore_index = True)
            
    print('Getting audio features... Done!', end='\n\n')

    return playlist_df