#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from itertools import combinations
from collections import defaultdict

# ---------------------------------------------------------------------------------------------------
# Function to compute the Jaccard coefficient between two sets
# ---------------------------------------------------------------------------------------------------

def jaccard_similarity(set1:set,
                       set2:set):
    
    # get union and intersection
    union = set1.union(set2)
    intersection = set1.intersection(set2)
    
    # compute jaccard coefficient
    jacc_coef = len(intersection) / len(union)
    
    return jacc_coef

# ---------------------------------------------------------------------------------------------------
# Function to compute user similarity using Jaccard coefficient
# ---------------------------------------------------------------------------------------------------

def user_similarity_using_jaccard_coefficient(user_movies:dict,
                                              similarity_threshold:float=0.5):
    
    # get all possible unique pairs of users
    pairs = list(combinations(list(user_movies.keys()),2))
    
    # initialize a dict
    # to store user similarity
    users_similarity = defaultdict()
    
    # loop through
    # each pair of users
    for u1,u2 in pairs:
        
        # get the set of movies seen from u1 and u2
        s1 = set(user_movies[u1])
        s2 = set(user_movies[u2])
        
        # compute jaccard similarity
        jaccard = jaccard_similarity(s1,s2)
        
        # pair dict key
        key = str(u1) + "_" + str(u2)
        
        # store pair similarity
        users_similarity[key] = jaccard
        
    # sort dict based on similarity score (descending)
    users_similarity = sorted(users_similarity.items(), key=lambda x:x[1], reverse=True)
    
    # get users with similarity score above threshold
    users_similarity_threshold = dict(filter(lambda x: x[1] >= similarity_threshold, users_similarity))
    
    return dict(users_similarity), users_similarity_threshold

# ---------------------------------------------------------------------------------------------------
# Function to get the movies seen from the most similar pair of users
# ---------------------------------------------------------------------------------------------------

def get_the_movies_of_the_most_similar_pair_of_users(movies:pd.DataFrame,
                                                     users_similarity:dict,
                                                     user_movies:dict):
    
    # get the most similar pair of users
    most_similar_pair = list(users_similarity.items())[0]
    
    # get the two user IDs
    u1 = int(most_similar_pair[0].split('_')[0])
    u2 = int(most_similar_pair[0].split('_')[1])
    
    # get the movie IDs seen from u1 and u2
    m1 = set(user_movies[u1])
    m2 = set(user_movies[u2])
    
    # get the common movies seen
    common_movies = m1.union(m2)
    
    # print
    print(f'Most similar pair of users: {u1} - {u2}')
    print()
    print('Movies seen from the most similar pair of users:')
    print()
    for movie_id in sorted(common_movies):
        print(f' {movie_id}: {movies[movies.movie_id == movie_id].title.values[0]}' if movie_id < 1000 else \
              f'{movie_id}: {movies[movies.movie_id == movie_id].title.values[0]}')
    
    return