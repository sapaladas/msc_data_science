#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from unidecode import unidecode

# ---------------------------------------------------------------------------------------------------
# Function to keep and rename only the (pre-decided) desired columns
# ---------------------------------------------------------------------------------------------------

def keep_and_rename_desired_columns(df:pd.DataFrame) -> pd.DataFrame:

    # list of columns to keep
    to_keep = [
        'Title',
        'Genre',
        'Tags',
        'Runtime',
        'Director',
        'Actors',
        'IMDb Score',
        'Release Date',
        'Production House',
        'Summary'
    ]

    # keep desired columns
    df = df[to_keep]

    # renaming schema
    to_rename = {
        'Title':'title',
        'Genre':'genre',
        'Tags':'tags',
        'Runtime':'runtime',
        'Director':'director',
        'Actors':'actors',
        'IMDb Score':'rating',
        'Release Date':'ryear',
        'Production House':'prod_house',
        'Summary':'summary'
    }

    # rename columns
    df = df.rename(columns=to_rename)

    return df

# ---------------------------------------------------------------------------------------------------
# Function to preprocess the data and bring it to the appropriate format
# ---------------------------------------------------------------------------------------------------

def preprocess_data(df:pd.DataFrame) -> pd.DataFrame:

    # create a copy to work on
    df_copy = df.copy()

    # mapping schema
    # of the runtime of each movie
    runtime_mapping = {
        '< 30 minutes':'15',
        '30-60 mins':'45',
        '1-2 hour':'90',
        '> 2 hrs':'150'
    }

    # transform runtime column
    df_copy.runtime = df_copy.runtime.map(runtime_mapping)

    # parse only the year from each movie's release date
    df_copy.ryear = df_copy.ryear.dt.strftime('%Y')

    # parse each movie's production house
    df_copy.prod_house = df_copy.prod_house.apply(lambda x: x.split(',')[0] if x is not np.nan else 'Unknown')

    # for the shake of the exercise
    # drop rows with null values to avoid any hassle
    df_copy = df_copy.dropna().reset_index()

    # convert column values from float to int
    df_copy.runtime = df_copy.runtime.astype(int)
    df_copy.ryear = df_copy.ryear.astype(int)

    # convert all characters to standard latin
    to_unidecode = ['director','actors']
    for col in to_unidecode:
        df_copy[col] = df_copy[col].apply(lambda x: unidecode(x))
    
    # get each movie's star actor
    df_copy['star_actor'] = df_copy.actors.apply(lambda x: x.split(',')[0] if x is not np.nan else x)

    return df_copy