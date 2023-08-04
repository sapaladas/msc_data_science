#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datasketch import MinHash, MinHashLSH
from collections import defaultdict
from math import log2

# ---------------------------------------------------------------------------------------------------
# Function to discretize ratings
# ---------------------------------------------------------------------------------------------------

def discretize_rating(rating:float):
    
    # initialize polarity
    polarity = 'A'
    
    # if rating below 0
    # then define as negative
    if rating < 0: polarity = 'N'
    
    # if rating above 5
    # then define as positive
    if rating > 5: polarity = 'P'
    
    return polarity

# ---------------------------------------------------------------------------------------------------
# Function to create a dictionary with userIDs as keys and jokeIDs and ratings (polarity) as values
# ---------------------------------------------------------------------------------------------------

def load_ratings(df:pd.DataFrame):
    
    # get distinct item IDs
    distinct_item_ids = set(df.joke_id)
    
    # initialize a dict
    # to store the ratings per each item ID
    ratings = dict()
    
    # loop through items
    for item in distinct_item_ids:
        
        # for the item in loop, get the respective users and ratings
        item_ratings = df[df.joke_id == item][['user_id','rating']]
        
        # discretize the ratings and attach them to the item in loop
        ratings[item] = set(zip(item_ratings.user_id, item_ratings.rating.apply(discretize_rating)))
    
    return ratings

# ---------------------------------------------------------------------------------------------------
# Function to create an index for each entity using Locality Sensitive Hashing (LSH)
# ---------------------------------------------------------------------------------------------------

def create_LSH_index(ratings:dict, # itemID as key, userID and rating as values
                     jaccard_threshold:float=0.2, # lower similarity bound for the LSH
                     index_weights:tuple=(0.2,0.8), # false pos and false neg weights
                     num_perm:int=1000, # number of random permutations (hash functions)
                     min_num_ratings:int=10): # entities with less than this many ratings will be ignored
    
    # initialize the LSH index
    index = MinHashLSH(threshold=jaccard_threshold, weights=index_weights, num_perm=num_perm)
    
    # create a dict
    # to store the hashes (min hash signatures) of each entity
    min_hash_signatures = dict()
    
    # initialize a counter
    # to keep track of the number of entities indexed
    counter = 0
    
    # total number of entities to index
    N = len(ratings)
    
    # loop through entities (joke_id) and their values (user_id, rating)
    for entity_id, its_ratings in ratings.items():
        
        # increment
        counter += 1
        
        # view indexing progress
        if counter % 50 == 0:
            # print progress
            print(f' {counter} out of {N} entities indexed.' if counter < 100 else f'{counter} out of {N} entities indexed.')
        if counter == N:
            # print progress
            print(f'{counter} out of {N} entities indexed.')
        
        # check if this entity (e.g., joke) has received enough ratings
        # if not, then continue to the next one
        if len(its_ratings) < min_num_ratings: continue
        
        # create a min hash signature for this entity
        signature = MinHash(num_perm=num_perm)
        
        # for the current entity (e.g., joke)
        # loop through users (that have rated the joke) and polarities (ratings given to the joke)
        for user_id, polarity in its_ratings:
            
            # create a key string
            ks = str(user_id) + '_' + polarity
            
            # add the key string to the min hash signature for this entity
            signature.update(ks.encode('utf8'))
            
        # store the min hash signature for this entity
        min_hash_signatures[entity_id] = signature
        
        # index the entity based on its hash signature
        index.insert(entity_id, signature)
        
    return index, min_hash_signatures

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
# Function to return the neighbors with a certain similarity threshold for a given entity
# ---------------------------------------------------------------------------------------------------

def get_neighbors(item_id:int, # item whose neighbors are to be retrieved
                  ratings:dict, # itemID as key, userID and rating as values
                  index:MinHashLSH, # MinHash indexing
                  hashes:dict, # dict with jokes and their min hash signatures
                  threshold:float=0.2): # lower true similarity bound
    
    # get the candidate neighbors (e.g., joke ids)
    candidates = index.query(hashes[item_id])
    
    # ignore the item ID itself
    neighbor_ids = [c for c in candidates if c != item_id]
    
    # initialize a list
    # to store neighbors and their jaccard similarity
    neighbors = list()
    
    # loop through neighbor ids 
    for neighbor_id in neighbor_ids:
        
        # get item and neighbor sets
        s1 = ratings[item_id]
        s2 = ratings[neighbor_id]
        
        # compute jaccard
        jaccard = jaccard_similarity(s1,s2)
        
        # check if jaccard sim is above threshold
        if jaccard >= threshold:
            
            # store neighbor id and jacc sim
            neighbors.append((neighbor_id,jaccard))
    
    return neighbors

