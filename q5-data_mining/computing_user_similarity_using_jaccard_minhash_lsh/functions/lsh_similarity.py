#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import random
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
# Function to create the hash tables (one hash table per band)
# ---------------------------------------------------------------------------------------------------

def create_hash_tables(signature_matrix:np.ndarray):
    
    # initialize some values needed
    num_users = signature_matrix.shape[0]
    num_bands = signature_matrix.shape[1]
    
    # initialize a list of dictionaries with lenght equal to the number of bands
    # each dictionary will store hash values as keys and lists of user indices as values
    hash_tables = [{} for _ in range(num_bands)]
    
    # loop through the number of users
    for i in range(num_users):
        
        # loop through the number of bands
        for b in range(num_bands):
            
            # get the signature
            # of the current user in the current band
            band = signature_matrix[i, b, :]
            
            # convert the signature
            # of the current user in the current band
            # into a tuple
            hash_value = tuple(band)
            
            # check if the current hash value
            # of the current user in the current band
            # does not exist in the current hash table
            if hash_value not in hash_tables[b]:
                
                # create an empty list
                # for the current hash value
                # for the current band
                hash_tables[b][hash_value] = []
                
            # append the index of the current user
            # to the list for the current hash value
            # for the current band
            hash_tables[b][hash_value].append(i)
            
    return hash_tables

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
# Function to find similar users, and get the number of True Positives and similarity evaluations
# ---------------------------------------------------------------------------------------------------

def find_similar_users(user_movies:dict,
                       signature_matrix:np.ndarray,
                       hash_tables:list,
                       similarity_threshold:float):
    
    # initialize some values needed
    num_users = signature_matrix.shape[0]
    num_bands = signature_matrix.shape[1]
    
    # initialize dict to store pairs of similar users
    similar_users = defaultdict()
    
    # variables to keep track of True Positives and similarity evaluations
    true_pairs = 0
    similarity_evaluations = 0
    
    # loop through the number of users
    for i in range(num_users):
        
        # loop through the number of users
        for j in range(i+1, num_users):
            
            # loop through the number of bands
            for b in range(num_bands):
                
                # get the signature
                # of the current user in the current band
                band = signature_matrix[i, b, :]
                
                # convert the signature
                # of the current user in the current band
                # into a tuple
                hash_value = tuple(band)
                
                # check if the current hash value
                # of the current user in the current band
                # exists in the current hash table
                if hash_value in hash_tables[b]:
                    
                    if j in hash_tables[b][hash_value]:
                        
                        # get the set of movies seen from u1 and u2
                        s1 = set(user_movies[i+1])
                        s2 = set(user_movies[j+1])
                        
                        # compute jaccard similarity
                        similarity = jaccard_similarity(s1,s2)
                        
                        # increment
                        similarity_evaluations += 1
                        
                        # check if user similarity is above threshold
                        if similarity >= similarity_threshold:
                            
                            # increment
                            true_pairs += 1
                            
                            # pair dict key
                            key = str(i+1) + "_" + str(j+1)
                            
                            # store pair similarity
                            similar_users[key] = similarity
                            
                            break
                        
    # sort dict based on similarity score (descending)
    similar_users = sorted(similar_users.items(), key=lambda x:x[1], reverse=True)
    
    return dict(similar_users), true_pairs, similarity_evaluations

# ---------------------------------------------------------------------------------------------------
# Function to compute user similarity using Locality Sensitive Hashing
# ---------------------------------------------------------------------------------------------------

def user_similarity_using_lsh(user_movies:dict,
                              num_bands:int,
                              num_rows_per_band:int,
                              R:int=1000003, # a large prime number
                              similarity_threshold:float=0.5):
    
    # calculate the number of hash functions to generate
    num_hash_functions = num_bands * num_rows_per_band
    
    # generate random hash functions and compute each user's MinHash signature
    user_signatures = generate_random_hash_functions_and_compute_user_signatures(user_movies, num_hash_functions, R)
    
    # create the signature matrix with dimensions: (# users, # bands, # rows per band)
    signature_matrix = np.array(user_signatures).reshape(len(user_signatures),num_bands,num_rows_per_band)
    
    # create the hash tables (one per band)
    hash_tables = create_hash_tables(signature_matrix)
    
    # find similar users, get the number of True Positives and the number of similarity evaluations
    user_similarity_threshold, true_pairs, similarity_evaluations = find_similar_users(user_movies,
                                                                                       signature_matrix,
                                                                                       hash_tables,
                                                                                       similarity_threshold)
    
    return user_similarity_threshold, true_pairs, similarity_evaluations