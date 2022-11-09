"""
This file contains:
- Helper function to clean and preprocess raw train data, as downloaded from Spotify Web API (customised for this project only)
- Helper function to clean and preprocess raw test data, as downloaded from Spotify Web API (customised for this project only)
"""

import pandas as pd

# ------------------------------------------------------------------------------
# Clean And Preprocess Train Data
# ------------------------------------------------------------------------------

def clean_and_preprocess_train_data(df):
    """
    Function to clean and preprocess train data
    Steps:
        1. Drop unwanted columns
        2. Drop duplicate track IDs
        3. Convert duration from milliseconds to seconds
        4. Drop rows with invalid time_signature values
        5. Get dummy variables for specific features
        6. Keep tracks with duration 1min-15min
        7. Return train data
    """
    
    print('Cleaning train data...')
    
    # Drop unwanted columns
    df.drop(columns=['song_name', 'artist', 'playlist'], inplace=True)
    
    # Drop duplicate IDs
    df.drop_duplicates(subset=['song_id'], inplace=True, ignore_index=True)
    
    # Convert duration from milliseconds to seconds
    df.duration_ms = df.duration_ms / 1000
    
    # Rename duration column
    df.rename(columns={'duration_ms':'duration'}, inplace=True)
    
    # List with valid time signature values
    valid_values = list(range(3,8))
    
    # Find indices with invalid time signature values
    idx = df[~df.time_signature.isin(valid_values)].index
    
    # Drop rows with invalid time signature values
    df.drop(labels=idx, inplace=True)
    
    # Reset index
    df.reset_index(inplace=True, drop=True)
    
    print('Preprocessing train data...')
    
    # Get dummy variables
    df = pd.get_dummies(df, columns=['key', 'mode', 'time_signature'], drop_first=False)
    
    # Keep tracks with 1min < duration < 15min
    df = df[(df.duration > 60) & (df.duration < 900)]
    
    print('Cleaning and preprocessing train data is done!', end='\n\n')
    
    return df

# ------------------------------------------------------------------------------
# Clean And Preprocess Test Data
# ------------------------------------------------------------------------------
    
def clean_and_preprocess_test_data(df):
    """
    Function to clean and preprocess test data
    Steps:
        1. Convert desired categorical columns to numeric
        2. Drop duplicate track IDs
        3. Convert duration from milliseconds to seconds
        4. Drop rows with invalid time_signature values
        5. Get dummy variables for specific features
        6. Return test data
    """
    
    print('Cleaning test data...')
    
    # Get categorical columns except for song id
    cat_cols = df.drop(columns=['song_id']).select_dtypes(include=['object'])
    
    # Convert categorical columns to numeric
    if len(cat_cols) > 0:
        for column in cat_cols:
            df[column] = pd.to_numeric(df[column])
    
    # Drop duplicate IDs
    df.drop_duplicates(subset=['song_id'], inplace=True, ignore_index=True)
    
    # Convert duration from milliseconds to seconds
    df.duration_ms = df.duration_ms / 1000
    
    # Rename duration column
    df.rename(columns={'duration_ms':'duration'}, inplace=True)
    
    # List with valid time signature values
    valid_values = list(range(3,8))
    
    # Find indices with invalid time signature values
    idx = df[~df.time_signature.isin(valid_values)].index
    
    # Drop rows with invalid time signature values
    df.drop(labels=idx, inplace=True)
    
    # Reset index
    df.reset_index(inplace=True, drop=True)
    
    print('Preprocessing test data...')
    
    # Get dummy variables
    df = pd.get_dummies(df, columns=['key', 'mode', 'time_signature'], drop_first=False)
    
    print('Cleaning and preprocessing test data is done!', end='\n\n')
    
    return df