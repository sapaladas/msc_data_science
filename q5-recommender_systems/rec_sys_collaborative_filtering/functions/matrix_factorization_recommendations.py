#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.metrics import mean_squared_error

# ---------------------------------------------------------------------------------------------------
# Function to make recommendations using matrix factorization (SVD)
# ---------------------------------------------------------------------------------------------------

def make_recommendations_using_matrix_factorization(svd, # SVD class from surprise library
                                                    user_id:int,
                                                    df_ratings_up:pd.DataFrame,
                                                    df_jokes:pd.DataFrame,
                                                    num_jokes_to_recommend:int=10):
    
    # get the user ratings
    user_ratings = df_ratings_up[df_ratings_up.user_id == user_id]
    
    # create a dict with the jokes and their respective ratings
    already_rated = dict(zip(user_ratings.joke_id, user_ratings.rating))
    
    # create a dict to store predicted ratings
    pred_ratings = {}
    
    # loop through jokes
    for i, row in df_jokes.iterrows():
        
        # make predictions for each joke
        pred_ratings[row.joke_id] = svd.predict(uid=user_id, iid=row.joke_id).est
        
    # sort jokes by their predicted rating
    pred_ratings_sorted = sorted(pred_ratings.items(), key=lambda x:x[1], reverse=True)
    
    # create a set to store jokes to be recommended
    jokes_to_recommend = set()
    
    # loop through jokes
    for joke_id, predicted_rating in pred_ratings_sorted:
        
        # check if the joke is already rated by the user
        if joke_id not in already_rated:
            
            # add to the set of jokes to be recommended
            jokes_to_recommend.add(joke_id)
            
            # check if reached the predefined number of jokes to recommend
            if len(jokes_to_recommend) == num_jokes_to_recommend: break
            
    # create a dataframe with the recommender jokes
    df_rec = pd.DataFrame(df_jokes[df_jokes.joke_id.isin(jokes_to_recommend)])
    
    # append the predicted rating
    df_rec['predicted_rating'] = df_rec.joke_id.map(pred_ratings)
    
    # sort jokes by their predicted rating
    df_rec = df_rec.sort_values(['predicted_rating'], ascending=False)
    
    return df_rec

# ---------------------------------------------------------------------------------------------------
# Function to evaluate the recommendations provided by matrix factorization (SVD)
# ---------------------------------------------------------------------------------------------------

def evaluate_recommendations_by_matrix_factorization(svd, # SVD class from surprise library
                                                     user_id:int,
                                                     df_ratings_up:pd.DataFrame,
                                                     df_jokes:pd.DataFrame):
    
    # get the user ratings
    user_ratings = df_ratings_up[df_ratings_up.user_id == user_id]
    
    # create a dict with the jokes and their respective ratings
    already_rated = dict(zip(user_ratings.joke_id, user_ratings.rating))
    
    # create a dict to store predicted ratings
    pred_ratings = {}
    
    # loop through jokes
    for i, row in df_jokes.iterrows():
        
        # make predictions for each joke
        pred_ratings[row.joke_id] = svd.predict(uid=user_id, iid=row.joke_id).est
        
    # initialize lists to store actual and predicted ratings
    actual, predicted = list(), list()
    
    # loop through rated jokes
    for joke_id in already_rated:
        
        # append actual and predicted ratings
        actual.append(already_rated[joke_id])
        predicted.append(pred_ratings[joke_id])
    
    # calculate RMSE
    rmse = mean_squared_error(actual, predicted, squared=False)
    
    # round
    rmse_rounded = round(rmse,2)
    
    # display result
    print(f'RMSE: {rmse_rounded}')
    
    return