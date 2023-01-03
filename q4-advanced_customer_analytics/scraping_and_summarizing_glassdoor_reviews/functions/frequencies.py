#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import spacy
nlp = spacy.load('en_core_web_lg')
from nltk.tokenize import sent_tokenize
from collections import defaultdict

# ------------------------------------------------------------------------------
# Function to count word and doc frequency
# ------------------------------------------------------------------------------

def count_word_frequencies(reviews:list, stop_words:list, nlp:spacy.lang.en.English):
    """
    Scope
    -----
    This function is used to count both word and doc frequency for each word included in the reviews.
    
    Parameters
    ----------
    reviews : list
        List of reviews whose words will be counted.
    stop_words : list
        List of stopwords of the English language.
    nlp : spacy.lang.en.English
        Spacy NLP object.

    Returns
    -------
    freq_word : dict
        Dictionary of word frequency.
    freq_doc : dict
        Dictionary of doc frequency.
    df_concat : pd.DataFrame
        DataFrame containing both word and doc frequency.
    """
    
    # initialize empty dicts
    freq_word = defaultdict(int)
    freq_doc = defaultdict(int)
    
    # loop through
    # the list of reviews
    for review in reviews:
        
        # initialize a temp dict
        freq_word_temp = defaultdict(int)
        
        # split review into sentences
        sentences = sent_tokenize(review)
        
        # loop through sentences
        for sentence in sentences:
            
            # create a spacy object
            nlp_obj = nlp(sentence)
            
            # list of tokens (lemma) that are nouns and have length greater than 3
            tokens = [token.lemma_.lower() for token in nlp_obj if ((token.pos_=='NOUN') & (len(token.lemma_)>3))]
            
            # loop through tokens
            for token in tokens:
                
                # check if token is alpha and not a stopword
                if token.isalpha() & (token not in stop_words):
                    
                    # append token
                    freq_word_temp[token]+=1
        
        # append the frequency values for the tokens of the review in loop
        freq_word = {key: freq_word.get(key, 0) + freq_word_temp.get(key, 0) for key in set(freq_word) | set(freq_word_temp)}
        
        # update the doc frequency values
        for key, _ in freq_word_temp.items():
            freq_doc[key]+=1
    
    # create dfs for word frequency and doc frequency
    df_word = pd.DataFrame(freq_word.items(), columns=['word','word_frequency'])
    df_doc = pd.DataFrame(freq_doc.items(), columns=['word','doc_frequency'])
    
    # concat dfs
    df_concat = df_word.merge(df_doc, on='word', how='inner')
    
    return freq_word, freq_doc, df_concat

# ------------------------------------------------------------------------------
# Function to get top k distinct words
# ------------------------------------------------------------------------------

def get_top_k_distinct_pros_and_cons_words(df1:pd.DataFrame,
                                           df2:pd.DataFrame,
                                           df1_word_column:str='word',
                                           df2_word_column:str='word',
                                           df1_word_freq_column:str='word_frequency',
                                           df2_word_freq_column:str='word_frequency',
                                           k:int=5):
    """
    Scope
    -----
    This function is used to find the top k words that appear ONLY either in pros or cons.

    Parameters
    ----------
    df1 : pd.DataFrame
        The DataFrame with either pros or cons.
    df2 : pd.DataFrame
        The DataFrame with either pros or cons.
    df1_word_column : str, optional
        The name of the column of the words in df1.
    df2_word_column : str, optional
        The name of the column of the words in df2.
    df1_word_freq_column : str, optional
        The name of the column of the words frequency in df1.
    df2_word_freq_column : str, optional
        The name of the column of the words frequency in df2.
    k : int, optional
        The number of top words we want the function to return.

    Returns
    -------
    df1_only : pd.DataFrame
        DataFrame with top k words that appear only in df1.
    df2_only : pd.DataFrame
        DataFrame with top k words that appear only in df2.
    """
    
    # find the top k words that appear only in df1
    words_only_df1 = [word for word in df1[df1_word_column] if word not in df2[df2_word_column].to_list()]
    df1_only = df1[df1[df1_word_column].isin(words_only_df1)].sort_values(by=df1_word_freq_column, ascending=False)
    df1_only = df1_only.iloc[0:k,:]
    df1_only[df1_word_column] = [w.capitalize() if len(w)>3 else w.upper() for w in df1_only[df1_word_column]]
    
    # find the top k words that appear only in df2
    words_only_df2 = [word for word in df2[df2_word_column] if word not in df1[df1_word_column].to_list()]
    df2_only = df2[df2[df2_word_column].isin(words_only_df2)].sort_values(by=df2_word_freq_column, ascending=False)
    df2_only = df2_only.iloc[0:k,:]
    df2_only[df2_word_column] = [w.capitalize() if len(w)>3 else w.upper() for w in df2_only[df2_word_column]]
    
    return df1_only, df2_only

# ------------------------------------------------------------------------------
# Function to get top k words appearing most frequently in each of two dataframes
# ------------------------------------------------------------------------------

