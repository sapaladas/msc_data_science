#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------------------------------------
# Plot the number of reviews per rating (e.g, 1 star, 2 stars, etc.)
# ------------------------------------------------------------------------------

def plot_number_of_reviews_per_rating(df:pd.DataFrame,
                                      rating_column:str='rating'):
    """
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame with our scraped data.
    rating_column : str
        The column name which contains the review ratings.
    filepath : str
        The path to the folder in which we want to save the graphs.

    Returns
    -------
    None.
    """
    
    # create the figure
    plt.figure(figsize=(9,6), dpi=100)
    
    # plot countplot
    ax = sns.countplot(data=df, x=rating_column, palette='RdYlGn', edgecolor='black', linewidth=.5)
    
    # add bar height labels
    ax.bar_label(ax.containers[0], padding=3)
    
    # params
    plt.xlabel(None)
    plt.ylabel(None)
    plt.yticks([])
    plt.title('Number of Reviews per Rating')
    
    # save image
    plt.tight_layout()
    plt.savefig('./images/number_of_reviews_per_rating.png', bbox_inches='tight')
    plt.close()

# ------------------------------------------------------------------------------
# Plot the number of reviews and average rating per year
# ------------------------------------------------------------------------------

def plot_number_of_reviews_and_avg_rating_per_year(df:pd.DataFrame,
                                                   date_column:str='date',
                                                   rating_column:str='rating'):
    """
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame with our scraped data.
    date_column : str
        The column name which contains the date each review was posted.
    rating_column : str
        The column name which contains the review ratings.
    filepath : str
        The path to the folder in which we want to save the graphs.

    Returns
    -------
    None.
    """
    
    # dummy (0,1) rating features
    df['r1'] = df[rating_column].apply(lambda x: 1 if x == 1 else 0)
    df['r2'] = df[rating_column].apply(lambda x: 1 if x == 2 else 0)
    df['r3'] = df[rating_column].apply(lambda x: 1 if x == 3 else 0)
    df['r4'] = df[rating_column].apply(lambda x: 1 if x == 4 else 0)
    df['r5'] = df[rating_column].apply(lambda x: 1 if x == 5 else 0)
    
    # group ratings by year
    grouped = df.groupby(df[date_column].dt.year).agg({'rating':'mean','r1':'sum','r2':'sum','r3':'sum','r4':'sum','r5':'sum'})
    
    # arrays of N-star ratings by year
    r1 = grouped.loc[:,'r1'].values # 1-star ratings
    r2 = grouped.loc[:,'r2'].values # 2-star ratings
    r3 = grouped.loc[:,'r3'].values # 3-star ratings
    r4 = grouped.loc[:,'r4'].values # 4-star ratings
    r5 = grouped.loc[:,'r5'].values # 5-star ratings
    r_ = r5 + r4 + r3 + r2 + r1     # workaround to show total value label in bars
    
    # array of average rating by year - to be used in lineplot
    avg_ratings = grouped.loc[:,rating_column].values
    
    # define the starting height of each star rating bar
    h1 = r5 + r4 + r3 + r2 # starting height for 1-star bar
    h2 = r5 + r4 + r3 # starting height for 2-star bar
    h3 = r5 + r4 # starting height for 3-star bar
    h4 = r5 # starting height for 4-star bar
    h5 = 0 # starting height for 5-star bar
    
    # create the figure
    fig, ax = plt.subplots(figsize=(9,6), dpi=100)
    
    # create the color palette
    palette = sns.color_palette('RdYlGn', 5).as_hex()
    
    # plot bars in primary y-axis
    ax.bar(grouped.index, r_, color='white', alpha=0.0)
    ax.bar(grouped.index, r5, bottom=h5, color=palette[4], edgecolor='black', linewidth=.5)
    ax.bar(grouped.index, r4, bottom=h4, color=palette[3], edgecolor='black', linewidth=.5)
    ax.bar(grouped.index, r3, bottom=h3, color=palette[2], edgecolor='black', linewidth=.5)
    ax.bar(grouped.index, r2, bottom=h2, color=palette[1], edgecolor='black', linewidth=.5)
    ax.bar(grouped.index, r1, bottom=h1, color=palette[0], edgecolor='black', linewidth=.5)
    
    # add bar height labels
    ax.bar_label(ax.containers[0], padding=3)
    
    # params in primary y-axis
    ax.set_yticks([])
    ax.set_title('Number of Reviews & Avg Rating per Year')
    
    # plot lineplot in secondary y-axis
    ax2 = ax.twinx()
    ax2.plot(grouped.index, avg_ratings, marker='o', markersize=5, color='black', linewidth=1)
    
    # params in secondary y-axis
    ax2.set_ylim(0,5)
    
    # save fig
    plt.tight_layout()
    plt.savefig('./images/number_of_reviews_and_avg_rating_per_year.png', bbox_inches='tight')
    plt.close()
    
# ------------------------------------------------------------------------------
# Plot the top k words
# ------------------------------------------------------------------------------
    
def plot_top_k_words(df:pd.DataFrame,
                     word_column:str='word',
                     word_freq_column:str='word_frequency',
                     is_pros:bool=True,
                     is_distinct:bool=True):
    """
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame with the words we want to provide.
    word_column : str, optional
        The name of the column of the words.
    word_freq_column : str, optional
        The name of the column of the words frequency.
    is_pros : bool, optional
        Whether the words provided are words from pros.
    is_distinct : bool, optional
        Whether the words provided appear ONLY in one DataFrame.

    Returns
    -------
    None.
    """
    
    # create the figure
    plt.figure(figsize=(6,6), dpi=100)
    
    # plot barplot
    palette = 'Greens_r' if is_pros else 'Reds_r'
    ax = sns.barplot(data=df, y=word_column, x=word_freq_column, palette=palette)
    
    # add bar height labels
    ax.bar_label(ax.containers[0], padding=5)
    
    # params
    plt.xlabel(None)
    plt.ylabel(None)
    plt.xticks([])
    plt.xlim(0,df[word_freq_column].max()*1.1)
    
    # custom title
    pros_or_cons = 'Pros' if is_pros else 'Cons'
    only_or_mixed = 'ONLY' if is_distinct else 'MOST FREQUENTLY'
    plt.title(f'Top {len(df)} words appearing {only_or_mixed} in {pros_or_cons}')
    
    # save image
    plt.tight_layout()
    plt.savefig(f'./images/top_{len(df)}_words_{only_or_mixed}_in_{pros_or_cons}.png', bbox_inches='tight')
    plt.close()