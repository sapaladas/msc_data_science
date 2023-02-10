#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from itertools import combinations
from collections import defaultdict

# ---------------------------------------------------------------------------------------------------
# Function to generate random hash functions and compute the MinHash signature of each user
# ---------------------------------------------------------------------------------------------------

def generate_random_hash_functions_and_compute_user_signatures(user_movies:dict,
                                                               num_hash_functions:int,
                                                               R:int):
    
    # generate random a,b integers
    a = random.sample(range(R), num_hash_functions)
    b = random.sample(range(R), num_hash_functions)
    hash_functions = [(ai, bi) for ai, bi in zip(a, b)]
        
    # list to store user signatures
    min_hash_signatures = []
    
    # loop through the sets of movies seen from the users
    for user_set in user_movies.values():
        
        # convert from array to set
        user_set = set(user_set)
        
        # initialize user signature
        signature = [R+1 for _ in range(num_hash_functions)]
        
        # loop through the movies in the current user set
        for item in user_set:
            
            # loop through the a,b combinations
            for i, (ai, bi) in enumerate(hash_functions):
                
                # create a hash function
                # and compute the MinHash signature for the current item
                hash_value = (ai * item + bi) % R
                
                # keep the min signature
                if hash_value < signature[i]:
                    signature[i] = hash_value
                    
        # append current user's MinHash signature
        min_hash_signatures.append(signature)
        
    return min_hash_signatures

# ---------------------------------------------------------------------------------------------------
# Function to estimate the similarity between two users using MinHash signatures
# ---------------------------------------------------------------------------------------------------

def estimated_similarity(user1:int,
                         user2:int,
                         min_hash_signatures:list):
    
    # initialize a variable
    # to hold the number of common outputs from the hash functions
    common_hash_functions = 0
    
    # get the set of signatures from u1 and u2
    s1 = set(min_hash_signatures[user1-1])
    s2 = set(min_hash_signatures[user2-1])
    
    # get their union
    union = s1.union(s2)
    
    # loop through signatures
    for i in range(len(min_hash_signatures[0])):
        
        # check if signatures are the same
        if min_hash_signatures[user1-1][i] == min_hash_signatures[user2-1][i]:
            
            # increment
            common_hash_functions += 1
            
    return common_hash_functions / len(union)

# ---------------------------------------------------------------------------------------------------
# Function to compute user similarity using MinHash signature
# ---------------------------------------------------------------------------------------------------

def user_similarity_using_min_hash_signatures(user_movies:dict,
                                              num_hash_functions:int,
                                              R:int=1000003, # a large prime number
                                              similarity_threshold:float=0.5):
    
    # generate random hash functions and compute each user's MinHash signature
    min_hash_signatures = generate_random_hash_functions_and_compute_user_signatures(user_movies,
                                                                                     num_hash_functions,
                                                                                     R)
    
    # get all possible unique pairs of users
    pairs = list(combinations(list(user_movies.keys()),2))
    
    # initialize a dict
    # to store user similarity
    users_similarity = defaultdict()
    
    # loop through
    # each pair of users
    for u1,u2 in pairs:
        
        # compute the estimated similarity between two users using MinHash signatures
        similarity = estimated_similarity(u1,u2,min_hash_signatures)
        
        # pair dict key
        key = str(u1) + "_" + str(u2)
        
        # store pair similarity
        users_similarity[key] = similarity
        
    # sort dict based on similarity score (descending)
    users_similarity = sorted(users_similarity.items(), key=lambda x:x[1], reverse=True)
    
    # get users with similarity score above threshold
    users_similarity_threshold = dict(filter(lambda x: x[1] >= similarity_threshold, users_similarity))
    
    return dict(users_similarity), users_similarity_threshold

# ---------------------------------------------------------------------------------------------------
# Function to compute the number of FP and FN (against the exact Jaccard similarity)
# ---------------------------------------------------------------------------------------------------

def compute_the_number_of_false_positives_and_false_negatives(jaccard:dict,
                                                              minhash:dict):
    
    # initialize FP and FN variables
    FP, FN = 0, 0
    
    # loop through pairs of users
    for key in jaccard.keys():
        
        # compare similarities
        if jaccard[key] < minhash[key]: FP += 1
        if jaccard[key] > minhash[key]: FN += 1
            
    return FP, FN