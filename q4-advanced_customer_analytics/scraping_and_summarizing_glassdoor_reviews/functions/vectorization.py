#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

def get_most_similar_and_frequently_shown_sentences(sentences:str,
                                                    ngram_range:tuple=(1,1),
                                                    stop_words:list=list(),
                                                    max_features:int=None,
                                                    threshold:float=0.1):
    """
    Scope
    -----
    This function is used to get the most similar and frequently shown sentences among the reviews.

    Parameters
    ----------
    sentences : str
        The review sentences.
    ngram_range : tuple, optional
        The ngrams that will be used for the sentence vectorization.
    stop_words : list, optional
        List of stopwords of the English language.
    max_features : int, optional
        The maximum number of features that will be retrieved from sentence vectorization.
    threshold : float, optional
        The percentage of the total sententes that will be retrieved as similar

    Returns
    -------
    similar_sentences
        List of the most similar and frequently shown sentences.

    """
    
    # split into sentences
    sentences = sent_tokenize(sentences)
    
    # lowercase and keep only sentences with more than 5 characters
    sentences = [s.lower() for s in sentences if len(s) > 5]
    
    # create a vectorizer instance
    vectorizer = TfidfVectorizer(ngram_range=ngram_range,
                                 stop_words=stop_words,
                                 max_features=max_features,
                                 use_idf=False,
                                 sublinear_tf=True)
    
    # create the sparse matrix
    matrix = vectorizer.fit_transform(sentences)

    # get the average vector value of each sentence
    avg_vectors = []
    for sent_index in range(matrix.shape[0]):
        avg_vectors.append(matrix.todense()[sent_index].mean())
    
    # get the average vector value among all sentences
    avg = np.mean(avg_vectors)
    
    # number of sentences to retrieve
    sents_to_get = int(len(sentences) * threshold)

    # function to retrieve the indices
    # of the k nearest values to the avg vector value
    def find_k_nearest_indices_to_mean_value(array:list, value:float, k:int): # isws na to dokimasw kai me Bert
        return np.argsort(abs(array - value))[:k]
    # execute the function
    index_list = find_k_nearest_indices_to_mean_value(avg_vectors, avg, sents_to_get)
            
    # get the sentences within boundaries
    sentences_list = []
    for sent_index in range(matrix.shape[0]):
        if sent_index in index_list:
            sentences_list.append(sentences[sent_index].capitalize())
    
    similar_sentences = list(set(sentences_list))
    
    return similar_sentences