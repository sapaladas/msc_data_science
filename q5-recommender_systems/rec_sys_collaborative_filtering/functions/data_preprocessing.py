#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------------------------------
# Function to preprocess the ratings dataset and bring it to the appropriate format
# ---------------------------------------------------------------------------------------------------

def preprocess_ratings_dataset(df:pd.DataFrame) -> pd.DataFrame:
    
    # rename index to "user_id"
    df.index.names = ['user_id']
    
    # increment to start counting from 1
    df.index += 1
    
    # replace 99 with nan values
    df.replace(99, np.nan, inplace=True)
    
    return df

# ---------------------------------------------------------------------------------------------------
# Function to preprocess the jokes dataset and bring it to the appropriate format
# ---------------------------------------------------------------------------------------------------

def preprocess_jokes_dataset(df:pd.DataFrame) -> pd.DataFrame:
    
    # reset index to use as joke_id
    df.reset_index(inplace=True)
    
    # rename the column to "joke_id"
    df.rename(columns={'index':'joke_id'}, inplace=True)
    
    # increment to start counting from 1
    df.joke_id += 1
    
    return df

# ---------------------------------------------------------------------------------------------------
# Function to load all the ratings submitted by each user
# ---------------------------------------------------------------------------------------------------

def unpivot_ratings(df:pd.DataFrame) -> pd.DataFrame:
    
    # create a copy of the initial df
    df_unpivot = df.copy()
    
    # reset index to use as identifier variable in pandas melt
    df_unpivot.reset_index(inplace=True)
    
    # unpivot the data
    df_unpivot = pd.melt(df_unpivot, id_vars='user_id', var_name='joke_id', value_name='rating')
    
    # drop rows of jokes that are not rated by each user
    df_unpivot.dropna(subset='rating', inplace=True)
    
    # sort data by user_id
    df_unpivot.sort_values(by='user_id', ascending=True, ignore_index=True, inplace=True)
    
    return df_unpivot