def get_top_k_mixed_pros_and_cons_words(df_pros:pd.DataFrame,
                                        df_cons:pd.DataFrame,
                                        df_pros_word_column:str='word',
                                        df_cons_word_column:str='word',
                                        df_pros_word_freq_column:str='word_frequency',
                                        df_cons_word_freq_column:str='word_frequency',
                                        df_pros_doc_freq_column:str='doc_frequency',
                                        df_cons_doc_freq_column:str='doc_frequency',
                                        k:int=5):
    """
    Scope
    -----
    The scope of this function is to find the top k words that appear MOST FREQUENTLY either in pros or cons.

    Parameters
    ----------
    df_pros : pd.DataFrame
        The DataFrame with pros.
    df_cons : pd.DataFrame
        The DataFrame with cons.
    df_pros_word_column : str, optional
        The name of the column of the words in df_pros.
    df_cons_word_column : str, optional
        The name of the column of the words in df_cons.
    df_pros_word_freq_column : str, optional
        The name of the column of the words frequency in df_pros.
    df_cons_word_freq_column : str, optional
        The name of the column of the words frequency in df_cons.
    df_pros_doc_freq_column : str, optional
        The name of the column of the doc frequency in df_pros.
    df_cons_doc_freq_column : str, optional
        The name of the column of the doc frequency in df_cons.
    k : int, optional
        The number of top words we want the function to return.

    Returns
    -------
    top_k_pros : pd.DataFrame
        DataFrame with top k words that appear most frequently in df_pros.
    top_k_cons : pd.DataFrame
        DataFrame with top k words that appear most frequently in df_cons.
    merged : pd.DataFrame
        Merged DataFrame of the aforementioned ones.
    """
    
    # rename pros columns
    df_pros = df_pros.rename(columns={df_pros_word_column:'word',
                                      df_pros_word_freq_column:'word_frequency',
                                      df_pros_doc_freq_column:'doc_frequency'})
    
    # rename cons columns
    df_cons = df_cons.rename(columns={df_cons_word_column:'word',
                                      df_cons_word_freq_column:'word_frequency',
                                      df_cons_doc_freq_column:'doc_frequency'})
    
    # merge dataframes
    merged = df_pros.merge(df_cons, on='word', how='outer')
    merged.fillna(0, inplace=True)
    merged['total_count'] = merged.word_frequency_x.astype(int) + merged.word_frequency_y.astype(int)
    
    # --------------------------------------------------------------------------
    # Create the Work Life Balance acronym to be treated as a single word
    # --------------------------------------------------------------------------

    # initialize conditions    
    work = merged.word == 'work'
    life = merged.word == 'life'
    balance = merged.word == 'balance'
    
    # find the minimum word and doc frequency among words "work", "life","balance",
    # and use this number number as the total number of occurences for the word WLB
    word_freq_x = np.min([merged[work]['word_frequency_x'],
                      merged[life]['word_frequency_x'],
                      merged[balance]['word_frequency_x']])
    
    doc_freq_x = np.min([merged[work]['doc_frequency_x'],
                         merged[life]['doc_frequency_x'],
                         merged[balance]['doc_frequency_x']])
    
    word_freq_y = np.min([merged[work]['word_frequency_y'],
                          merged[life]['word_frequency_y'],
                          merged[balance]['word_frequency_y']])
    
    doc_freq_y = np.min([merged[work]['doc_frequency_y'],
                         merged[life]['doc_frequency_y'],
                         merged[balance]['doc_frequency_y']])
    
    # get the number of total occurences of "work","life","balance"
    w = merged[work].total_count.values[0]
    l = merged[life].total_count.values[0]
    b = merged[balance].total_count.values[0]
    
    # get the min number of occurences
    # to subtract this value from the values of "work","life","balance"
    min_count = np.min([w,l,b])
    
    # create and append a new record for the WLB acronym
    new = ['wlb', word_freq_x, doc_freq_x, word_freq_y, doc_freq_y, min_count]
    merged.loc[len(merged.index)] = new
    
    # get the indices of the words "work","life","balance" in the dataframe
    wlb_idx_list = [idx for idx in merged.index if merged.loc[idx, 'word'] in ['work','life','balance']]
    
    # subtract their values by the min_count above
    merged.loc[wlb_idx_list, 'total_count'] = merged.total_count - min_count
    
    # --------------------------------------------------------------------------
    # Get the top k words appearing MOST FREQUENTLY in pros or cons
    # --------------------------------------------------------------------------
    
    # depending on whether a word appears more frequently in pros or cons, label it accordingly
    merged['label'] = np.where(merged.word_frequency_x > merged.word_frequency_y, 'positive', 'negative')
    
    # sort values by total_count
    merged = merged.sort_values(by='total_count', ascending=False)
    
    # capitalize words
    merged.word = [w.capitalize() if len(w)>3 else w.upper() for w in merged.word]
    
    # get top k words discussed in pros
    top_k_pros = merged[merged.label == 'positive'].iloc[0:k,:].sort_values(by='word_frequency_x', ascending=False)
    top_k_pros = top_k_pros.rename(columns={'word_frequency_x':'word_frequency'})
    top_k_pros = top_k_pros.loc[:,['word','word_frequency']]
    
    # get top k words discussed in cons
    top_k_cons = merged[merged.label == 'negative'].iloc[0:k,:].sort_values(by='word_frequency_y', ascending=False)
    top_k_cons = top_k_cons.rename(columns={'word_frequency_y':'word_frequency'})
    top_k_cons = top_k_cons.loc[:,['word','word_frequency']]
    
    return top_k_pros, top_k_cons, merged