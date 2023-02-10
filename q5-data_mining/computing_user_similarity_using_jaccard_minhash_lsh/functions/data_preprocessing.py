#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# ---------------------------------------------------------------------------------------------------
# Function to create a dictionary with users (key) and the movies (values) they have seen
# ---------------------------------------------------------------------------------------------------

def load_movies(df:pd.DataFrame):
    
    # get distinct user ids
    distinct_user_ids = set(df.user_id)
    
    # initialize a dict
    # to store the movies seen from each users
    movies = dict()

    # loop through users
    for user_id in distinct_user_ids:
        
        # for the user in loop, get the respective movies
        user_movies = df[df.user_id == user_id]['movie_id']

        # assign movies the user in loop
        movies[user_id] = user_movies.values
        
    return movies