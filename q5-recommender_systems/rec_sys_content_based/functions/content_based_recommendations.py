#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import csv
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer, util
from torch import Tensor
from random import random, sample
from collections import defaultdict
import time
from math import log2

# ---------------------------------------------------------------------------------------------------
# Function to load and prepare the data for the next steps
# ---------------------------------------------------------------------------------------------------

def load_and_prepare_data(input_file_path:str):

    @dataclass
    class movie:
        title:str
        genre:str
        tags:str
        runtime:int
        director:str
        actors:str
        rating:float
        ryear:int
        prod_house:str
        summary:str
        star_actor:str

    # create an empty dictionary
    # to hold the index of each movie title
    title_index = {}

    # create an empty list
    # to hold each movie object
    # that will be created below
    movies = []

    # open the input file
    # and read each row as a dictionary
    with open(input_file_path, encoding='utf-8') as f:

        # create an empty list
        # to hold the summaries of each movie
        summaries = []

        # loop through rows in the csv file
        for row in csv.DictReader(f):

            # create a new movie object
            # from the data in the row in loop
            new_movie = movie(
                row['title'],
                set([x.strip() for x in row['genre'].split(',')]),
                set([x.strip() for x in row['tags'].split(',')]),
                int(row['runtime']),
                set([x.strip() for x in row['director'].split(',')]),
                set([x.strip() for x in row['actors'].split(',')]),
                float(row['rating']),
                int(row['ryear']),
                row['prod_house'],
                row['summary'],
                row['star_actor']
            )

            # append the summary of the movie to the summaries list
            summaries.append(row['summary'])

            # add the index of the movie to the movie_index dictionary
            title_index[row['title']] = len(movies)

            # apend the new movie object to the movies list
            movies.append(new_movie)

    # load the pretrained model
    sbert = SentenceTransformer('all-MiniLM-L6-v2')

    # encode the summaries using Sentence-BERT
    embedded = sbert.encode(summaries, convert_to_tensor=True)

    # compute the cosine similarity matrix between the summaries
    sum_sim_matrix = util.cos_sim(embedded, embedded)

    # return the list of movies, the title index and the summaries similarity matrix
    return movies, title_index, sum_sim_matrix

# ---------------------------------------------------------------------------------------------------
# Function to compute the similarity between two movies
# ---------------------------------------------------------------------------------------------------

def compute_similarity(title1:str,
                       title2:str,
                       movies:dict,
                       title_index:dict,
                       summaries_sim_matrix:Tensor,
                       weights:dict
                       )->float:
    
    # get the indices of the movies based on their titles
    idx_m1, idx_m2 = title_index[title1], title_index[title2]

    # get the movie objects for the two objects being compared
    m1 = movies[idx_m1]
    m2 = movies[idx_m2]

    # create an empty dictionary
    # to hold the similarity score for each factor between the two movies
    scores = dict()

    # compute genre similarity using jaccard
    scores['genre'] = len(m1.genre.intersection(m2.genre)) / len(m1.genre.union(m2.genre))

    # compute tags similarity using jaccard
    scores['tags'] = len(m1.tags.intersection(m2.tags)) / len(m1.tags.union(m2.tags))

    # compute runtime similarity as the absolute difference between the movies' runtimes,
    # normalized by the maximum and minimum values
    min_runtime = float('inf')
    max_runtime = float('-inf')
    for movie_obj in movies:
        if movie_obj.runtime < min_runtime:
            min_runtime = movie_obj.runtime
        if movie_obj.runtime > max_runtime:
            max_runtime = movie_obj.runtime
    scores['runtime'] = (np.abs(m1.runtime - m2.runtime)) / (max_runtime-min_runtime)

    # compute director similarity using jaccard
    scores['director'] = len(m1.director.intersection(m2.director)) / len(m1.director.union(m2.director))

    # compute director similarity using jaccard
    scores['actors'] = len(m1.actors.intersection(m2.actors)) / len(m1.actors.union(m2.actors))

    # normalized candidate rating
    scores['rating'] = m1.rating / 10

    # release year difference
    scores['ryear'] = abs(m1.ryear-m2.ryear) / 100

    # compute similarity of nominal attribute as
    # s(a,b) == 1 if a == b, 0 otherwise 
    scores['prod_house'] = 1 if m1.prod_house == m2.prod_house else 0
    
    # compute summary similarity using cosine similarity
    scores['summary']=summaries_sim_matrix[idx_m1,idx_m2].numpy()
    
    # compute similarity of nominal attribute as
    # s(a,b) == 1 if a == b, 0 otherwise 
    scores['star_actor'] = 1 if m1.star_actor == m2.star_actor else 0

    # calculate the similarity score for each factor
    # with their corresponding weight from the weights dictionary
    factors = {x:round(scores[x]*weights[x],2) for x in scores}

    # sort the factors based on their score in descending order
    sorted_factors = [factor for factor in sorted(factors.items(), key=lambda x:x[1], reverse=True) if factor[1]>0]

    # calculate the total similarity score for the two movies based on all factors and their weights
    total_similarity = round(np.sum(list(factors.values())),2)

    # return the total similarity and the score of each factor
    return total_similarity, sorted_factors