# ---------------------------------------------------------------------------------------------------
# Function to recommend jokes for a given entity
# ---------------------------------------------------------------------------------------------------

def make_recommendations_using_item_based_technique(user_id:int,
                                                    df_ratings:pd.DataFrame,
                                                    df_jokes:pd.DataFrame,
                                                    ratings:dict,
                                                    index:MinHashLSH,
                                                    hashes:dict,
                                                    num_recommendations:int=10):
    
    # get all the jokes rated by this user
    user_jokes = df_ratings[df_ratings.user_id == user_id][['joke_id','rating']]
    
    # convert them to a dict
    user_jokes = dict(zip(user_jokes.joke_id, user_jokes.rating.apply(discretize_rating)))
    
    # create an empty dict
    # to store votes for each joke
    votes = defaultdict(int)
    
    # loop through jokes and their polarity
    for joke_id, polarity in user_jokes.items():
        
        # consider only positively rated jokes
        if polarity != 'P': continue # skip
        
        # get the neighbors of the current joke
        joke_neighbors = get_neighbors(joke_id, ratings, index, hashes)
        
        # loop through neighbors and their similarity value
        for neighbor, sim_value in joke_neighbors:
            
            # add a scaled vote
            # to the current neighbor
            votes[neighbor] += sim_value
    
    # sort neighbor jokes by their scaled votes score
    srt = dict(sorted(votes.items(), key=lambda x:x[1], reverse=True))
    
    # ---------------------------------
    # - Find Jokes to Recommend
    # - Skip Already Rated Jokes
    # ---------------------------------
    
    # create an empty dict
    # to store jokes suggested, but already rated
    already_rated = dict()
    
    # create an empty list
    # to store joke ids to recommend
    to_recommend = dict()
    
    # loop through joke IDs and their scaled votes score
    for i, (joke_id, score) in enumerate(srt.items()):
        
        # get the joke
        joke = df_jokes[df_jokes.joke_id == joke_id]['joke'].values[0]

        # get the polarity
        # if there is no polarity, then None
        joke_polarity = user_jokes.get(joke_id,None)
        
        # get the joke votes score
        joke_score = votes[joke_id]
        
        # get all values together
        joke_values = (joke, joke_polarity, joke_score)
        
        # check if the joke is rated
        # if yes, add it to already rated
        # so that it will not be recommended
        if joke_polarity:
            
            # add joke to already rated
            already_rated[joke_id] = joke_values
            
            # skip
            continue
            
        # store the joke
        to_recommend[joke_id] = joke_values
        
        # check if the max number of recommendations has been reached
        if len(to_recommend) == num_recommendations: break
        
    # sort recommended jokes by their scaled votes score
    to_recommend = dict(sorted(to_recommend.items(), key=lambda x:x[1][2], reverse=True))
    
    return to_recommend, already_rated

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the item-based recommendations using decision support methods
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_decision_support_methods(user_id:int,
                                                            df_ratings:pd.DataFrame,
                                                            already_rated:dict):
    
    # get all the jokes rated by this user
    user_jokes = df_ratings[df_ratings.user_id == user_id][['joke_id','rating']]
    
    # convert them to a dict
    user_jokes = dict(zip(user_jokes.joke_id, user_jokes.rating.apply(discretize_rating)))
    
    # ---------------------------------
    # Precision
    # - Compute number of "P" rated jokes in recommended jokes
    # - Compute total number of rated jokes in recommended jokes
    # - Compute Precision
    # ---------------------------------
    
    # number of "P" rated jokes in recommended jokes
    count_p = [i[1] for i in list(already_rated.values())].count('P')
    
    # total number of rated jokes in recommended jokes
    count_total = len(already_rated)
    
    # compute precision
    precision = count_p / count_total
    
    # round to percentage
    precision_rounded = int(round(precision,2)*100)
    
    # display result
    print(f'Precision: {precision_rounded}% - ({count_p}/{count_total})')
    
    # ---------------------------------
    # Recall
    # - Compute number of "P" rated jokes in recommended jokes
    # - Compute total number of "P" rated jokes in recommended jokes
    # - Compute Recall
    # ---------------------------------
    
    # total number of "P" rated jokes in recommended jokes
    count_total_p = list(user_jokes.values()).count('P')
    
    # compute recall
    recall = count_p / count_total_p
    
    # round to percentage
    recall_rounded = int(round(recall,2)*100)
    
    # display result
    print(f'   Recall: {recall_rounded}% - ({count_p}/{count_total_p})')
    
    return

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the item-based recommendations using Normalized Discounted Cumulative Gains
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_nDCG(already_rated:dict):
    
    # create a list with all item ids
    item_ids = list(already_rated.keys())
    
    # create a list with respective polarities
    polarity = [v[1] for v in list(already_rated.values())]
    
    # create a list of tuples with key-value pairs
    data = [(k,v) for k,v in dict(zip(item_ids,polarity)).items()]
    
    # create a dataframe
    df = pd.DataFrame(data, columns=['joke_id','polarity'])
    
    # create a column to store the relevancy score
    df['relevancy_score'] = np.where(df.polarity == 'P',2,
                                     np.where(df.polarity == 'A',1,
                                              0))
    
    # compute Discounted Cumulative Gain
    DCG = 0
    for i in range(len(df)):
        DCG += df.iloc[i,2] / log2((i+1)+1)
    
    # sort jokes by their relevancy score
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
    print(f'nDCG: {round(nDCG,2)}')
    
    return 

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the item-based recommendations using Mean Reciprocal Rank (MRR)
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_MRR(already_rated:dict):
    
    # get the number of relevant items recommended
    # in our case, relevant items are considered the positively rated jokes
    num_relevant_items = [v[1] for v in list(already_rated.values())].count('P')
    
    # check if there are any relevant items
    # otherwise, MRR = 0
    if num_relevant_items == 0: return 0
    
    # create an empty list
    # to store the reciprocal ranks of the relevant items
    reciprocal_ranks = list()
    
    # loop through recommendations
    # joke_id: (joke, polarity, scaled votes score)
    for i, (jid,(j,p,s)) in enumerate(already_rated.items()):
        
        # check if it is a relevant item ('P')
        if p == 'P':
            
            # compute current item reciprocal rank
            item_reciprocal_rank = 1 / (i+1)

            # append to list of reciprocal ranks
            reciprocal_ranks.append(item_reciprocal_rank)
            
    # compute mean reciprocal rank
    MRR = sum(reciprocal_ranks) / num_relevant_items
    
    # round
    MRR_rounded = round(MRR,2)
    
    # display result
    print(f'Mean Reciprocal Rank: {MRR_rounded}')
    
    return

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the item-based recommendations using Average Precision (AP)
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_using_AP(already_rated:dict):
    
    # get the number of relevant items recommended
    # in our case, relevant items are considered the positively rated jokes
    num_relevant_items = [v[1] for v in list(already_rated.values())].count('P')
    
    # check if there are any relevant items
    # otherwise, AP = 0
    if num_relevant_items == 0: return 0
    
    # initialize list
    # to store precisions
    precisions = list()
    
    # relevant item counter
    relevant_so_far = 0
    
    # loop through recommended items
    # joke_id: (joke, polarity, scaled votes score)
    for i, (jid,(j,p,s)) in enumerate(already_rated.items()):
        
        # check if it is a relevant item ('P')
        if p == 'P':
            
            # increment
            relevant_so_far += 1
            
            # compute current item precision
            precision = relevant_so_far / (i + 1)
            
            # append to precisions
            precisions.append(precision)
            
    # compute average precision
    AP = sum(precisions) / num_relevant_items
    
    # round to percentage
    AP_round = int(round(AP,2)*100)
    
    # display result
    print(f'Average Precision: {AP_round}%')
    
    return