# ---------------------------------------------------------------------------------------------------
# Function to recommend similar movies given an input movie title
# ---------------------------------------------------------------------------------------------------

def recommend_movies(input_title:str,
                     movies:dict,
                     title_index:dict,
                     summaries_sim_matrix:Tensor,
                     weights:dict,
                     k:int=50
                     )->list:
    
    # create an empty dict to hold the recommendation results
    recommendation_results = dict()

    # loop through each movie in the movies dictionary
    for candidate_movie in movies:

        # compute the similarity between the candidate movie and the input title
        similarity, factor_scores = compute_similarity(candidate_movie.title,
                                                       input_title,
                                                       movies,
                                                       title_index,
                                                       summaries_sim_matrix,
                                                       weights)
        
        # add the similarity score and the factor scores to the recommendation results
        recommendation_results[candidate_movie.title] = (similarity, factor_scores)

    # sort the results by similarity score and return the top k items
    return sorted(recommendation_results.items(), key=lambda x:x[1][0], reverse=True)[:k]

# ---------------------------------------------------------------------------------------------------
# Function to generate fake users
# ---------------------------------------------------------------------------------------------------

def generate_fake_users(movies:list,
                        title_index:dict,
                        summaries_sim_matrix:Tensor,
                        factors:list,
                        num_users:int=10, # number of users to generate
                        num_seed_movies:int=5, # number of random seed movies to choose
                        std_multiplier:float=1.5 # std multiplier to define upper and lower bound
                        ):
    
    @dataclass
    class User:
        seed_movies:list # latent movies that the user likes
        likes:list # known movies that the user has liked
        dislikes:list # known movies that the user has disliked
        weights:dict # user preferences
        like_threshold:float # similarity threshold for liking a movie

    # create an empty list to hold the generated users
    generated_users = list()

    # for each fake user to create
    for i in range(num_users):

        print(f'Creating fake user {i+1}...')

        # create an empty dictionary
        # to hold user preferences for each factor
        weights = dict()

        # for each factor to consider
        for factor in factors:

            # sample a random preference value (weight) between 0 and 1
            weights[factor] = round(random(),2)

        # sample a set number of random movies
        # to use as seed movies for this user
        seed_movies = sample(movies, num_seed_movies)

        """
        - Compute the "like" threshold for this user.
        - If a movie has an above-threshold similarity with (at least) one of the seed movies,
            then we assume that the user will like it.
        - The threshold is defined to be equal to the average similarity of all movies with the seed movies,
            plus <std_multiplier> standard deviation.
        """

        # create an empty dictionary
        # to hold the similarity score
        sim_scores = list()

        # for each seed movie of this user
        for seed_movie in seed_movies:

            # for each other movie
            for candidate_movie in movies:

                # compute the similarity between the candidate movie and the current seed movie
                similarity, _ = compute_similarity(candidate_movie.title,
                                                   seed_movie.title,
                                                   movies,
                                                   title_index,
                                                   summaries_sim_matrix,
                                                   weights)

                # store the similarity score
                sim_scores.append(similarity)

        # compute the "like" threshold for this user (mean + <std_multiplier> standard deviation)
        like_threshold = np.mean(sim_scores) + std_multiplier*np.std(sim_scores)

        # create a new user object with the selected:
        # - seed movies
        # - empty liked movies list
        # - empty disliked movies list
        # - weight factor user preferences
        # - calculated "like" threshold
        generated_users.append(User(seed_movies,
                                    [], # liked movied
                                    [], # disliked movies
                                    weights, # user preferences
                                    round(like_threshold,2)) # "like" threshold
        )

    print()
    print('Fake users have been created successfully!')
    
    # return generated fake users
    return generated_users

# ---------------------------------------------------------------------------------------------------
# Function to make movie recommendations with exploit logic
# ---------------------------------------------------------------------------------------------------

def exploit_simulate(generated_fake_users:list,
                     movies:list,
                     title_index:dict,
                     summaries_sim_matrix:Tensor,
                     factors:list,
                     num_rec_per_user:int=50, # number of recommendations to make
                     num_neighbors:int=10, # number of neighbors to consider when looking for candidates
                     num_liked_sample_size:int=10, # number of liked movies to consider when looking for candidates
                     ):
    
    # create an empty dictionary to hold each user's recommended movies
    total_users_dict = defaultdict()
    
    # loop through fake users
    for c, user in enumerate(generated_fake_users):

        st = time.time() # keep track of start time
        
        # create an empty dictionary to hold current user's recommended movies
        current_user_dict = defaultdict()

        # reset user's likes and dislikes for each iteration
        user.likes = []
        user.dislikes = []

        # initialize estimated weights for each factor
        estimated_weights = {factor:1 for factor in factors}

        # create an empty set to hold the recommender movies for the user
        recommended_movies = set()

        # make <num_rec_per_user> recommendations for this user
        for i in range(num_rec_per_user):

            # initialize a recommended movie to None
            rec_movie = None

            # check if the user has no liked movies yet
            if len(user.likes) == 0:

                # sample a random movie until one is found that hasn't been recommended yet
                while rec_movie == None or rec_movie.title in recommended_movies:
                    rec_movie = sample(movies,1)[0]
            
            else:

                # create an empty dictionary to store candidate movies and their scores
                candidate_movies = defaultdict(float)

                # sample some of the user's liked movies (up to liked_sample_size) to use when searching for candidates
                # we are using only a sample of the user's liked movied for speed 
                sampled_likes = sample(user.likes, min(len(user.likes), num_liked_sample_size))

                # for each sampled liked movie
                for liked_movie in sampled_likes:

                    # recommended some similar movies using the recommend_movies function
                    neighbors = recommend_movies(liked_movie.title,
                                                 movies,
                                                 title_index,
                                                 summaries_sim_matrix,
                                                 estimated_weights,
                                                 num_neighbors)

                    # for each recommended movie
                    for neighbor, metrics in neighbors:

                        # if the movie hasn't been recommender before
                        if neighbor not in recommended_movies:

                            # add the movie's similarity score to the candidate dictionary
                            candidate_movies[neighbor] += metrics[0]
                
                # if no candidates were found
                if len(candidate_movies) == 0:

                    # sample a random movie until one is found that hasn't been recommended yet
                    while rec_movie == None or rec_movie.title in recommended_movies:
                        rec_movie = sample(movies,1)[0]
                
                else:

                    # recommend the movie with the highest score from the candidates
                    rec_movie = movies[title_index[sorted(candidate_movies.items(), key=lambda x:x[1], reverse=True)[0][0]]]
            
            # add the recommended movie to the set of recommended movies
            recommended_movies.add(rec_movie.title)

            # initialize a flag to track if the recommended movie is similar enough to any of the user's seed movies to be liked
            found_seed = False

            # for each seed movie
            for seed_movie in user.seed_movies:

                # compute the similarity between the recommended movie and the seed movie
                similarity, _ = compute_similarity(rec_movie.title,
                                                   seed_movie.title,
                                                   movies,
                                                   title_index,
                                                   summaries_sim_matrix,
                                                   user.weights)
                
                # if the similarity is above the user's like threshold
                if similarity > user.like_threshold:

                    # mark the recommended movie as liked and exit the loop
                    found_seed = True
                    
                    break
            
            # if the movie is similar enough to at least one seed movie
            if found_seed:

                # add the movie to the user's liked movies
                user.likes.append(rec_movie)
                
                # add the movie to the user's recommended movies
                current_user_dict[rec_movie.title] = 'Y'

                print(f' {i+1}/{num_rec_per_user} - {rec_movie.title} [Yes]' if (i+1) < 10 else
                      f'{i+1}/{num_rec_per_user} - {rec_movie.title} [Yes]')
            
            else:

                # add the movie to the user's disliked movies
                user.dislikes.append(rec_movie)

                # add the movie to the user's recommended movies
                current_user_dict[rec_movie.title] = 'N'

                print(f' {i+1}/{num_rec_per_user} - {rec_movie.title} [No]' if (i+1) < 10 else
                      f'{i+1}/{num_rec_per_user} - {rec_movie.title} [No]')

        # add the current user to the total users dictionary
        total_users_dict[f'user_{c+1}'] = current_user_dict

        et = time.time() # keep track of end time
     
        print(f'User {c+1}: {len(user.likes)}/{num_rec_per_user} liked movies ({int(et-st)} secs.)')
        print()

    return total_users_dict

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the recommendations using Normalized Discounted Cumulative Gains (nDCG)
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_nDCG(recommended_items:dict):
    
    # create a list with all item ids
    item_ids = list(recommended_items.keys())
    
    # create a list with respective polarities
    polarity = [v for v in list(recommended_items.values())]
    
    # create a list of tuples with key-value pairs
    data = [(k,v) for k,v in dict(zip(item_ids,polarity)).items()]
    
    # create a dataframe
    df = pd.DataFrame(data, columns=['movie_title','polarity'])
    
    # create a column to store the relevancy score
    df['relevancy_score'] = np.where(df.polarity == 'Y',1,0)
    
    # compute Discounted Cumulative Gain
    DCG = 0
    for i in range(len(df)):
        DCG += df.iloc[i,2] / log2((i+1)+1)
    
    # sort movies by their relevancy score
    # to compute the Ideal Discounted Cumulative Gain
    df = df.sort_values('relevancy_score', ascending=False)
        
    # compute Ideal Discounted Cumulative Gain
    IDCG = 0
    for i in range(len(df)):
        IDCG += df.iloc[i,2] / log2((i+1)+1)
    
    # compute nDCG
    if (DCG == 0) | (IDCG == 0): nDCG = 0
    else: nDCG = DCG/IDCG
    
    # display result
    # print(f'nDCG: {round(nDCG,2)}')
    
    return nDCG

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the recommendations using Mean Reciprocal Rank (MRR)
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_MRR(recommended_items:dict):
    
    # get the number of relevant items recommended
    # in our case, relevant items are considered the liked movies
    num_relevant_items = [v for v in list(recommended_items.values())].count('Y')
    
    # check if there are any relevant items
    # otherwise, MRR = 0
    if num_relevant_items == 0: return 0
    
    # create an empty list
    # to store the reciprocal ranks of the relevant items
    reciprocal_ranks = list()
    
    # loop through recommended items
    # k = movie title
    # v = 'Y' or 'N'
    for i, (k,v) in enumerate(recommended_items.items()):
        
        # check if it is a relevant item ('Y')
        if v == 'Y':
            
            # compute current item reciprocal rank
            item_reciprocal_rank = 1 / (i+1)

            # append to list of reciprocal ranks
            reciprocal_ranks.append(item_reciprocal_rank)
            
    # compute mean reciprocal rank
    MRR = sum(reciprocal_ranks) / num_relevant_items
    
    # round
    # MRR_rounded = round(MRR,2)
    
    # display result
    # print(f'Mean Reciprocal Rank: {MRR_rounded}')
    
    return MRR

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the recommendations using Average Precision (AP)
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_AP(recommended_items:dict):
    
    # get the number of relevant items recommended
    # in our case, relevant items are considered the liked movies
    num_relevant_items = [v for v in list(recommended_items.values())].count('Y')
    
    # check if there are any relevant items
    # otherwise, AP = 0
    if num_relevant_items == 0: return 0
    
    # initialize list
    # to store precisions
    precisions = list()
    
    # relevant item counter
    relevant_so_far = 0
    
    # loop through recommended items
    # k = movie title
    # v = 'Y' or 'N'
    for i, (k,v) in enumerate(recommended_items.items()):
        
        # check if it is a relevant item ('Y')
        if v == 'Y':
            
            # increment
            relevant_so_far += 1
            
            # compute current item precision
            precision = relevant_so_far / (i + 1)
            
            # append to precisions
            precisions.append(precision)
            
    # compute average precision
    AP = sum(precisions) / num_relevant_items
    
    # round to percentage
    # AP_round = int(round(AP,2)*100)
    
    # display result
    # print(f'Average Precision: {AP_round}%')
    
    return AP